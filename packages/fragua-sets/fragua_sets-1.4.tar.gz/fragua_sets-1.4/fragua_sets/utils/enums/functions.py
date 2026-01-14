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
    CAPITALIZE_STRINGS_COLUMNS = "capitalize_string_columns"


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
