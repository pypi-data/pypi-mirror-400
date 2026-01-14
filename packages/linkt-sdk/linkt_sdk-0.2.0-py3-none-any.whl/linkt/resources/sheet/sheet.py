# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime

import httpx

from .entity import (
    EntityResource,
    AsyncEntityResource,
    EntityResourceWithRawResponse,
    AsyncEntityResourceWithRawResponse,
    EntityResourceWithStreamingResponse,
    AsyncEntityResourceWithStreamingResponse,
)
from .schema import (
    SchemaResource,
    AsyncSchemaResource,
    SchemaResourceWithRawResponse,
    AsyncSchemaResourceWithRawResponse,
    SchemaResourceWithStreamingResponse,
    AsyncSchemaResourceWithStreamingResponse,
)
from ...types import (
    EntityType,
    sheet_list_params,
    sheet_create_params,
    sheet_update_params,
    sheet_export_csv_params,
    sheet_get_entities_params,
)
from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.entity_type import EntityType
from ...types.sheet.sheet import Sheet
from ...types.sheet_list_response import SheetListResponse
from ...types.sheet_get_entities_response import SheetGetEntitiesResponse

__all__ = ["SheetResource", "AsyncSheetResource"]


class SheetResource(SyncAPIResource):
    @cached_property
    def entity(self) -> EntityResource:
        return EntityResource(self._client)

    @cached_property
    def schema(self) -> SchemaResource:
        return SchemaResource(self._client)

    @cached_property
    def with_raw_response(self) -> SheetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return SheetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SheetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return SheetResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        description: str,
        entity_type: EntityType,
        icp_id: str,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Sheet:
        """
        Create a new sheet linked to an ICP.

        Sheets hold entities of a single type (company or person) and must reference an
        ICP. The entity type must match one of the ICP's configured entity targets.

        Args:
          entity_type: Type of entities to store

          icp_id: ICP this sheet belongs to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/sheet",
            body=maybe_transform(
                {
                    "description": description,
                    "entity_type": entity_type,
                    "icp_id": icp_id,
                    "name": name,
                },
                sheet_create_params.SheetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Sheet,
        )

    def retrieve(
        self,
        sheet_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Sheet:
        """
        Get a specific sheet by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return self._get(
            f"/v1/sheet/{sheet_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Sheet,
        )

    def update(
        self,
        sheet_id: str,
        *,
        description: Optional[str] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
        name: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update an existing sheet.

        Only provided fields will be updated; omitted fields remain unchanged. The ICP
        reference and entity_type cannot be changed after creation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._put(
            f"/v1/sheet/{sheet_id}",
            body=maybe_transform(
                {
                    "description": description,
                    "icp_id": icp_id,
                    "name": name,
                },
                sheet_update_params.SheetUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def list(
        self,
        *,
        entity_type: Optional[str] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
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
    ) -> SheetListResponse:
        """
        List all sheets for the organization.

        Filter by ICP to see sheets for a specific targeting profile, or by entity type
        to see all company or person sheets.

        Args:
          order: Sort order: -1 for descending, 1 for ascending

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'name')

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/sheet",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "entity_type": entity_type,
                        "icp_id": icp_id,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "sort_by": sort_by,
                    },
                    sheet_list_params.SheetListParams,
                ),
            ),
            cast_to=SheetListResponse,
        )

    def delete(
        self,
        sheet_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a sheet and all its entities.

        **Cascade delete**: This permanently removes the sheet and all entities within
        it. This operation cannot be undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/sheet/{sheet_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def export_csv(
        self,
        sheet_id: str,
        *,
        entity_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Export sheet entities as a CSV file.

        Exports entities with proper field formatting based on the sheet's schema. Pass
        specific entity_ids to export a subset, or omit to export all entities.

        Args:
          entity_ids: Optional list of entity IDs to export. If not provided, exports all entities.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return self._get(
            f"/v1/sheet/{sheet_id}/export-csv",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"entity_ids": entity_ids}, sheet_export_csv_params.SheetExportCsvParams),
            ),
            cast_to=object,
        )

    def get_entities(
        self,
        sheet_id: str,
        *,
        created_after: Union[str, datetime, None] | Omit = omit,
        created_before: Union[str, datetime, None] | Omit = omit,
        has_comments: Optional[bool] | Omit = omit,
        order: Optional[int] | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        search: Optional[str] | Omit = omit,
        sort_by: Optional[str] | Omit = omit,
        status: Optional[bool] | Omit = omit,
        updated_after: Union[str, datetime, None] | Omit = omit,
        updated_before: Union[str, datetime, None] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SheetGetEntitiesResponse:
        """
        List all entities in a sheet.

        Supports text search across name/company fields and comprehensive filtering by
        status, comments, and date ranges.

        Args:
          created_after: Filter entities created after this date (ISO 8601 format: 2024-01-15T10:30:00Z)

          created_before: Filter entities created before this date (ISO 8601 format)

          has_comments: Filter entities with or without user comments

          order: Sort order: -1 for descending, 1 for ascending

          page: Page number (1-based)

          page_size: Items per page (max 100, default 50)

          search: Search entities by name or company

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'status')

          status: Filter by entity status (true=active, false=inactive)

          updated_after: Filter entities updated after this date (ISO 8601 format)

          updated_before: Filter entities updated before this date (ISO 8601 format)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return self._get(
            f"/v1/sheet/{sheet_id}/entities",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "created_after": created_after,
                        "created_before": created_before,
                        "has_comments": has_comments,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "search": search,
                        "sort_by": sort_by,
                        "status": status,
                        "updated_after": updated_after,
                        "updated_before": updated_before,
                    },
                    sheet_get_entities_params.SheetGetEntitiesParams,
                ),
            ),
            cast_to=SheetGetEntitiesResponse,
        )


