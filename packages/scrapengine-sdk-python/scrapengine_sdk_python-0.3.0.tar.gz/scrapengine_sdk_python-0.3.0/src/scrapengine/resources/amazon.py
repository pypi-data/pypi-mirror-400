# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import amazon_search_params
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
from ..types.amazon_search_response import AmazonSearchResponse

__all__ = ["AmazonResource", "AsyncAmazonResource"]


class AmazonResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AmazonResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AmazonResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AmazonResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return AmazonResourceWithStreamingResponse(self)

    def search(
        self,
        *,
        q: str,
        amazon_domain: Literal[
            "www.amazon.com",
            "www.amazon.co.uk",
            "www.amazon.de",
            "www.amazon.fr",
            "www.amazon.co.jp",
            "www.amazon.in",
            "www.amazon.ca",
            "www.amazon.es",
            "www.amazon.it",
            "www.amazon.com.au",
        ]
        | Omit = omit,
        async_: bool | Omit = omit,
        country: str | Omit = omit,
        department: str | Omit = omit,
        page: int | Omit = omit,
        price_max: float | Omit = omit,
        price_min: float | Omit = omit,
        prime: bool | Omit = omit,
        raw_html: bool | Omit = omit,
        sort_by: Literal["relevanceblender", "price-asc-rank", "price-desc-rank", "review-rank", "date-desc-rank"]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AmazonSearchResponse:
        """
        Search Amazon and return parsed product results including prices, ratings, and
        Prime eligibility.

        Args:
          q: Search query

          amazon_domain: Amazon domain to use

          async_: Run asynchronously and return job ID

          country: Country code for localized results

          department: Department/Category filter

          page: Page number

          price_max: Maximum price filter

          price_min: Minimum price filter

          prime: Filter by Prime eligible products

          raw_html: Return raw HTML instead of parsed results

          sort_by: Sort order

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/amazon/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "q": q,
                        "amazon_domain": amazon_domain,
                        "async_": async_,
                        "country": country,
                        "department": department,
                        "page": page,
                        "price_max": price_max,
                        "price_min": price_min,
                        "prime": prime,
                        "raw_html": raw_html,
                        "sort_by": sort_by,
                    },
                    amazon_search_params.AmazonSearchParams,
                ),
            ),
            cast_to=AmazonSearchResponse,
        )


class AsyncAmazonResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAmazonResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAmazonResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAmazonResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return AsyncAmazonResourceWithStreamingResponse(self)

    async def search(
        self,
        *,
        q: str,
        amazon_domain: Literal[
            "www.amazon.com",
            "www.amazon.co.uk",
            "www.amazon.de",
            "www.amazon.fr",
            "www.amazon.co.jp",
            "www.amazon.in",
            "www.amazon.ca",
            "www.amazon.es",
            "www.amazon.it",
            "www.amazon.com.au",
        ]
        | Omit = omit,
        async_: bool | Omit = omit,
        country: str | Omit = omit,
        department: str | Omit = omit,
        page: int | Omit = omit,
        price_max: float | Omit = omit,
        price_min: float | Omit = omit,
        prime: bool | Omit = omit,
        raw_html: bool | Omit = omit,
        sort_by: Literal["relevanceblender", "price-asc-rank", "price-desc-rank", "review-rank", "date-desc-rank"]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AmazonSearchResponse:
        """
        Search Amazon and return parsed product results including prices, ratings, and
        Prime eligibility.

        Args:
          q: Search query

          amazon_domain: Amazon domain to use

          async_: Run asynchronously and return job ID

          country: Country code for localized results

          department: Department/Category filter

          page: Page number

          price_max: Maximum price filter

          price_min: Minimum price filter

          prime: Filter by Prime eligible products

          raw_html: Return raw HTML instead of parsed results

          sort_by: Sort order

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/amazon/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "q": q,
                        "amazon_domain": amazon_domain,
                        "async_": async_,
                        "country": country,
                        "department": department,
                        "page": page,
                        "price_max": price_max,
                        "price_min": price_min,
                        "prime": prime,
                        "raw_html": raw_html,
                        "sort_by": sort_by,
                    },
                    amazon_search_params.AmazonSearchParams,
                ),
            ),
            cast_to=AmazonSearchResponse,
        )


class AmazonResourceWithRawResponse:
    def __init__(self, amazon: AmazonResource) -> None:
        self._amazon = amazon

        self.search = to_raw_response_wrapper(
            amazon.search,
        )


class AsyncAmazonResourceWithRawResponse:
    def __init__(self, amazon: AsyncAmazonResource) -> None:
        self._amazon = amazon

        self.search = async_to_raw_response_wrapper(
            amazon.search,
        )


class AmazonResourceWithStreamingResponse:
    def __init__(self, amazon: AmazonResource) -> None:
        self._amazon = amazon

        self.search = to_streamed_response_wrapper(
            amazon.search,
        )


class AsyncAmazonResourceWithStreamingResponse:
    def __init__(self, amazon: AsyncAmazonResource) -> None:
        self._amazon = amazon

        self.search = async_to_streamed_response_wrapper(
            amazon.search,
        )
