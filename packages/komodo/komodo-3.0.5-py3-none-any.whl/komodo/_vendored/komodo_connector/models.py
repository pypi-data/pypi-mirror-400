from typing import Dict, Union
from urllib.parse import quote

from pydantic import BaseModel, model_validator

from komodo._vendored.komodo_connector.constants import Environment
from komodo._vendored.komodo_connector.creator import ConnectionCreator


class KomodoAuthenticationParams(BaseModel):
    komodo_account: str
    komodo_user: str
    komodo_token: str

    @model_validator(mode="after")
    def clean_and_quote(self) -> "KomodoAuthenticationParams":
        self.komodo_account = quote(self.komodo_account)
        self.komodo_user = quote(self.komodo_user)

        token = self.komodo_token.strip()

        if token and token[0] in ('"', "'") and token[-1] == token[0]:
            token = token[1:-1]

        # Remove any existing Bearer prefix, ignoring case.
        if token.lower().startswith("bearer "):
            token = token[7:]

        # URL-encode the token and add the standardized Bearer prefix.
        self.komodo_token = f"Bearer {quote(token)}"
        return self


class KomodoConnectionConfig(BaseModel):
    komodo_account: str
    komododb_port: Union[int, None]
    komodo_user: str
    komodo_token: str
    environment: Environment = Environment.PROD
    query_params: Dict[str, Union[str, Dict[str, str]]]

    @model_validator(mode="after")
    def add_bearer(self) -> "KomodoConnectionConfig":
        if not (self.komodo_token.startswith("bearer ") or self.komodo_token.startswith("Bearer ")):
            self.komodo_token = f"Bearer {self.komodo_token}"
        return self


class DriverConfig(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    driver_module_path: str
    driver_creator_class: ConnectionCreator
