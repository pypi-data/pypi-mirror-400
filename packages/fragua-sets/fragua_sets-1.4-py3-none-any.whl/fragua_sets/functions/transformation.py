"""Transform Functions."""

from typing import Callable, List
import pandas as pd


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


def create_derived_column(
    df: pd.DataFrame,
    *,
    col_a: str,
    col_b: str,
    new_col: str,
    operation: Callable[[pd.Series, pd.Series], pd.Series],
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
    df[new_col] = operation(df[col_a], df[col_b])

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


TRANSFORMATION_FUNCTIONS: List[Callable[..., pd.DataFrame]] = [
    strip_whitespace,
    fill_missing_values,
    create_derived_column,
    capitalize_string_columns,
]
