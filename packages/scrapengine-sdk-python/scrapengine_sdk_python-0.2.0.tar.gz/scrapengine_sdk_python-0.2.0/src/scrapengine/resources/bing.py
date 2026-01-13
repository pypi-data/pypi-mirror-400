# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import bing_search_params
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
from ..types.bing_search_response import BingSearchResponse

__all__ = ["BingResource", "AsyncBingResource"]


class BingResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return BingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return BingResourceWithStreamingResponse(self)

    def search(
        self,
        *,
        q: str,
        async_: bool | Omit = omit,
        cc: str | Omit = omit,
        count: int | Omit = omit,
        device: Literal["desktop", "mobile", "tablet"] | Omit = omit,
        freshness: Literal["Day", "Week", "Month"] | Omit = omit,
        location: str | Omit = omit,
        mkt: str | Omit = omit,
        offset: int | Omit = omit,
        raw_html: bool | Omit = omit,
        response_filter: Literal["Webpages", "Images", "Videos", "News"] | Omit = omit,
        safe_search: Literal["Off", "Moderate", "Strict"] | Omit = omit,
        set_lang: str | Omit = omit,
        text_decorations: bool | Omit = omit,
        text_format: Literal["Raw", "HTML"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BingSearchResponse:
        """
        Execute a Bing search and return parsed results.

        Args:
          q: Search query

          async_: Run asynchronously and return job ID

          cc: Country code

          count: Number of results (1-50)

          device: Device type

          freshness: Freshness filter

          location: Location for geo-targeted results

          mkt: Market code (language-country format)

          offset: Pagination offset

          raw_html: Return raw HTML instead of parsed results

          response_filter: Response content filter

          safe_search: Safe search mode

          set_lang: UI language

          text_decorations: Add bold markers around search terms

          text_format: Text format

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/bing/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "q": q,
                        "async_": async_,
                        "cc": cc,
                        "count": count,
                        "device": device,
                        "freshness": freshness,
                        "location": location,
                        "mkt": mkt,
                        "offset": offset,
                        "raw_html": raw_html,
                        "response_filter": response_filter,
                        "safe_search": safe_search,
                        "set_lang": set_lang,
                        "text_decorations": text_decorations,
                        "text_format": text_format,
                    },
                    bing_search_params.BingSearchParams,
                ),
            ),
            cast_to=BingSearchResponse,
        )


class AsyncBingResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return AsyncBingResourceWithStreamingResponse(self)

    async def search(
        self,
        *,
        q: str,
        async_: bool | Omit = omit,
        cc: str | Omit = omit,
        count: int | Omit = omit,
        device: Literal["desktop", "mobile", "tablet"] | Omit = omit,
        freshness: Literal["Day", "Week", "Month"] | Omit = omit,
        location: str | Omit = omit,
        mkt: str | Omit = omit,
        offset: int | Omit = omit,
        raw_html: bool | Omit = omit,
        response_filter: Literal["Webpages", "Images", "Videos", "News"] | Omit = omit,
        safe_search: Literal["Off", "Moderate", "Strict"] | Omit = omit,
        set_lang: str | Omit = omit,
        text_decorations: bool | Omit = omit,
        text_format: Literal["Raw", "HTML"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BingSearchResponse:
        """
        Execute a Bing search and return parsed results.

        Args:
          q: Search query

          async_: Run asynchronously and return job ID

          cc: Country code

          count: Number of results (1-50)

          device: Device type

          freshness: Freshness filter

          location: Location for geo-targeted results

          mkt: Market code (language-country format)

          offset: Pagination offset

          raw_html: Return raw HTML instead of parsed results

          response_filter: Response content filter

          safe_search: Safe search mode

          set_lang: UI language

          text_decorations: Add bold markers around search terms

          text_format: Text format

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/bing/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "q": q,
                        "async_": async_,
                        "cc": cc,
                        "count": count,
                        "device": device,
                        "freshness": freshness,
                        "location": location,
                        "mkt": mkt,
                        "offset": offset,
                        "raw_html": raw_html,
                        "response_filter": response_filter,
                        "safe_search": safe_search,
                        "set_lang": set_lang,
                        "text_decorations": text_decorations,
                        "text_format": text_format,
                    },
                    bing_search_params.BingSearchParams,
                ),
            ),
            cast_to=BingSearchResponse,
        )


class BingResourceWithRawResponse:
    def __init__(self, bing: BingResource) -> None:
        self._bing = bing

        self.search = to_raw_response_wrapper(
            bing.search,
        )


class AsyncBingResourceWithRawResponse:
    def __init__(self, bing: AsyncBingResource) -> None:
        self._bing = bing

        self.search = async_to_raw_response_wrapper(
            bing.search,
        )


class BingResourceWithStreamingResponse:
    def __init__(self, bing: BingResource) -> None:
        self._bing = bing

        self.search = to_streamed_response_wrapper(
            bing.search,
        )


class AsyncBingResourceWithStreamingResponse:
    def __init__(self, bing: AsyncBingResource) -> None:
        self._bing = bing

        self.search = async_to_streamed_response_wrapper(
            bing.search,
        )
