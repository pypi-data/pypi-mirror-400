# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scrapengine import Scrapengine, AsyncScrapengine
from tests.utils import assert_matches_type
from scrapengine.types import AmazonSearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAmazon:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_search(self, client: Scrapengine) -> None:
        amazon = client.amazon.search(
            q="q",
        )
        assert_matches_type(AmazonSearchResponse, amazon, path=["response"])

    @parametrize
    def test_method_search_with_all_params(self, client: Scrapengine) -> None:
        amazon = client.amazon.search(
            q="q",
            amazon_domain="www.amazon.com",
            async_=True,
            country="country",
            department="department",
            page=1,
            price_max=0,
            price_min=0,
            prime=True,
            raw_html=True,
            sort_by="relevanceblender",
        )
        assert_matches_type(AmazonSearchResponse, amazon, path=["response"])

    @parametrize
    def test_raw_response_search(self, client: Scrapengine) -> None:
        response = client.amazon.with_raw_response.search(
            q="q",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        amazon = response.parse()
        assert_matches_type(AmazonSearchResponse, amazon, path=["response"])

    @parametrize
    def test_streaming_response_search(self, client: Scrapengine) -> None:
        with client.amazon.with_streaming_response.search(
            q="q",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            amazon = response.parse()
            assert_matches_type(AmazonSearchResponse, amazon, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAmazon:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_search(self, async_client: AsyncScrapengine) -> None:
        amazon = await async_client.amazon.search(
            q="q",
        )
        assert_matches_type(AmazonSearchResponse, amazon, path=["response"])

    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncScrapengine) -> None:
        amazon = await async_client.amazon.search(
            q="q",
            amazon_domain="www.amazon.com",
            async_=True,
            country="country",
            department="department",
            page=1,
            price_max=0,
            price_min=0,
            prime=True,
            raw_html=True,
            sort_by="relevanceblender",
        )
        assert_matches_type(AmazonSearchResponse, amazon, path=["response"])

    @parametrize
    async def test_raw_response_search(self, async_client: AsyncScrapengine) -> None:
        response = await async_client.amazon.with_raw_response.search(
            q="q",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        amazon = await response.parse()
        assert_matches_type(AmazonSearchResponse, amazon, path=["response"])

    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncScrapengine) -> None:
        async with async_client.amazon.with_streaming_response.search(
            q="q",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            amazon = await response.parse()
            assert_matches_type(AmazonSearchResponse, amazon, path=["response"])

        assert cast(Any, response.is_closed) is True
