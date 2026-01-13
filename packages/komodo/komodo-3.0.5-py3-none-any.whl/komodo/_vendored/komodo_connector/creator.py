from typing import Any, Dict, Protocol, Union, runtime_checkable

from komodo._vendored.komodo_connector.connection_creators.snowflake.utils import (
    SQLALCHEMY_VERSION_1_4_0,
    sql_alchemy_version_greater_than,
)

if sql_alchemy_version_greater_than(SQLALCHEMY_VERSION_1_4_0):
    from sqlalchemy.engine import URL
else:
    from sqlalchemy.engine.url import URL

from komodo._vendored.komodo_connector.connection import Connection


@runtime_checkable
class ConnectionCreator(Protocol):
    def __init__(self, driver: Any, connection_config: Dict[str, str]) -> None: ...

    def create(self) -> Connection: ...

    def build_connection_url(self) -> Union[str, URL, None]: ...
