# -*- coding: utf-8 -*-
# copyright 2025 Snow Leopard, Inc
# released under the MIT license - see LICENSE file

import json
from typing import AsyncGenerator, Optional, Dict, Any

import httpx
from snowleopard.client_base import SLClientBase
from snowleopard.models import ResponseDataObjects, RetrieveResponseObjects, parse


class AsyncSnowLeopardClient(SLClientBase):
    client: httpx.AsyncClient

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: Optional[httpx.Timeout] = None,
        loc: str = None,
    ):
        config = self._config(api_key, timeout, loc)
        self.client = httpx.AsyncClient(
            base_url=config.loc, headers=config.headers(), timeout=config.timeout
        )

    async def retrieve(
        self,
        *,
        user_query: str,
        known_data: Optional[Dict[str, Any]] = None,
        datafile_id: Optional[str] = None,
    ) -> RetrieveResponseObjects:
        resp = await self.client.post(
            url=self._build_path(datafile_id, "retrieve"),
            json=self._build_request_body(user_query, known_data),
        )
        return self._parse_retrieve(resp)

    async def response(
        self,
        *,
        known_data: Optional[Dict[str, Any]] = None,
        user_query: str,
        datafile_id: Optional[str] = None,
    ) -> AsyncGenerator[ResponseDataObjects, None]:
        async with self.client.stream(
            "POST",
            self._build_path(datafile_id, "response"),
            json=self._build_request_body(user_query, known_data),
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                yield parse(json.loads(line))

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        await self.client.aclose()
