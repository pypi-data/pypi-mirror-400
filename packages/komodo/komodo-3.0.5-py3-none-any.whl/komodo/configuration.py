import copy
import logging
from logging import FileHandler
import multiprocessing
import sys
from typing import Optional
import httpx

import http.client as httplib


class Configuration:
    """This class contains various settings of the API client.

        :param api_key: Dict to store API key(s).
          Each entry in the dict specifies an API key.
          The dict key is the name of the security scheme in the OAS specification.
          The dict value is the API key secret.
        :param api_key_prefix: Dict to store API prefix (e.g. Bearer).
          The dict key is the name of the security scheme in the OAS specification.
          The dict value is an API key prefix when generating the auth data.
        :param access_token: Access token.
        :param retries: Number of retries for API requests.

        :Example:

        API Key Authentication Example.
        Given the following security scheme in the OpenAPI specification:
          components:
            securitySchemes:
              cookieAuth:         # name for the security scheme
                type: apiKey
                in: cookie
                name: JSESSIONID  # cookie name

        You can programmatically set the cookie:

    conf = komodo.Configuration(
        api_key={'cookieAuth': 'abc123'}
        api_key_prefix={'cookieAuth': 'JSESSIONID'}
    )

        The following cookie will be added to the HTTP request:
           Cookie: JSESSIONID abc123
    """

    _default = None

    def __init__(
        self,
        api_key=None,
        api_key_prefix=None,
        access_token=None,
        retries=None,
    ) -> None:
        """Constructor"""
        self.temp_folder_path = None
        """Temp file folder for downloading files
        """
        # Authentication Settings
        self.api_key = {}
        if api_key:
            self.api_key = api_key
        """dict to store API key(s)
        """
        self.api_key_prefix = {}
        if api_key_prefix:
            self.api_key_prefix = api_key_prefix
        """dict to store API prefix (e.g. Bearer)
        """
        self.refresh_api_key_hook = None
        """function hook to refresh API key if expired
        """
        self.access_token = access_token
        """Access token
        """
        self.logger = {}
        """Logging Settings
        """
        self.logger["package_logger"] = logging.getLogger("komodo")
        self.logger["urllib3_logger"] = logging.getLogger("urllib3")

        self.verify_ssl = True
        """SSL/TLS verification
           Set this to false to skip verifying SSL certificate when calling API
           from https server.
        """
        self.safe_chars_for_path_param = ""
        """Safe chars for path_param
        """
        self.retries = retries
        """Adding retries to override default value 3
        """

    @classmethod
    def set_default(cls, default):
        """Set default instance of configuration.

        It stores default configuration, which can be
        returned by get_default_copy method.

        :param default: object of Configuration
        """
        cls._default = default

    @classmethod
    def get_default_copy(cls):
        """Deprecated. Please use `get_default` instead.

        Deprecated. Please use `get_default` instead.

        :return: The configuration object.
        """
        return cls.get_default()

    @classmethod
    def get_default(cls):
        """Return the default configuration.

        This method returns newly created, based on default constructor,
        object of Configuration class or returns a copy of default
        configuration.

        :return: The configuration object.
        """
        if cls._default is None:
            cls._default = Configuration()
        return cls._default

    def get_api_key_with_prefix(self, identifier, alias=None):
        """Gets API key (with prefix if set).

        :param identifier: The identifier of apiKey.
        :param alias: The alternative identifier of apiKey.
        :return: The token for api key authentication.
        """
        if self.refresh_api_key_hook is not None:
            self.refresh_api_key_hook(self)
        key = self.api_key.get(identifier, self.api_key.get(alias) if alias is not None else None)
        if key:
            prefix = self.api_key_prefix.get(identifier)
            if prefix:
                return "%s %s" % (prefix, key)
            else:
                return key

    def auth_settings(self):
        """Gets Auth Settings dict for api client.

        :return: The Auth Settings information dict.
        """
        auth = {}
        if self.access_token is not None:
            auth["HTTPBearer"] = {"type": "bearer", "in": "header", "key": "Authorization", "value": self.get_api_key_with_prefix("HTTPBearer")}
        if "x-account-id" in self.api_key:
            auth["x-account-id"] = {
                "type": "api_key",
                "in": "header",
                "key": "x-account-id",
                "value": self.get_api_key_with_prefix(
                    "x-account-id",
                ),
            }
        return auth
