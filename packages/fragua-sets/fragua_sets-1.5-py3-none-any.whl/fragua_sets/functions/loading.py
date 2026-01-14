"""Load type functions."""

from typing import Any, Callable, Dict, List, Literal, Optional

import requests
from sqlalchemy.engine import Engine

import pandas as pd

from fragua.utils.helpers.get_project_root import get_project_root

# pylint: disable=too-many-arguments


def load_to_csv(
    df: pd.DataFrame,
    filename: str,
    sep: str = ",",
    subdir: str = "pipeline_output",
) -> None:
    """
    Save a DataFrame to a CSV file in the project root.
    """
    base_path = get_project_root()
    output_dir = base_path / subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / filename
    df.to_csv(file_path, sep=sep, index=False)


def load_to_excel(
    df: pd.DataFrame,
    filename: str,
    subdir: str = "pipeline_output",
    *,
    sheet_name: str = "Sheet1",
    index: bool = False,
    **kwargs: Any,
) -> None:
    """
    Load a pandas DataFrame into an Excel file.

    This function writes the DataFrame to an Excel file using
    pandas.to_excel.

    Parameters
    ----------
    df:
        DataFrame to be persisted.
    filename:
        Destination filename.
    subdir:
        Subdirectory within project root.
    sheet_name:
        Name of the Excel sheet.
    index:
        Whether to write row indices.
    **kwargs:
        Additional keyword arguments forwarded to pandas.to_excel.
    """
    base_path = get_project_root()
    output_dir = base_path / subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / filename
    df.to_excel(
        file_path,
        sheet_name=sheet_name,
        index=index,
        **kwargs,
    )


def load_to_database(
    df: pd.DataFrame,
    engine: Engine,
    table_name: str,
    *,
    if_exists: Literal["fail", "replace", "append", "delete_rows"] = "append",
    index: bool = False,
    **kwargs: Any,
) -> None:
    """
    Load a pandas DataFrame into a relational database table.

    This function uses pandas.to_sql to persist data into a database
    via a SQLAlchemy engine.

    Parameters
    ----------
    df:
        DataFrame to be persisted.
    engine:
        SQLAlchemy Engine connected to the target database.
    table_name:
        Name of the destination table.
    if_exists:
        Behavior if the table already exists ('fail', 'replace', 'append').
    index:
        Whether to write row indices as a column.
    **kwargs:
        Additional keyword arguments forwarded to pandas.to_sql.
    """
    # Persist DataFrame into database table
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists=if_exists,
        index=index,
        **kwargs,
    )


def load_to_api(
    df: pd.DataFrame,
    url: str,
    *,
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    json_orient: Literal[
        "dict",
        "list",
        "series",
        "split",
        "tight",
        "records",
        "index",
    ] = "records",
) -> None:
    """
    Load a pandas DataFrame to an HTTP API endpoint.

    The DataFrame is serialized to JSON and sent as the request body.

    Parameters
    ----------
    df:
        DataFrame to be sent.
    url:
        API endpoint URL.
    method:
        HTTP method to use (e.g. 'POST', 'PUT').
    headers:
        Optional HTTP headers.
    timeout:
        Request timeout in seconds.
    json_orient:
        JSON orientation used when serializing the DataFrame.
    """
    # Serialize DataFrame to JSON-compatible structure
    payload = df.to_dict(orient=json_orient)

    # Perform HTTP request
    response = requests.request(
        method=method,
        url=url,
        json=payload,
        headers=headers,
        timeout=timeout,
    )

    # Raise exception for non-success status codes
    response.raise_for_status()


LOADING_FUNCTIONS: List[Callable[..., None]] = [
    load_to_api,
    load_to_csv,
    load_to_database,
    load_to_excel,
]
