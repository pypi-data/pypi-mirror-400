"""Custom exceptions for dvt."""


class DvtError(Exception):
    """Base exception for all dvt errors."""


class ConfigurationError(DvtError):
    """Error in configuration or environment setup."""


class ModelNotFoundError(DvtError):
    """Requested model was not found."""


class ValidationError(DvtError):
    """Error during validation execution."""
