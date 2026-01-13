# type: ignore
# fmt: off
import logging
import os
from typing import Dict, Optional, Type

from snowflake.connector import connection, errorcode, errors
from snowflake.connector.constants import (
    PARAMETER_AUTOCOMMIT,
    PARAMETER_CLIENT_PREFETCH_THREADS,
    PARAMETER_CLIENT_SESSION_KEEP_ALIVE,
    PARAMETER_CLIENT_SESSION_KEEP_ALIVE_HEARTBEAT_FREQUENCY,
    PARAMETER_CLIENT_VALIDATE_DEFAULT_PARAMETERS,
    PARAMETER_TIMEZONE,
)

from komodo._vendored.komodo_connector.connection_creators.snowflake.cursor import KomodoSnowflakeCursor
from komodo._vendored.komodo_connector.connection_creators.snowflake.komodo_auth import AuthByKomodoProxy
from komodo._vendored.komodo_connector.connection_creators.snowflake.network import ProxySnowflakeRestful
from komodo._vendored.komodo_connector.connection_creators.snowflake.utils import (
    is_authentication_error,
)
from komodo._vendored.komodo_connector.setup_driver import Environment

logger = logging.getLogger(__name__)

class UnsupportedCursorTypeException(Exception):
    pass


class KomodoSnowflakeConnection(connection.SnowflakeConnection):
    KOMODO_AUTH_PARAMS = ("kh_token", "kh_account", "kh_user")

    def __init__(
        self,
        *args,
        environment: Optional[str],
        komodo_host: Optional[str] = None,
        komodo_credentials: Optional[Dict[str, str]] = None,
        komodo_auth_use_env_vars: bool = False,
        **kwargs,
    ) -> None:
        if not komodo_auth_use_env_vars:
            assert komodo_credentials and isinstance(komodo_credentials, dict)
            self.kh_token, self.kh_account, self.kh_user, self.app_id = (
                komodo_credentials.get("kh_token"),
                komodo_credentials.get("kh_account"),
                komodo_credentials.get("kh_user"),
                kwargs.get("app_id"),
            )
        else:
            self.kh_token, self.kh_account, self.kh_user, self.app_id = (
                os.getenv("KH_TOKEN"),
                os.getenv("KH_ACCOUNT"),
                os.getenv("KH_USER"),
                os.getenv("APP_ID"),
            )

        if not self.kh_token or not self.kh_account or not self.kh_user:
            raise errors.ForbiddenError(
                msg=f"Missing required parameters for Komodo Proxy Authenticator: {self.KOMODO_AUTH_PARAMS}",
                errno=errorcode.ER_INVALID_VALUE,
            )
        # Komodo driver sdk should default to prod environment, but allow for override for testing
        self.komodo_env = Environment(environment) if environment else Environment.PROD
        self.komodo_host = komodo_host

        try:
            super().__init__(*args, **kwargs)
        except errors.DatabaseError as err:
            if not is_authentication_error(err):
                raise err
        # The connect below appears to act as some kind of health-check / to send early telemetry data. Either way,
        # it's not necessary for our purposes and can be skipped
        # self.connect(**kwargs)
        self.komodo_credentials = komodo_credentials

    def connect(self, **kwargs) -> None:
        try:
            if kwargs:
                # Not as sketchy as it seems! In restricted environments we can't hit Snowflake's OCSP Location, and
                # our proxy address isn't even in the json that's returned so this removes upto 0.6s of overhead
                # during initial connection
                super()._SnowflakeConnection__config(insecure_mode=True, disable_ocsp_checks=True, **kwargs)
        except errors.ProgrammingError as err:
            if not is_authentication_error(err):
                raise err
        self.__open_connection()

    def __open_connection(self) -> None:
        """Opens a new network connection."""

        # use_numpy and support_negative_year are set later during execution anyway, but are required params :/
        self.converter = self.converter_class(
            use_numpy=True, support_negative_year=True
        )

        # Make sure that a HTTP proxy isn't specified as it causes a different (untested) code-path later
        if self.proxy_host:
            raise NotImplementedError("HTTP Proxy is not supported in Komodo Snowflake Connections")

        self._rest = ProxySnowflakeRestful(
            kh_token=self.kh_token,
            kh_account=self.kh_account,
            kh_user=self.kh_user,
            app_id=self.app_id,
            komodo_env=self.komodo_env,
            host=self.host,
            port=self.port,
            protocol=self._protocol,
            inject_client_pause=self._inject_client_pause,
            connection=self,
        )
        logger.debug("REST API object was created: %s:%s", self.host, self.port)

        # The remainder of this method is cribbed from Snowflake's implementation unless commented

        if self._session_parameters is None:
            self._session_parameters = {}
        if self._autocommit is not None:
            self._session_parameters[PARAMETER_AUTOCOMMIT] = self._autocommit

        if self._timezone is not None:
            self._session_parameters[PARAMETER_TIMEZONE] = self._timezone

        if self._validate_default_parameters:
            # Snowflake will validate the requested database, schema, and warehouse
            self._session_parameters[PARAMETER_CLIENT_VALIDATE_DEFAULT_PARAMETERS] = (
                True
            )

        if self.client_session_keep_alive is not None:
            self._session_parameters[PARAMETER_CLIENT_SESSION_KEEP_ALIVE] = (
                self._client_session_keep_alive
            )

        if self.client_session_keep_alive_heartbeat_frequency is not None:
            self._session_parameters[
                PARAMETER_CLIENT_SESSION_KEEP_ALIVE_HEARTBEAT_FREQUENCY
            ] = self._validate_client_session_keep_alive_heartbeat_frequency()

        if self.client_prefetch_threads:
            self._session_parameters[PARAMETER_CLIENT_PREFETCH_THREADS] = (
                self._validate_client_prefetch_threads()
            )

        # Explicitly call our auth method instead of relying on a failure path from the 'regular' one.
        self.auth_class = AuthByKomodoProxy(
            self.kh_token, self.kh_account, self.kh_user, self.komodo_env, self.komodo_host
        )
        self.authenticate_with_retry(self.auth_class)

        self._password = None  # ensure password won't persist
        self.auth_class.reset_secrets()

        self.initialize_query_context_cache()

        if self.client_session_keep_alive:
            # This will be called after the heartbeat frequency has actually been set.
            # By this point it should have been decided if the heartbeat has to be enabled
            # and what would the heartbeat frequency be
            self._add_heartbeat()

    def cursor(self, cursor_class: Type[KomodoSnowflakeCursor] = KomodoSnowflakeCursor):
        if not issubclass(cursor_class, KomodoSnowflakeCursor):
            raise UnsupportedCursorTypeException(f"Unsupported cursor type: {cursor_class}")
        return cursor_class(self)

    def execute_string(self, sql_text: str, remove_comments: bool = False, return_cursors: bool = True, cursor_class: Type[KomodoSnowflakeCursor] = KomodoSnowflakeCursor, **kwargs):
        return super().execute_string(sql_text, remove_comments, return_cursors, cursor_class, **kwargs)
