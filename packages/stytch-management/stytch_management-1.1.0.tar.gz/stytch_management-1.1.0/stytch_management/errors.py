#!/usr/bin/env python3

from __future__ import annotations

from typing import Any, Dict, Optional

import pydantic


class ClientError(Exception):
    """
    Exception raised for client-side errors, such as missing required
    path parameters before making an API request.
    """

    def __init__(self, code: str, message: str, cause: Optional[Exception] = None):
        self.code = code
        self.message = message
        self.cause = cause
        super().__init__(message)

    def __repr__(self) -> str:
        return f"ClientError(code={self.code}, message={self.message})"

    def __str__(self) -> str:
        return self.message


class ResponseError(ValueError):
    """Internal exception used to signal a non-2xx response."""

    ...


class StytchErrorDetails(pydantic.BaseModel):
    """Details about an error response from the Stytch Management API."""

    status_code: int
    request_id: str
    error_type: Optional[str] = pydantic.Field(
        validation_alias=pydantic.AliasChoices("error_type", "error"), default=None
    )
    error_message: str = pydantic.Field(
        validation_alias=pydantic.AliasChoices("error_message", "error_description")
    )
    error_url: Optional[str] = pydantic.Field(
        validation_alias=pydantic.AliasChoices("error_url", "error_uri"), default=None
    )
    original_json: Optional[Dict[str, Any]] = None

    @classmethod
    def from_unknown(
        cls, status_code: int, original_json: Optional[Dict[str, Any]] = None
    ) -> StytchErrorDetails:
        """Create error details for unknown errors."""
        message = "An unknown error occurred"
        if 200 <= status_code < 300:
            message = "Failed to parse JSON into target object type"
        result = StytchErrorDetails(
            status_code=status_code,
            request_id="",
            error_type=None,
            error_message=message,
            error_url=None,
            original_json=original_json,
        )
        return result


class StytchError(Exception):
    """
    Exception raised when the Stytch Management API returns an error response.

    Attributes:
        details: Detailed information about the error
        status_code: HTTP status code
        request_id: Unique request identifier for support
        error_type: Type of error that occurred
        error_message: Human-readable error message
        error_url: URL to documentation about the error
    """

    def __init__(self, details: StytchErrorDetails) -> None:
        self.details = details
        self.status_code = details.status_code
        self.request_id = details.request_id
        self.error_type = details.error_type
        self.error_message = details.error_message
        self.error_url = details.error_url
        super().__init__(details.error_message)

    def __repr__(self) -> str:
        return f"StytchError {{{self.details}}}"

    def __str__(self) -> str:
        return str(self.details)
