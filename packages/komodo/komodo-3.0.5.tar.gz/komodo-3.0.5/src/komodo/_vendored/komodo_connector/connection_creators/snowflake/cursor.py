# type: ignore
# fmt: off
import logging
import re
import traceback

from snowflake.connector import cursor

logger = logging.getLogger(__name__)


class KomodoSnowflakeCursor(cursor.SnowflakeCursor):
    USE_WAREHOUSE_QUERY = r"\buse\s+warehouse\b"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute(self, command: str, *args, **kwargs) -> None:
        if re.search(self.USE_WAREHOUSE_QUERY, command, re.IGNORECASE):
            logging.warning(f"Invalid Query: {command}")
            raise ValueError("Invalid Query: The 'USE WAREHOUSE' command is not permitted.")
        try:
            return super().execute(command, *args, **kwargs)
        except AttributeError as e:
            if "serialize_to_dict" in str(e):
                logger.error(
                    f"Error executing query: {command}. Error: {e}. Traceback: {traceback.format_exc()}"
                )
                raise Exception(
                    "This query failed to execute. Please check the query syntax or connection settings or permissions on the role used.")
            raise


class KomodoSnowflakeDictCursor(KomodoSnowflakeCursor):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, use_dict_result=True)
