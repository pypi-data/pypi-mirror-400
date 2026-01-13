class CyberLicensingError(Exception):
    """Base class for SDK-specific exceptions."""


class AuthenticationError(CyberLicensingError):
    """Raised when authentication fails or a token is missing."""


class ApiError(CyberLicensingError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code: int, message: str, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}

    def __str__(self) -> str:
        return f"API Error {self.status_code}: {super().__str__()}"


class BadRequestError(ApiError):
    """Raised when the API returns HTTP 400 (Bad Request)."""

    def __init__(self, message: str, payload=None):
        super().__init__(400, message, payload)


class ForbiddenError(ApiError):
    """Raised when the API returns HTTP 403 (Forbidden - insufficient project scope)."""

    def __init__(self, message: str, payload=None):
        super().__init__(403, message, payload)


class NotFoundError(ApiError):
    """Raised when the API returns HTTP 404 (Not Found)."""

    def __init__(self, message: str, payload=None):
        super().__init__(404, message, payload)
