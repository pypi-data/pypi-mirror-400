# -*- coding: utf-8 -*-
# copyright 2025 Snow Leopard, Inc
# released under the MIT license - see LICENSE file

import json
from typing import Optional, Generator, Dict, Any

import httpx
from snowleopard.client_base import SLClientBase
from snowleopard.models import parse, RetrieveResponseObjects, ResponseDataObjects


class SnowLeopardClient(SLClientBase):
    client: httpx.Client

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: Optional[httpx.Timeout] = None,
        loc: str = None,
    ):
        config = self._config(api_key, timeout, loc)
        self.client = httpx.Client(
            base_url=config.loc, headers=config.headers(), timeout=config.timeout
        )

    def retrieve(
        self,
        *,
        user_query: str,
        known_data: Optional[Dict[str, Any]] = None,
        datafile_id: Optional[str] = None,
    ) -> RetrieveResponseObjects:
        resp = self.client.post(
            url=self._build_path(datafile_id, "retrieve"),
            json=self._build_request_body(user_query, known_data),
        )
        if resp.status_code not in (200, 409):
            resp.raise_for_status()
        return self._parse_retrieve(resp)

    def response(
        self,
        *,
        known_data: Optional[Dict[str, Any]] = None,
        user_query: str,
        datafile_id: Optional[str] = None,
    ) -> Generator[ResponseDataObjects, None, None]:
        with self.client.stream(
            "POST",
            url=self._build_path(datafile_id, "response"),
            json=self._build_request_body(user_query, known_data),
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                yield parse(json.loads(line))

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.__exit__(exc_type, exc_val, exc_tb)

    def close(self):
        self.client.close()
