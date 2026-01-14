# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from linkt import Linkt, AsyncLinkt
from tests.utils import assert_matches_type
from linkt.types.sheet import (
    SchemaGetResponse,
    SchemaGetDefaultResponse,
    SchemaGetFieldDefinitionsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSchema:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_add_fields(self, client: Linkt) -> None:
        schema = client.sheet.schema.add_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=[
                {
                    "field_type": "string",
                    "name": "name",
                }
            ],
        )
        assert schema is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_add_fields(self, client: Linkt) -> None:
        response = client.sheet.schema.with_raw_response.add_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=[
                {
                    "field_type": "string",
                    "name": "name",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = response.parse()
        assert schema is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_add_fields(self, client: Linkt) -> None:
        with client.sheet.schema.with_streaming_response.add_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=[
                {
                    "field_type": "string",
                    "name": "name",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = response.parse()
            assert schema is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_add_fields(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.schema.with_raw_response.add_fields(
                sheet_id="",
                fields=[
                    {
                        "field_type": "string",
                        "name": "name",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_fields(self, client: Linkt) -> None:
        schema = client.sheet.schema.delete_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=["string"],
        )
        assert schema is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_fields(self, client: Linkt) -> None:
        response = client.sheet.schema.with_raw_response.delete_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = response.parse()
        assert schema is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_fields(self, client: Linkt) -> None:
        with client.sheet.schema.with_streaming_response.delete_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = response.parse()
            assert schema is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_fields(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.schema.with_raw_response.delete_fields(
                sheet_id="",
                fields=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Linkt) -> None:
        schema = client.sheet.schema.get(
            "5eb7cf5a86d9755df3a6c593",
        )
        assert_matches_type(SchemaGetResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Linkt) -> None:
        response = client.sheet.schema.with_raw_response.get(
            "5eb7cf5a86d9755df3a6c593",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = response.parse()
        assert_matches_type(SchemaGetResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Linkt) -> None:
        with client.sheet.schema.with_streaming_response.get(
            "5eb7cf5a86d9755df3a6c593",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = response.parse()
            assert_matches_type(SchemaGetResponse, schema, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.schema.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_default(self, client: Linkt) -> None:
        schema = client.sheet.schema.get_default()
        assert_matches_type(SchemaGetDefaultResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_default(self, client: Linkt) -> None:
        response = client.sheet.schema.with_raw_response.get_default()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = response.parse()
        assert_matches_type(SchemaGetDefaultResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_default(self, client: Linkt) -> None:
        with client.sheet.schema.with_streaming_response.get_default() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = response.parse()
            assert_matches_type(SchemaGetDefaultResponse, schema, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_field_definitions(self, client: Linkt) -> None:
        schema = client.sheet.schema.get_field_definitions()
        assert_matches_type(SchemaGetFieldDefinitionsResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_field_definitions(self, client: Linkt) -> None:
        response = client.sheet.schema.with_raw_response.get_field_definitions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = response.parse()
        assert_matches_type(SchemaGetFieldDefinitionsResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_field_definitions(self, client: Linkt) -> None:
        with client.sheet.schema.with_streaming_response.get_field_definitions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = response.parse()
            assert_matches_type(SchemaGetFieldDefinitionsResponse, schema, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSchema:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_add_fields(self, async_client: AsyncLinkt) -> None:
        schema = await async_client.sheet.schema.add_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=[
                {
                    "field_type": "string",
                    "name": "name",
                }
            ],
        )
        assert schema is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_add_fields(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.schema.with_raw_response.add_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=[
                {
                    "field_type": "string",
                    "name": "name",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = await response.parse()
        assert schema is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_add_fields(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.schema.with_streaming_response.add_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=[
                {
                    "field_type": "string",
                    "name": "name",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = await response.parse()
            assert schema is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_add_fields(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.schema.with_raw_response.add_fields(
                sheet_id="",
                fields=[
                    {
                        "field_type": "string",
                        "name": "name",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_fields(self, async_client: AsyncLinkt) -> None:
        schema = await async_client.sheet.schema.delete_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=["string"],
        )
        assert schema is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_fields(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.schema.with_raw_response.delete_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = await response.parse()
        assert schema is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_fields(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.schema.with_streaming_response.delete_fields(
            sheet_id="5eb7cf5a86d9755df3a6c593",
            fields=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = await response.parse()
            assert schema is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_fields(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.schema.with_raw_response.delete_fields(
                sheet_id="",
                fields=["string"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncLinkt) -> None:
        schema = await async_client.sheet.schema.get(
            "5eb7cf5a86d9755df3a6c593",
        )
        assert_matches_type(SchemaGetResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.schema.with_raw_response.get(
            "5eb7cf5a86d9755df3a6c593",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = await response.parse()
        assert_matches_type(SchemaGetResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.schema.with_streaming_response.get(
            "5eb7cf5a86d9755df3a6c593",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = await response.parse()
            assert_matches_type(SchemaGetResponse, schema, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.schema.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_default(self, async_client: AsyncLinkt) -> None:
        schema = await async_client.sheet.schema.get_default()
        assert_matches_type(SchemaGetDefaultResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_default(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.schema.with_raw_response.get_default()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = await response.parse()
        assert_matches_type(SchemaGetDefaultResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_default(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.schema.with_streaming_response.get_default() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = await response.parse()
            assert_matches_type(SchemaGetDefaultResponse, schema, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_field_definitions(self, async_client: AsyncLinkt) -> None:
        schema = await async_client.sheet.schema.get_field_definitions()
        assert_matches_type(SchemaGetFieldDefinitionsResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_field_definitions(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.schema.with_raw_response.get_field_definitions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = await response.parse()
        assert_matches_type(SchemaGetFieldDefinitionsResponse, schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_field_definitions(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.schema.with_streaming_response.get_field_definitions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = await response.parse()
            assert_matches_type(SchemaGetFieldDefinitionsResponse, schema, path=["response"])

        assert cast(Any, response.is_closed) is True
