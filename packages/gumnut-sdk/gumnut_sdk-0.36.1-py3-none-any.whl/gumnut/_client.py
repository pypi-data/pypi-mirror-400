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
    Headers,
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
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import faces, oauth, users, albums, assets, events, people, search, api_keys, libraries
    from .resources.faces import FacesResource, AsyncFacesResource
    from .resources.oauth import OAuthResource, AsyncOAuthResource
    from .resources.users import UsersResource, AsyncUsersResource
    from .resources.assets import AssetsResource, AsyncAssetsResource
    from .resources.events import EventsResource, AsyncEventsResource
    from .resources.people import PeopleResource, AsyncPeopleResource
    from .resources.search import SearchResource, AsyncSearchResource
    from .resources.api_keys import APIKeysResource, AsyncAPIKeysResource
    from .resources.libraries import LibrariesResource, AsyncLibrariesResource
    from .resources.albums.albums import AlbumsResource, AsyncAlbumsResource

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Gumnut", "AsyncGumnut", "Client", "AsyncClient"]


class Gumnut(SyncAPIClient):
    # client options
    api_key: str | None

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
        """Construct a new synchronous Gumnut client instance.

        This automatically infers the `api_key` argument from the `GUMNUT_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("GUMNUT_API_KEY")
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("GUMNUT_BASE_URL")
        if base_url is None:
            base_url = f"https://api.gumnut.ai"

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
    def api_keys(self) -> APIKeysResource:
        from .resources.api_keys import APIKeysResource

        return APIKeysResource(self)

    @cached_property
    def assets(self) -> AssetsResource:
        from .resources.assets import AssetsResource

        return AssetsResource(self)

    @cached_property
    def albums(self) -> AlbumsResource:
        from .resources.albums import AlbumsResource

        return AlbumsResource(self)

    @cached_property
    def events(self) -> EventsResource:
        from .resources.events import EventsResource

        return EventsResource(self)

    @cached_property
    def faces(self) -> FacesResource:
        from .resources.faces import FacesResource

        return FacesResource(self)

    @cached_property
    def libraries(self) -> LibrariesResource:
        from .resources.libraries import LibrariesResource

        return LibrariesResource(self)

    @cached_property
    def oauth(self) -> OAuthResource:
        from .resources.oauth import OAuthResource

        return OAuthResource(self)

    @cached_property
    def people(self) -> PeopleResource:
        from .resources.people import PeopleResource

        return PeopleResource(self)

    @cached_property
    def search(self) -> SearchResource:
        from .resources.search import SearchResource

        return SearchResource(self)

    @cached_property
    def users(self) -> UsersResource:
        from .resources.users import UsersResource

        return UsersResource(self)

    @cached_property
    def with_raw_response(self) -> GumnutWithRawResponse:
        return GumnutWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GumnutWithStreamedResponse:
        return GumnutWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        if api_key is None:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if headers.get("Authorization") or isinstance(custom_headers.get("Authorization"), Omit):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected the api_key to be set. Or for the `Authorization` headers to be explicitly omitted"'
        )

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


class AsyncGumnut(AsyncAPIClient):
    # client options
    api_key: str | None

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
        """Construct a new async AsyncGumnut client instance.

        This automatically infers the `api_key` argument from the `GUMNUT_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("GUMNUT_API_KEY")
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("GUMNUT_BASE_URL")
        if base_url is None:
            base_url = f"https://api.gumnut.ai"

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
    def api_keys(self) -> AsyncAPIKeysResource:
        from .resources.api_keys import AsyncAPIKeysResource

        return AsyncAPIKeysResource(self)

    @cached_property
    def assets(self) -> AsyncAssetsResource:
        from .resources.assets import AsyncAssetsResource

        return AsyncAssetsResource(self)

    @cached_property
    def albums(self) -> AsyncAlbumsResource:
        from .resources.albums import AsyncAlbumsResource

        return AsyncAlbumsResource(self)

    @cached_property
    def events(self) -> AsyncEventsResource:
        from .resources.events import AsyncEventsResource

        return AsyncEventsResource(self)

    @cached_property
    def faces(self) -> AsyncFacesResource:
        from .resources.faces import AsyncFacesResource

        return AsyncFacesResource(self)

    @cached_property
    def libraries(self) -> AsyncLibrariesResource:
        from .resources.libraries import AsyncLibrariesResource

        return AsyncLibrariesResource(self)

    @cached_property
    def oauth(self) -> AsyncOAuthResource:
        from .resources.oauth import AsyncOAuthResource

        return AsyncOAuthResource(self)

    @cached_property
    def people(self) -> AsyncPeopleResource:
        from .resources.people import AsyncPeopleResource

        return AsyncPeopleResource(self)

    @cached_property
    def search(self) -> AsyncSearchResource:
        from .resources.search import AsyncSearchResource

        return AsyncSearchResource(self)

    @cached_property
    def users(self) -> AsyncUsersResource:
        from .resources.users import AsyncUsersResource

        return AsyncUsersResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncGumnutWithRawResponse:
        return AsyncGumnutWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGumnutWithStreamedResponse:
        return AsyncGumnutWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        if api_key is None:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if headers.get("Authorization") or isinstance(custom_headers.get("Authorization"), Omit):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected the api_key to be set. Or for the `Authorization` headers to be explicitly omitted"'
        )

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


class GumnutWithRawResponse:
    _client: Gumnut

    def __init__(self, client: Gumnut) -> None:
        self._client = client

    @cached_property
    def api_keys(self) -> api_keys.APIKeysResourceWithRawResponse:
        from .resources.api_keys import APIKeysResourceWithRawResponse

        return APIKeysResourceWithRawResponse(self._client.api_keys)

    @cached_property
    def assets(self) -> assets.AssetsResourceWithRawResponse:
        from .resources.assets import AssetsResourceWithRawResponse

        return AssetsResourceWithRawResponse(self._client.assets)

    @cached_property
    def albums(self) -> albums.AlbumsResourceWithRawResponse:
        from .resources.albums import AlbumsResourceWithRawResponse

        return AlbumsResourceWithRawResponse(self._client.albums)

    @cached_property
    def events(self) -> events.EventsResourceWithRawResponse:
        from .resources.events import EventsResourceWithRawResponse

        return EventsResourceWithRawResponse(self._client.events)

    @cached_property
    def faces(self) -> faces.FacesResourceWithRawResponse:
        from .resources.faces import FacesResourceWithRawResponse

        return FacesResourceWithRawResponse(self._client.faces)

    @cached_property
    def libraries(self) -> libraries.LibrariesResourceWithRawResponse:
        from .resources.libraries import LibrariesResourceWithRawResponse

        return LibrariesResourceWithRawResponse(self._client.libraries)

    @cached_property
    def oauth(self) -> oauth.OAuthResourceWithRawResponse:
        from .resources.oauth import OAuthResourceWithRawResponse

        return OAuthResourceWithRawResponse(self._client.oauth)

    @cached_property
    def people(self) -> people.PeopleResourceWithRawResponse:
        from .resources.people import PeopleResourceWithRawResponse

        return PeopleResourceWithRawResponse(self._client.people)

    @cached_property
    def search(self) -> search.SearchResourceWithRawResponse:
        from .resources.search import SearchResourceWithRawResponse

        return SearchResourceWithRawResponse(self._client.search)

    @cached_property
    def users(self) -> users.UsersResourceWithRawResponse:
        from .resources.users import UsersResourceWithRawResponse

        return UsersResourceWithRawResponse(self._client.users)


class AsyncGumnutWithRawResponse:
    _client: AsyncGumnut

    def __init__(self, client: AsyncGumnut) -> None:
        self._client = client

    @cached_property
    def api_keys(self) -> api_keys.AsyncAPIKeysResourceWithRawResponse:
        from .resources.api_keys import AsyncAPIKeysResourceWithRawResponse

        return AsyncAPIKeysResourceWithRawResponse(self._client.api_keys)

    @cached_property
    def assets(self) -> assets.AsyncAssetsResourceWithRawResponse:
        from .resources.assets import AsyncAssetsResourceWithRawResponse

        return AsyncAssetsResourceWithRawResponse(self._client.assets)

    @cached_property
    def albums(self) -> albums.AsyncAlbumsResourceWithRawResponse:
        from .resources.albums import AsyncAlbumsResourceWithRawResponse

        return AsyncAlbumsResourceWithRawResponse(self._client.albums)

    @cached_property
    def events(self) -> events.AsyncEventsResourceWithRawResponse:
        from .resources.events import AsyncEventsResourceWithRawResponse

        return AsyncEventsResourceWithRawResponse(self._client.events)

    @cached_property
    def faces(self) -> faces.AsyncFacesResourceWithRawResponse:
        from .resources.faces import AsyncFacesResourceWithRawResponse

        return AsyncFacesResourceWithRawResponse(self._client.faces)

    @cached_property
    def libraries(self) -> libraries.AsyncLibrariesResourceWithRawResponse:
        from .resources.libraries import AsyncLibrariesResourceWithRawResponse

        return AsyncLibrariesResourceWithRawResponse(self._client.libraries)

    @cached_property
    def oauth(self) -> oauth.AsyncOAuthResourceWithRawResponse:
        from .resources.oauth import AsyncOAuthResourceWithRawResponse

        return AsyncOAuthResourceWithRawResponse(self._client.oauth)

    @cached_property
    def people(self) -> people.AsyncPeopleResourceWithRawResponse:
        from .resources.people import AsyncPeopleResourceWithRawResponse

        return AsyncPeopleResourceWithRawResponse(self._client.people)

    @cached_property
    def search(self) -> search.AsyncSearchResourceWithRawResponse:
        from .resources.search import AsyncSearchResourceWithRawResponse

        return AsyncSearchResourceWithRawResponse(self._client.search)

    @cached_property
    def users(self) -> users.AsyncUsersResourceWithRawResponse:
        from .resources.users import AsyncUsersResourceWithRawResponse

        return AsyncUsersResourceWithRawResponse(self._client.users)


class GumnutWithStreamedResponse:
    _client: Gumnut

    def __init__(self, client: Gumnut) -> None:
        self._client = client

    @cached_property
    def api_keys(self) -> api_keys.APIKeysResourceWithStreamingResponse:
        from .resources.api_keys import APIKeysResourceWithStreamingResponse

        return APIKeysResourceWithStreamingResponse(self._client.api_keys)

    @cached_property
    def assets(self) -> assets.AssetsResourceWithStreamingResponse:
        from .resources.assets import AssetsResourceWithStreamingResponse

        return AssetsResourceWithStreamingResponse(self._client.assets)

    @cached_property
    def albums(self) -> albums.AlbumsResourceWithStreamingResponse:
        from .resources.albums import AlbumsResourceWithStreamingResponse

        return AlbumsResourceWithStreamingResponse(self._client.albums)

    @cached_property
    def events(self) -> events.EventsResourceWithStreamingResponse:
        from .resources.events import EventsResourceWithStreamingResponse

        return EventsResourceWithStreamingResponse(self._client.events)

    @cached_property
    def faces(self) -> faces.FacesResourceWithStreamingResponse:
        from .resources.faces import FacesResourceWithStreamingResponse

        return FacesResourceWithStreamingResponse(self._client.faces)

    @cached_property
    def libraries(self) -> libraries.LibrariesResourceWithStreamingResponse:
        from .resources.libraries import LibrariesResourceWithStreamingResponse

        return LibrariesResourceWithStreamingResponse(self._client.libraries)

    @cached_property
    def oauth(self) -> oauth.OAuthResourceWithStreamingResponse:
        from .resources.oauth import OAuthResourceWithStreamingResponse

        return OAuthResourceWithStreamingResponse(self._client.oauth)

    @cached_property
    def people(self) -> people.PeopleResourceWithStreamingResponse:
        from .resources.people import PeopleResourceWithStreamingResponse

        return PeopleResourceWithStreamingResponse(self._client.people)

    @cached_property
    def search(self) -> search.SearchResourceWithStreamingResponse:
        from .resources.search import SearchResourceWithStreamingResponse

        return SearchResourceWithStreamingResponse(self._client.search)

    @cached_property
    def users(self) -> users.UsersResourceWithStreamingResponse:
        from .resources.users import UsersResourceWithStreamingResponse

        return UsersResourceWithStreamingResponse(self._client.users)


class AsyncGumnutWithStreamedResponse:
    _client: AsyncGumnut

    def __init__(self, client: AsyncGumnut) -> None:
        self._client = client

    @cached_property
    def api_keys(self) -> api_keys.AsyncAPIKeysResourceWithStreamingResponse:
        from .resources.api_keys import AsyncAPIKeysResourceWithStreamingResponse

        return AsyncAPIKeysResourceWithStreamingResponse(self._client.api_keys)

    @cached_property
    def assets(self) -> assets.AsyncAssetsResourceWithStreamingResponse:
        from .resources.assets import AsyncAssetsResourceWithStreamingResponse

        return AsyncAssetsResourceWithStreamingResponse(self._client.assets)

    @cached_property
    def albums(self) -> albums.AsyncAlbumsResourceWithStreamingResponse:
        from .resources.albums import AsyncAlbumsResourceWithStreamingResponse

        return AsyncAlbumsResourceWithStreamingResponse(self._client.albums)

    @cached_property
    def events(self) -> events.AsyncEventsResourceWithStreamingResponse:
        from .resources.events import AsyncEventsResourceWithStreamingResponse

        return AsyncEventsResourceWithStreamingResponse(self._client.events)

    @cached_property
    def faces(self) -> faces.AsyncFacesResourceWithStreamingResponse:
        from .resources.faces import AsyncFacesResourceWithStreamingResponse

        return AsyncFacesResourceWithStreamingResponse(self._client.faces)

    @cached_property
    def libraries(self) -> libraries.AsyncLibrariesResourceWithStreamingResponse:
        from .resources.libraries import AsyncLibrariesResourceWithStreamingResponse

        return AsyncLibrariesResourceWithStreamingResponse(self._client.libraries)

    @cached_property
    def oauth(self) -> oauth.AsyncOAuthResourceWithStreamingResponse:
        from .resources.oauth import AsyncOAuthResourceWithStreamingResponse

        return AsyncOAuthResourceWithStreamingResponse(self._client.oauth)

    @cached_property
    def people(self) -> people.AsyncPeopleResourceWithStreamingResponse:
        from .resources.people import AsyncPeopleResourceWithStreamingResponse

        return AsyncPeopleResourceWithStreamingResponse(self._client.people)

    @cached_property
    def search(self) -> search.AsyncSearchResourceWithStreamingResponse:
        from .resources.search import AsyncSearchResourceWithStreamingResponse

        return AsyncSearchResourceWithStreamingResponse(self._client.search)

    @cached_property
    def users(self) -> users.AsyncUsersResourceWithStreamingResponse:
        from .resources.users import AsyncUsersResourceWithStreamingResponse

        return AsyncUsersResourceWithStreamingResponse(self._client.users)


Client = Gumnut

AsyncClient = AsyncGumnut
