# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import signal_list_params
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
from ..types.signal_response import SignalResponse
from ..types.signal_list_response import SignalListResponse

__all__ = ["SignalResource", "AsyncSignalResource"]


class SignalResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SignalResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return SignalResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SignalResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return SignalResourceWithStreamingResponse(self)

    def retrieve(
        self,
        signal_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignalResponse:
        """
        Get a specific signal by ID (read-only).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signal_id:
            raise ValueError(f"Expected a non-empty value for `signal_id` but received {signal_id!r}")
        return self._get(
            f"/v1/signal/{signal_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignalResponse,
        )

    def list(
        self,
        *,
        days: int | Omit = omit,
        entity_id: Optional[str] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
        order: Optional[int] | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        search_term: Optional[str] | Omit = omit,
        signal_type: Optional[str] | Omit = omit,
        sort_by: Optional[str] | Omit = omit,
        strength: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignalListResponse:
        """
        List signals for the organization (read-only).

        Signals are immutable event records detected by AI agents, such as funding
        rounds, hiring events, and leadership changes. They cannot be created or
        modified through the API.

        Args:
          days: Number of days to look back

          entity_id: Filter by entity

          icp_id: Filter by ICP

          order: Sort order: -1 for descending, 1 for ascending

          search_term: Search in signal summary or type

          signal_type: Filter by type

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'signal_type', 'strength')

          strength: Filter by strength

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/signal",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "days": days,
                        "entity_id": entity_id,
                        "icp_id": icp_id,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "search_term": search_term,
                        "signal_type": signal_type,
                        "sort_by": sort_by,
                        "strength": strength,
                    },
                    signal_list_params.SignalListParams,
                ),
            ),
            cast_to=SignalListResponse,
        )


class AsyncSignalResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSignalResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSignalResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSignalResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return AsyncSignalResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        signal_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignalResponse:
        """
        Get a specific signal by ID (read-only).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signal_id:
            raise ValueError(f"Expected a non-empty value for `signal_id` but received {signal_id!r}")
        return await self._get(
            f"/v1/signal/{signal_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignalResponse,
        )

    async def list(
        self,
        *,
        days: int | Omit = omit,
        entity_id: Optional[str] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
        order: Optional[int] | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        search_term: Optional[str] | Omit = omit,
        signal_type: Optional[str] | Omit = omit,
        sort_by: Optional[str] | Omit = omit,
        strength: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignalListResponse:
        """
        List signals for the organization (read-only).

        Signals are immutable event records detected by AI agents, such as funding
        rounds, hiring events, and leadership changes. They cannot be created or
        modified through the API.

        Args:
          days: Number of days to look back

          entity_id: Filter by entity

          icp_id: Filter by ICP

          order: Sort order: -1 for descending, 1 for ascending

          search_term: Search in signal summary or type

          signal_type: Filter by type

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'signal_type', 'strength')

          strength: Filter by strength

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/signal",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "days": days,
                        "entity_id": entity_id,
                        "icp_id": icp_id,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "search_term": search_term,
                        "signal_type": signal_type,
                        "sort_by": sort_by,
                        "strength": strength,
                    },
                    signal_list_params.SignalListParams,
                ),
            ),
            cast_to=SignalListResponse,
        )


class SignalResourceWithRawResponse:
    def __init__(self, signal: SignalResource) -> None:
        self._signal = signal

        self.retrieve = to_raw_response_wrapper(
            signal.retrieve,
        )
        self.list = to_raw_response_wrapper(
            signal.list,
        )


class AsyncSignalResourceWithRawResponse:
    def __init__(self, signal: AsyncSignalResource) -> None:
        self._signal = signal

        self.retrieve = async_to_raw_response_wrapper(
            signal.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            signal.list,
        )


class SignalResourceWithStreamingResponse:
    def __init__(self, signal: SignalResource) -> None:
        self._signal = signal

        self.retrieve = to_streamed_response_wrapper(
            signal.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            signal.list,
        )


class AsyncSignalResourceWithStreamingResponse:
    def __init__(self, signal: AsyncSignalResource) -> None:
        self._signal = signal

        self.retrieve = async_to_streamed_response_wrapper(
            signal.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            signal.list,
        )
