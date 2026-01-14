"""

All exceptions in use by the blox.api package.

"""

# Base Exceptions

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .api_types import *


class BloxException(Exception):
    """Base exception, can be used to catch all package exception."""

    def __init__(self, message: str, *args):
        super().__init__(message, *args)


class HTTPException(BloxException):
    """Base exception to catch all HTTP response errors."""

    def __init__(self, message: str, status_code: int, *args):
        self._message = message
        self._status_code = status_code

        super().__init__(f"[{status_code}] {message}", *args)

    @property
    def status_code(self) -> int:
        """The HTTP response status code."""

        return self._status_code

    @status_code.setter
    def status_code(self, value: int):
        self._status_code = value

    @property
    def message(self) -> str:
        """The generic error message."""

        return self._message

    def is_server_error(self) -> bool:
        """Whether the response status is a `5XX`."""

        return self.status_code >= 500 and self.status_code <= 599

    def is_client_error(self) -> bool:
        """Whether the response status is a `4XX`."""

        return self.status_code >= 400 and self.status_code <= 499

    def __str__(self):
        return f"[{self.status_code}] {self.message}"


# Generic Exceptions


class RequestTimeout(BloxException):
    """Exception raised when a HTTP request times out."""

    def __init__(self, retry: int, max_retries: int, timeout: float):
        self.retry = retry
        self.max_retries = max_retries
        self.timeout = timeout

        super().__init__(
            f"Roblox API took too long to respond. ({retry}/{max_retries} retries) ({timeout}s timeout)"
        )


class NoMoreItems(BloxException):
    """Exception raised when there are no more items left to iterate through."""

    pass


class BadContentType(HTTPException):
    """Exception raised when a non-JSON content type is received."""

    def __init__(self, status_code: int, content_type: Optional[str] = None):
        self.content_type = content_type

        super().__init__(
            f"Received a non-json content type: '{content_type}'", status_code
        )


# Web API Exceptions


class WebAPIError:
    """Represents an error item returned by Roblox Web API unsuccessful responses."""

    code: int
    message: Optional[str] = None

    def __init__(self, data: "web_types.ErrorItem"):
        print("err data", data)
        self.code = int(data["code"])

        if message := data.get("message"):
            self.message = message.strip()


def parse_web_errors(errors: List["web_types.ErrorItem"]):
    return [WebAPIError(error) for error in errors if error.keys()]


class UnhandledWebException(HTTPException):
    """Base exception to catch any Roblox Web API error responses. **Errors may be empty.**"""

    def __init__(self, errors: List["web_types.ErrorItem"], status_code: int = 0):
        self.errors = parse_web_errors(errors)

        message = "A web API error has occurred."
        for error in self.errors:
            message += f"\n\t{error.code} = {error.message}"

        super().__init__(message, status_code)


# Shared Exceptions


class UserNotFound(HTTPException):
    """Exception raised when a user could not be found."""


class GroupNotFound(HTTPException):
    """Exception raised when a group could not be found."""


class RoleNotFound(HTTPException):
    """Exception raised when a group role could not be found."""


class InsufficientPermissions(HTTPException):
    """Exception raised when a resource could not be accessed by the authenticated user due to insufficient permissions."""
