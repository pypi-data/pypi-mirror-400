class RideScanError(Exception):
    """Base exception for all RideScan API errors."""
    def __init__(self, message: str, code: str = None, details: str = None):
        self.code = code
        self.details = details
        super().__init__(f"[{code}] {message}" if code else message)

class AuthenticationError(RideScanError):
    """Raised when the API key is invalid or missing (RS-AUTH)."""
    pass

class ValidationError(RideScanError):
    """Raised when arguments are invalid or missing (RS-VAL)."""
    pass

class ResourceNotFoundError(RideScanError):
    """Raised when a requested resource (Robot/Mission) is not found (RS-ROBOT-002, etc.)."""
    pass

class ConflictError(RideScanError):
    """Raised when creating a duplicate resource (RS-ROBOT-001, RS-MSN-001)."""
    pass

class ServerError(RideScanError):
    """Raised when the RideScan server encounters an internal error (RS-SYS)."""
    pass