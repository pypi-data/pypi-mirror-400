import logging.config
from uuid import UUID
from typing import Optional

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


class SDKSettings(BaseSettings):
    # All environment variables related to the komodo platform should start with the prefix "KOMODO_"
    model_config = SettingsConfigDict(env_prefix="KOMODO_")

    environment: str = Field(default="production", env="ENVIRONMENT")
    access_token: Optional[SecretStr] = Field(default=None, env="ACCESS_TOKEN")
    refresh_token: Optional[SecretStr] = Field(default=None, env="REFRESH_TOKEN")
    token_expiration: Optional[int] = Field(default=None, env="TOKEN_EXPIRATION")
    client_id: Optional[str] = Field(default=None, env="CLIENT_ID")
    client_secret: Optional[SecretStr] = Field(default=None, env="CLIENT_SECRET")
    account_id: Optional[UUID] = Field(default=None, env="ACCOUNT_ID")
    account_slug: Optional[str] = Field(default=None, env="ACCOUNT_SLUG")

    @property
    def komodo_external(self) -> str:
        return "https://api.komodohealth.com" if self.environment == "production" else "https://dev-api.khinternal.net"

    @property
    def proxy_domain(self) -> str:
        return "https://connector-gateway.onkomodo.com" if self.environment == "production" else "https://connector-gateway.staging.onkomodo.com"

    @property
    def komodo_rbac_me(self) -> str:
        return f"{self.komodo_external}/platform-rbac-prod/v1/iam/users/me" if self.environment == "production" else f"{self.komodo_external}/platform-rbac-stage/v1/iam/users/me"

    @property
    def komodo_idp_domain(self) -> str:
        return "auth.komodohealth.com" if self.environment == "production" else "auth-staging.komodohealth.com"

    @property
    def komodo_client_id(self) -> str:
        return "mkxXDmAae54idV6TIpviUfq2ySuRdC9Y" if self.environment == "production" else "O69UYSTsC6Tz2jBgzSC30odgX5fmu0xh"

    @property
    def komodo_idp_audience(self) -> str:
        return "https://komodohealth-platform.us.auth0.com/api/v2/" if self.environment == "production" else "https://komodohealth-platform-staging.us.auth0.com/api/v2/"
