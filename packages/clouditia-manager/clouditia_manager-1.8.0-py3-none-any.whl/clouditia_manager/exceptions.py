"""
Exceptions for Clouditia Manager SDK
"""


class ClouditiaManagerError(Exception):
    """Base exception for Clouditia Manager SDK"""
    pass


class AuthenticationError(ClouditiaManagerError):
    """Raised when API key is invalid or expired"""
    pass


class SessionNotFoundError(ClouditiaManagerError):
    """Raised when session is not found"""
    pass


class InsufficientResourcesError(ClouditiaManagerError):
    """Raised when requested GPU resources are not available"""
    pass


class APIError(ClouditiaManagerError):
    """Raised when API returns an error"""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
