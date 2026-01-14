"""Data Validation Tool - CLI for dbt data validation workflows."""

try:
    from importlib.metadata import version

    __version__ = version("data-validation-tool")
except Exception:
    __version__ = "0.0.0"
