# -*- coding: utf-8 -*-
# copyright 2025 Snow Leopard, Inc
# released under the MIT license - see LICENSE file

import os
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any

import httpx

from snowleopard.models import parse


@dataclass
class SLConfig:
    api_key: str
    timeout: httpx.Timeout
    loc: str

    def headers(self):
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


class SLClientBase:
    @abstractmethod
    def retrieve(
        self,
        *,
        user_query: str,
        known_data: Optional[Dict[str, Any]] = None,
        datafile_id: Optional[str] = None,
    ):
        """
        The primary for developers building AI agents that needs to retrieve data from a database directly.

        Takes a natural language question (usually from the user or the agent) and returns the data required to answer
        the query in an LLM-friendly object.

        :param datafile_id: (optional) The playground datafile-id if hitting a Snow Leopard api directly
        :param user_query: Natural language query to execute against the Playground datafile
        :param known_data: Additional context about the user_query
        """
        ...

    @abstractmethod
    def response(
        self,
        *,
        known_data: Optional[Dict[str, Any]] = None,
        user_query: str,
        datafile_id: Optional[str] = None,
    ):
        """
        Takes a natural language question (usually from the user or the agent) and returns the data required to answer
        the query as well as a LLM summary of the returned data.

        :param datafile_id: (optional) The playground datafile-id if hitting a Snow Leopard api directly
        :param user_query: Natural language query to execute against the Playground datafile
        :param known_data: (optional) Additional context about the user_query
        """
        ...

    @staticmethod
    def _config(
        api_key: Optional[str], timeout: Optional[httpx.Timeout], loc: Optional[str]
    ) -> SLConfig:
        api_key = api_key or os.environ.get("SNOWLEOPARD_API_KEY")
        if api_key is None:
            raise ValueError(
                'Missing required argument "api_key" and environment variable "SNOWLEOPARD_API_KEY" not set'
            )
        timeout = timeout or httpx.Timeout(
            connect=5.0, read=600.0, write=10.0, pool=5.0
        )
        loc = loc or os.environ.get("SNOWLEOPARD_LOC", "https://api.snowleopard.ai")
        if not loc:
            raise ValueError(
                'Missing required argument "loc" and environment variable "SNOWLEOPARD_LOC" not set'
            )
        return SLConfig(api_key, timeout, loc)

    @staticmethod
    def _build_path(datafile_id: str, endpoint: str) -> str:
        if datafile_id is None:
            return endpoint
        else:
            return f"datafiles/{datafile_id}/{endpoint}"

    @staticmethod
    def _build_request_body(
        user_query: str, known_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        body = {"userQuery": user_query}
        if known_data is not None:
            body["knownData"] = known_data
        return body

    @staticmethod
    def _parse_retrieve(resp):
        try:
            return parse(resp.json())
        except Exception:
            resp.raise_for_status()
            raise
