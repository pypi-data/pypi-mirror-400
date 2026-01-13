# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal

import httpx

from ..types import scrape_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.scrape_create_response import ScrapeCreateResponse
from ..types.scrape_get_status_response import ScrapeGetStatusResponse

__all__ = ["ScrapeResource", "AsyncScrapeResource"]


class ScrapeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ScrapeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ScrapeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ScrapeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return ScrapeResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        url: str,
        async_: bool | Omit = omit,
        body: Dict[str, object] | Omit = omit,
        country: str | Omit = omit,
        extract: scrape_create_params.Extract | Omit = omit,
        format: Literal["raw", "json", "markdown"] | Omit = omit,
        headers: Dict[str, str] | Omit = omit,
        include_headers: bool | Omit = omit,
        method: Literal["get", "post", "put", "delete", "patch", "head", "options"] | Omit = omit,
        render: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ScrapeCreateResponse:
        """
        Scrape any URL with built-in stealthy capabilities with optional JavaScript
        rendering, custom headers, and AI-powered data extraction.

        Args:
          url: The URL to scrape

          async_: Run asynchronously and return job ID

          body: Request body for POST/PUT/PATCH requests

          country: Proxy country for geo-targeted requests

          extract: AI-powered data extraction options

          format: Response format

          headers: Custom HTTP headers for the request

          include_headers: Include response headers in the result

          method: HTTP method for the request

          render: Render JavaScript on the page using a headless browser

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/scrape",
            body=maybe_transform(
                {
                    "url": url,
                    "async_": async_,
                    "body": body,
                    "country": country,
                    "extract": extract,
                    "format": format,
                    "headers": headers,
                    "include_headers": include_headers,
                    "method": method,
                    "render": render,
                },
                scrape_create_params.ScrapeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeCreateResponse,
        )

    def get_status(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ScrapeGetStatusResponse:
        """
        Retrieve the status and results of an asynchronous scrape job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get(
            f"/scrape/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeGetStatusResponse,
        )


class AsyncScrapeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncScrapeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncScrapeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncScrapeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return AsyncScrapeResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        url: str,
        async_: bool | Omit = omit,
        body: Dict[str, object] | Omit = omit,
        country: str | Omit = omit,
        extract: scrape_create_params.Extract | Omit = omit,
        format: Literal["raw", "json", "markdown"] | Omit = omit,
        headers: Dict[str, str] | Omit = omit,
        include_headers: bool | Omit = omit,
        method: Literal["get", "post", "put", "delete", "patch", "head", "options"] | Omit = omit,
        render: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ScrapeCreateResponse:
        """
        Scrape any URL with built-in stealthy capabilities with optional JavaScript
        rendering, custom headers, and AI-powered data extraction.

        Args:
          url: The URL to scrape

          async_: Run asynchronously and return job ID

          body: Request body for POST/PUT/PATCH requests

          country: Proxy country for geo-targeted requests

          extract: AI-powered data extraction options

          format: Response format

          headers: Custom HTTP headers for the request

          include_headers: Include response headers in the result

          method: HTTP method for the request

          render: Render JavaScript on the page using a headless browser

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/scrape",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "async_": async_,
                    "body": body,
                    "country": country,
                    "extract": extract,
                    "format": format,
                    "headers": headers,
                    "include_headers": include_headers,
                    "method": method,
                    "render": render,
                },
                scrape_create_params.ScrapeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeCreateResponse,
        )

    async def get_status(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ScrapeGetStatusResponse:
        """
        Retrieve the status and results of an asynchronous scrape job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._get(
            f"/scrape/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeGetStatusResponse,
        )


class ScrapeResourceWithRawResponse:
    def __init__(self, scrape: ScrapeResource) -> None:
        self._scrape = scrape

        self.create = to_raw_response_wrapper(
            scrape.create,
        )
        self.get_status = to_raw_response_wrapper(
            scrape.get_status,
        )


class AsyncScrapeResourceWithRawResponse:
    def __init__(self, scrape: AsyncScrapeResource) -> None:
        self._scrape = scrape

        self.create = async_to_raw_response_wrapper(
            scrape.create,
        )
        self.get_status = async_to_raw_response_wrapper(
            scrape.get_status,
        )


class ScrapeResourceWithStreamingResponse:
    def __init__(self, scrape: ScrapeResource) -> None:
        self._scrape = scrape

        self.create = to_streamed_response_wrapper(
            scrape.create,
        )
        self.get_status = to_streamed_response_wrapper(
            scrape.get_status,
        )


class AsyncScrapeResourceWithStreamingResponse:
    def __init__(self, scrape: AsyncScrapeResource) -> None:
        self._scrape = scrape

        self.create = async_to_streamed_response_wrapper(
            scrape.create,
        )
        self.get_status = async_to_streamed_response_wrapper(
            scrape.get_status,
        )