class AsyncSheetResource(AsyncAPIResource):
    @cached_property
    def entity(self) -> AsyncEntityResource:
        return AsyncEntityResource(self._client)

    @cached_property
    def schema(self) -> AsyncSchemaResource:
        return AsyncSchemaResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSheetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSheetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSheetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return AsyncSheetResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        description: str,
        entity_type: EntityType,
        icp_id: str,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Sheet:
        """
        Create a new sheet linked to an ICP.

        Sheets hold entities of a single type (company or person) and must reference an
        ICP. The entity type must match one of the ICP's configured entity targets.

        Args:
          entity_type: Type of entities to store

          icp_id: ICP this sheet belongs to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/sheet",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "entity_type": entity_type,
                    "icp_id": icp_id,
                    "name": name,
                },
                sheet_create_params.SheetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Sheet,
        )

    async def retrieve(
        self,
        sheet_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Sheet:
        """
        Get a specific sheet by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return await self._get(
            f"/v1/sheet/{sheet_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Sheet,
        )

    async def update(
        self,
        sheet_id: str,
        *,
        description: Optional[str] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
        name: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update an existing sheet.

        Only provided fields will be updated; omitted fields remain unchanged. The ICP
        reference and entity_type cannot be changed after creation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._put(
            f"/v1/sheet/{sheet_id}",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "icp_id": icp_id,
                    "name": name,
                },
                sheet_update_params.SheetUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def list(
        self,
        *,
        entity_type: Optional[str] | Omit = omit,
        icp_id: Optional[str] | Omit = omit,
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
    ) -> SheetListResponse:
        """
        List all sheets for the organization.

        Filter by ICP to see sheets for a specific targeting profile, or by entity type
        to see all company or person sheets.

        Args:
          order: Sort order: -1 for descending, 1 for ascending

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'name')

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/sheet",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "entity_type": entity_type,
                        "icp_id": icp_id,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "sort_by": sort_by,
                    },
                    sheet_list_params.SheetListParams,
                ),
            ),
            cast_to=SheetListResponse,
        )

    async def delete(
        self,
        sheet_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a sheet and all its entities.

        **Cascade delete**: This permanently removes the sheet and all entities within
        it. This operation cannot be undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/sheet/{sheet_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def export_csv(
        self,
        sheet_id: str,
        *,
        entity_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Export sheet entities as a CSV file.

        Exports entities with proper field formatting based on the sheet's schema. Pass
        specific entity_ids to export a subset, or omit to export all entities.

        Args:
          entity_ids: Optional list of entity IDs to export. If not provided, exports all entities.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return await self._get(
            f"/v1/sheet/{sheet_id}/export-csv",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"entity_ids": entity_ids}, sheet_export_csv_params.SheetExportCsvParams
                ),
            ),
            cast_to=object,
        )

    async def get_entities(
        self,
        sheet_id: str,
        *,
        created_after: Union[str, datetime, None] | Omit = omit,
        created_before: Union[str, datetime, None] | Omit = omit,
        has_comments: Optional[bool] | Omit = omit,
        order: Optional[int] | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        search: Optional[str] | Omit = omit,
        sort_by: Optional[str] | Omit = omit,
        status: Optional[bool] | Omit = omit,
        updated_after: Union[str, datetime, None] | Omit = omit,
        updated_before: Union[str, datetime, None] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SheetGetEntitiesResponse:
        """
        List all entities in a sheet.

        Supports text search across name/company fields and comprehensive filtering by
        status, comments, and date ranges.

        Args:
          created_after: Filter entities created after this date (ISO 8601 format: 2024-01-15T10:30:00Z)

          created_before: Filter entities created before this date (ISO 8601 format)

          has_comments: Filter entities with or without user comments

          order: Sort order: -1 for descending, 1 for ascending

          page: Page number (1-based)

          page_size: Items per page (max 100, default 50)

          search: Search entities by name or company

          sort_by: Field to sort by (e.g., 'created_at', 'updated_at', 'status')

          status: Filter by entity status (true=active, false=inactive)

          updated_after: Filter entities updated after this date (ISO 8601 format)

          updated_before: Filter entities updated before this date (ISO 8601 format)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return await self._get(
            f"/v1/sheet/{sheet_id}/entities",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "created_after": created_after,
                        "created_before": created_before,
                        "has_comments": has_comments,
                        "order": order,
                        "page": page,
                        "page_size": page_size,
                        "search": search,
                        "sort_by": sort_by,
                        "status": status,
                        "updated_after": updated_after,
                        "updated_before": updated_before,
                    },
                    sheet_get_entities_params.SheetGetEntitiesParams,
                ),
            ),
            cast_to=SheetGetEntitiesResponse,
        )


