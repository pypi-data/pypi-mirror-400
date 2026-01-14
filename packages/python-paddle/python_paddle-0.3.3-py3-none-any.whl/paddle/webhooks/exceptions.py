from paddle.exceptions import PaddleException


class ValidationError(PaddleException):
    """Exception raised for validation errors in Paddle webhooks."""
