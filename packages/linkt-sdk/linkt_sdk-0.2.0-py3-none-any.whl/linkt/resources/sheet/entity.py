# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.sheet import entity_update_status_params, entity_update_comments_params
from ..._base_client import make_request_options
from ...types.sheet.entity_retrieve_response import EntityRetrieveResponse

__all__ = ["EntityResource", "AsyncEntityResource"]


class EntityResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EntityResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return EntityResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EntityResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return EntityResourceWithStreamingResponse(self)

    def retrieve(
        self,
        entity_id: str,
        *,
        sheet_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EntityRetrieveResponse:
        """
        Get a specific entity from a sheet.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        if not entity_id:
            raise ValueError(f"Expected a non-empty value for `entity_id` but received {entity_id!r}")
        return self._get(
            f"/v1/sheet/{sheet_id}/entity/{entity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityRetrieveResponse,
        )

    def update_comments(
        self,
        entity_id: str,
        *,
        sheet_id: str,
        comments: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update the comments on an entity.

        Pass null to clear existing comments.

        Args:
          comments: Comments for the entity

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        if not entity_id:
            raise ValueError(f"Expected a non-empty value for `entity_id` but received {entity_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._put(
            f"/v1/sheet/{sheet_id}/entity/{entity_id}/comments",
            body=maybe_transform({"comments": comments}, entity_update_comments_params.EntityUpdateCommentsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def update_status(
        self,
        entity_id: str,
        *,
        sheet_id: str,
        status: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update the status of an entity.

        Use status to mark entities as qualified (true) or disqualified (false) from
        your target list.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        if not entity_id:
            raise ValueError(f"Expected a non-empty value for `entity_id` but received {entity_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._put(
            f"/v1/sheet/{sheet_id}/entity/{entity_id}/status",
            body=maybe_transform({"status": status}, entity_update_status_params.EntityUpdateStatusParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncEntityResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEntityResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncEntityResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEntityResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return AsyncEntityResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        entity_id: str,
        *,
        sheet_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EntityRetrieveResponse:
        """
        Get a specific entity from a sheet.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        if not entity_id:
            raise ValueError(f"Expected a non-empty value for `entity_id` but received {entity_id!r}")
        return await self._get(
            f"/v1/sheet/{sheet_id}/entity/{entity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityRetrieveResponse,
        )

    async def update_comments(
        self,
        entity_id: str,
        *,
        sheet_id: str,
        comments: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update the comments on an entity.

        Pass null to clear existing comments.

        Args:
          comments: Comments for the entity

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        if not entity_id:
            raise ValueError(f"Expected a non-empty value for `entity_id` but received {entity_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._put(
            f"/v1/sheet/{sheet_id}/entity/{entity_id}/comments",
            body=await async_maybe_transform(
                {"comments": comments}, entity_update_comments_params.EntityUpdateCommentsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def update_status(
        self,
        entity_id: str,
        *,
        sheet_id: str,
        status: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update the status of an entity.

        Use status to mark entities as qualified (true) or disqualified (false) from
        your target list.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        if not entity_id:
            raise ValueError(f"Expected a non-empty value for `entity_id` but received {entity_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._put(
            f"/v1/sheet/{sheet_id}/entity/{entity_id}/status",
            body=await async_maybe_transform({"status": status}, entity_update_status_params.EntityUpdateStatusParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class EntityResourceWithRawResponse:
    def __init__(self, entity: EntityResource) -> None:
        self._entity = entity

        self.retrieve = to_raw_response_wrapper(
            entity.retrieve,
        )
        self.update_comments = to_raw_response_wrapper(
            entity.update_comments,
        )
        self.update_status = to_raw_response_wrapper(
            entity.update_status,
        )


class AsyncEntityResourceWithRawResponse:
    def __init__(self, entity: AsyncEntityResource) -> None:
        self._entity = entity

        self.retrieve = async_to_raw_response_wrapper(
            entity.retrieve,
        )
        self.update_comments = async_to_raw_response_wrapper(
            entity.update_comments,
        )
        self.update_status = async_to_raw_response_wrapper(
            entity.update_status,
        )


class EntityResourceWithStreamingResponse:
    def __init__(self, entity: EntityResource) -> None:
        self._entity = entity

        self.retrieve = to_streamed_response_wrapper(
            entity.retrieve,
        )
        self.update_comments = to_streamed_response_wrapper(
            entity.update_comments,
        )
        self.update_status = to_streamed_response_wrapper(
            entity.update_status,
        )


class AsyncEntityResourceWithStreamingResponse:
    def __init__(self, entity: AsyncEntityResource) -> None:
        self._entity = entity

        self.retrieve = async_to_streamed_response_wrapper(
            entity.retrieve,
        )
        self.update_comments = async_to_streamed_response_wrapper(
            entity.update_comments,
        )
        self.update_status = async_to_streamed_response_wrapper(
            entity.update_status,
        )
