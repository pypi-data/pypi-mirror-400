#!/usr/bin/env python


from compliance_checker.base import BaseCheck, Result, TestCtx

import numpy as np
from esgvoc import api as voc
import re


def check_attribute_suite(
    ds,
    attribute_name,
    severity,
    value_type=None,
    is_required=True,
    cv_collection=None,
    cv_collection_key=None,
    constraint=None,
    var_name=None,
    project_name=None,
    attribute_nc_name=None,
):
    """
    Generic attribute validation suite.

    ATTR001 — Existence
    ATTR002 — Type
    ATTR003 — UTF-8 Encoding
    ATTR004 — Value validation (Regex or ESGVOC)
    """
    if var_name:
        nc_attrs = ds.variables[var_name].ncattrs() if var_name in ds.variables else []
    else:
        nc_attrs = ds.ncattrs()

    if attribute_nc_name:
        nc_key = attribute_nc_name
    else:
        matches = [a for a in nc_attrs if a.lower() == attribute_name.lower()]
        nc_key = matches[0] if matches else attribute_name

    # Label builder
    def label(code, desc):
        prefix = f"[{code}]"
        if var_name:
            return (
                f"{prefix} {var_name} | {desc}: Variable Attribute '{attribute_name}'"
            )
        else:
            return f"{prefix} {desc}: Global Attribute '{attribute_name}'"

    results = []
    attr_value = None

    # =========================================================
    # ATTR001 — EXISTENCE
    # =========================================================
    existence_ctx = TestCtx(severity, label("ATTR001", "Existence"))
    try:
        if var_name:
            if var_name not in ds.variables:
                existence_ctx.add_failure(
                    f"Cannot check attribute '{attribute_name}' because variable '{var_name}' does not exist."
                )
                results.append(existence_ctx.to_result())
                return results

            attr_value = ds.variables[var_name].getncattr(nc_key)
        else:
            attr_value = ds.getncattr(nc_key)

        existence_ctx.add_pass()
        results.append(existence_ctx.to_result())

    except AttributeError:
        if is_required:
            existence_ctx.add_failure(
                f"Required attribute '{attribute_name}' (NetCDF key '{nc_key}') is missing."
            )
            results.append(existence_ctx.to_result())

        return results

    if attr_value is None:
        return results

    # =========================================================
    # ATTR002 — TYPE CHECK
    # =========================================================
    if value_type:
        type_ctx = TestCtx(severity, label("ATTR002", "Type"))

        type_map = {
            "str": str,
            "int": (int, np.integer),
            "float": (float, np.floating),
            "str_array": list,  # <--- NEW
        }

        expected_py_type = type_map.get(str(value_type).lower())

        # Convert raw NetCDF value into correct runtime type for "str_array"
        if value_type == "str_array":
            attr_value_for_type = str(attr_value).strip().split()
        else:
            attr_value_for_type = attr_value

        if expected_py_type is None:
            type_ctx.add_failure(f"Invalid value_type '{value_type}'.")
        elif isinstance(attr_value_for_type, expected_py_type):
            type_ctx.add_pass()
        else:
            type_ctx.add_failure(
                f"Type mismatch: got {type(attr_value).__name__}, expected {expected_py_type}."
            )

        results.append(type_ctx.to_result())

    # =========================================================
    # ATTR003 — UTF-8 ENCODING
    # =========================================================
    if isinstance(attr_value, str):
        utf8_ctx = TestCtx(severity, label("ATTR003", "UTF-8 Encoding"))
        try:
            attr_value.encode("utf-8")
            utf8_ctx.add_pass()
        except UnicodeEncodeError:
            utf8_ctx.add_failure("Non UTF-8 characters detected.")
        results.append(utf8_ctx.to_result())

    # =========================================================
    # ATTR004 — Value Validation
    # =========================================================

    # ---------- CASE A: REGEX ----------
    if constraint is not None:
        pattern_ctx = TestCtx(severity, label("ATTR004", "Regex Match Check"))
        try:
            if re.fullmatch(constraint, str(attr_value)):
                pattern_ctx.add_pass()
            else:
                pattern_ctx.add_failure(
                    f"Value '{attr_value}' does not match regex '{constraint}'."
                )
        except re.error:
            pattern_ctx.add_failure(f"Invalid regex expression '{constraint}'.")
        results.append(pattern_ctx.to_result())
        return results

    # ---------- CASE B: ESGVOC ----------
    if cv_collection:
        vocab_ctx = TestCtx(severity, label("ATTR004", "ESGVOC Vocabulary Check"))
        if value_type == "str_array":
            values = str(attr_value).strip().split()
        else:
            values = [attr_value]

        invalid = []

        try:
            for val in values:
                if cv_collection_key:
                    term = voc.get_term_in_collection(
                        project_id=project_name,
                        collection_id=cv_collection,
                        term_id=cv_collection_key,
                    )

                    if not term:
                        vocab_ctx.add_failure(
                            f"Term '{cv_collection_key}' not found in collection '{cv_collection}'."
                        )
                        results.append(vocab_ctx.to_result())
                        return results

                    expected_val = str(term.value).strip()

                    if str(val).strip() != expected_val:
                        invalid.append(val)

                else:
                    if not voc.valid_term_in_collection(
                        value=val, project_id=project_name, collection_id=cv_collection
                    ):
                        invalid.append(val)

            if invalid:
                vocab_ctx.add_failure(
                    f"Invalid values {invalid} for CV '{cv_collection}'."
                )
            else:
                vocab_ctx.add_pass()

        except Exception as e:
            vocab_ctx.add_failure(f"Vocabulary lookup error: {e}")

        results.append(vocab_ctx.to_result())

    return results
