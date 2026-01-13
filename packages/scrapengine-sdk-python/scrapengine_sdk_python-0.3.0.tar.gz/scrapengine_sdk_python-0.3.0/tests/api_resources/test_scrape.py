# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from scrapengine import Scrapengine, AsyncScrapengine
from tests.utils import assert_matches_type
from scrapengine.types import ScrapeCreateResponse, ScrapeGetStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestScrape:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Scrapengine) -> None:
        scrape = client.scrape.create(
            url="https://www.example.com",
        )
        assert_matches_type(ScrapeCreateResponse, scrape, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Scrapengine) -> None:
        scrape = client.scrape.create(
            url="https://www.example.com",
            async_=True,
            body={"foo": "bar"},
            country="country",
            extract={
                "include_metadata": True,
                "model": "gpt-4o",
                "prompt": "Extract the product name, price, and all features from this page",
                "schema": {"foo": "bar"},
                "system_prompt": "systemPrompt",
            },
            format="raw",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "en-US",
            },
            include_headers=True,
            method="get",
            render=True,
        )
        assert_matches_type(ScrapeCreateResponse, scrape, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Scrapengine) -> None:
        response = client.scrape.with_raw_response.create(
            url="https://www.example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = response.parse()
        assert_matches_type(ScrapeCreateResponse, scrape, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Scrapengine) -> None:
        with client.scrape.with_streaming_response.create(
            url="https://www.example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = response.parse()
            assert_matches_type(ScrapeCreateResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_status(self, client: Scrapengine) -> None:
        scrape = client.scrape.get_status(
            "job_abc123_xyz789",
        )
        assert_matches_type(ScrapeGetStatusResponse, scrape, path=["response"])

    @parametrize
    def test_raw_response_get_status(self, client: Scrapengine) -> None:
        response = client.scrape.with_raw_response.get_status(
            "job_abc123_xyz789",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = response.parse()
        assert_matches_type(ScrapeGetStatusResponse, scrape, path=["response"])

    @parametrize
    def test_streaming_response_get_status(self, client: Scrapengine) -> None:
        with client.scrape.with_streaming_response.get_status(
            "job_abc123_xyz789",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = response.parse()
            assert_matches_type(ScrapeGetStatusResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get_status(self, client: Scrapengine) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.scrape.with_raw_response.get_status(
                "",
            )


class TestAsyncScrape:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncScrapengine) -> None:
        scrape = await async_client.scrape.create(
            url="https://www.example.com",
        )
        assert_matches_type(ScrapeCreateResponse, scrape, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncScrapengine) -> None:
        scrape = await async_client.scrape.create(
            url="https://www.example.com",
            async_=True,
            body={"foo": "bar"},
            country="country",
            extract={
                "include_metadata": True,
                "model": "gpt-4o",
                "prompt": "Extract the product name, price, and all features from this page",
                "schema": {"foo": "bar"},
                "system_prompt": "systemPrompt",
            },
            format="raw",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "en-US",
            },
            include_headers=True,
            method="get",
            render=True,
        )
        assert_matches_type(ScrapeCreateResponse, scrape, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncScrapengine) -> None:
        response = await async_client.scrape.with_raw_response.create(
            url="https://www.example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = await response.parse()
        assert_matches_type(ScrapeCreateResponse, scrape, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncScrapengine) -> None:
        async with async_client.scrape.with_streaming_response.create(
            url="https://www.example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = await response.parse()
            assert_matches_type(ScrapeCreateResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_status(self, async_client: AsyncScrapengine) -> None:
        scrape = await async_client.scrape.get_status(
            "job_abc123_xyz789",
        )
        assert_matches_type(ScrapeGetStatusResponse, scrape, path=["response"])

    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncScrapengine) -> None:
        response = await async_client.scrape.with_raw_response.get_status(
            "job_abc123_xyz789",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = await response.parse()
        assert_matches_type(ScrapeGetStatusResponse, scrape, path=["response"])

    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncScrapengine) -> None:
        async with async_client.scrape.with_streaming_response.get_status(
            "job_abc123_xyz789",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = await response.parse()
            assert_matches_type(ScrapeGetStatusResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get_status(self, async_client: AsyncScrapengine) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.scrape.with_raw_response.get_status(
                "",
            )
