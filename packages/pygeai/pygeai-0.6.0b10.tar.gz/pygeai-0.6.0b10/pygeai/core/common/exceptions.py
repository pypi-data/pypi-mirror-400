

class GEAIException(Exception):
    """Base class for all PyGEAI exceptions."""
    pass


class UnknownArgumentError(GEAIException):
    """Raised when an unknown or invalid command/option is provided"""
    pass


class MissingRequirementException(GEAIException):
    """Raised when a required parameter or argument is missing"""
    pass


class WrongArgumentError(GEAIException):
    """Raised when arguments are incorrectly formatted or invalid"""
    pass


class ServerResponseError(GEAIException):
    """Raised when the server returns an error response"""
    pass


class APIError(GEAIException):
    """Raised when an API request fails"""
    pass


class InvalidPathException(GEAIException):
    """Raised when a file or directory path is invalid or not found"""
    pass


class InvalidJSONException(GEAIException):
    """Raised when JSON data cannot be parsed or is malformed"""
    pass


class InvalidAPIResponseException(GEAIException):
    """Raised when the API response format is unexpected or invalid"""
    pass


class InvalidResponseException(GEAIException):
    """Raised when a response cannot be retrieved or processed"""
    pass


class InvalidAgentException(GEAIException):
    """Raised when an agent cannot be retrieved, validated, or is misconfigured"""
    pass


class APIResponseError(GEAIException):
    """Raised when there is an error in the API response"""
    pass

