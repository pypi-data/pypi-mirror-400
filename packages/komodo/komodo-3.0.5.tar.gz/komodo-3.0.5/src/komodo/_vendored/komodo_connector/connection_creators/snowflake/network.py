from __future__ import annotations

import functools
import gzip
import json
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

import snowflake
from snowflake.connector.network import NO_TOKEN, AuthBase, SnowflakeRestful

from komodo._vendored.komodo_connector.connection_creators.snowflake.utils import remove_port_from_url
from komodo._vendored.komodo_connector.setup_driver import Environment

HEADER_AUTHORIZATION_KEY = "Authorization"
HEADER_SNOWFLAKE_TOKEN = 'Snowflake Token="{token}"'
KH_ACCOUNT_ID_KEY = "x-account-id"
KH_USER_ID = "x-user-id"
KH_APP_ID = "x-app-id"
KH_SNOWFLAKE_HEADER_AUTHORIZATION_KEY = "Snowflake-Authorization"
COMMON_ERROR_KEYS = ["message", "error", "detail"]
SENSITIVE_STRINGS = ["password", "secret", "token", "key", "credentials"]

if TYPE_CHECKING:
    from snowflake.connector.vendored.requests.sessions import (
        Session as SnowflakeVendorSession,
    )


class KomodoSnowflakeAuth(AuthBase):
    """Attaches HTTP Authorization header for Snowflake."""

    def __init__(self, token: str) -> None:
        # setup any auth-related data here
        self.token = token

    def __call__(self, r: Any) -> Any:
        """Modifies and returns the request."""

        # KH Proxy Support
        if KH_ACCOUNT_ID_KEY in r.headers:
            if self.token != NO_TOKEN:
                r.headers[KH_SNOWFLAKE_HEADER_AUTHORIZATION_KEY] = HEADER_SNOWFLAKE_TOKEN.format(token=self.token)
            return r

        if HEADER_AUTHORIZATION_KEY in r.headers:
            del r.headers[HEADER_AUTHORIZATION_KEY]
        if self.token != NO_TOKEN:
            r.headers[HEADER_AUTHORIZATION_KEY] = HEADER_SNOWFLAKE_TOKEN.format(token=self.token)
        return r


snowflake.connector.network.__dict__["SnowflakeAuth"] = KomodoSnowflakeAuth


