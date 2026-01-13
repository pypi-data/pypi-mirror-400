from typing import Any, Dict, Optional

from sqlalchemy.engine import CreateEnginePlugin
from sqlalchemy.engine.url import URL

from komodo._vendored.komodo_sqlalchemy.dialect import KomodoDriverDialect


class KomodoEnginePlugin(CreateEnginePlugin):
    def __init__(self, url: URL, *kwargs: Optional[Dict[str, Any]]) -> None:
        KomodoDriverDialect.connection_string = url

    def update_url(self, url: URL) -> URL:
        # Store the connection string in KomodoDriverDialect
        KomodoDriverDialect.connection_string = url
        # Return the URL without modification
        return url