class SheetResourceWithRawResponse:
    def __init__(self, sheet: SheetResource) -> None:
        self._sheet = sheet

        self.create = to_raw_response_wrapper(
            sheet.create,
        )
        self.retrieve = to_raw_response_wrapper(
            sheet.retrieve,
        )
        self.update = to_raw_response_wrapper(
            sheet.update,
        )
        self.list = to_raw_response_wrapper(
            sheet.list,
        )
        self.delete = to_raw_response_wrapper(
            sheet.delete,
        )
        self.export_csv = to_raw_response_wrapper(
            sheet.export_csv,
        )
        self.get_entities = to_raw_response_wrapper(
            sheet.get_entities,
        )

    @cached_property
    def entity(self) -> EntityResourceWithRawResponse:
        return EntityResourceWithRawResponse(self._sheet.entity)

    @cached_property
    def schema(self) -> SchemaResourceWithRawResponse:
        return SchemaResourceWithRawResponse(self._sheet.schema)


class AsyncSheetResourceWithRawResponse:
    def __init__(self, sheet: AsyncSheetResource) -> None:
        self._sheet = sheet

        self.create = async_to_raw_response_wrapper(
            sheet.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            sheet.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            sheet.update,
        )
        self.list = async_to_raw_response_wrapper(
            sheet.list,
        )
        self.delete = async_to_raw_response_wrapper(
            sheet.delete,
        )
        self.export_csv = async_to_raw_response_wrapper(
            sheet.export_csv,
        )
        self.get_entities = async_to_raw_response_wrapper(
            sheet.get_entities,
        )

    @cached_property
    def entity(self) -> AsyncEntityResourceWithRawResponse:
        return AsyncEntityResourceWithRawResponse(self._sheet.entity)

    @cached_property
    def schema(self) -> AsyncSchemaResourceWithRawResponse:
        return AsyncSchemaResourceWithRawResponse(self._sheet.schema)


class SheetResourceWithStreamingResponse:
    def __init__(self, sheet: SheetResource) -> None:
        self._sheet = sheet

        self.create = to_streamed_response_wrapper(
            sheet.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            sheet.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            sheet.update,
        )
        self.list = to_streamed_response_wrapper(
            sheet.list,
        )
        self.delete = to_streamed_response_wrapper(
            sheet.delete,
        )
        self.export_csv = to_streamed_response_wrapper(
            sheet.export_csv,
        )
        self.get_entities = to_streamed_response_wrapper(
            sheet.get_entities,
        )

    @cached_property
    def entity(self) -> EntityResourceWithStreamingResponse:
        return EntityResourceWithStreamingResponse(self._sheet.entity)

    @cached_property
    def schema(self) -> SchemaResourceWithStreamingResponse:
        return SchemaResourceWithStreamingResponse(self._sheet.schema)


class AsyncSheetResourceWithStreamingResponse:
    def __init__(self, sheet: AsyncSheetResource) -> None:
        self._sheet = sheet

        self.create = async_to_streamed_response_wrapper(
            sheet.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            sheet.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            sheet.update,
        )
        self.list = async_to_streamed_response_wrapper(
            sheet.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            sheet.delete,
        )
        self.export_csv = async_to_streamed_response_wrapper(
            sheet.export_csv,
        )
        self.get_entities = async_to_streamed_response_wrapper(
            sheet.get_entities,
        )

    @cached_property
    def entity(self) -> AsyncEntityResourceWithStreamingResponse:
        return AsyncEntityResourceWithStreamingResponse(self._sheet.entity)

    @cached_property
    def schema(self) -> AsyncSchemaResourceWithStreamingResponse:
        return AsyncSchemaResourceWithStreamingResponse(self._sheet.schema)
