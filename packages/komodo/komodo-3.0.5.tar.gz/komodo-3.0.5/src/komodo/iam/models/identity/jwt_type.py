from __future__ import annotations
import json
from enum import Enum
from typing_extensions import Self


class JWTType(str, Enum):
    """
    JWTType
    """

    """
    allowed enum values
    """
    USER = "user"
    SERVICE_PRINCIPAL = "service_principal"

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of JWTType from a JSON string"""
        return cls(json.loads(json_str))
