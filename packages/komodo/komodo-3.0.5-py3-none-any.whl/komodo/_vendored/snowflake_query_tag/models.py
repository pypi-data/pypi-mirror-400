from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, RootModel,field_validator
from typing import Union, Annotated, Literal, List
from packaging import version


class EnvEnum(str, Enum):
    local = "local"
    dev = "dev"
    test = "test"
    qa = "qa"
    stage = "stage"
    integration = "integration"
    prod = "prod"

class Trace(BaseModel):
    """A class used to represent a Trace (cf definition here https://opentelemetry.io/docs/concepts/signals/traces/)

    Attributes
    ----------
    trace_id: str
        Represents the trace id
    parent_id: str
        Represents the parent id
    """
    
    trace_id: str
    parent_id: str

class BasicProperties(BaseModel):
    """A class used to represent a service or an application

    Attributes
    ----------
    name: str
        Represents the name of the service
    properties: dict
        Represents any additional properties. Could be empty but not None

    """

    name: str
    properties: dict

class VersionedProperties(BasicProperties):
    """A class used to represent a service or an application

    Attributes
    ----------
    name: str
        Represents the name of the object
    properties: dict
        Represents any additional properties. Could be empty but not None
    version: str
        Represents the version of the object. Must be a valid version
    """

    version: str
    
    @field_validator('version')
    def must_be_a_version(cls, v):
        try:
            version.parse(v)
        except:
            raise ValueError('must be a version, for more information: https://packaging.python.org/en/latest/specifications/version-specifiers/')
        return v

class RootSnowflakeTag(BaseModel, extra='forbid'):
    """A class used to represent a service or an application

    Attributes
    ----------
    version: str = "3.0.0"
        The version of the current schema. Please do not modify this value.
    type: str
        commercial or eng
    env: EnvEnum
        The environment of the executed query
    nest: str
        The nest that is requesting the execution of the query
    account_id: Optional[UUID]
        The account id coming from common RBAC service, Otherwise, the tenantId.
   """

    version: str = "3.0.0"
    env: EnvEnum
    nest: str
    account_id: Optional[UUID] = None    

class EngSnowflakeTag(RootSnowflakeTag):
    """A class used to represent a service or an application

    Attributes
    ----------
    user_id: Optional[UUID]
        The user id coming from common RBAC service.
    trace: Optional[Trace]
        The trace id and parent id of the query execution (could be None)
    service: BasicProperties
        The service that is issuing the query. Should match the APM name in New Relic 
        Relates to SERVICE_NAME attribute if using OTEL https://opentelemetry.io/docs/concepts/sdk-configuration/general-sdk-configuration/#otel_service_name
        or [app_name conf if using NR agent]https://docs.newrelic.com/docs/apm/agents/python-agent/configuration/python-agent-configuration/#app_name 
    client: BasicProperties
        The client application that the service is executing on its behalf (could be None) 
        It related to the "app-id". Also a version is needed 
    """
    type: Literal['eng']
    user_id: Optional[UUID] = None
    trace: Optional[Trace] = None
    service: VersionedProperties 
    client: VersionedProperties

class CommercialSnowflakeTag(RootSnowflakeTag):
    """A class used to represent a service or an application

    Attributes
    ----------

    subnest: str
        The subnest that is requesting the execution of the query
    opportunity_id: str
        The opportunity id from salesforce related to the query
    application: BasicProperties
        The application name for which the query is running 
    data: VersionedProperties
        The fabric that the application is executing the query 
    data_products: List[VersionedProperties]
        Multiple fabrics can be utilized across various applications executing queries
    time_tracking_id: str
        NetSuite OpenAir ID associated with services provided to a prospect/customer
    """
    type : Literal['commercial']
    subnest: Optional[str] = None
    opportunity_id: str
    application: BasicProperties
    data: VersionedProperties
    data_products: Optional[List[VersionedProperties]]
    time_tracking_id: str

class DataFoundationSnowflakeTag(RootSnowflakeTag):
    """A class used to track the production of data products by the Data Foundation liar

    Attributes
    ----------

    data_product: VersionedProperties
        The fabric that the application is executing the query
        examples:
            - {"name": "polyester", "version": "23.0.0", "data_type": "rx", "properties": {}}
            - {"name": "patient_demographics", "version": "23.0.0", "properties": {}}
            - {"name": "arbok", "version": "1.0.0", "stage": "raw", "properties": {}}
            - {"name": "arbok", "version": "23.0.0", "stage": "johto", "data_type": "rx", "properties": {}}
    """
    type : Literal["data_foundation"]
    nest: Literal["foundation", "context", "cdo", "data_ingestion", "events", "product", "quality"]
    data_product: VersionedProperties

class SnowflakeTag(RootModel):
    root: Annotated[Union[CommercialSnowflakeTag, EngSnowflakeTag, DataFoundationSnowflakeTag], Field(..., discriminator='type')]
    
    def dict(self, **kwargs):
        return super().model_dump(exclude_none=True, **kwargs)
