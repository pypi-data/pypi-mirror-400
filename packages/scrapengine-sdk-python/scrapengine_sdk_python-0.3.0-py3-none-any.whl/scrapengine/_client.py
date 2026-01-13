# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, ScrapengineError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import bing, amazon, google, lazada, scrape
    from .resources.bing import BingResource, AsyncBingResource
    from .resources.amazon import AmazonResource, AsyncAmazonResource
    from .resources.google import GoogleResource, AsyncGoogleResource
    from .resources.lazada import LazadaResource, AsyncLazadaResource
    from .resources.scrape import ScrapeResource, AsyncScrapeResource

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Scrapengine",
    "AsyncScrapengine",
    "Client",
    "AsyncClient",
]


class Scrapengine(SyncAPIClient):
    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Scrapengine client instance.

        This automatically infers the `api_key` argument from the `SCRAPENGINE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("SCRAPENGINE_API_KEY")
        if api_key is None:
            raise ScrapengineError(
                "The api_key client option must be set either by passing api_key to the client or by setting the SCRAPENGINE_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("SCRAPENGINE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.scrapengine.io/api/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def scrape(self) -> ScrapeResource:
        from .resources.scrape import ScrapeResource

        return ScrapeResource(self)

    @cached_property
    def google(self) -> GoogleResource:
        from .resources.google import GoogleResource

        return GoogleResource(self)

    @cached_property
    def bing(self) -> BingResource:
        from .resources.bing import BingResource

        return BingResource(self)

    @cached_property
    def amazon(self) -> AmazonResource:
        from .resources.amazon import AmazonResource

        return AmazonResource(self)

    @cached_property
    def lazada(self) -> LazadaResource:
        from .resources.lazada import LazadaResource

        return LazadaResource(self)

    @cached_property
    def with_raw_response(self) -> ScrapengineWithRawResponse:
        return ScrapengineWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ScrapengineWithStreamedResponse:
        return ScrapengineWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncScrapengine(AsyncAPIClient):
    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncScrapengine client instance.

        This automatically infers the `api_key` argument from the `SCRAPENGINE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("SCRAPENGINE_API_KEY")
        if api_key is None:
            raise ScrapengineError(
                "The api_key client option must be set either by passing api_key to the client or by setting the SCRAPENGINE_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("SCRAPENGINE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.scrapengine.io/api/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def scrape(self) -> AsyncScrapeResource:
        from .resources.scrape import AsyncScrapeResource

        return AsyncScrapeResource(self)

    @cached_property
    def google(self) -> AsyncGoogleResource:
        from .resources.google import AsyncGoogleResource

        return AsyncGoogleResource(self)

    @cached_property
    def bing(self) -> AsyncBingResource:
        from .resources.bing import AsyncBingResource

        return AsyncBingResource(self)

    @cached_property
    def amazon(self) -> AsyncAmazonResource:
        from .resources.amazon import AsyncAmazonResource

        return AsyncAmazonResource(self)

    @cached_property
    def lazada(self) -> AsyncLazadaResource:
        from .resources.lazada import AsyncLazadaResource

        return AsyncLazadaResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncScrapengineWithRawResponse:
        return AsyncScrapengineWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncScrapengineWithStreamedResponse:
        return AsyncScrapengineWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class ScrapengineWithRawResponse:
    _client: Scrapengine

    def __init__(self, client: Scrapengine) -> None:
        self._client = client

    @cached_property
    def scrape(self) -> scrape.ScrapeResourceWithRawResponse:
        from .resources.scrape import ScrapeResourceWithRawResponse

        return ScrapeResourceWithRawResponse(self._client.scrape)

    @cached_property
    def google(self) -> google.GoogleResourceWithRawResponse:
        from .resources.google import GoogleResourceWithRawResponse

        return GoogleResourceWithRawResponse(self._client.google)

    @cached_property
    def bing(self) -> bing.BingResourceWithRawResponse:
        from .resources.bing import BingResourceWithRawResponse

        return BingResourceWithRawResponse(self._client.bing)

    @cached_property
    def amazon(self) -> amazon.AmazonResourceWithRawResponse:
        from .resources.amazon import AmazonResourceWithRawResponse

        return AmazonResourceWithRawResponse(self._client.amazon)

    @cached_property
    def lazada(self) -> lazada.LazadaResourceWithRawResponse:
        from .resources.lazada import LazadaResourceWithRawResponse

        return LazadaResourceWithRawResponse(self._client.lazada)


class AsyncScrapengineWithRawResponse:
    _client: AsyncScrapengine

    def __init__(self, client: AsyncScrapengine) -> None:
        self._client = client

    @cached_property
    def scrape(self) -> scrape.AsyncScrapeResourceWithRawResponse:
        from .resources.scrape import AsyncScrapeResourceWithRawResponse

        return AsyncScrapeResourceWithRawResponse(self._client.scrape)

    @cached_property
    def google(self) -> google.AsyncGoogleResourceWithRawResponse:
        from .resources.google import AsyncGoogleResourceWithRawResponse

        return AsyncGoogleResourceWithRawResponse(self._client.google)

    @cached_property
    def bing(self) -> bing.AsyncBingResourceWithRawResponse:
        from .resources.bing import AsyncBingResourceWithRawResponse

        return AsyncBingResourceWithRawResponse(self._client.bing)

    @cached_property
    def amazon(self) -> amazon.AsyncAmazonResourceWithRawResponse:
        from .resources.amazon import AsyncAmazonResourceWithRawResponse

        return AsyncAmazonResourceWithRawResponse(self._client.amazon)

    @cached_property
    def lazada(self) -> lazada.AsyncLazadaResourceWithRawResponse:
        from .resources.lazada import AsyncLazadaResourceWithRawResponse

        return AsyncLazadaResourceWithRawResponse(self._client.lazada)


class ScrapengineWithStreamedResponse:
    _client: Scrapengine

    def __init__(self, client: Scrapengine) -> None:
        self._client = client

    @cached_property
    def scrape(self) -> scrape.ScrapeResourceWithStreamingResponse:
        from .resources.scrape import ScrapeResourceWithStreamingResponse

        return ScrapeResourceWithStreamingResponse(self._client.scrape)

    @cached_property
    def google(self) -> google.GoogleResourceWithStreamingResponse:
        from .resources.google import GoogleResourceWithStreamingResponse

        return GoogleResourceWithStreamingResponse(self._client.google)

    @cached_property
    def bing(self) -> bing.BingResourceWithStreamingResponse:
        from .resources.bing import BingResourceWithStreamingResponse

        return BingResourceWithStreamingResponse(self._client.bing)

    @cached_property
    def amazon(self) -> amazon.AmazonResourceWithStreamingResponse:
        from .resources.amazon import AmazonResourceWithStreamingResponse

        return AmazonResourceWithStreamingResponse(self._client.amazon)

    @cached_property
    def lazada(self) -> lazada.LazadaResourceWithStreamingResponse:
        from .resources.lazada import LazadaResourceWithStreamingResponse

        return LazadaResourceWithStreamingResponse(self._client.lazada)


class AsyncScrapengineWithStreamedResponse:
    _client: AsyncScrapengine

    def __init__(self, client: AsyncScrapengine) -> None:
        self._client = client

    @cached_property
    def scrape(self) -> scrape.AsyncScrapeResourceWithStreamingResponse:
        from .resources.scrape import AsyncScrapeResourceWithStreamingResponse

        return AsyncScrapeResourceWithStreamingResponse(self._client.scrape)

    @cached_property
    def google(self) -> google.AsyncGoogleResourceWithStreamingResponse:
        from .resources.google import AsyncGoogleResourceWithStreamingResponse

        return AsyncGoogleResourceWithStreamingResponse(self._client.google)

    @cached_property
    def bing(self) -> bing.AsyncBingResourceWithStreamingResponse:
        from .resources.bing import AsyncBingResourceWithStreamingResponse

        return AsyncBingResourceWithStreamingResponse(self._client.bing)

    @cached_property
    def amazon(self) -> amazon.AsyncAmazonResourceWithStreamingResponse:
        from .resources.amazon import AsyncAmazonResourceWithStreamingResponse

        return AsyncAmazonResourceWithStreamingResponse(self._client.amazon)

    @cached_property
    def lazada(self) -> lazada.AsyncLazadaResourceWithStreamingResponse:
        from .resources.lazada import AsyncLazadaResourceWithStreamingResponse

        return AsyncLazadaResourceWithStreamingResponse(self._client.lazada)


Client = Scrapengine

AsyncClient = AsyncScrapengine
