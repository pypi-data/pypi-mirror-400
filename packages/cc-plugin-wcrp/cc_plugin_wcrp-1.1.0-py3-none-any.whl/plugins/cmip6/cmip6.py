#!/usr/bin/env python
# =============================================================================
# WCRP CMIP6 project
# =============================================================================

from __future__ import annotations

import os
import re
from typing import Dict, Optional, List, Literal, Any, Tuple

import toml
from netCDF4 import Dataset
from pydantic import BaseModel, Field, model_validator

from compliance_checker.base import BaseCheck, TestCtx
from plugins.wcrp_base import WCRPBaseCheck
from checks.attribute_checks.check_attribute_suite import check_attribute_suite
from checks.variable_checks.check_variable_existence import check_variable_existence
from checks.variable_checks.check_variable_type import check_variable_type
from checks.dimension_checks.check_dimension_existence import check_dimension_existence
from checks.dimension_checks.check_dimension_positive import check_dimension_positive
from checks.dimension_checks.check_dimension_size import (
    check_dimension_size_is_equals_to,
)
from checks.variable_checks.check_bounds_value_consistency import (
    check_bounds_value_consistency,
)
from checks.consistency_checks.check_drs_filename_cv import (
    check_drs_filename,
    check_drs_directory,
)
from checks.consistency_checks.check_drs_consistency import (
    check_attributes_match_directory_structure,
    check_filename_matches_directory_structure,
)
from checks.consistency_checks.check_attributes_match_filename import (
    check_filename_vs_global_attrs,
)
from checks.consistency_checks.check_variant_label_consistency import (
    check_variant_label_consistency,
)
from checks.consistency_checks.check_frequency_table_consistency import (
    check_frequency_table_id_consistency,
)
from checks.consistency_checks.check_experiment_consistency import (
    check_experiment_consistency,
)
from checks.consistency_checks.check_institution_source_consistency import (
    check_institution_consistency,
    check_source_consistency,
)
from checks.format_checks.check_compression import check_compression
from checks.format_checks.check_format import check_format
from checks.time_checks.check_time_bounds import check_time_bounds
from checks.time_checks.check_time_range_vs_filename import check_time_range_vs_filename
from checks.time_checks.check_time_squareness import check_time_squareness


# --- CF Checker helpers ---
try:
    from compliance_checker.cf.util import (
        get_geophysical_variables,
        get_coordinate_variables,  # To find lat(lat), lon(lon), time(time)
        get_auxiliary_coordinate_variables,  # To find height, etc.
    )
except ImportError as e:
    raise ImportError("Unable to import utils from compliance_checker.cf.util.") from e

# --- ESGVOC (Variable Registry) ---
try:
    from esgvoc import api as voc

    ESG_VOCAB_AVAILABLE = True
except Exception:
    ESG_VOCAB_AVAILABLE = False

try:
    from esgvoc.api.universe import find_terms_in_data_descriptor
except Exception:
    find_terms_in_data_descriptor = None


# =============================================================================
# Pydantic models
# =============================================================================

Severity = Literal["H", "M", "L"]
ValueType = Literal["str", "int", "float", "str_array"]


class SimpleCheck(BaseModel):
    severity: Severity


class AttributeRule(BaseModel):
    severity: Severity
    value_type: ValueType
    is_required: bool = True
    attribute_name: Optional[str] = None
    constraint: Optional[str] = None
    cv_source_collection: Optional[str] = None
    cv_source_collection_key: Optional[str] = None

    @model_validator(mode="after")
    def _exclusive_rules(self):
        if self.constraint and self.cv_source_collection:
            raise ValueError(
                "constraint and cv_source_collection are mutually exclusive"
            )
        return self


class FileFormatRule(BaseModel):
    severity: Severity
    expected_format: str
    expected_data_model: str


class FileCompressionRule(BaseModel):
    severity: Severity
    expected_complevel: int
    expected_shuffle: bool


class FileChecks(BaseModel):
    format: Optional[FileFormatRule] = None
    compression: Optional[FileCompressionRule] = None


class DrsChecks(BaseModel):
    filename: Optional[SimpleCheck] = None
    directory: Optional[SimpleCheck] = None
    attributes_vs_directory: Optional[SimpleCheck] = None  # PATH001
    filename_vs_directory: Optional[SimpleCheck] = None  # PATH002


