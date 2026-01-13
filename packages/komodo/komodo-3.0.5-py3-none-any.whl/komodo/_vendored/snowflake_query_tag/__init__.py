"""
This module provides pydantic classes to build a standard Snowflake query tag for KH applications and services.

Example usage:
>>> env = EnvEnum("prod")
>>> type = "eng"
>>> nest = "compute"
>>> account_id = "00000000-0000-0000-0000-000000000000"
>>> user_id = "00000000-0000-0000-0000-000000000000"
>>> service = VersionedProperties(name="ucc",version="1.0.0", properties={"cohort_run_id": 42})
>>> client = VersionedProperties(name="prism",version="1.0.0", properties={})
>>> trace = Trace(trace_id="00000000-0000-0000-0000-000000000000", parent_id="00000000-0000-0000-0000-000000000000")
>>> snowflakeTag = SnowflakeTag(type=type,env=env, nest=nest, account_id=account_id, user_id=user_id, service=service, client=client,trace=trace)
>>> query_tag = snowflakeTag.model_dump_json(exclude_none=True,exclude_unset=True, by_alias=True, indent=4)

Output (formatted):
{
    "env": "prod",
    "nest": "compute",
    "account_id": "00000000-0000-0000-0000-000000000000",
    "type": "eng",
    "user_id": "00000000-0000-0000-0000-000000000000",
    "trace": {
        "trace_id": "00000000-0000-0000-0000-000000000000",
        "parent_id": "00000000-0000-0000-0000-000000000000"
    },
    "service": {
        "name": "ucc",
        "properties": {
            "cohort_run_id": 42
        },
        "version": "1.0.0"
    },
    "client": {
        "name": "prism",
        "properties": {},
        "version": "1.0.0"
    }
}
"""


__version__ = "1.0.0"
