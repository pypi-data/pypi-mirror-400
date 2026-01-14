# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..types import run_list_params, run_create_params, run_get_queue_params
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
from ..types.run_list_response import RunListResponse
from ..types.run_create_response import RunCreateResponse
from ..types.run_retrieve_response import RunRetrieveResponse
from ..types.run_get_queue_response import RunGetQueueResponse

__all__ = ["RunResource", "AsyncRunResource"]


class RunResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RunResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return RunResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return RunResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        agent_id: str,
        parameters: Dict[str, object],
        icp_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunCreateResponse:
        """
        Execute an agent by creating a new run.

        Creates a new workflow execution asynchronously. Prefer using POST
        /v1/task/{task_id}/execute for task-based workflows.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/run",
            body=maybe_transform(
                {
                    "agent_id": agent_id,
                    "parameters": parameters,
                    "icp_id": icp_id,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCreateResponse,
        )

    def retrieve(
        self,
        run_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunRetrieveResponse:
        """
        Get a specific run by ID.

        Automatically refreshes status from Prefect if the run is still active.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return self._get(
            f"/v1/run/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunRetrieveResponse,
        )

    def list(
        self,
        *,
        agent_id: Optional[str] | Omit = omit,
        agent_type: Optional[str] | Omit = omit,
        created_after: Union[str, datetime, None] | Omit = omit,
        created_before: Union[str, datetime, None] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
        order: Optional[int] | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort_by: Optional[str] | Omit = omit,
        status: Optional[
            Literal["SCHEDULED", "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELED", "CRASHED", "PAUSED"]
        ]
        | Omit = omit,
        task_id: Optional[str] | Omit = omit,
        task_type: Optional[str] | Omit = omit,
        updated_after: Union[str, datetime, None] | Omit = omit,
        updated_before: Union[str, datetime, None] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunListResponse:
        """
        List all runs for the organization.

        Runs are workflow executions created from tasks. Filter by status to find active
        runs (RUNNING, PENDING) or completed ones (COMPLETED, FAILED).

        Args:
          agent_id: Filter by agent ID (legacy)

          agent_type: Filter by agent type

          created_after: Filter runs created after this date (ISO 8601 format: 2024-01-15T10:30:00Z)

          created_before: Filter runs created before this date (ISO 8601 format)

          icp_id: Filter by ICP ID

          order: Sort order: -1 for descending, 1 for ascending

          page: Page number (1-based)

          page_size: Items per page (max 100)

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'agent_type')

          status: Filter by run status (SCHEDULED, PENDING, RUNNING, COMPLETED, FAILED, CANCELED,
              CRASHED, PAUSED)

          task_id: Filter by task ID

          task_type: Filter by task type (signal, search, profile, ingest)

          updated_after: Filter runs updated after this date (ISO 8601 format)

          updated_before: Filter runs updated before this date (ISO 8601 format)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/run",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "agent_id": agent_id,
                        "agent_type": agent_type,
                        "created_after": created_after,
                        "created_before": created_before,
                        "icp_id": icp_id,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "status": status,
                        "task_id": task_id,
                        "task_type": task_type,
                        "updated_after": updated_after,
                        "updated_before": updated_before,
                    },
                    run_list_params.RunListParams,
                ),
            ),
            cast_to=RunListResponse,
        )

    def delete(
        self,
        run_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Delete a run.

        Permanently deletes the run record.

        This operation cannot be undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/run/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def cancel(
        self,
        run_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Cancel a running workflow.

        Cancels both the Prefect flow and updates the database record. Only effective
        for non-terminal runs.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/v1/run/{run_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_queue(
        self,
        run_id: str,
        *,
        include_history: bool | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        state: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunGetQueueResponse:
        """Get the queue status for a run.

        Shows entities being processed by the workflow.

        States: queued (waiting),
        processing (active), completed (done), discarded (skipped). Set
        include_history=true to see all processed entities.

        Args:
          include_history: Include processing history from all states

          limit: Maximum number of entities to return

          offset: Starting position in queue (0-indexed)

          state: Filter by state: queued, processing, completed, discarded

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return self._get(
            f"/v1/run/{run_id}/queue",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include_history": include_history,
                        "limit": limit,
                        "offset": offset,
                        "state": state,
                    },
                    run_get_queue_params.RunGetQueueParams,
                ),
            ),
            cast_to=RunGetQueueResponse,
        )


class AsyncRunResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRunResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncRunResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return AsyncRunResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        agent_id: str,
        parameters: Dict[str, object],
        icp_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunCreateResponse:
        """
        Execute an agent by creating a new run.

        Creates a new workflow execution asynchronously. Prefer using POST
        /v1/task/{task_id}/execute for task-based workflows.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/run",
            body=await async_maybe_transform(
                {
                    "agent_id": agent_id,
                    "parameters": parameters,
                    "icp_id": icp_id,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCreateResponse,
        )

    async def retrieve(
        self,
        run_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunRetrieveResponse:
        """
        Get a specific run by ID.

        Automatically refreshes status from Prefect if the run is still active.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return await self._get(
            f"/v1/run/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunRetrieveResponse,
        )

    async def list(
        self,
        *,
        agent_id: Optional[str] | Omit = omit,
        agent_type: Optional[str] | Omit = omit,
        created_after: Union[str, datetime, None] | Omit = omit,
        created_before: Union[str, datetime, None] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
        order: Optional[int] | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort_by: Optional[str] | Omit = omit,
        status: Optional[
            Literal["SCHEDULED", "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELED", "CRASHED", "PAUSED"]
        ]
        | Omit = omit,
        task_id: Optional[str] | Omit = omit,
        task_type: Optional[str] | Omit = omit,
        updated_after: Union[str, datetime, None] | Omit = omit,
        updated_before: Union[str, datetime, None] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunListResponse:
        """
        List all runs for the organization.

        Runs are workflow executions created from tasks. Filter by status to find active
        runs (RUNNING, PENDING) or completed ones (COMPLETED, FAILED).

        Args:
          agent_id: Filter by agent ID (legacy)

          agent_type: Filter by agent type

          created_after: Filter runs created after this date (ISO 8601 format: 2024-01-15T10:30:00Z)

          created_before: Filter runs created before this date (ISO 8601 format)

          icp_id: Filter by ICP ID

          order: Sort order: -1 for descending, 1 for ascending

          page: Page number (1-based)

          page_size: Items per page (max 100)

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'agent_type')

          status: Filter by run status (SCHEDULED, PENDING, RUNNING, COMPLETED, FAILED, CANCELED,
              CRASHED, PAUSED)

          task_id: Filter by task ID

          task_type: Filter by task type (signal, search, profile, ingest)

          updated_after: Filter runs updated after this date (ISO 8601 format)

          updated_before: Filter runs updated before this date (ISO 8601 format)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/run",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "agent_id": agent_id,
                        "agent_type": agent_type,
                        "created_after": created_after,
                        "created_before": created_before,
                        "icp_id": icp_id,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "sort_by": sort_by,
                        "status": status,
                        "task_id": task_id,
                        "task_type": task_type,
                        "updated_after": updated_after,
                        "updated_before": updated_before,
                    },
                    run_list_params.RunListParams,
                ),
            ),
            cast_to=RunListResponse,
        )

    async def delete(
        self,
        run_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Delete a run.

        Permanently deletes the run record.

        This operation cannot be undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/run/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def cancel(
        self,
        run_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Cancel a running workflow.

        Cancels both the Prefect flow and updates the database record. Only effective
        for non-terminal runs.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/v1/run/{run_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_queue(
        self,
        run_id: str,
        *,
        include_history: bool | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        state: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunGetQueueResponse:
        """Get the queue status for a run.

        Shows entities being processed by the workflow.

        States: queued (waiting),
        processing (active), completed (done), discarded (skipped). Set
        include_history=true to see all processed entities.

        Args:
          include_history: Include processing history from all states

          limit: Maximum number of entities to return

          offset: Starting position in queue (0-indexed)

          state: Filter by state: queued, processing, completed, discarded

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return await self._get(
            f"/v1/run/{run_id}/queue",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "include_history": include_history,
                        "limit": limit,
                        "offset": offset,
                        "state": state,
                    },
                    run_get_queue_params.RunGetQueueParams,
                ),
            ),
            cast_to=RunGetQueueResponse,
        )


class RunResourceWithRawResponse:
    def __init__(self, run: RunResource) -> None:
        self._run = run

        self.create = to_raw_response_wrapper(
            run.create,
        )
        self.retrieve = to_raw_response_wrapper(
            run.retrieve,
        )
        self.list = to_raw_response_wrapper(
            run.list,
        )
        self.delete = to_raw_response_wrapper(
            run.delete,
        )
        self.cancel = to_raw_response_wrapper(
            run.cancel,
        )
        self.get_queue = to_raw_response_wrapper(
            run.get_queue,
        )


class AsyncRunResourceWithRawResponse:
    def __init__(self, run: AsyncRunResource) -> None:
        self._run = run

        self.create = async_to_raw_response_wrapper(
            run.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            run.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            run.list,
        )
        self.delete = async_to_raw_response_wrapper(
            run.delete,
        )
        self.cancel = async_to_raw_response_wrapper(
            run.cancel,
        )
        self.get_queue = async_to_raw_response_wrapper(
            run.get_queue,
        )


class RunResourceWithStreamingResponse:
    def __init__(self, run: RunResource) -> None:
        self._run = run

        self.create = to_streamed_response_wrapper(
            run.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            run.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            run.list,
        )
        self.delete = to_streamed_response_wrapper(
            run.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            run.cancel,
        )
        self.get_queue = to_streamed_response_wrapper(
            run.get_queue,
        )


class AsyncRunResourceWithStreamingResponse:
    def __init__(self, run: AsyncRunResource) -> None:
        self._run = run

        self.create = async_to_streamed_response_wrapper(
            run.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            run.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            run.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            run.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            run.cancel,
        )
        self.get_queue = async_to_streamed_response_wrapper(
            run.get_queue,
        )
