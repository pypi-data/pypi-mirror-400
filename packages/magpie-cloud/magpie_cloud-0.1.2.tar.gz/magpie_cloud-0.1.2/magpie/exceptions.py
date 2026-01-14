"""
Exception classes for Magpie SDK
"""


class MagpieError(Exception):
    """Base exception for all Magpie SDK errors"""
    pass


class AuthenticationError(MagpieError):
    """Raised when authentication fails"""
    pass


class JobNotFoundError(MagpieError):
    """Raised when a job is not found"""
    pass


class TemplateNotFoundError(MagpieError):
    """Raised when a template is not found"""
    pass


class ValidationError(MagpieError):
    """Raised when validation fails"""
    pass


class APIError(MagpieError):
    """Raised for general API errors"""
    pass


class TimeoutError(MagpieError):
    """Raised when an operation times out"""
    pass