# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..._types import Body, Query, Headers, NoneType, NotGiven, SequenceNotStr, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.sheet import schema_add_fields_params, schema_delete_fields_params
from ..._base_client import make_request_options
from ...types.sheet.schema_get_response import SchemaGetResponse
from ...types.sheet.schema_get_default_response import SchemaGetDefaultResponse
from ...types.sheet.schema_get_field_definitions_response import SchemaGetFieldDefinitionsResponse

__all__ = ["SchemaResource", "AsyncSchemaResource"]


class SchemaResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SchemaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return SchemaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SchemaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return SchemaResourceWithStreamingResponse(self)

    def add_fields(
        self,
        sheet_id: str,
        *,
        fields: Iterable[schema_add_fields_params.Field],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Add custom fields to a sheet's entity schema.

        Custom fields extend the default schema to capture additional data points for
        entities in this sheet.

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
            f"/v1/sheet/schema/{sheet_id}",
            body=maybe_transform({"fields": fields}, schema_add_fields_params.SchemaAddFieldsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def delete_fields(
        self,
        sheet_id: str,
        *,
        fields: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Remove custom fields from a sheet's entity schema.

        Only custom fields can be removed; default fields cannot be deleted. Existing
        entity data in removed fields remains in the database but becomes inaccessible.

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
            f"/v1/sheet/schema/{sheet_id}",
            body=maybe_transform({"fields": fields}, schema_delete_fields_params.SchemaDeleteFieldsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        sheet_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SchemaGetResponse:
        """
        Get the schema for a specific sheet.

        Returns the sheet's current schema including default fields and any custom
        fields that have been added.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return self._get(
            f"/v1/sheet/schema/{sheet_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaGetResponse,
        )

    def get_default(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SchemaGetDefaultResponse:
        """
        Get the default schemas for all entity types.

        Returns JSON Schema definitions for company, person, job_board, and
        school_district entity types. Use this to understand the standard fields
        available before adding custom fields.
        """
        return self._get(
            "/v1/sheet/schema/default",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaGetDefaultResponse,
        )

    def get_field_definitions(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SchemaGetFieldDefinitionsResponse:
        """
        Get the available field type definitions.

        Returns JSON Schema definitions for field types that can be used when adding
        custom fields to sheets.
        """
        return self._get(
            "/v1/sheet/schema/field",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaGetFieldDefinitionsResponse,
        )


class AsyncSchemaResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSchemaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSchemaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSchemaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/linkt-ai/linkt-python-sdk#with_streaming_response
        """
        return AsyncSchemaResourceWithStreamingResponse(self)

    async def add_fields(
        self,
        sheet_id: str,
        *,
        fields: Iterable[schema_add_fields_params.Field],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Add custom fields to a sheet's entity schema.

        Custom fields extend the default schema to capture additional data points for
        entities in this sheet.

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
            f"/v1/sheet/schema/{sheet_id}",
            body=await async_maybe_transform({"fields": fields}, schema_add_fields_params.SchemaAddFieldsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def delete_fields(
        self,
        sheet_id: str,
        *,
        fields: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Remove custom fields from a sheet's entity schema.

        Only custom fields can be removed; default fields cannot be deleted. Existing
        entity data in removed fields remains in the database but becomes inaccessible.

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
            f"/v1/sheet/schema/{sheet_id}",
            body=await async_maybe_transform({"fields": fields}, schema_delete_fields_params.SchemaDeleteFieldsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        sheet_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SchemaGetResponse:
        """
        Get the schema for a specific sheet.

        Returns the sheet's current schema including default fields and any custom
        fields that have been added.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not sheet_id:
            raise ValueError(f"Expected a non-empty value for `sheet_id` but received {sheet_id!r}")
        return await self._get(
            f"/v1/sheet/schema/{sheet_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaGetResponse,
        )

    async def get_default(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SchemaGetDefaultResponse:
        """
        Get the default schemas for all entity types.

        Returns JSON Schema definitions for company, person, job_board, and
        school_district entity types. Use this to understand the standard fields
        available before adding custom fields.
        """
        return await self._get(
            "/v1/sheet/schema/default",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaGetDefaultResponse,
        )

    async def get_field_definitions(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SchemaGetFieldDefinitionsResponse:
        """
        Get the available field type definitions.

        Returns JSON Schema definitions for field types that can be used when adding
        custom fields to sheets.
        """
        return await self._get(
            "/v1/sheet/schema/field",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SchemaGetFieldDefinitionsResponse,
        )


class SchemaResourceWithRawResponse:
    def __init__(self, schema: SchemaResource) -> None:
        self._schema = schema

        self.add_fields = to_raw_response_wrapper(
            schema.add_fields,
        )
        self.delete_fields = to_raw_response_wrapper(
            schema.delete_fields,
        )
        self.get = to_raw_response_wrapper(
            schema.get,
        )
        self.get_default = to_raw_response_wrapper(
            schema.get_default,
        )
        self.get_field_definitions = to_raw_response_wrapper(
            schema.get_field_definitions,
        )


class AsyncSchemaResourceWithRawResponse:
    def __init__(self, schema: AsyncSchemaResource) -> None:
        self._schema = schema

        self.add_fields = async_to_raw_response_wrapper(
            schema.add_fields,
        )
        self.delete_fields = async_to_raw_response_wrapper(
            schema.delete_fields,
        )
        self.get = async_to_raw_response_wrapper(
            schema.get,
        )
        self.get_default = async_to_raw_response_wrapper(
            schema.get_default,
        )
        self.get_field_definitions = async_to_raw_response_wrapper(
            schema.get_field_definitions,
        )


class SchemaResourceWithStreamingResponse:
    def __init__(self, schema: SchemaResource) -> None:
        self._schema = schema

        self.add_fields = to_streamed_response_wrapper(
            schema.add_fields,
        )
        self.delete_fields = to_streamed_response_wrapper(
            schema.delete_fields,
        )
        self.get = to_streamed_response_wrapper(
            schema.get,
        )
        self.get_default = to_streamed_response_wrapper(
            schema.get_default,
        )
        self.get_field_definitions = to_streamed_response_wrapper(
            schema.get_field_definitions,
        )


class AsyncSchemaResourceWithStreamingResponse:
    def __init__(self, schema: AsyncSchemaResource) -> None:
        self._schema = schema

        self.add_fields = async_to_streamed_response_wrapper(
            schema.add_fields,
        )
        self.delete_fields = async_to_streamed_response_wrapper(
            schema.delete_fields,
        )
        self.get = async_to_streamed_response_wrapper(
            schema.get,
        )
        self.get_default = async_to_streamed_response_wrapper(
            schema.get_default,
        )
        self.get_field_definitions = async_to_streamed_response_wrapper(
            schema.get_field_definitions,
        )
