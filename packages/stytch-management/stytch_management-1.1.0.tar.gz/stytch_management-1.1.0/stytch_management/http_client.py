#!/usr/bin/env python3

from typing import Any, Dict, Optional

import requests
import requests.auth
from stytch_management.errors import StytchError, StytchErrorDetails
from stytch_management.version import __version__

DEFAULT_BASE_URL = "https://management.stytch.com/"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": f"Stytch Management Python v{__version__}",
}


class HTTPClient:
    """HTTP client for making requests to the Stytch Management API."""

    def __init__(
        self,
        workspace_key_id: str,
        workspace_key_secret: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
        session: Optional[requests.Session] = None,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.auth = requests.auth.HTTPBasicAuth(workspace_key_id, workspace_key_secret)
        self.__session = session

    @property
    def _session(self) -> requests.Session:
        """Lazy-initialize the session."""
        if self.__session is None:
            self.__session = requests.Session()
        return self.__session

    def _build_url(self, path: str) -> str:
        """Build a full URL from a path."""
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parse and validate an HTTP response.

        Raises:
            StytchError: If the API returns an error response
        """
        try:
            response_json = response.json()
        except Exception:
            response_json = {}

        # Check for non-2xx responses
        if response.status_code >= 400:
            try:
                details = StytchErrorDetails(**response_json)
                details.original_json = response_json
            except Exception as e:
                details = StytchErrorDetails.from_unknown(
                    response.status_code, response_json
                )
                raise StytchError(details) from e
            raise StytchError(details)

        return response_json

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        final_headers = HEADERS.copy()
        final_headers.update(headers or {})

        url = self._build_url(path)
        response = self._session.get(
            url,
            params=params,
            headers=final_headers,
            auth=self.auth,
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        final_headers = HEADERS.copy()
        final_headers.update(headers or {})

        url = self._build_url(path)
        response = self._session.post(
            url,
            json=json,
            headers=final_headers,
            auth=self.auth,
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        final_headers = HEADERS.copy()
        final_headers.update(headers or {})

        url = self._build_url(path)
        response = self._session.put(
            url,
            json=json,
            params=params,
            headers=final_headers,
            auth=self.auth,
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def patch(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a PATCH request."""
        final_headers = HEADERS.copy()
        final_headers.update(headers or {})

        url = self._build_url(path)
        response = self._session.patch(
            url,
            json=json,
            params=params,
            headers=final_headers,
            auth=self.auth,
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        final_headers = HEADERS.copy()
        final_headers.update(headers or {})

        url = self._build_url(path)
        response = self._session.delete(
            url,
            params=params,
            headers=final_headers,
            auth=self.auth,
            timeout=self.timeout,
        )
        return self._handle_response(response)
