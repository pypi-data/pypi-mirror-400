"""Functions Enum."""

from enum import Enum


# ----------------------------
# EXTRACTION FUNCTIONS
# ----------------------------
class ExtractionFunction(str, Enum):
    """Extraction function types."""

    EXTRACT_FROM_CSV = "extract_from_csv"
    EXTRACT_FROM_EXCEL = "extract_from_excel"
    EXTRACT_FROM_API = "extract_from_api"
    EXTRACT_FROM_DB = "extract_from_database"


# ----------------------------
# TRANSFORMATION FUNCTIONS
# ----------------------------


class TransfomationFunction(str, Enum):
    """Transformation functions."""

    STRIP_WHITESPACE = "strip_whitespace"
    FILL_MISSING_VALUES = "fill_missing_values"
    CREATE_DERIVED_COLUMN = "create_derived_column"
    CAPITALIZE_STRING_COLUMNS = "capitalize_string_columns"

    NORMALIZE_COLUMN_NAMES = "normalize_column_names"
    DROP_NULLS_IN_COLUMNS = "drop_nulls_in_columns"
    PARSE_DATETIME_COLUMN = "parse_datetime_column"
    CREATE_SUM_COLUMN = "create_sum_column"
    FILTER_BY_MIN_VALUE = "filter_by_min_value"

    STRIP_STRING_COLUMNS = "strip_string_columns"
    FILL_NULLS_WITH_VALUE = "fill_nulls_with_value"
    RENAME_COLUMNS = "rename_columns"
    CAST_COLUMN_TO_NUMERIC = "cast_column_to_numeric"
    SORT_BY_COLUMN = "sort_by_column"


# ----------------------------
# LOAD FUNCTIONS
# ----------------------------
class LoadFunction(str, Enum):
    """Extraction function types."""

    LOAD_TO_CSV = "load_to_csv"
    LOAD_TO_EXCEL = "load_to_excel"
    LOAD_TO_API = "load_to_api"
    LOAD_TO_DB = "load_to_database"


# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------
class UtilityFunction(str, Enum):
    """Extraction function types."""

    PATH_EXISTS = "path_exists"
    ENSURE_DIR_EXISTS = "ensure_dir_exists"
    ENSURE_PARENT_DIR_EXISTS = "ensure_parent_dir_exists"
