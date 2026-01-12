class SoulSenseError(Exception):
    """Base exception for SoulSense application."""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

class DatabaseError(SoulSenseError):
    """Raised when a database operation fails."""
    pass

class ConfigurationError(SoulSenseError):
    """Raised when configuration is missing or invalid."""
    pass

class ResourceError(SoulSenseError):
    """Raised when a required resource (file, asset, question) is missing."""
    pass

class ValidationError(SoulSenseError):
    """Raised when user input is invalid."""
    pass

class AuthenticationError(SoulSenseError):
    """Raised when authentication fails."""
    pass

class APIConnectionError(SoulSenseError):
    """Raised when external API connection fails."""
    pass
