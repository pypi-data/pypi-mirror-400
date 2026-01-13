# type: ignore
from typing import Any, Dict, List, Optional, Tuple

from komodo._vendored.komodo_connector.connection import Connection
from komodo._vendored.komodo_connector.connector import connect as komodo_connect
from snowflake.sqlalchemy import dialect as SnowflakeDialect
from sqlalchemy.engine import default, reflection
from sqlalchemy.engine.url import URL

VENDOR_DIALECTS = {
    "snowflake": SnowflakeDialect,
}


class KomodoDialectMeta(type):
    def __getattr__(cls, name: str) -> Any:
        vendor_dialect = cls.get_dialect_class_from_url(cls.connection_string)
        if vendor_dialect is None:
            raise AttributeError(f"{cls.__name__} object has no attribute {name}")

        return getattr(vendor_dialect, name)


class KomodoDriverDialect(default.DefaultDialect, metaclass=KomodoDialectMeta):
    # A Dialect class needs to be configured at build time for a SQLAlchemy plugin.
    #
    # However, since we need to dynamically determine the vendor to inherit from at runtime,
    # we use a combination of a sqlAlchemy engine plugin that populates the class attribute
    # 'connection_string' at runtime, and a metaclass that uses this class attribute to
    # dynamically sets a __getattr__ from dialect of the vendor set in the connection string.
    #
    # We cannot dynamically set properties at runtime in the class methods because sqlAlchemy
    # looks up class attributes that need to be fetched from the vendor Dialect before any
    # KomodoDriverDialect instances are created, so none of the class method bodies are *executed*
    # until after the class is instantiated.
    #
    # This allows us to use the same Dialect class for all vendors, and dynamically inherit
    # from the correct vendor dialect at runtime.

    connection_string: URL = None  # Populated at runtime, do not set here
    optional_connection_params: Tuple[str, ...] = ("protocol", "env", "komodo_host", "app_id", "role", "warehouse")
    dialect_connection_args_key = "dialect_connection_args"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.connection_string is None:
            raise ValueError("Connection string cannot be None")

        vendor_dialect_class = self.get_dialect_class_from_url(self.connection_string)
        self._delegate = vendor_dialect_class(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")

        if callable(attr := getattr(self._delegate, name)):

            def wrapper(*args, **kwargs):
                return attr(*args, **kwargs)

            return wrapper
        else:
            return attr

    @classmethod
    def get_dialect_class_from_url(cls, engine_url: Optional[URL]) -> Optional[default.DefaultDialect]:
        if engine_url is None:
            raise ValueError("Engine URL cannot be None")

        if vendor := (engine_url.query.get("dialect") or engine_url.username.split("+", 1)[0]):
            try:
                return VENDOR_DIALECTS[vendor]
            except KeyError as e:
                raise NotImplementedError(f"Vendor {vendor} is not supported") from e
        raise NotImplementedError("Vendor not specified")

    def create_connect_args(self, url: URL) -> Tuple[List[Any], Dict[str, str]]:
        return self._delegate.create_connect_args(url)

    def connect(self, *cargs: Dict[str, str], **cparams: Dict[str, str]) -> Connection:
        connect_params = {param: cparams[param] for param in self.optional_connection_params if param in cparams}
        # Need to account for if the params are in the query string
        query_string_params = {
            param: self.connection_string.query.get(param)
            for param in self.optional_connection_params
            if self.connection_string.query.get(param)
        }

        if query_arg := self.connection_string.query.get("dialect"):
            # SQLAlchemy doesn't support multiple dialects in the connection string, so we
            # need to add the dialect to the username and parse it out later in the Komodo driver
            username = f"{query_arg}+{self.connection_string.username}"
        else:
            username = self.connection_string.username

        self.connection_string = URL(
            drivername=self.connection_string.drivername,
            username=username,
            password=self.connection_string.password,
            host=self.connection_string.host,
            port=self.connection_string.port,
            database=self.connection_string.database,
            query=connect_params | query_string_params,
        )
        connection = komodo_connect(
            self.connection_string.render_as_string(hide_password=False),
            **cparams.get(self.dialect_connection_args_key, {}),
        )
        return connection

    @reflection.cache
    def _current_database_schema(self, connection, **kw):
        return self._delegate._current_database_schema(connection, **kw)

    @reflection.cache
    def get_indexes(self, connection, table_name, schema=None, **kw):
        return self._delegate.get_indexes(connection, table_name, schema, **kw)

    @reflection.cache
    def get_check_constraints(self, connection, table_name, schema, **kw):
        return self._delegate.get_check_constraints(connection, table_name, schema, **kw)

    @reflection.cache
    def _get_schema_primary_keys(self, connection, schema, **kw):
        return self._delegate._get_schema_primary_keys(connection, schema, **kw)

    @reflection.cache
    def _get_schema_unique_constraints(self, connection, schema, **kw):
        return self._delegate._get_schema_unique_constraints(connection, schema, **kw)

    @reflection.cache
    def _get_schema_foreign_keys(self, connection, schema, **kw):
        return self._delegate._get_schema_foreign_keys(connection, schema, **kw)

    @reflection.cache
    def _get_schema_columns(self, connection, schema, **kw):
        return self._delegate._get_schema_columns(connection, schema, **kw)

    @reflection.cache
    def _get_table_columns(self, connection, table_name, schema=None, **kw):
        return self._delegate._get_table_columns(connection, table_name, schema, **kw)

    @reflection.cache
    def get_table_names(self, connection, schema=None, **kw):
        return self._delegate.get_table_names(connection, schema, **kw)

    @reflection.cache
    def get_view_names(self, connection, schema=None, **kw):
        return self._delegate.get_view_names(connection, schema, **kw)

    @reflection.cache
    def get_view_definition(self, connection, view_name, schema=None, **kw):
        return self._delegate.get_view_definition(connection, view_name, schema, **kw)

    @reflection.cache
    def get_sequence_names(self, connection, schema=None, **kw):
        return self._delegate.get_sequence_names(connection, schema, **kw)

    @reflection.cache
    def get_schema_names(self, connection, **kw):
        return self._delegate.get_schema_names(connection, **kw)

    @reflection.cache
    def get_columns(self, connection, table_name, schema=None, **kw):
        return self._delegate.get_columns(connection, table_name, schema, **kw)

    @reflection.cache
    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        return self._delegate.get_pk_constraint(connection, table_name, schema, **kw)

    @reflection.cache
    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        return self._delegate.get_foreign_keys(connection, table_name, schema, **kw)

    @reflection.cache
    def has_table(self, connection, table_name, schema=None):
        return self._delegate.has_table(connection, table_name, schema)

    @reflection.cache
    def has_sequence(self, connection, sequence_name, schema=None):
        return self._delegate.has_sequence(connection, sequence_name, schema)
