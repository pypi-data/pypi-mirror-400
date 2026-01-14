import json
class EndeeException(Exception):
    """Base class for all Endee related exceptions."""
    def __init__(self, message="An error occurred in Endee"):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message

class APIException(EndeeException):
    """Generic Exception. Raised when an API call returns an error."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"API Error: {message}")

class ServerException(EndeeException):
    """ 5xx Server Errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Server Busy: {message}")

class ForbiddenException(EndeeException):
    """User is not allowed to perform the operation."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Forbidden: {message}")

class ConflictException(EndeeException):
    """Raised when we try to create an index which exists."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Conflict: {message}")

class NotFoundException(EndeeException):
    """Raised when the index is not there."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Resource Not Found: {message}")

class AuthenticationException(EndeeException):
    """Exception raised for token is invalid."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Authentication Error: {message}")

class SubscriptionException(EndeeException):
    """Exception raised when metadata is no JSON."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Subscription Error: {message}")

def raise_exception(code:int, text:str=None):
    """Raise an exception based on the error code."""
    message = None
    try:
        message = json.loads(text).get("error", "Unknown error")
    except (json.JSONDecodeError, TypeError, AttributeError):
        message = text or "Unknown error"

    if code == 400:
        raise APIException(message)
    elif code == 401:
        raise AuthenticationException(message)
    elif code == 402:
        raise SubscriptionException(message)
    elif code == 403:
        raise ForbiddenException(message)
    elif code == 404:
        raise NotFoundException(message)
    elif code == 409:
        raise ConflictException(message)
    elif code >= 500:
        message = "Server is busy. Please try again in sometime"
        raise ServerException(message)
    else:
        message = "Unknown Error. Please try again in sometime"
        raise APIException(message)