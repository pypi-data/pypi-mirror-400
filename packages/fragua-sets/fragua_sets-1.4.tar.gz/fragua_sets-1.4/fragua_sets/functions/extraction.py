"""Extraction type functions."""

from typing import Callable, Dict, List, Optional, Union, Any, cast

import requests
from sqlalchemy.engine import Engine

import pandas as pd

# pylint: disable=too-many-arguments


def extract_from_csv(
    path: str,
    *,
    sep: str = ",",
    encoding: Optional[str] = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Extract data from a CSV file into a pandas DataFrame.

    This function is a thin wrapper around pandas.read_csv and is intended
    to be used as an extraction primitive within Fragua pipelines.

    Parameters
    ----------
    path:
        Path to the CSV file.
    sep:
        Column separator used in the CSV file.
    encoding:
        Optional file encoding (e.g. 'utf-8', 'latin-1').
    **kwargs:
        Additional keyword arguments forwarded to pandas.read_csv.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the extracted data.
    """
    # Read CSV file using pandas
    df = pd.read_csv(
        path,
        sep=sep,
        encoding=encoding,
        **kwargs,
    )

    return cast(pd.DataFrame, df)


def extract_from_excel(
    path: str,
    *,
    sheet_name: Union[str, int] = 0,
    **kwargs: Any,
) -> pd.DataFrame:
    """
        Extract data from an Excel file into a pandas DataFrame.

        This function wraps pandas.read_excel and provides a minimal,
        explicit interface suitable for ETL pipelines.

        Parameters
        ----------
        path:
            Path to the Excel file.
        sheet_name:
            Name of the sheet to read. If None, the first sheet is used.
        **kwargs:
            Additional keyword arguments forwarded to pandas.read_excel.
    |
        Returns
        -------
        pd.DataFrame
            DataFrame containing the extracted data.
    """
    # Read Excel file using pandas
    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        **kwargs,
    )

    return df


def extract_from_api(
    url: str,
    *,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_path: Optional[str] = None,
    timeout: int = 30,
) -> pd.DataFrame:
    """
    Extract data from an HTTP API endpoint into a pandas DataFrame.

    This function performs an HTTP request and assumes the response
    body contains JSON data that can be normalized into tabular form.

    Parameters
    ----------
    url:
        API endpoint URL.
    method:
        HTTP method to use (e.g. 'GET', 'POST').
    headers:
        Optional HTTP headers.
    params:
        Optional query parameters or request payload.
    json_path:
        Optional key to extract a nested list from the JSON response.
        If None, the full JSON response is used.
    timeout:
        Request timeout in seconds.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the extracted data.
    """
    # Perform HTTP request
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        timeout=timeout,
    )

    # Raise exception for non-success status codes
    response.raise_for_status()

    # Parse JSON response
    data = response.json()

    # Extract nested data if a json_path is provided
    if json_path is not None:
        data = data.get(json_path, [])

    # Normalize JSON data into a DataFrame
    df = pd.json_normalize(data)

    return df


def extract_from_database(
    engine: Engine,
    query: str,
    *,
    params: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Extract data from a relational database into a pandas DataFrame.

    This function executes a SQL query using a SQLAlchemy engine
    and returns the result as a DataFrame.

    Parameters
    ----------
    engine:
        SQLAlchemy Engine instance connected to the target database.
    query:
        SQL query to execute.
    params:
        Optional query parameters.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the extracted data.
    """
    # Execute SQL query and load result into a DataFrame
    df = pd.read_sql_query(
        sql=query,
        con=engine,
        params=params,
    )

    return df


EXTRACTION_FUNCTIONS: List[Callable[..., pd.DataFrame]] = [
    extract_from_excel,
    extract_from_csv,
    extract_from_api,
    extract_from_database,
]
