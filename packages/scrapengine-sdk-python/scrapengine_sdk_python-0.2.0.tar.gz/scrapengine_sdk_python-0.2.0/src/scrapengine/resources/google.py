# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import google_search_params
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
from ..types.google_search_response import GoogleSearchResponse

__all__ = ["GoogleResource", "AsyncGoogleResource"]


class GoogleResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GoogleResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return GoogleResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GoogleResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return GoogleResourceWithStreamingResponse(self)

    def search(
        self,
        *,
        q: str,
        async_: bool | Omit = omit,
        device: Literal["desktop", "mobile", "tablet"] | Omit = omit,
        filter: Literal[0, 1] | Omit = omit,
        gl: str | Omit = omit,
        google_domain: str | Omit = omit,
        hl: str | Omit = omit,
        location: str | Omit = omit,
        nfpr: Literal[0, 1] | Omit = omit,
        num: int | Omit = omit,
        raw_html: bool | Omit = omit,
        safe: Literal["off", "medium", "high"] | Omit = omit,
        start: int | Omit = omit,
        tbm: Literal["search", "images", "news", "videos"] | Omit = omit,
        tbs: str | Omit = omit,
        uule: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GoogleSearchResponse:
        """
        Execute a Google search and return parsed results including organic results,
        ads, and related searches.

        Args:
          q: Search query

          async_: Run asynchronously and return job ID

          device: Device type for user agent simulation

          filter: Filter duplicate results (0=show all, 1=filter)

          gl: Country code (ISO 3166-1 alpha-2)

          google_domain: Google domain to use

          hl: Language code (ISO 639-1)

          location: Location for geo-targeted results

          nfpr: Disable auto-correct (0=allow, 1=disable)

          num: Number of results to return (1-100)

          raw_html: Return raw HTML instead of parsed results

          safe: Safe search mode

          start: Pagination offset

          tbm: Search type

          tbs: Time-based filter (qdr:d=day, qdr:w=week, qdr:m=month, qdr:y=year)

          uule: Encoded location for geo-targeted results (UULE format)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/google/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "q": q,
                        "async_": async_,
                        "device": device,
                        "filter": filter,
                        "gl": gl,
                        "google_domain": google_domain,
                        "hl": hl,
                        "location": location,
                        "nfpr": nfpr,
                        "num": num,
                        "raw_html": raw_html,
                        "safe": safe,
                        "start": start,
                        "tbm": tbm,
                        "tbs": tbs,
                        "uule": uule,
                    },
                    google_search_params.GoogleSearchParams,
                ),
            ),
            cast_to=GoogleSearchResponse,
        )


class AsyncGoogleResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGoogleResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGoogleResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGoogleResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Scrapengines/scrapengine-sdk-python#with_streaming_response
        """
        return AsyncGoogleResourceWithStreamingResponse(self)

    async def search(
        self,
        *,
        q: str,
        async_: bool | Omit = omit,
        device: Literal["desktop", "mobile", "tablet"] | Omit = omit,
        filter: Literal[0, 1] | Omit = omit,
        gl: str | Omit = omit,
        google_domain: str | Omit = omit,
        hl: str | Omit = omit,
        location: str | Omit = omit,
        nfpr: Literal[0, 1] | Omit = omit,
        num: int | Omit = omit,
        raw_html: bool | Omit = omit,
        safe: Literal["off", "medium", "high"] | Omit = omit,
        start: int | Omit = omit,
        tbm: Literal["search", "images", "news", "videos"] | Omit = omit,
        tbs: str | Omit = omit,
        uule: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GoogleSearchResponse:
        """
        Execute a Google search and return parsed results including organic results,
        ads, and related searches.

        Args:
          q: Search query

          async_: Run asynchronously and return job ID

          device: Device type for user agent simulation

          filter: Filter duplicate results (0=show all, 1=filter)

          gl: Country code (ISO 3166-1 alpha-2)

          google_domain: Google domain to use

          hl: Language code (ISO 639-1)

          location: Location for geo-targeted results

          nfpr: Disable auto-correct (0=allow, 1=disable)

          num: Number of results to return (1-100)

          raw_html: Return raw HTML instead of parsed results

          safe: Safe search mode

          start: Pagination offset

          tbm: Search type

          tbs: Time-based filter (qdr:d=day, qdr:w=week, qdr:m=month, qdr:y=year)

          uule: Encoded location for geo-targeted results (UULE format)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/google/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "q": q,
                        "async_": async_,
                        "device": device,
                        "filter": filter,
                        "gl": gl,
                        "google_domain": google_domain,
                        "hl": hl,
                        "location": location,
                        "nfpr": nfpr,
                        "num": num,
                        "raw_html": raw_html,
                        "safe": safe,
                        "start": start,
                        "tbm": tbm,
                        "tbs": tbs,
                        "uule": uule,
                    },
                    google_search_params.GoogleSearchParams,
                ),
            ),
            cast_to=GoogleSearchResponse,
        )


class GoogleResourceWithRawResponse:
    def __init__(self, google: GoogleResource) -> None:
        self._google = google

        self.search = to_raw_response_wrapper(
            google.search,
        )


class AsyncGoogleResourceWithRawResponse:
    def __init__(self, google: AsyncGoogleResource) -> None:
        self._google = google

        self.search = async_to_raw_response_wrapper(
            google.search,
        )


class GoogleResourceWithStreamingResponse:
    def __init__(self, google: GoogleResource) -> None:
        self._google = google

        self.search = to_streamed_response_wrapper(
            google.search,
        )


class AsyncGoogleResourceWithStreamingResponse:
    def __init__(self, google: AsyncGoogleResource) -> None:
        self._google = google

        self.search = async_to_streamed_response_wrapper(
            google.search,
        )
