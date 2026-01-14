# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal

import httpx

from ..types import icp_list_params, icp_create_params, icp_update_params
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
from ..types.icp_response import IcpResponse
from ..types.icp_list_response import IcpListResponse
from ..types.entity_target_config_param import EntityTargetConfigParam
from ..types.icp_get_active_runs_response import IcpGetActiveRunsResponse

__all__ = ["IcpResource", "AsyncIcpResource"]


class IcpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IcpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return IcpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IcpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return IcpResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        description: str,
        entity_targets: Iterable[EntityTargetConfigParam],
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpResponse:
        """
        Create a new Ideal Customer Profile (ICP).

        ICPs are the foundation of your research workflows. They define WHAT entities to
        target using business-level descriptions and filters, without specifying
        technical implementation details.

        Create an ICP first, then link Sheets to it for entity storage.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/icp",
            body=maybe_transform(
                {
                    "description": description,
                    "entity_targets": entity_targets,
                    "name": name,
                },
                icp_create_params.IcpCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IcpResponse,
        )

    def retrieve(
        self,
        icp_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpResponse:
        """
        Get a specific ICP by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not icp_id:
            raise ValueError(f"Expected a non-empty value for `icp_id` but received {icp_id!r}")
        return self._get(
            f"/v1/icp/{icp_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IcpResponse,
        )

    def update(
        self,
        icp_id: str,
        *,
        description: Optional[str] | Omit = omit,
        entity_targets: Optional[Iterable[EntityTargetConfigParam]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpResponse:
        """
        Update an existing ICP.

        Only provided fields will be updated; omitted fields remain unchanged.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not icp_id:
            raise ValueError(f"Expected a non-empty value for `icp_id` but received {icp_id!r}")
        return self._put(
            f"/v1/icp/{icp_id}",
            body=maybe_transform(
                {
                    "description": description,
                    "entity_targets": entity_targets,
                    "name": name,
                },
                icp_update_params.IcpUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IcpResponse,
        )

    def list(
        self,
        *,
        mode: Optional[Literal["discovery", "monitoring"]] | Omit = omit,
        order: Optional[int] | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort_by: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpListResponse:
        """List all ICPs for the organization.

        Results are scoped to your organization.

        Use the `mode` filter to separate
        discovery ICPs (for finding new entities) from monitoring ICPs (for tracking
        existing entities).

        Args:
          mode: Filter by ICP mode: 'discovery' or 'monitoring'

          order: Sort order: -1 for descending, 1 for ascending

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'name')

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/icp",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "mode": mode,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "sort_by": sort_by,
                    },
                    icp_list_params.IcpListParams,
                ),
            ),
            cast_to=IcpListResponse,
        )

    def delete(
        self,
        icp_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete an ICP and all related resources.

        **Cascade delete**: This permanently removes the ICP along with all associated
        sheets, entities, schedules, tasks, and signals. This operation cannot be
        undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not icp_id:
            raise ValueError(f"Expected a non-empty value for `icp_id` but received {icp_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/icp/{icp_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_active_runs(
        self,
        icp_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpGetActiveRunsResponse:
        """
        Get all active runs for an ICP.

        Returns runs in non-terminal states (RUNNING, SCHEDULED, PENDING). Useful for
        checking if workflows are currently processing this ICP before making changes.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not icp_id:
            raise ValueError(f"Expected a non-empty value for `icp_id` but received {icp_id!r}")
        return self._get(
            f"/v1/icp/{icp_id}/active_runs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IcpGetActiveRunsResponse,
        )


class AsyncIcpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIcpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncIcpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIcpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return AsyncIcpResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        description: str,
        entity_targets: Iterable[EntityTargetConfigParam],
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpResponse:
        """
        Create a new Ideal Customer Profile (ICP).

        ICPs are the foundation of your research workflows. They define WHAT entities to
        target using business-level descriptions and filters, without specifying
        technical implementation details.

        Create an ICP first, then link Sheets to it for entity storage.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/icp",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "entity_targets": entity_targets,
                    "name": name,
                },
                icp_create_params.IcpCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IcpResponse,
        )

    async def retrieve(
        self,
        icp_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpResponse:
        """
        Get a specific ICP by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not icp_id:
            raise ValueError(f"Expected a non-empty value for `icp_id` but received {icp_id!r}")
        return await self._get(
            f"/v1/icp/{icp_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IcpResponse,
        )

    async def update(
        self,
        icp_id: str,
        *,
        description: Optional[str] | Omit = omit,
        entity_targets: Optional[Iterable[EntityTargetConfigParam]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpResponse:
        """
        Update an existing ICP.

        Only provided fields will be updated; omitted fields remain unchanged.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not icp_id:
            raise ValueError(f"Expected a non-empty value for `icp_id` but received {icp_id!r}")
        return await self._put(
            f"/v1/icp/{icp_id}",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "entity_targets": entity_targets,
                    "name": name,
                },
                icp_update_params.IcpUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IcpResponse,
        )

    async def list(
        self,
        *,
        mode: Optional[Literal["discovery", "monitoring"]] | Omit = omit,
        order: Optional[int] | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort_by: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpListResponse:
        """List all ICPs for the organization.

        Results are scoped to your organization.

        Use the `mode` filter to separate
        discovery ICPs (for finding new entities) from monitoring ICPs (for tracking
        existing entities).

        Args:
          mode: Filter by ICP mode: 'discovery' or 'monitoring'

          order: Sort order: -1 for descending, 1 for ascending

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'name')

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/icp",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "mode": mode,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "sort_by": sort_by,
                    },
                    icp_list_params.IcpListParams,
                ),
            ),
            cast_to=IcpListResponse,
        )

    async def delete(
        self,
        icp_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete an ICP and all related resources.

        **Cascade delete**: This permanently removes the ICP along with all associated
        sheets, entities, schedules, tasks, and signals. This operation cannot be
        undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not icp_id:
            raise ValueError(f"Expected a non-empty value for `icp_id` but received {icp_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/icp/{icp_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_active_runs(
        self,
        icp_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IcpGetActiveRunsResponse:
        """
        Get all active runs for an ICP.

        Returns runs in non-terminal states (RUNNING, SCHEDULED, PENDING). Useful for
        checking if workflows are currently processing this ICP before making changes.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not icp_id:
            raise ValueError(f"Expected a non-empty value for `icp_id` but received {icp_id!r}")
        return await self._get(
            f"/v1/icp/{icp_id}/active_runs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IcpGetActiveRunsResponse,
        )


class IcpResourceWithRawResponse:
    def __init__(self, icp: IcpResource) -> None:
        self._icp = icp

        self.create = to_raw_response_wrapper(
            icp.create,
        )
        self.retrieve = to_raw_response_wrapper(
            icp.retrieve,
        )
        self.update = to_raw_response_wrapper(
            icp.update,
        )
        self.list = to_raw_response_wrapper(
            icp.list,
        )
        self.delete = to_raw_response_wrapper(
            icp.delete,
        )
        self.get_active_runs = to_raw_response_wrapper(
            icp.get_active_runs,
        )


class AsyncIcpResourceWithRawResponse:
    def __init__(self, icp: AsyncIcpResource) -> None:
        self._icp = icp

        self.create = async_to_raw_response_wrapper(
            icp.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            icp.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            icp.update,
        )
        self.list = async_to_raw_response_wrapper(
            icp.list,
        )
        self.delete = async_to_raw_response_wrapper(
            icp.delete,
        )
        self.get_active_runs = async_to_raw_response_wrapper(
            icp.get_active_runs,
        )


class IcpResourceWithStreamingResponse:
    def __init__(self, icp: IcpResource) -> None:
        self._icp = icp

        self.create = to_streamed_response_wrapper(
            icp.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            icp.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            icp.update,
        )
        self.list = to_streamed_response_wrapper(
            icp.list,
        )
        self.delete = to_streamed_response_wrapper(
            icp.delete,
        )
        self.get_active_runs = to_streamed_response_wrapper(
            icp.get_active_runs,
        )


class AsyncIcpResourceWithStreamingResponse:
    def __init__(self, icp: AsyncIcpResource) -> None:
        self._icp = icp

        self.create = async_to_streamed_response_wrapper(
            icp.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            icp.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            icp.update,
        )
        self.list = async_to_streamed_response_wrapper(
            icp.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            icp.delete,
        )
        self.get_active_runs = async_to_streamed_response_wrapper(
            icp.get_active_runs,
        )
