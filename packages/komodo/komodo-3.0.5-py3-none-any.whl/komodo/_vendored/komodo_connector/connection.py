from typing import Any, Dict, Optional


class Connection(object):
    """
    Komodo database driver following DB 2.0 API
    This driver is a wrapper around snowflake or databricks drivers
    It is used to connect to the database and execute queries
    It is also used to get the list of tables and columns in the database
    It should completely implement all DB 2.0 API methods for Connection.

    """

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def close(self, *args: Optional[Any], **kwargs: Optional[Dict[str, Any]]) -> None:
        self.connection.close(*args, **kwargs)

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def cursor(self, *args: Optional[Any], **kwargs: Optional[Dict[str, Any]]) -> Any:
        return self.connection.cursor(*args, **kwargs)

    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def __del__(self) -> None:
        del self.connection

    def __getattr__(self, name: str) -> Any:
        return getattr(self.connection, name)
