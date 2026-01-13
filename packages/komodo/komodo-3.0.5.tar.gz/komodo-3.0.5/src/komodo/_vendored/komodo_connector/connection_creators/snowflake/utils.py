from functools import lru_cache
from importlib import metadata
from typing import Union
from urllib.parse import urlparse, urlunparse

from packaging.version import Version, parse
from snowflake.connector import errorcode, errors

SNOWFLAKE_VERSION_3_0_0 = "3.0.0"
SQLALCHEMY_VERSION_1_4_0 = "1.4.0"


def is_authentication_error(err: Union[errors.ProgrammingError, errors.DatabaseError]) -> bool:
    return err.errno in (
        errorcode.ER_FAILED_TO_CONNECT_TO_DB,
        errorcode.ER_NO_ACCOUNT_NAME,
        errorcode.ER_NO_PASSWORD,
    )


@lru_cache(maxsize=1)
def sf_connector_version_greater_than(version: str) -> bool:
    return parse(metadata.version("snowflake-connector-python")) > Version(version)  # type: ignore


@lru_cache(maxsize=1)
def sql_alchemy_version_greater_than(version: str) -> bool:
    return parse(metadata.version("sqlalchemy")) > Version(version)  # type: ignore


def remove_port_from_url(url: str) -> str:
    parsed_url = urlparse(url)

    new_netloc = parsed_url.hostname

    path_parts = parsed_url.path.split("/")
    if len(path_parts) > 1 and ":" in path_parts[1]:
        path_parts[1] = path_parts[1].split(":")[0]
    new_path = "/".join(path_parts)

    new_url_parts = (parsed_url.scheme, new_netloc, new_path, parsed_url.params, parsed_url.query, parsed_url.fragment)
    return urlunparse(new_url_parts)
