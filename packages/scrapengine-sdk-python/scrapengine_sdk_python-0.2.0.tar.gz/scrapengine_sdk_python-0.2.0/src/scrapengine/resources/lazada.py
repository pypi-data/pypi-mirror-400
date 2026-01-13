# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import lazada_search_params
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
from ..types.lazada_search_response import LazadaSearchResponse

__all__ = ["LazadaResource", "AsyncLazadaResource"]


class LazadaResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LazadaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return LazadaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LazadaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return LazadaResourceWithStreamingResponse(self)

    def search(
        self,
        *,
        q: str,
        async_: bool | Omit = omit,
        category: str | Omit = omit,
        country: str | Omit = omit,
        lazada_domain: Literal[
            "www.lazada.sg",
            "www.lazada.com.my",
            "www.lazada.co.th",
            "www.lazada.com.ph",
            "www.lazada.co.id",
            "www.lazada.vn",
        ]
        | Omit = omit,
        laz_mall: bool | Omit = omit,
        location: str | Omit = omit,
        page: int | Omit = omit,
        price_max: float | Omit = omit,
        price_min: float | Omit = omit,
        rating: float | Omit = omit,
        raw_json: bool | Omit = omit,
        sort_by: Literal["relevance", "priceasc", "pricedesc", "sales", "rating"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LazadaSearchResponse:
        """
        Search Lazada and return parsed product results including prices, ratings, and
        seller information.

        Args:
          q: Search query

          async_: Run asynchronously and return job ID

          category: Category filter

          country: Country code for localized results

          lazada_domain: Lazada domain to use

          laz_mall: Filter by LazMall products only

          location: Location filter

          page: Page number

          price_max: Maximum price filter

          price_min: Minimum price filter

          rating: Minimum rating filter (0-5)

          raw_json: Return raw JSON response

          sort_by: Sort order

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/lazada/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "q": q,
                        "async_": async_,
                        "category": category,
                        "country": country,
                        "lazada_domain": lazada_domain,
                        "laz_mall": laz_mall,
                        "location": location,
                        "page": page,
                        "price_max": price_max,
                        "price_min": price_min,
                        "rating": rating,
                        "raw_json": raw_json,
                        "sort_by": sort_by,
                    },
                    lazada_search_params.LazadaSearchParams,
                ),
            ),
            cast_to=LazadaSearchResponse,
        )


class AsyncLazadaResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLazadaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLazadaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLazadaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return AsyncLazadaResourceWithStreamingResponse(self)

    async def search(
        self,
        *,
        q: str,
        async_: bool | Omit = omit,
        category: str | Omit = omit,
        country: str | Omit = omit,
        lazada_domain: Literal[
            "www.lazada.sg",
            "www.lazada.com.my",
            "www.lazada.co.th",
            "www.lazada.com.ph",
            "www.lazada.co.id",
            "www.lazada.vn",
        ]
        | Omit = omit,
        laz_mall: bool | Omit = omit,
        location: str | Omit = omit,
        page: int | Omit = omit,
        price_max: float | Omit = omit,
        price_min: float | Omit = omit,
        rating: float | Omit = omit,
        raw_json: bool | Omit = omit,
        sort_by: Literal["relevance", "priceasc", "pricedesc", "sales", "rating"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LazadaSearchResponse:
        """
        Search Lazada and return parsed product results including prices, ratings, and
        seller information.

        Args:
          q: Search query

          async_: Run asynchronously and return job ID

          category: Category filter

          country: Country code for localized results

          lazada_domain: Lazada domain to use

          laz_mall: Filter by LazMall products only

          location: Location filter

          page: Page number

          price_max: Maximum price filter

          price_min: Minimum price filter

          rating: Minimum rating filter (0-5)

          raw_json: Return raw JSON response

          sort_by: Sort order

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/lazada/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "q": q,
                        "async_": async_,
                        "category": category,
                        "country": country,
                        "lazada_domain": lazada_domain,
                        "laz_mall": laz_mall,
                        "location": location,
                        "page": page,
                        "price_max": price_max,
                        "price_min": price_min,
                        "rating": rating,
                        "raw_json": raw_json,
                        "sort_by": sort_by,
                    },
                    lazada_search_params.LazadaSearchParams,
                ),
            ),
            cast_to=LazadaSearchResponse,
        )


class LazadaResourceWithRawResponse:
    def __init__(self, lazada: LazadaResource) -> None:
        self._lazada = lazada

        self.search = to_raw_response_wrapper(
            lazada.search,
        )


class AsyncLazadaResourceWithRawResponse:
    def __init__(self, lazada: AsyncLazadaResource) -> None:
        self._lazada = lazada

        self.search = async_to_raw_response_wrapper(
            lazada.search,
        )


class LazadaResourceWithStreamingResponse:
    def __init__(self, lazada: LazadaResource) -> None:
        self._lazada = lazada

        self.search = to_streamed_response_wrapper(
            lazada.search,
        )


class AsyncLazadaResourceWithStreamingResponse:
    def __init__(self, lazada: AsyncLazadaResource) -> None:
        self._lazada = lazada

        self.search = async_to_streamed_response_wrapper(
            lazada.search,
        )
