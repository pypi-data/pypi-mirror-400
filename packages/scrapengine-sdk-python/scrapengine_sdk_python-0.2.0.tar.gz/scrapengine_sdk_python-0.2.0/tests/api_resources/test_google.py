# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scrapengine import Scrapengine, AsyncScrapengine
from tests.utils import assert_matches_type
from scrapengine.types import GoogleSearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGoogle:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_search(self, client: Scrapengine) -> None:
        google = client.google.search(
            q="q",
        )
        assert_matches_type(GoogleSearchResponse, google, path=["response"])

    @parametrize
    def test_method_search_with_all_params(self, client: Scrapengine) -> None:
        google = client.google.search(
            q="q",
            async_=True,
            device="desktop",
            filter=0,
            gl="gl",
            google_domain="googleDomain",
            hl="hl",
            location="location",
            nfpr=0,
            num=1,
            raw_html=True,
            safe="off",
            start=0,
            tbm="search",
            tbs="tbs",
            uule="uule",
        )
        assert_matches_type(GoogleSearchResponse, google, path=["response"])

    @parametrize
    def test_raw_response_search(self, client: Scrapengine) -> None:
        response = client.google.with_raw_response.search(
            q="q",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        google = response.parse()
        assert_matches_type(GoogleSearchResponse, google, path=["response"])

    @parametrize
    def test_streaming_response_search(self, client: Scrapengine) -> None:
        with client.google.with_streaming_response.search(
            q="q",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            google = response.parse()
            assert_matches_type(GoogleSearchResponse, google, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGoogle:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_search(self, async_client: AsyncScrapengine) -> None:
        google = await async_client.google.search(
            q="q",
        )
        assert_matches_type(GoogleSearchResponse, google, path=["response"])

    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncScrapengine) -> None:
        google = await async_client.google.search(
            q="q",
            async_=True,
            device="desktop",
            filter=0,
            gl="gl",
            google_domain="googleDomain",
            hl="hl",
            location="location",
            nfpr=0,
            num=1,
            raw_html=True,
            safe="off",
            start=0,
            tbm="search",
            tbs="tbs",
            uule="uule",
        )
        assert_matches_type(GoogleSearchResponse, google, path=["response"])

    @parametrize
    async def test_raw_response_search(self, async_client: AsyncScrapengine) -> None:
        response = await async_client.google.with_raw_response.search(
            q="q",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        google = await response.parse()
        assert_matches_type(GoogleSearchResponse, google, path=["response"])

    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncScrapengine) -> None:
        async with async_client.google.with_streaming_response.search(
            q="q",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            google = await response.parse()
            assert_matches_type(GoogleSearchResponse, google, path=["response"])

        assert cast(Any, response.is_closed) is True
