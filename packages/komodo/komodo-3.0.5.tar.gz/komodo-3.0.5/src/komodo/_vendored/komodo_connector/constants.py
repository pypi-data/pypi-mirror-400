import os
from enum import Enum
from typing import Dict


class Vendors(str, Enum):
    SNOWFLAKE = "snowflake"
    SNOWFLAKE_NATIVE = "snowflake-native"
    SNOWFLAKE_ROTATE_KEYS = "snowflake-rotate-keys"

    @staticmethod
    def values() -> Dict[str, Enum]:
        return Vendors._value2member_map_


class Environment(Enum):
    PROD = "prod"
    DEV = "dev"
    STAGE = "stage"
    LOCAL = "local"


# TODO: Update the host config to the proper DNS for each environment
KOMODO_PROXY_HOST = {
    Environment.PROD: "connector-gateway.onkomodo.com",
    Environment.DEV: "connector-gateway.staging.onkomodo.com",
    Environment.STAGE: "connector-gateway.staging.onkomodo.com",
    Environment.LOCAL: "127.0.0.1",
}

# This port is only used for local development.
# For all remote requests, we remove the port before sending the request and only rely on the dns
DEV_KOMODO_PROXY_SERVICE_DEFAULT_PORT = os.getenv("DEV_KOMODO_PROXY_SERVICE_DEFAULT_PORT", "8000")

VENDOR_CONNECTION_STRING_MAP: Dict[Vendors, str] = {
    Vendors.SNOWFLAKE: "snowflake",
    Vendors.SNOWFLAKE_NATIVE: "snowflake",
    Vendors.SNOWFLAKE_ROTATE_KEYS: "snowflake",
}
# TODO: Remove komodohealth-komodohealthent_compute_dev after testing
SNOWFLAKE_MAIN_ACCOUNTS = ("komodohealthent", "komodohealth")