class TimeSquarenessRule(BaseModel):
    severity: Severity
    calendar: str = ""
    ref_time_units: str = ""
    frequency: Dict[str, str] = Field(default_factory=dict)


class TimeSection(BaseModel):
    squareness: Optional[TimeSquarenessRule] = None


class ConsistencyChecks(BaseModel):
    variant_label: Optional[SimpleCheck] = None
    filename_vs_attributes: Optional[SimpleCheck] = None
    experiment_details: Optional[SimpleCheck] = None
    institution_details: Optional[SimpleCheck] = None
    source_details: Optional[SimpleCheck] = None
    freq_tableid: Optional[SimpleCheck] = None


class VariableAttributesSection(BaseModel):
    severity: Optional[Severity] = None
    items: Dict[str, SimpleCheck] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _split_severity_and_items(cls, values):
        if values is None or not isinstance(values, dict):
            return values
        sev = values.get("severity")
        items = {k: v for k, v in values.items() if k != "severity"}
        return {"severity": sev, "items": items}


class VariableSection(BaseModel):
    existence: Optional[SimpleCheck] = None
    type: Optional[SimpleCheck] = None
    dimensions: Optional[SimpleCheck] = None
    attributes: Optional[VariableAttributesSection] = None
    shape_bounds: Optional[SimpleCheck] = None
    bnds_vertices: Optional[SimpleCheck] = None
    time_checks: Optional[SimpleCheck] = None


class CoordinatesSection(BaseModel):
    auxiliary: Optional[SimpleCheck] = None
    bounds: Optional[SimpleCheck] = None
    properties: Optional[SimpleCheck] = None
    time: Optional[TimeSection] = None


class CMIP6Config(BaseModel):
    project_name: str
    project_version: str
    drs: Optional[DrsChecks] = None
    file: Optional[FileChecks] = None
    global_attributes: Dict[str, AttributeRule] = Field(default_factory=dict)
    variable_attributes: Optional[Dict[str, Dict[str, AttributeRule]]] = None
    variable: Optional[VariableSection] = None
    coordinates: Optional[CoordinatesSection] = None
    consistency_checks: Optional[ConsistencyChecks] = None
    frequency_table_id_mapping: Optional[Dict[str, List[str]]] = None


# =============================================================================
# CMIP6 Project Checker
# =============================================================================


