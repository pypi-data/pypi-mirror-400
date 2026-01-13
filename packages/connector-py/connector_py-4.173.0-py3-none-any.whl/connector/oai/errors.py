import json
import logging
import traceback
from abc import abstractmethod
from collections.abc import Callable
from typing import Any

from connector_sdk_types.generated import Error, ErrorCode, ErrorResponse
from httpx import ConnectError

logger = logging.getLogger("integration-connectors.sdk")


class ConnectorError(Exception):
    """
    Base exception class for Lumos connectors.
    Preferred way to raise exceptions inside the conenctors.
    `raise ConnectorError(message, error_code)`

    message: str (Custom error message)
    error_code: ErrorCode (The actual error code, eg. "internal_error")
    app_error_code: str | None (The application-specific error code, eg. "my_app.internal_error" or Zoom error 300)
    """

    def __init__(
        self,
        *,
        message: str,
        error_code: ErrorCode,
        app_error_code: str | None = None,
    ):
        self.error_code = error_code
        self.app_error_code = app_error_code
        self.message = message

    def __str__(self) -> str:
        """Return the error message for string representation."""
        return self.message


class ExceptionHandler:
    """
    Abstract class for handling exceptions. You can subclass this to create your own exception handler.
    """

    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def handle(
        e: Exception,
        original_func: Any,
        response: ErrorResponse,
        error_code: ErrorCode | None = None,
    ) -> ErrorResponse:
        """
        Handle an exception. (ErrorHandler signature typing)

        e: Exception (An exception that was raised)
        original_func: FunctionType (The original method that was called, eg. validate_credentials)
        response: ErrorResp (The output of the connector call)
        error_code: str | None (The application-specific error code, eg. "my_app.internal_error")
        """
        return response


class DefaultHandler(ExceptionHandler):
    """
    Default exception handler that handles the basic HTTPX/GQL extraction (etc.) and chains onto the global handler.
    These are operations that are always done on the raised error.
    """

    @staticmethod
    def _extract_status_code(e: Exception) -> int | None:
        status_code: int | None = None
        if hasattr(e, "response") and hasattr(e.response, "status_code"):  # type: ignore
            status_code = e.response.status_code  # type: ignore
        if hasattr(e, "code"):
            status_code = e.code  # type: ignore
        if not isinstance(status_code, int):
            status_code = None
        return status_code

    @staticmethod
    def _extract_error_message(e: Exception, status_code: int | None) -> str | None:
        response_message = None
        try:
            error_data = e.response.json()  # type: ignore
            if error_data and not (isinstance(error_data, dict | list) and len(error_data) == 0):
                if hasattr(e, "response") and hasattr(e.response, "url"):  # type: ignore
                    response_message = (
                        f"[{status_code}][{str(e.response.url).split('?')[0]}] {str(error_data)}"  # type: ignore
                    )
                else:
                    response_message = f"[{status_code}] {str(error_data)}"
        except Exception:
            if hasattr(e, "response") and hasattr(e.response, "text"):  # type: ignore
                if hasattr(e.response, "url") and hasattr(e.response, "status_code"):  # type: ignore
                    response_message = (
                        f"[{e.response.status_code}][{str(e.response.url).split('?')[0]}] {e.response.text}"  # type: ignore
                        if e.response.text  # type: ignore
                        else None
                    )
                else:
                    response_message = e.response.text or None  # type: ignore
            else:
                response_message = str(e.message) if hasattr(e, "message") else str(e)  # type: ignore
        return response_message

    @staticmethod
    def _populate_base_error_info(
        response: ErrorResponse,
        e: Exception,
        original_func: Any,
        status_code: int | None,
        message: str | None,
    ) -> None:
        if message:
            response.error.message = message
        else:
            response.error.message = e.message if hasattr(e, "message") else str(e)  # type: ignore

        response.error.status_code = status_code
        response.error.raised_in = f"{original_func.__module__}:{original_func.__name__}"
        response.error.raised_by = f"{e.__class__.__name__}"

    @staticmethod
    def _handle_connector_error(response: ErrorResponse, e: ConnectorError) -> None:
        response.error.error_code = e.error_code
        response.error.app_error_code = e.app_error_code if e.app_error_code else None

    @staticmethod
    def _handle_special_cases(response: ErrorResponse, e: Exception) -> None:
        traceback.print_exception(e)
        response.error.error_code = ErrorCode.UNEXPECTED_ERROR

        if "Illegal header" in response.error.message:
            response.error.message = "Illegal header constructed for API request. Please check the app configuration and try again."
            response.error.error_code = ErrorCode.BAD_REQUEST

        error_messages = ["name or service not known", "nodename nor servname provided"]
        if isinstance(e, ConnectError) or any(
            error_message in str(response.error.message).lower() for error_message in error_messages
        ):
            response.error.message = "Failed to connect to the API. Please verify the URL or try at a later time due to a potential temporary network issue."
            response.error.error_code = ErrorCode.API_ERROR

        if isinstance(e, json.JSONDecodeError):
            response.error.error_code = ErrorCode.API_ERROR
            if not response.error.message or response.error.message == str(e):
                response.error.message = f"Failed to parse JSON response: {str(e)}"

    @staticmethod
    def handle(
        e: Exception,
        original_func: Any,
        response: ErrorResponse,
        error_code: ErrorCode | None = None,
    ) -> ErrorResponse:
        logger.debug(e, exc_info=True)

        status_code = DefaultHandler._extract_status_code(e)
        response_message = DefaultHandler._extract_error_message(e, status_code)
        DefaultHandler._populate_base_error_info(
            response, e, original_func, status_code, response_message
        )

        if isinstance(e, ConnectorError):
            DefaultHandler._handle_connector_error(response, e)
        else:
            DefaultHandler._handle_special_cases(response, e)

        return response