class ProxySnowflakeRestful(SnowflakeRestful):
    def __init__(
        self,
        *args: Optional[Any],
        kh_token: Optional[str] = None,
        kh_account: Optional[str] = None,
        kh_user: Optional[str] = None,
        app_id: Optional[str] = None,
        komodo_env: Environment,
        **kwargs: Optional[Any],
    ):
        self.kh_token = kh_token
        self.kh_account = kh_account
        self.kh_user = kh_user
        self.app_id = app_id
        self.komodo_env = komodo_env
        super().__init__(*args, **kwargs)

    def _sanitize_error_message(self, error_body: Any) -> str:
        """
        Sanitizes error messages to prevent leaking sensitive information.

        In order for a proxy service response to be surfaced to the user, it has to be explicitly marked with an X-Komodo-Error header. As such, this is simply an additional fallback in case the proxy service accidentally returns a sensitive response - hence, the naive approach. Update this if a more sophisticated approach is needed.



        Args:
            error_body: Raw error response from the server

        Returns:
            str: Sanitized error message
        """
        try:
            if isinstance(error_body, str) and (parsed := json.loads(error_body)):
                error_body = parsed

            # ruff: noqa: SIM102 (ruff wants to combine the if statements, but that hurts readability in this case)
            if isinstance(error_body, dict):
                if error_msg := next((str(error_body[key]) for key in COMMON_ERROR_KEYS if key in error_body), None):
                    # TODO: Doing a very naive check here. Move to a more sophisticated approach if needed.
                    error_msg_contains_sensitive_info = any(
                        sensitive_string in error_msg.lower().strip() for sensitive_string in SENSITIVE_STRINGS
                    )
                    if not error_msg_contains_sensitive_info:
                        return error_msg

            return "An error occurred while processing your request"
        except json.JSONDecodeError:
            return "An error occurred while processing your request"

    def _check_for_komodo_err(
        self, request: Type[SnowflakeVendorSession.request], *args: Dict[str, Any], **kwargs: Dict[str, Any]
    ) -> Any:
        """
        Checks for Komodo-specific errors and HTTP errors in the response.

        Args:
            request: The request function to execute
            *args: Positional arguments for the request
            **kwargs: Keyword arguments for the request

        Returns:
            Any: The response if no errors are found

        Raises:
            Exception: If a Komodo error or HTTP error is detected
        """
        response = request(*args, **kwargs)
        if komodo_error := getattr(response, "headers", {}).get("x-komodo-error"):
            error_message = f"Komodo Error: {komodo_error}"
            trace_id = self.fetch_trace_id_request(kwargs)
            if trace_id:
                error_message += f" (Trace ID: {trace_id})"
            if (status_code := getattr(response, "status_code")) is not None:
                error_message += f" - Status Code: {status_code}"
            raise Exception(error_message)

        # Check for HTTP errors
        if not (200 <= (status_code := response.status_code) < 300):
            try:
                if (
                    hasattr(response, "json")
                    and (error_body := response.json())
                    or hasattr(response, "text")
                    and (error_body := response.text)
                ):
                    pass
                else:
                    error_body = "Unknown error occurred"
            except (AttributeError, json.JSONDecodeError):
                error_body = "Unknown error occurred"

            sanitized_message = self._sanitize_error_message(error_body)
            error_message = f"HTTP Error {status_code}: {sanitized_message}"
            trace_id = self.fetch_trace_id_request(kwargs)
            if trace_id:
                error_message += f" (Trace ID: {trace_id})"
            raise Exception(error_message)

        return response

    def fetch_trace_id_request(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """
        Extracts trace ID from gzipped request data if available.

        Args:
            kwargs: Request keyword arguments containing data and headers

        Returns:
            Optional[str]: Trace ID if found in the request data, None otherwise
        """
        trace_id = None
        if kwargs.get("data") and kwargs.get("headers", {}).get("Content-Encoding") == "gzip":
            try:
                decompressed_body = gzip.decompress(kwargs["data"])
                body_dict = json.loads(decompressed_body)
                query_tag = body_dict.get("data", {}).get("SESSION_PARAMETERS", {}).get("QUERY_TAG")
                if query_tag:
                    tag_data = json.loads(query_tag)
                    trace_id = tag_data.get("root", {}).get("trace", {}).get("trace_id")
            except (OSError, json.JSONDecodeError):
                pass
        return trace_id

    def _request_exec(self, session: SnowflakeVendorSession, *args: Dict[str, Any], **kwargs: Dict[str, Any]) -> Any:
        # kill all telemetry sending
        # a basic intercept here eliminates the need for a much more intrusive change to the telemetry module
        if "telemetry" in kwargs["full_url"]:
            return {"code": None, "data": "Log Received", "message": None, "success": True}

        updated_headers = kwargs.get("headers", {})
        if self.kh_account:
            updated_headers[KH_ACCOUNT_ID_KEY] = self.kh_account
        if self.kh_token:
            updated_headers[HEADER_AUTHORIZATION_KEY] = self.kh_token
        if self.kh_user:
            updated_headers[KH_USER_ID] = self.kh_user
        if self.app_id:
            updated_headers[KH_APP_ID] = self.app_id

        kwargs["headers"] = updated_headers
        session.request = functools.partial(self._check_for_komodo_err, session.request)
        return super()._request_exec(session, *args, **kwargs)

    def fetch(
        self,
        method: str,
        full_url: str,
        headers: Dict[str, str],
        data: Optional[Any] = None,
        timeout: Optional[Any] = None,
        **kwargs: Optional[Any],
    ) -> Any:
        updated_url = remove_port_from_url(full_url) if self.komodo_env != Environment.LOCAL else full_url
        return super().fetch(method, updated_url, headers, data, timeout, **kwargs)