class Cmip6ProjectCheck(WCRPBaseCheck):
    _cc_spec = "wcrp_cmip6"
    _cc_spec_version = "1.0"
    _cc_description = "WCRP Project Checks"
    supported_ds = [Dataset]

    def __init__(self, options=None):
        super().__init__(options)
        self.project_name = "cmip6"
        self.config: Optional[CMIP6Config] = None
        self._geo_var_cache = None
        self._vr_expected_cache = None
        self._vr_expected_dims_cache = None

        if options and "project_config_path" in options:
            self.project_config_path = options["project_config_path"]
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            self.project_config_path = os.path.join(
                this_dir, "resources", "wcrp_config.toml"
            )

    def setup(self, ds):
        super().setup(ds)
        self._load_project_config()
        self._load_mapping()
        if self.consistency_output:
            self._write_consistency_output()
        self._geo_var_cache = None
        self._vr_expected_cache = None
        self._vr_expected_dims_cache = None

    def _load_project_config(self):
        if not os.path.exists(self.project_config_path):
            raise RuntimeError(f"Config not found: {self.project_config_path}")
        with open(self.project_config_path, "r", encoding="utf-8") as f:
            self.config = CMIP6Config(**toml.load(f))

    def _load_mapping(self):
        """
        Load the mapping file by searching in two locations:
        1. Root directory (where cmip6.py is located)
        2. Resources directory
        """
        # 1. Search in root directory
        root_dir = os.path.dirname(os.path.abspath(__file__))
        path_root = os.path.join(root_dir, "mapping_variables.toml")

        # 2. Search in resources directory
        config_dir = os.path.dirname(self.project_config_path)
        path_resources = os.path.join(config_dir, "mapping_variables.toml")

        path_to_use = None
        if os.path.exists(path_root):
            path_to_use = path_root
        elif os.path.exists(path_resources):
            path_to_use = path_resources

        if not path_to_use:
            print(
                f"WARNING: mapping_variables.toml not found in {root_dir} or {config_dir}"
            )
            self.variable_mapping = {}
            return

        try:
            with open(path_to_use, "r", encoding="utf-8") as f:
                data = toml.load(f)
                self.variable_mapping = data.get("mapping_variables", {})
                if not self.variable_mapping:
                    print(
                        f"WARNING: File {path_to_use} loaded but [mapping_variables] section is empty."
                    )
        except Exception as e:
            print(f"CRITICAL ERROR loading mapping {path_to_use}: {e}")
            self.variable_mapping = {}

    # --- Helpers ---
    def _get_geo_var(self, ds, severity) -> Tuple[Optional[str], List[Any]]:
        if self._geo_var_cache and self._geo_var_cache in ds.variables:
            return self._geo_var_cache, []
        results = []
        try:
            geo_vars = list(get_geophysical_variables(ds))
        except Exception as e:
            ctx = TestCtx(severity, "Geophysical Variable Detection")
            ctx.add_failure(f"Error detecting variables: {e}")
            results.append(ctx.to_result())
            return None, results

        if len(geo_vars) != 1:
            ctx = TestCtx(severity, "Geophysical Variable Detection")
            ctx.add_failure(
                f"Expected exactly 1 geophysical variable, found {len(geo_vars)}: {geo_vars}"
            )
            results.append(ctx.to_result())
            return None, results

        self._geo_var_cache = geo_vars[0]
        return self._geo_var_cache, results

    def _get_expected_from_registry(self, ds, severity):
        if self._vr_expected_cache is not None:
            return self._vr_expected_cache, self._vr_expected_dims_cache, []

        results = []

        if not ESG_VOCAB_AVAILABLE or find_terms_in_data_descriptor is None:
            # If library is missing, we just return empty
            return None, None, results

        try:
            variable_id = ds.getncattr("variable_id")
            table_id = ds.getncattr("table_id")
        except Exception as e:
            ctx = TestCtx(severity, "Variable Registry")
            ctx.add_failure(f"Missing required attributes for VR lookup: {e}")
            results.append(ctx.to_result())
            return None, None, results

        mapping_key = f"{table_id}.{variable_id}"
        branded = getattr(self, "variable_mapping", {}).get(mapping_key)

        if not branded:
            ctx = TestCtx(severity, "Variable Registry")
            ctx.add_failure(
                f"No mapping found for '{mapping_key}' in mapping_variables.toml"
            )
            results.append(ctx.to_result())
            return None, None, results

        fields_to_get = [
            "cf_standard_name",
            "cf_units",
            "dimensions",
            "cell_methods",
            "cell_measures",
            "description",
            "long_name",
        ]

        expected = None
        try:
            terms = find_terms_in_data_descriptor(
                expression=str(branded),
                data_descriptor_id="known_branded_variable",
                only_id=True,
                selected_term_fields=fields_to_get,
            )
            if terms:
                expected = terms[0]
        except Exception as e:
            ctx = TestCtx(severity, "Variable Registry")
            ctx.add_failure(f"Error querying ESGVOC (find_terms) for '{branded}': {e}")
            results.append(ctx.to_result())
            return None, None, results

        if not expected:
            ctx = TestCtx(severity, "Variable Registry")
            ctx.add_failure(f"Term '{branded}' not found in Variable Registry.")
            results.append(ctx.to_result())
            return None, None, results

        # Extract dimensions
        try:
            expected_dims = getattr(expected, "dimensions", []) or []
        except Exception:
            expected_dims = []

        self._vr_expected_cache = expected
        self._vr_expected_dims_cache = expected_dims

        return expected, expected_dims, results

    @staticmethod
    def _fuzzy_match_dim(expected, actuals):
        if expected in actuals:
            return expected
        for a in actuals:
            if a in expected or expected in a:
                return a
        return None

    # --- File Checks ---
    def check_File_Format(self, ds):
        if not self.config or not self.config.file or not self.config.file.format:
            return []
        r = self.config.file.format
        return check_format(
            ds, r.expected_format, r.expected_data_model, self.get_severity(r.severity)
        )

    def check_File_Compression(self, ds):
        if not self.config or not self.config.file or not self.config.file.compression:
            return []
        r = self.config.file.compression
        return check_compression(
            ds,
            None,
            r.expected_complevel,
            r.expected_shuffle,
            self.get_severity(r.severity),
        )

    def check_Drs_Vocabulary(self, ds):
        res = []
        if self.config and self.config.drs:
            if self.config.drs.filename:
                res.extend(
                    check_drs_filename(
                        ds,
                        self.get_severity(self.config.drs.filename.severity),
                        self.project_name,
                    )
                )
            if self.config.drs.directory:
                res.extend(
                    check_drs_directory(
                        ds,
                        self.get_severity(self.config.drs.directory.severity),
                        self.project_name,
                    )
                )
        return res

    # --- Attribute Checks ---
    def check_Global_Variable_Attributes(self, ds):
        res = []
        if not self.config:
            return res

        # 1. Global Attributes
        for k, r in self.config.global_attributes.items():
            res.extend(
                check_attribute_suite(
                    ds=ds,
                    attribute_name=k,
                    attribute_nc_name=r.attribute_name,
                    severity=self.get_severity(r.severity),
                    value_type=r.value_type,
                    is_required=r.is_required,
                    constraint=r.constraint,
                    cv_collection=r.cv_source_collection,
                    cv_collection_key=r.cv_source_collection_key,
                    var_name=None,
                    project_name=self.project_name,
                )
            )

        if self.config.variable_attributes:
            for v, attrs in self.config.variable_attributes.items():
                for k, r in attrs.items():
                    res.extend(
                        check_attribute_suite(
                            ds=ds,
                            attribute_name=k,
                            attribute_nc_name=r.attribute_name,
                            severity=self.get_severity(r.severity),
                            value_type=r.value_type,
                            is_required=r.is_required,
                            constraint=r.constraint,
                            cv_collection=r.cv_source_collection,
                            cv_collection_key=r.cv_source_collection_key,
                            var_name=v,
                            project_name=self.project_name,
                        )
                    )
        return res

    # --- Variable Checks ---
    def check_variable_existence(self, ds):
        res = []
        if (
            not self.config
            or not self.config.variable
            or not self.config.variable.existence
        ):
            return res
        sev = self.get_severity(self.config.variable.existence.severity)
        geo, r = self._get_geo_var(ds, sev)
        res.extend(r)
        if geo:
            res.extend(check_variable_existence(ds, geo, sev))
        return res

    def check_variable_type(self, ds):
        res = []
        if not self.config or not self.config.variable or not self.config.variable.type:
            return res
        sev = self.get_severity(self.config.variable.type.severity)
        geo, r = self._get_geo_var(ds, sev)
        res.extend(r)
        if geo:
            # For geophysical variable, we expect strict float ('f')
            res.extend(check_variable_type(ds, geo, allowed_types=["f"], severity=sev))
        return res

    def check_variable_dimensions(self, ds):
        """
        [variable.dimensions]
        Checks existence of dimensions and compares with Variable Registry.
        """
        res = []
        if (
            not self.config
            or not self.config.variable
            or not self.config.variable.dimensions
        ):
            return res

        sev = self.get_severity(self.config.variable.dimensions.severity)
        geo, r = self._get_geo_var(ds, sev)
        res.extend(r)
        if not geo:
            return res

        # 1. Checks on actual dimensions
        act = list(ds.variables[geo].dimensions)
        for d in act:
            res.extend(check_dimension_existence(ds, d, sev))
            res.extend(check_dimension_positive(ds, d, sev))
            res.extend(check_variable_existence(ds, d, sev))

        # 2. Comparison with Variable Registry (VR)
        exp, exp_dims, vr_r = self._get_expected_from_registry(ds, sev)
        res.extend(vr_r)

        if exp_dims:
            # --- VAR000: Count comparison ---
            ctx_len = TestCtx(BaseCheck.MEDIUM, "[VAR000] Dimensions count vs VR")

            if len(act) == len(exp_dims):
                ctx_len.add_pass()
            else:
                ctx_len.add_failure(
                    f"Variable '{geo}' has {len(act)} dims {act}, "
                    f"but VR expects {len(exp_dims)} {exp_dims}. "
                    "(Note: Scalar coordinates like 'height' are often counted in VR but absent from dims)"
                )
            res.append(ctx_len.to_result())
            # --------------------------------------

            # 3. Fuzzy Match of names
            for ed in exp_dims:
                eds = str(ed)
                if eds in {"bnds", "axis_nbounds", "vertices", "nv4"}:
                    continue
                if self._fuzzy_match_dim(eds, act):
                    continue
                if eds.lower().startswith("height") and "height" in ds.variables:
                    continue

                res.extend(check_dimension_existence(ds, eds, sev))

        return res

    def check_variable_attributes_registry(self, ds):
        res = []
        if (
            not self.config
            or not self.config.variable
            or not self.config.variable.attributes
        ):
            return res
        d_sev = (
            self.get_severity(self.config.variable.attributes.severity)
            if self.config.variable.attributes.severity
            else BaseCheck.HIGH
        )
        geo, r = self._get_geo_var(ds, d_sev)
        res.extend(r)
        if not geo:
            return res
        exp, _, vr_r = self._get_expected_from_registry(ds, d_sev)
        res.extend(vr_r)
        if not exp:
            return res

        mapping = {
            "units": ("cf_units", "units"),
            "standard_name": ("cf_standard_name", "standard_name"),
            "cell_methods": ("cell_methods", "cell_methods"),
            "cell_measures": ("cell_measures", "cell_measures"),
            "description": ("description", "description"),
            "long_name": ("long_name", "long_name"),
        }

        for k, item in self.config.variable.attributes.items.items():
            sev = self.get_severity(item.severity) if item else d_sev
            if k in mapping:
                vr_f, nc_a = mapping[k]
                val = getattr(exp, vr_f, None)
                if val and str(val).strip():
                    # Explicit format
                    res.extend(
                        check_attribute_suite(
                            ds=ds,
                            attribute_name=nc_a,
                            attribute_nc_name=None,
                            severity=sev,
                            value_type="str",
                            is_required=True,
                            constraint=re.escape(str(val).strip()),
                            cv_collection=None,
                            cv_collection_key=None,
                            var_name=geo,
                            project_name=self.project_name,
                        )
                    )
        return res

    def check_variable_bounds(self, ds):
        res = []
        if self.config and self.config.variable and self.config.variable.shape_bounds:
            sev = self.get_severity(self.config.variable.shape_bounds.severity)
            geo, r = self._get_geo_var(ds, sev)
            if geo:
                res.extend(check_bounds_value_consistency(ds, geo, sev))
        return res

    def check_variable_bnds_vertices(self, ds):
        res = []
        if self.config and self.config.variable and self.config.variable.bnds_vertices:
            sev = self.get_severity(self.config.variable.bnds_vertices.severity)
            for d, s in [("bnds", 2), ("axis_nbounds", 2), ("vertices", 4), ("nv4", 4)]:
                if d in ds.dimensions:
                    res.extend(check_dimension_size_is_equals_to(ds, d, s, sev))
        return res

    def check_variable_time_checks(self, ds):
        res = []
        if self.config and self.config.variable and self.config.variable.time_checks:
            sev = self.get_severity(self.config.variable.time_checks.severity)
            if "time" in ds.variables:
                res.extend(check_time_range_vs_filename(ds, sev))
                res.extend(check_time_bounds(ds, sev))
        return res

    # --- Coordinates Checks ---
    def check_coordinates_auxiliary(self, ds):
        res = []
        if (
            not self.config
            or not self.config.coordinates
            or not self.config.coordinates.auxiliary
        ):
            return res
        sev = self.get_severity(self.config.coordinates.auxiliary.severity)
        geo, r = self._get_geo_var(ds, sev)
        res.extend(r)
        if geo:
            try:
                for n in str(ds.variables[geo].getncattr("coordinates")).split():
                    res.extend(check_variable_existence(ds, n.strip(), sev))
            except Exception:
                pass
        return res

    def check_coordinates_bounds(self, ds):
        res = []
        if (
            not self.config
            or not self.config.coordinates
            or not self.config.coordinates.bounds
        ):
            return res
        sev = self.get_severity(self.config.coordinates.bounds.severity)
        geo, r = self._get_geo_var(ds, sev)
        if not geo:
            return res
        cand = set()
        try:
            cand.update(ds.variables[geo].dimensions)
        except (AttributeError, KeyError):
            pass
        try:
            cand.update(str(ds.variables[geo].getncattr("coordinates")).split())
        except (AttributeError, KeyError):
            pass
        for c in cand:
            if c in ds.variables and hasattr(ds.variables[c], "bounds"):
                res.extend(check_variable_existence(ds, ds.variables[c].bounds, sev))
        return res

    def check_coordinates_properties(self, ds):
        """
        Checks type (float/int) and units for all coordinate variables.
        """
        res = []
        if (
            not self.config
            or not self.config.coordinates
            or not self.config.coordinates.properties
        ):
            return res

        sev = self.get_severity(self.config.coordinates.properties.severity)

        try:
            coords_dim = get_coordinate_variables(ds)
            coords_aux = get_auxiliary_coordinate_variables(ds)
            all_coords = set(coords_dim + coords_aux)
        except Exception as e:
            ctx = TestCtx(sev, "Coordinates Discovery")
            ctx.add_failure(f"Failed to identify coordinates: {e}")
            res.append(ctx.to_result())
            return res

        for cname in all_coords:
            if cname not in ds.variables:
                continue
            var = ds.variables[cname]

            # Skip string labels
            if var.dtype.kind in ["S", "U", "O"]:
                continue

            # Check Type (allow float or int)
            res.extend(
                check_variable_type(ds, cname, allowed_types=["f", "i"], severity=sev)
            )

            # Skip technical variables for units check
            if hasattr(var, "compress") or "bnds" in cname or "bounds" in cname:
                continue

            # Check Units
            res.extend(
                check_attribute_suite(
                    ds=ds,
                    attribute_name="units",
                    severity=sev,
                    is_required=True,
                    var_name=cname,
                    project_name=self.project_name,
                )
            )

        return res

    def check_coordinates_time_squareness(self, ds):
        res = []

        if (
            not self.config
            or not self.config.coordinates
            or not self.config.coordinates.time
            or not self.config.coordinates.time.squareness
        ):
            return res

        rule = self.config.coordinates.time.squareness
        sev = self.get_severity(rule.severity)

        res.extend(
            check_time_squareness(
                ds,
                severity=sev,
                calendar=rule.calendar or "",
                ref_time_units=rule.ref_time_units or "",
                frequency=rule.frequency or {},
            )
        )
        return res

    # --- Consistency Checks ---

    def check_consistency_drs_from_config(self, ds):
        res = []
        if not self.config or not self.config.drs:
            return res

        # 1. Check PATH001
        if self.config.drs.attributes_vs_directory:
            sev = self.get_severity(self.config.drs.attributes_vs_directory.severity)
            res.extend(
                check_attributes_match_directory_structure(ds, sev, self.project_name)
            )

        # 2. Check PATH002
        if self.config.drs.filename_vs_directory:
            sev = self.get_severity(self.config.drs.filename_vs_directory.severity)
            res.extend(
                check_filename_matches_directory_structure(ds, sev, self.project_name)
            )

        return res

    def check_consistency_filename(self, ds):
        res = []
        if (
            self.config
            and self.config.consistency_checks
            and self.config.consistency_checks.filename_vs_attributes
        ):
            sev = self.get_severity(
                self.config.consistency_checks.filename_vs_attributes.severity
            )
            res.extend(check_filename_vs_global_attrs(ds, sev))
        return res

    def check_frequency_consistency(self, ds):
        res = []
        if (
            self.config
            and self.config.consistency_checks
            and self.config.consistency_checks.freq_tableid
        ):
            sev = self.get_severity(
                self.config.consistency_checks.freq_tableid.severity
            )
            res.extend(
                check_frequency_table_id_consistency(
                    ds, self.config.frequency_table_id_mapping or {}, sev
                )
            )
        return res

    def check_experiment_consistency(self, ds):
        res = []
        if (
            self.config
            and self.config.consistency_checks
            and self.config.consistency_checks.experiment_details
        ):
            sev = self.get_severity(
                self.config.consistency_checks.experiment_details.severity
            )
            res.extend(check_experiment_consistency(ds, sev, self.project_name))
        return res

    def check_variantlabel_consistency(self, ds):
        res = []
        if (
            self.config
            and self.config.consistency_checks
            and self.config.consistency_checks.variant_label
        ):
            sev = self.get_severity(
                self.config.consistency_checks.variant_label.severity
            )
            res.extend(check_variant_label_consistency(ds, sev))
        return res

    def check_consistency_institution_source(self, ds):
        res = []
        if not self.config or not self.config.consistency_checks:
            return res
        if self.config.consistency_checks.institution_details:
            sev = self.get_severity(
                self.config.consistency_checks.institution_details.severity
            )
            res.extend(check_institution_consistency(ds, sev, self.project_name))
        if self.config.consistency_checks.source_details:
            sev = self.get_severity(
                self.config.consistency_checks.source_details.severity
            )
            res.extend(check_source_consistency(ds, sev, self.project_name))
        return res