class HTTPHandler(ExceptionHandler):
    """
    Default exception handler for simple HTTP exceptions.
    If you want to handle more complicated exceptions, you can create your own instead.
    """

    @staticmethod
    def handle(
        e: Exception,
        original_func: Any,
        response: ErrorResponse,
        error_code: ErrorCode | None = None,
    ) -> ErrorResponse:
        match response.error.status_code:
            case 400:
                response.error.error_code = ErrorCode.BAD_REQUEST
            case 401:
                response.error.error_code = ErrorCode.UNAUTHORIZED
            case 403:
                response.error.error_code = ErrorCode.PERMISSION_DENIED
            case 404:
                response.error.error_code = ErrorCode.NOT_FOUND
            case 429:
                response.error.error_code = ErrorCode.RATE_LIMIT
            case 502:
                response.error.error_code = ErrorCode.BAD_GATEWAY
            case _:
                response.error.error_code = ErrorCode.API_ERROR

        return response


ErrorMap = list[tuple[type[Exception], type[ExceptionHandler], ErrorCode | None]]


def handle_exception(
    error: Exception, exception_classes: ErrorMap, capability: Callable[[Any], Any], app_id: str
) -> ErrorResponse:
    """
    Decorator that adds error handling to a method. Uses the default Lumos error handler if no exception handler is provided.

    Example:
    ```python
    @exception_handler(
        (httpx.HTTPStatusError, ExceptionHandler, "error.code"),
    )
    async def verify_credentials(self, args: ValidateCredentialsArgs) -> ValidateCredentialsResp:
        pass
    ```

    Args:
        exception_classes (tuple): Tuple of exception classes to be handled. Map of exception class to handler function.

    Returns
    -------
        function: Decorated function.
    """

    resp = ErrorResponse(
        is_error=True,
        error=Error(message=str(error), error_code=ErrorCode.UNEXPECTED_ERROR, app_id=app_id),
    )

    resp = DefaultHandler.handle(
        error,
        capability,
        resp,
        None,
    )

    if not isinstance(error, ConnectorError):
        for exception_class, handler, code in exception_classes:
            if isinstance(error, exception_class) and handler:
                resp = handler.handle(error, capability, resp, code)

    logger.error(
        f"{resp.error.app_id}/{resp.error.error_code}: {resp.error.message}",
        exc_info=True,
    )
    return resp
