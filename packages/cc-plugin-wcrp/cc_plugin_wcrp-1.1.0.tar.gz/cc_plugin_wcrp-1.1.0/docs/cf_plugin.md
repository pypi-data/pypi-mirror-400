# CF Plugin (IOOS Compliance Checker)

The IOOS Compliance Checker ships with a native **CF (Climate & Forecast) metadata plugin**. Many of those CF checks are directly relevant to WCRP projects (CMIP, CORDEX, …). To avoid redundancy, we **did not duplicate** these validations inside ESGF-QC.

---

## Where to find detailed CF checks

- **Official IOOS Compliance Checker documentation** (complete list and descriptions):  
  [IOOS Compliance Checker](https://ioos.github.io/compliance-checker/)

- **Our internal summary table** :  

| check_name | check_description | CF 1.6 | CF 1.7 | CF 1.8 | CF 1.9 |
|---|---|---|---|---|---|
| check_filename | Verifies that the dataset’s filename ends with “.nc” | ✓ | ✓ | ✓ | ✓ |
| check_data_types | Ensures every variable uses one of the allowed data types (char, byte, short, int, float/real, double) | ✓ | ✓ | ✓ | ✓ |
| check_child_attr_data_types | For attributes like valid_min, valid_max, valid_range, _FillValue, actual_range, ensures each attribute’s type matches its parent variable’s type | ✓ | ✓ | ✓ | ✓ |
| check_add_offset_scale_factor_type | If a variable has both add_offset and scale_factor, checks they share the same type, or that integer variables use float/double attributes | ✓ | ✓ | ✓ | ✓ |
| check_naming_conventions | Validates that variable, dimension, and attribute names begin with a letter and consist only of letters, digits, and underscores | ✓ | ✓ | ✓ | ✓ |
| check_names_unique | Ensures names are unique regardless of case (i.e. no two names differ only by letter case), | ✓ | ✓ | ✓ | ✓ |
| check_dimension_names | Verifies that each variable’s dimensions all have distinct names (no duplicates) | ✓ | ✓ | ✓ | ✓ |
| check_dimension_order | Checks that spatio-temporal dimensions, if present, appear in the recommended T, Z, Y, X order, with any other dimensions to their left | ✓ | ✓ | ✓ | ✓ |
| check_fill_value_equal_missing_value | If both _FillValue and missing_value are defined on a variable, ensures they have the same numeric value | ✓ | ✓ | ✓ | ✓ |
| check_valid_range_and_valid_min_max_present | Checks that valid_range is not used in conjunction with valid_min or valid_max | ✓ | ✓ | ✓ | ✓ |
| check_fill_value_outside_valid_range | Ensures any _FillValue lies outside the declared valid_range (or outside valid_min/valid_max | ✓ | ✓ | ✓ | ✓ |
| check_convention_globals | Verifies that the global title and history attributes, if present, are non-empty strings  | ✓ | ✓ | ✓ | ✓ |
| check_coordinate_variables_strict_monotonicity | Checks that each 1D coordinate variable is strictly monotonic (either increasing or decreasing) | ✓ | ✓ | ✓ | ✓ |
| check_convention_possibly_var_attrs | For optional attributes (institution, source, references, comment), verifies any instance where they appear (globally or on variables) they are non-empty strings | ✓ | ✓ | ✓ | ✓ |
| check_units | For any variable requiring units (i.e. dimensional quantities excluding bounds and climatology), ensures: A units attribute exists (unless dimensionless), it’s a string, it’s recognized by UDUnits, it’s convertible to the CF “canonical” units for its standard name. | ✓ | ✓ | ✓ | ✓ |
| check_standard_name | Confirms that variables needing a standard_name (coordinate, auxiliary, flag, geophysical, etc.) have one; that it’s a valid string; and that it matches an entry in the CF Standard Name Table | ✓ | ✓ | ✓ | ✓ |
| check_ancillary_variables | Verifies that any variable listed in another’s ancillary_variables attribute actually exists in the file | ✓ | ✓ | ✓ | ✓ |
| check_flags | Ensures flag variables define flag_values and/or flag_masks, that they’re consistent in length with flag_meanings, share types with each other and with the variable, and combine correctly if both are presen | ✓ | ✓ | ✓ | ✓ |
| check_coordinate_types | Classifies and validates coordinate variables (time, latitude, longitude, vertical) against CF rules, ensuring they have the correct axis indicators or standard names  | ✓ | ✓ | ✓ | ✓ |
| check_latitude | Checks that latitude coordinate variables have standard_name="latitude", units="degrees_north", monotonic bounds, and axis="Y | ✓ | ✓ | ✓ | ✓ |
| check_longitude | Checks that longitude coordinate variables have standard_name="longitude", units="degrees_east", monotonic bounds, and axis="X" | ✓ | ✓ | ✓ | ✓ |
| check_dimensional_vertical_coordinate | Validates vertical coordinates (e.g. pressure, height) have appropriate units, positive, axis="Z" or a recognized standard name | ✓ | ✓ | ✓ | ✓ |
| check_dimensionless_vertical_coordinates | Ensures dimensionless vertical coordinates follow Appendix D rules: correct standard_name, optional formula_terms, and no units  | ✓ | ✓ | ✓ | ✓ |
| check_time_coordinate | Verifies time coordinates have standard_name="time", CF-compliant units, monotonic values, and correct reference-second (< 60) when a calendar is specified | ✓ | ✓ | ✓ | ✓ |
| check_calendar | Ensures any time variable with a calendar attribute uses a valid CF calendar string (e.g. “gregorian”, “noleap”) | ✓ | ✓ | ✓ | ✓ |
| check_standard_calendar_no_cross | Confirms no mixing of calendars across variables (e.g. all time coords use the same calendar), per CF recommendations. | ✓ | ✓ | ✓ | ✓ |
| check_aux_coordinates | Validates that any auxiliary coordinate listed in a variable’s coordinates attribute exists as a variable and has correct dimensionality  | ✓ | ✓ | ✓ | ✓ |
| check_duplicate_axis | Ensures no variable is assigned more than one axis role (e.g. X and Y simultaneously) | ✓ | ✓ | ✓ | ✓ |
| check_multi_dimensional_coords | Checks that 2D coordinate variables (e.g. latitude on a curvilinear grid) have appropriate shapes and monotonicity  | ✓ | ✓ | ✓ | ✓ |
| check_grid_coordinates | Validates that data variables either use standard lat/lon or specify a grid_mapping describing their projection | ✓ | ✓ | ✓ | ✓ |
| check_reduced_horizontal_grid | erifies reduced/grid-compression coordinates and their bounds follow CF rules | ✓ | ✓ | ✓ | ✓ |
| check_geographic_region | (Optional) Checks that any declared geographic extents or regions match actual coordinate ranges. | ✓ | ✓ | ✓ | ✓ |
| check_cell_boundaries | Ensures that any “bounds” variables referenced by bounds attributes exist, have one extra dimension, numeric type, and matching leading dimensions with CF-1.7 extensions (checking formula_terms on bounds) | ✓ | ✓ | ✓ | ✓ |
| check_cell_measures | Checks cell_measures attributes reference valid variables (e.g. area) and that those variables exist | ✓ | ✓ | ✓ | ✓ |
| check_cell_methods | Validates that any cell_methods string follows CF syntax (e.g. area: time: mean) | ✓ | ✓ | ✓ | ✓ |
| check_climatological_statistics | If a variable has climatology, ensures the referenced climatology variable exists and matches expected dimensions | ✓ | ✓ | ✓ | ✓ |
| check_packed_data | Verifies that packed data variables with scale_factor/add_offset conform to CF packing guidelines, including type matching  | ✓ | ✓ | ✓ | ✓ |
| check_compression_gathering | Ensures optional packing by “compression by gathering” (using scale/offset) is used correctly | ✓ | ✓ | ✓ | ✓ |
| check_feature_type | Checks any featureType attribute matches CF’s allowed feature types (e.g. timeSeries, trajectory) | ✓ | ✓ | ✓ | ✓ |
| check_cf_role | Validates that any variable with cf_role uses one of the CF-defined roles | ✓ | ✓ | ✓ | ✓ |
| check_variable_features | Ensures that variables representing features have the appropriate coordinate and metadata variables attached | ✓ | ✓ | ✓ | ✓ |
| check_hints | Processes any compliance hints (warnings) embedded in attributes, ensuring they don’t violate CF rules.  | ✓ | ✓ | ✓ | ✓ |
| check_external_variables | For CF 1.7+, checks global external_variables lists variables that must not be present in the file but are referenced elsewhere | nan | ✓ | ✓ | ✓ |
| check_actual_range | In CF 1.7+, if actual_range is provided, verifies it has two elements matching the true data min/max, matches unpacked data type, and lies within any valid_range/valid_min/valid_max | nan | ✓ | ✓ | ✓ |
| check_cell_boundaries_interval | In CF 1.7+, ensures the size of the boundary dimension matches the number of vertices for intervalL bounds | nan | ✓ | ✓ | ✓ |
| check_grid_mapping_attr_condition | Validates that each grid mapping variable defines the required attributes (grid_mapping_name, projection parameters) and that any grid_mapping attribute on data variables references an existing mapping | nan | ✓ | ✓ | ✓ |
| check_gmattr_existence_condition_geoid_name_geoptl_datum_name | In CF 1.7+, ensures that a grid mapping variable includes at most one of geoid_name or geopotential_datum_name, and that any provided value is valid in the PROJ vertical datum database | nan | ✓ | ✓ | ✓ |
| check_gmattr_existence_condition_ell_pmerid_hdatum | Also in CF 1.7+, checks ellipsoid_name, horizontal_datum_name, and prime_meridian_name attributes against approved lists or OGC WKT names. | nan | ✓ | ✓ | ✓ |
| check_standard_name_deprecated_modifiers | Warns if any variables use deprecated standard-name modifiers | nan | ✓ | ✓ | ✓ |
| check_dimensionless_vertical_coordinate_1_7 | CF 1.7 extension: additional validation of dimensionless vertical coords (formula_terms and computed_standard_name) against Appendix D 1.7 definitions. | nan | ✓ | ✓ | ✓ |
| check_groups | In CF 1.8+, ensures that attributes Conventions and external_variables appear only in the root group, while title and history may optionally appear in non-root groups | nan | nan | ✓ | ✓ |
| check_geometry | CF 1.8+: for any variable with a geometry attribute, checks associated node_coordinates, node_count, part_node_count, and interior_ring exist and form well-formed point/line/polygon definitions | nan | nan | ✓ | ✓ |
| check_taxa | CF 1.8+ verifies that biological_taxon_name and optional biological_taxon_lsid auxiliary coordinates are present and correctly formatted, and that LSID names match their resolved taxa  | nan | nan | ✓ | ✓ |
| check_time_coordinate_variable_has_calendar | CF 1.9 addition: ensures that every time coordinate variable has a calendar attribute of type string | nan | nan | nan | ✓ |
| check_domain_variables | CF 1.9 addition: for any “domain” variable (one with a coordinates attribute), verifies it has a dimensions attribute listing existing dimensions, that these are scalar dimensions, and that its coordinates reference valid coordinate variables; includes ragged-array support | nan | nan | nan | ✓ |


✨ PS :  You can also visit the **CF Convention website** : 

[![Cfconvention](img/CF_logo2.jpg)](https://cfconventions.org/)