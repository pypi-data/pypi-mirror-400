"""Setup file."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fragua-sets",
    version="1.4",
    author="SagoDev",
    description="Package with fragua sets with reutilizable functions for ETL process.",
    packages=find_packages(where=".", include=["fragua_sets", "fragua_sets.*"]),
    include_package_data=True,
    package_data={"fragua-sets": ["py.typed"]},
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    url="https://github.com/SagoDev/fragua-sets",
    install_requires=[
        "fragua",
        "requests",
        "pandas",
        "numpy",
        "sqlalchemy",
    ],
)
