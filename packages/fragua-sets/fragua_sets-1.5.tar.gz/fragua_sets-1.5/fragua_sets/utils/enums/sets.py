"""Sets Enum."""

from enum import Enum


class Sets(str, Enum):
    """Sets enum class."""

    UTILITY = "utility"
    EXTRACTION = "extraction"
    LOADING = "loading"
    PIPELINES = "pipelines"
