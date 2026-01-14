class PaddleException(Exception):
    """Base exception for Paddle SDK errors."""


class ApiError(PaddleException):
    """Exception raised for API-related errors."""


class ValidationError(PaddleException):
    """Exception raised for validation errors, when Paddle's API returns an unrecognized schema."""
