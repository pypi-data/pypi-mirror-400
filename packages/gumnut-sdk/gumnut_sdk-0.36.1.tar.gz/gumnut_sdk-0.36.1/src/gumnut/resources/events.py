# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime

import httpx

from ..types import event_get_params
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
from ..types.events_response import EventsResponse

__all__ = ["EventsResource", "AsyncEventsResource"]


class EventsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return EventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return EventsResourceWithStreamingResponse(self)

    def get(
        self,
        *,
        entity_types: Optional[str] | Omit = omit,
        library_id: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        starting_after_id: Optional[str] | Omit = omit,
        updated_at_gte: Union[str, datetime, None] | Omit = omit,
        updated_at_lt: Union[str, datetime, None] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventsResponse:
        """
        Retrieves a list of entity change events for syncing.

        Events are returned in order of entity type priority (assets first, then exif,
        albums, etc.), then by `updated_at` timestamp (oldest first), then by entity ID
        for tie-breaking.

        **Pagination:** Use `updated_at_gte` with the timestamp of the last received
        event to fetch the next page. When multiple entities share the same timestamp,
        also provide `starting_after_id` with the last entity's ID to avoid duplicates.
        Use `updated_at_lt` to bound the sync window and prevent infinite loops when new
        events are created during sync.

        **Important:** When using `starting_after_id`, you must specify exactly one
        `entity_types` value. This ensures the cursor ID is unambiguous. To sync all
        entity types with cursor support, query each entity type separately.

        **Recommended sync pattern (per entity type):**

        1. Capture current time as `sync_started_at`
        2. For each entity type, fetch events with
           `entity_types={type}&updated_at_lt=sync_started_at`
        3. For subsequent pages, use
           `entity_types={type}&updated_at_gte={last.updated_at}&starting_after_id={last.id}&updated_at_lt=sync_started_at`
        4. Continue until an empty result set is returned
        5. Store `sync_started_at` as checkpoint for next sync

        **Entity ID field by type:**

        - Most entities: use the `id` field from the response
        - Exif: use the `asset_id` field (exif has no separate id)

        Args:
          entity_types: Comma-separated list of entity types to include (e.g., 'asset,album'). Valid
              types: asset, album, person, face, album_asset, exif. Default: all types.

          library_id: Library to list events from. If not provided, uses the user's default library.

          limit: Maximum number of events to return (1-500)

          starting_after_id: Entity ID to start after for tie-breaking when paginating. Used with
              updated_at_gte for composite keyset pagination. Requires exactly one
              entity_types value. For exif entities, use asset_id.

          updated_at_gte: Only return events with updated_at >= this timestamp (ISO 8601 format)

          updated_at_lt: Only return events with updated_at < this timestamp (ISO 8601 format).
              Recommended for bounding sync operations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "entity_types": entity_types,
                        "library_id": library_id,
                        "limit": limit,
                        "starting_after_id": starting_after_id,
                        "updated_at_gte": updated_at_gte,
                        "updated_at_lt": updated_at_lt,
                    },
                    event_get_params.EventGetParams,
                ),
            ),
            cast_to=EventsResponse,
        )


class AsyncEventsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return AsyncEventsResourceWithStreamingResponse(self)

    async def get(
        self,
        *,
        entity_types: Optional[str] | Omit = omit,
        library_id: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        starting_after_id: Optional[str] | Omit = omit,
        updated_at_gte: Union[str, datetime, None] | Omit = omit,
        updated_at_lt: Union[str, datetime, None] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventsResponse:
        """
        Retrieves a list of entity change events for syncing.

        Events are returned in order of entity type priority (assets first, then exif,
        albums, etc.), then by `updated_at` timestamp (oldest first), then by entity ID
        for tie-breaking.

        **Pagination:** Use `updated_at_gte` with the timestamp of the last received
        event to fetch the next page. When multiple entities share the same timestamp,
        also provide `starting_after_id` with the last entity's ID to avoid duplicates.
        Use `updated_at_lt` to bound the sync window and prevent infinite loops when new
        events are created during sync.

        **Important:** When using `starting_after_id`, you must specify exactly one
        `entity_types` value. This ensures the cursor ID is unambiguous. To sync all
        entity types with cursor support, query each entity type separately.

        **Recommended sync pattern (per entity type):**

        1. Capture current time as `sync_started_at`
        2. For each entity type, fetch events with
           `entity_types={type}&updated_at_lt=sync_started_at`
        3. For subsequent pages, use
           `entity_types={type}&updated_at_gte={last.updated_at}&starting_after_id={last.id}&updated_at_lt=sync_started_at`
        4. Continue until an empty result set is returned
        5. Store `sync_started_at` as checkpoint for next sync

        **Entity ID field by type:**

        - Most entities: use the `id` field from the response
        - Exif: use the `asset_id` field (exif has no separate id)

        Args:
          entity_types: Comma-separated list of entity types to include (e.g., 'asset,album'). Valid
              types: asset, album, person, face, album_asset, exif. Default: all types.

          library_id: Library to list events from. If not provided, uses the user's default library.

          limit: Maximum number of events to return (1-500)

          starting_after_id: Entity ID to start after for tie-breaking when paginating. Used with
              updated_at_gte for composite keyset pagination. Requires exactly one
              entity_types value. For exif entities, use asset_id.

          updated_at_gte: Only return events with updated_at >= this timestamp (ISO 8601 format)

          updated_at_lt: Only return events with updated_at < this timestamp (ISO 8601 format).
              Recommended for bounding sync operations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "entity_types": entity_types,
                        "library_id": library_id,
                        "limit": limit,
                        "starting_after_id": starting_after_id,
                        "updated_at_gte": updated_at_gte,
                        "updated_at_lt": updated_at_lt,
                    },
                    event_get_params.EventGetParams,
                ),
            ),
            cast_to=EventsResponse,
        )


class EventsResourceWithRawResponse:
    def __init__(self, events: EventsResource) -> None:
        self._events = events

        self.get = to_raw_response_wrapper(
            events.get,
        )


class AsyncEventsResourceWithRawResponse:
    def __init__(self, events: AsyncEventsResource) -> None:
        self._events = events

        self.get = async_to_raw_response_wrapper(
            events.get,
        )


class EventsResourceWithStreamingResponse:
    def __init__(self, events: EventsResource) -> None:
        self._events = events

        self.get = to_streamed_response_wrapper(
            events.get,
        )


class AsyncEventsResourceWithStreamingResponse:
    def __init__(self, events: AsyncEventsResource) -> None:
        self._events = events

        self.get = async_to_streamed_response_wrapper(
            events.get,
        )
