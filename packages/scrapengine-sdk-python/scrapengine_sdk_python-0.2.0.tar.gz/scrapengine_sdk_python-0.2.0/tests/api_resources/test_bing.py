# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scrapengine import Scrapengine, AsyncScrapengine
from tests.utils import assert_matches_type
from scrapengine.types import BingSearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBing:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_search(self, client: Scrapengine) -> None:
        bing = client.bing.search(
            q="q",
        )
        assert_matches_type(BingSearchResponse, bing, path=["response"])

    @parametrize
    def test_method_search_with_all_params(self, client: Scrapengine) -> None:
        bing = client.bing.search(
            q="q",
            async_=True,
            cc="cc",
            count=1,
            device="desktop",
            freshness="Day",
            location="location",
            mkt="mkt",
            offset=0,
            raw_html=True,
            response_filter="Webpages",
            safe_search="Off",
            set_lang="setLang",
            text_decorations=True,
            text_format="Raw",
        )
        assert_matches_type(BingSearchResponse, bing, path=["response"])

    @parametrize
    def test_raw_response_search(self, client: Scrapengine) -> None:
        response = client.bing.with_raw_response.search(
            q="q",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bing = response.parse()
        assert_matches_type(BingSearchResponse, bing, path=["response"])

    @parametrize
    def test_streaming_response_search(self, client: Scrapengine) -> None:
        with client.bing.with_streaming_response.search(
            q="q",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bing = response.parse()
            assert_matches_type(BingSearchResponse, bing, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBing:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_search(self, async_client: AsyncScrapengine) -> None:
        bing = await async_client.bing.search(
            q="q",
        )
        assert_matches_type(BingSearchResponse, bing, path=["response"])

    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncScrapengine) -> None:
        bing = await async_client.bing.search(
            q="q",
            async_=True,
            cc="cc",
            count=1,
            device="desktop",
            freshness="Day",
            location="location",
            mkt="mkt",
            offset=0,
            raw_html=True,
            response_filter="Webpages",
            safe_search="Off",
            set_lang="setLang",
            text_decorations=True,
            text_format="Raw",
        )
        assert_matches_type(BingSearchResponse, bing, path=["response"])

    @parametrize
    async def test_raw_response_search(self, async_client: AsyncScrapengine) -> None:
        response = await async_client.bing.with_raw_response.search(
            q="q",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bing = await response.parse()
        assert_matches_type(BingSearchResponse, bing, path=["response"])

    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncScrapengine) -> None:
        async with async_client.bing.with_streaming_response.search(
            q="q",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bing = await response.parse()
            assert_matches_type(BingSearchResponse, bing, path=["response"])

        assert cast(Any, response.is_closed) is True
