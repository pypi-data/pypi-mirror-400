# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional

import httpx

from ..types import task_list_params, task_create_params, task_update_params, task_execute_params
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
from ..types.task_list_response import TaskListResponse
from ..types.task_create_response import TaskCreateResponse
from ..types.task_execute_response import TaskExecuteResponse
from ..types.task_retrieve_response import TaskRetrieveResponse

__all__ = ["TaskResource", "AsyncTaskResource"]


class TaskResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return TaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return TaskResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        deployment_name: str,
        description: str,
        flow_name: str,
        name: str,
        icp_id: Optional[str] | Omit = omit,
        prompt: Optional[str] | Omit = omit,
        task_config: Optional[task_create_params.TaskConfig] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskCreateResponse:
        """
        Create a new task template.

        Tasks define reusable workflow configurations that reference Prefect
        deployments. Execute a task to create runs.

        Args:
          deployment_name: The Prefect deployment name for this flow

          description: Detailed description of what this task accomplishes

          flow_name: The Prefect flow name (e.g., 'search', 'ingest', 'signal')

          name: Human-readable name for the task

          icp_id: Optional ICP ID for signal monitoring tasks

          prompt: Template prompt for the task. Can include placeholders for runtime parameters.

          task_config: Flow-specific task configuration with versioning

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/task",
            body=maybe_transform(
                {
                    "deployment_name": deployment_name,
                    "description": description,
                    "flow_name": flow_name,
                    "name": name,
                    "icp_id": icp_id,
                    "prompt": prompt,
                    "task_config": task_config,
                },
                task_create_params.TaskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCreateResponse,
        )

    def retrieve(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskRetrieveResponse:
        """
        Get a specific task by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/v1/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskRetrieveResponse,
        )

    def update(
        self,
        task_id: str,
        *,
        deployment_name: Optional[str] | Omit = omit,
        description: Optional[str] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
        name: Optional[str] | Omit = omit,
        prompt: Optional[str] | Omit = omit,
        task_config: Optional[task_update_params.TaskConfig] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update an existing task.

        Only provided fields will be updated; omitted fields remain unchanged. The
        flow_name cannot be changed after creation.

        Args:
          deployment_name: Updated deployment name

          description: Updated task description

          icp_id: Updated ICP Connection

          name: Updated task name

          prompt: Updated task prompt template

          task_config: Updated flow-specific task configuration with versioning

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._put(
            f"/v1/task/{task_id}",
            body=maybe_transform(
                {
                    "deployment_name": deployment_name,
                    "description": description,
                    "icp_id": icp_id,
                    "name": name,
                    "prompt": prompt,
                    "task_config": task_config,
                },
                task_update_params.TaskUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def list(
        self,
        *,
        flow_name: Optional[str] | Omit = omit,
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
    ) -> TaskListResponse:
        """List all tasks for the organization.

        Tasks are reusable workflow templates.

        Filter by flow_name to see specific
        workflow types (search, ingest, signal).

        Args:
          flow_name: Filter by flow name

          order: Sort order: -1 for descending, 1 for ascending

          page: Page number (1-based)

          page_size: Items per page (max 100)

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'name')

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/task",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "flow_name": flow_name,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "sort_by": sort_by,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            cast_to=TaskListResponse,
        )

    def delete(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Delete a task.

        A task cannot be deleted if it has active (non-terminal) runs.

        This operation
        cannot be undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def execute(
        self,
        task_id: str,
        *,
        icp_id: Optional[str] | Omit = omit,
        parameters: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskExecuteResponse:
        """
        Execute a task by creating a new run.

        Creates a new workflow execution asynchronously and returns tracking information
        immediately. Monitor the run status using the returned run_id.

        Args:
          icp_id: Optional ICP ID to attach to this run for workflows that require ICP context

          parameters: Runtime parameters to pass to the task execution

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._post(
            f"/v1/task/{task_id}/execute",
            body=maybe_transform(
                {
                    "icp_id": icp_id,
                    "parameters": parameters,
                },
                task_execute_params.TaskExecuteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskExecuteResponse,
        )


class AsyncTaskResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return AsyncTaskResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        deployment_name: str,
        description: str,
        flow_name: str,
        name: str,
        icp_id: Optional[str] | Omit = omit,
        prompt: Optional[str] | Omit = omit,
        task_config: Optional[task_create_params.TaskConfig] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskCreateResponse:
        """
        Create a new task template.

        Tasks define reusable workflow configurations that reference Prefect
        deployments. Execute a task to create runs.

        Args:
          deployment_name: The Prefect deployment name for this flow

          description: Detailed description of what this task accomplishes

          flow_name: The Prefect flow name (e.g., 'search', 'ingest', 'signal')

          name: Human-readable name for the task

          icp_id: Optional ICP ID for signal monitoring tasks

          prompt: Template prompt for the task. Can include placeholders for runtime parameters.

          task_config: Flow-specific task configuration with versioning

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/task",
            body=await async_maybe_transform(
                {
                    "deployment_name": deployment_name,
                    "description": description,
                    "flow_name": flow_name,
                    "name": name,
                    "icp_id": icp_id,
                    "prompt": prompt,
                    "task_config": task_config,
                },
                task_create_params.TaskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCreateResponse,
        )

    async def retrieve(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskRetrieveResponse:
        """
        Get a specific task by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/v1/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskRetrieveResponse,
        )

    async def update(
        self,
        task_id: str,
        *,
        deployment_name: Optional[str] | Omit = omit,
        description: Optional[str] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
        name: Optional[str] | Omit = omit,
        prompt: Optional[str] | Omit = omit,
        task_config: Optional[task_update_params.TaskConfig] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update an existing task.

        Only provided fields will be updated; omitted fields remain unchanged. The
        flow_name cannot be changed after creation.

        Args:
          deployment_name: Updated deployment name

          description: Updated task description

          icp_id: Updated ICP Connection

          name: Updated task name

          prompt: Updated task prompt template

          task_config: Updated flow-specific task configuration with versioning

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._put(
            f"/v1/task/{task_id}",
            body=await async_maybe_transform(
                {
                    "deployment_name": deployment_name,
                    "description": description,
                    "icp_id": icp_id,
                    "name": name,
                    "prompt": prompt,
                    "task_config": task_config,
                },
                task_update_params.TaskUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def list(
        self,
        *,
        flow_name: Optional[str] | Omit = omit,
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
    ) -> TaskListResponse:
        """List all tasks for the organization.

        Tasks are reusable workflow templates.

        Filter by flow_name to see specific
        workflow types (search, ingest, signal).

        Args:
          flow_name: Filter by flow name

          order: Sort order: -1 for descending, 1 for ascending

          page: Page number (1-based)

          page_size: Items per page (max 100)

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'name')

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/task",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "flow_name": flow_name,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "sort_by": sort_by,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            cast_to=TaskListResponse,
        )

    async def delete(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Delete a task.

        A task cannot be deleted if it has active (non-terminal) runs.

        This operation
        cannot be undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def execute(
        self,
        task_id: str,
        *,
        icp_id: Optional[str] | Omit = omit,
        parameters: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskExecuteResponse:
        """
        Execute a task by creating a new run.

        Creates a new workflow execution asynchronously and returns tracking information
        immediately. Monitor the run status using the returned run_id.

        Args:
          icp_id: Optional ICP ID to attach to this run for workflows that require ICP context

          parameters: Runtime parameters to pass to the task execution

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._post(
            f"/v1/task/{task_id}/execute",
            body=await async_maybe_transform(
                {
                    "icp_id": icp_id,
                    "parameters": parameters,
                },
                task_execute_params.TaskExecuteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskExecuteResponse,
        )


class TaskResourceWithRawResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.create = to_raw_response_wrapper(
            task.create,
        )
        self.retrieve = to_raw_response_wrapper(
            task.retrieve,
        )
        self.update = to_raw_response_wrapper(
            task.update,
        )
        self.list = to_raw_response_wrapper(
            task.list,
        )
        self.delete = to_raw_response_wrapper(
            task.delete,
        )
        self.execute = to_raw_response_wrapper(
            task.execute,
        )


class AsyncTaskResourceWithRawResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.create = async_to_raw_response_wrapper(
            task.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            task.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            task.update,
        )
        self.list = async_to_raw_response_wrapper(
            task.list,
        )
        self.delete = async_to_raw_response_wrapper(
            task.delete,
        )
        self.execute = async_to_raw_response_wrapper(
            task.execute,
        )


class TaskResourceWithStreamingResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.create = to_streamed_response_wrapper(
            task.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            task.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            task.update,
        )
        self.list = to_streamed_response_wrapper(
            task.list,
        )
        self.delete = to_streamed_response_wrapper(
            task.delete,
        )
        self.execute = to_streamed_response_wrapper(
            task.execute,
        )


class AsyncTaskResourceWithStreamingResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.create = async_to_streamed_response_wrapper(
            task.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            task.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            task.update,
        )
        self.list = async_to_streamed_response_wrapper(
            task.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            task.delete,
        )
        self.execute = async_to_streamed_response_wrapper(
            task.execute,
        )
