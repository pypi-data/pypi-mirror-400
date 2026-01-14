"""Transform Functions."""

from typing import Any, Callable, Dict, List
import pandas as pd


def drop_nulls_in_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Drop rows with null values in specified columns.
    """
    return df.dropna(subset=columns)


def parse_datetime_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Convert a column to datetime.
    """
    df_copy = df.copy()
    df_copy[column] = pd.to_datetime(df_copy[column], errors="coerce")
    return df_copy


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names: lowercase and replace spaces with underscores.
    """
    df_copy = df.copy()
    df_copy.columns = df_copy.columns.str.strip().str.lower().str.replace(" ", "_")
    return df_copy


def filter_by_min_value(
    df: pd.DataFrame, column: str, min_value: float
) -> pd.DataFrame:
    """
    Filter rows where column value is greater than or equal to min_value.
    """
    return df[df[column] >= min_value]


def create_sum_column(
    df: pd.DataFrame, col_a: str, col_b: str, new_col: str
) -> pd.DataFrame:
    """
    Create a new column as the sum of two existing columns.
    """
    df_copy = df.copy()
    df_copy[new_col] = df_copy[col_a] + df_copy[col_b]
    return df_copy


def add_total_price_derived_column(
    df: pd.DataFrame,
    *,
    col_a: str,
    col_b: str,
) -> pd.DataFrame:
    """
    Create a derived column from two existing columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    col_a : str
        First source column name.
    col_b : str
        Second source column name.
    new_col : str
        Name of the derived column to create.
    operation : Callable
        Function that receives two pandas Series and returns a Series.

    Returns
    -------
    pd.DataFrame
        DataFrame with the derived column added.

    Raises
    ------
    KeyError
        If any of the source columns do not exist.
    """
    if col_a not in df.columns:
        raise KeyError(f"Column '{col_a}' does not exist in DataFrame")

    if col_b not in df.columns:
        raise KeyError(f"Column '{col_b}' does not exist in DataFrame")

    df = df.copy()
    df["total_price"] = df[col_a] * df[col_b]

    return df


def strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove leading and trailing whitespace from all string columns
    in a pandas DataFrame.
    """
    df = df.copy()

    string_cols = df.select_dtypes(include=["object", "string"]).columns

    for col in string_cols:
        df[col] = df[col].astype("string").str.strip()

    return df


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in a DataFrame.

    - Numeric columns are filled with their mean.
    - Categorical / string columns are filled with 'desconocido'.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with missing values filled.
    """
    df = df.copy()

    # Numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        mean_value = df[col].mean()
        df[col] = df[col].fillna(mean_value)

    # Categorical / string columns
    categorical_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in categorical_cols:
        df[col] = df[col].fillna("desconocido")

    return df


def capitalize_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Capitalize all string / categorical columns in a DataFrame.

    Example:
        'montevideo' -> 'Montevideo'
        'SALTO'      -> 'Salto'

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with capitalized string columns.
    """
    df = df.copy()

    string_cols = df.select_dtypes(include=["object", "string"]).columns

    for col in string_cols:
        df[col] = df[col].astype("string").str.capitalize()

    return df


def strip_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip leading and trailing whitespace from all string columns.
    """
    df_copy = df.copy()
    string_columns = df_copy.select_dtypes(include="object").columns

    for col in string_columns:
        df_copy[col] = df_copy[col].str.strip()

    return df_copy


def fill_nulls_with_value(df: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
    """
    Fill null values in a specific column with a fixed value.
    """
    df_copy = df.copy()
    df_copy[column] = df_copy[column].fillna(value)
    return df_copy


def rename_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Rename columns using a mapping dictionary.
    """
    return df.rename(columns=mapping)


def cast_column_to_numeric(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Cast a column to numeric type.
    """
    df_copy = df.copy()
    df_copy[column] = pd.to_numeric(df_copy[column], errors="coerce")
    return df_copy


def sort_by_column(
    df: pd.DataFrame, column: str, ascending: bool = True
) -> pd.DataFrame:
    """
    Sort DataFrame by a column.
    """
    return df.sort_values(by=column, ascending=ascending)


TRANSFORMATION_FUNCTIONS: List[Callable[..., pd.DataFrame]] = [
    strip_whitespace,
    fill_missing_values,
    add_total_price_derived_column,
    capitalize_string_columns,
    drop_nulls_in_columns,
    normalize_column_names,
    parse_datetime_column,
    filter_by_min_value,
    create_sum_column,
    cast_column_to_numeric,
    rename_columns,
    fill_nulls_with_value,
    strip_string_columns,
    sort_by_column,
]
