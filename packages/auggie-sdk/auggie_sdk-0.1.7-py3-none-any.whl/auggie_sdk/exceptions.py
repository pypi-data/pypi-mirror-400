"""Custom exceptions for the Augment SDK"""


class AugmentError(Exception):
    """Base exception for all Augment SDK errors"""

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AugmentError):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class RateLimitError(AugmentError):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class NotFoundError(AugmentError):
    """Raised when a resource is not found"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AugmentError):
    """Raised when request validation fails"""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=400)


class AugmentCLIError(AugmentError):
    """Raised when the auggie CLI command fails"""

    def __init__(self, message: str, return_code: int = None, stderr: str = None):
        super().__init__(message)
        self.return_code = return_code
        self.stderr = stderr


class AugmentNotFoundError(AugmentError):
    """Raised when auggie CLI is not found or accessible"""

    def __init__(self, message: str = "auggie CLI not found"):
        super().__init__(message)


class AugmentWorkspaceError(AugmentError):
    """Raised when workspace path is invalid or inaccessible"""

    def __init__(self, message: str):
        super().__init__(message)


class AugmentParseError(AugmentError):
    """Raised when parsing agent response fails"""

    def __init__(self, message: str):
        super().__init__(message)


class AugmentJSONError(AugmentError):
    """Raised when JSON parsing fails"""

    def __init__(self, message: str):
        super().__init__(message)


class AugmentVerificationError(AugmentError):
    """Raised when success criteria verification fails after max rounds"""

    def __init__(
        self,
        message: str,
        unmet_criteria: list = None,
        issues: list = None,
        rounds_attempted: int = None,
    ):
        super().__init__(message)
        self.unmet_criteria = unmet_criteria or []
        self.issues = issues or []
        self.rounds_attempted = rounds_attempted
