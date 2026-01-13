"""
HexelStudio SDK Exceptions
"""


class HxError(Exception):
    """Base exception for HX SDK"""
    pass


class HxConfigError(HxError):
    """Configuration error - missing or invalid config"""
    pass


class HxAuthError(HxError):
    """Authentication error - token issues"""
    pass


class HxAPIError(HxError):
    """API error - request failed"""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}


class HxValidationError(HxError):
    """Validation error - invalid input"""
    pass


class HxNotFoundError(HxAPIError):
    """Resource not found"""
    def __init__(self, message: str, response: dict = None):
        super().__init__(message, status_code=404, response=response)


class HxRateLimitError(HxAPIError):
    """Rate limit exceeded"""
    def __init__(self, message: str, response: dict = None):
        super().__init__(message, status_code=429, response=response)
