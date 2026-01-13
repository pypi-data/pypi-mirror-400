# Helix Connect Exceptions


class HelixError(Exception):
    """Base exception for all Helix Connect errors"""

    pass


class AuthenticationError(HelixError):
    """Raised when authentication fails"""

    pass


class PermissionDeniedError(HelixError):
    """Raised when user lacks permissions for an operation"""

    pass


class DatasetNotFoundError(HelixError):
    """Raised when a dataset cannot be found"""

    pass


class RateLimitError(HelixError):
    """Raised when rate limit is exceeded"""

    pass


class ConflictError(HelixError):
    """Raised when a resource already exists (409 Conflict)"""

    pass


class UploadError(HelixError):
    """Raised when dataset upload fails"""

    pass


class DownloadError(HelixError):
    """Raised when dataset download fails"""

    pass
