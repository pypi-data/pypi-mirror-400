# type: ignore
from typing import Dict, Type, Union

from snowflake.snowpark import Session

from komodo._vendored.komodo_connector.connector import connect as komodo_connect


class KomodoSessionBuilder(Session.SessionBuilder):
    def __init__(self) -> None:
        super().__init__()

    def configs(self, options: Dict[str, Union[int, str]]) -> "Session.SessionBuilder":
        conn = komodo_connect(
            account_id=options.get("account_id"),
            profile_id=options.get("profile_id"),
            secret=options.get("secret"),
            port=options.get("port"),
            protocol=options.get("protocol"),
            environment=options.get("environment"),
            session_parameters=options.get("session_parameters"),
        )
        self._options = {
            **self._options,
            **{
                "connection": conn,
            },
        }
        return super().configs(options)


class SnowparkSession(Session):
    @classmethod
    @property
    def builder(cls: Type[Session]) -> "Session.SessionBuilder":
        return KomodoSessionBuilder()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
