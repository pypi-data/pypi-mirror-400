# -*- coding: utf-8 -*-
# copyright 2025 Snow Leopard, Inc
# released under the MIT license - see LICENSE file

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class StrEnum(str, Enum):
    """String enum compatible with Python 3.8"""

    pass


@dataclass
class RetrieveResponse:
    objType = "retrieveResponse"

    callId: str
    data: List[Union[SchemaData, ErrorSchemaData]]
    responseStatus: ResponseStatus


@dataclass
class RetrieveResponseError:
    objType = "apiError"

    callId: str
    responseStatus: str
    description: str


@dataclass
class SchemaData:
    objType = "schemaData"

    schemaId: str
    schemaType: str
    query: str
    rows: List[Dict[str, Any]]
    querySummary: Dict[str, Any]
    rowMax: int
    isTrimmed: bool
    callId: str = None


@dataclass
class ErrorSchemaData:
    objType = "errorSchemaData"

    schemaType: str
    schemaId: str
    query: str
    error: str
    querySummary: Dict[str, Any]
    datastoreExceptionInfo: Optional[str] = None
    callId: str = None


@dataclass
class ResponseStart:
    objType = "responseStart"

    callId: str
    userQuery: str


@dataclass
class ResponseData:
    objType = "responseData"

    callId: str
    data: List[Union[SchemaData, ErrorSchemaData]]


@dataclass
class EarlyTermination:
    objType = "earlyTermination"

    callId: str
    responseStatus: ResponseStatus
    reason: str
    extra: dict


@dataclass
class ResponseLLMResult:
    objType = "responseResult"

    callId: str
    responseStatus: ResponseStatus
    llmResponse: Dict[str, Any]


class ResponseStatus(StrEnum):
    SUCCESS = "SUCCESS"
    NOT_FOUND_IN_SCHEMA = "NOT_FOUND_IN_SCHEMA"
    UNKNOWN = "UNKNOWN"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    LLM_ERROR = "LLM_ERROR"
    LLM_TOKEN_LIMIT_REACHED = "LLM_TOKEN_LIMIT_REACHED"


_PARSE_OBJS = {
    o.objType: o
    for o in (
        RetrieveResponse,
        RetrieveResponseError,
        SchemaData,
        ErrorSchemaData,
        ResponseStart,
        ResponseData,
        EarlyTermination,
        ResponseLLMResult,
    )
}

RetrieveResponseObjects = Union[RetrieveResponse, RetrieveResponseError]

ResponseDataObjects = Union[
    ErrorSchemaData,
    ResponseStart,
    ResponseData,
    EarlyTermination,
    ResponseLLMResult,
]


def parse(obj):
    if isinstance(obj, dict):
        kind = _PARSE_OBJS.get(obj.get("__type__"))
        if kind:
            keys = {f.name for f in fields(kind)}
            kwargs = {k: parse(v) for k, v in obj.items() if k in keys}
            return kind(**kwargs)
        else:
            return obj
    elif isinstance(obj, list):
        return [parse(v) for v in obj]
    else:
        return obj
