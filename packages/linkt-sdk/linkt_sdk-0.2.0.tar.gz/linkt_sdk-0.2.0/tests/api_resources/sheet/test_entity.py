# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from linkt import Linkt, AsyncLinkt
from tests.utils import assert_matches_type
from linkt.types.sheet import EntityRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEntity:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Linkt) -> None:
        entity = client.sheet.entity.retrieve(
            entity_id="entity_id",
            sheet_id="sheet_id",
        )
        assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Linkt) -> None:
        response = client.sheet.entity.with_raw_response.retrieve(
            entity_id="entity_id",
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Linkt) -> None:
        with client.sheet.entity.with_streaming_response.retrieve(
            entity_id="entity_id",
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.entity.with_raw_response.retrieve(
                entity_id="entity_id",
                sheet_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            client.sheet.entity.with_raw_response.retrieve(
                entity_id="",
                sheet_id="sheet_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_comments(self, client: Linkt) -> None:
        entity = client.sheet.entity.update_comments(
            entity_id="entity_id",
            sheet_id="sheet_id",
        )
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_comments_with_all_params(self, client: Linkt) -> None:
        entity = client.sheet.entity.update_comments(
            entity_id="entity_id",
            sheet_id="sheet_id",
            comments="comments",
        )
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_comments(self, client: Linkt) -> None:
        response = client.sheet.entity.with_raw_response.update_comments(
            entity_id="entity_id",
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_comments(self, client: Linkt) -> None:
        with client.sheet.entity.with_streaming_response.update_comments(
            entity_id="entity_id",
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert entity is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_comments(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.entity.with_raw_response.update_comments(
                entity_id="entity_id",
                sheet_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            client.sheet.entity.with_raw_response.update_comments(
                entity_id="",
                sheet_id="sheet_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_status(self, client: Linkt) -> None:
        entity = client.sheet.entity.update_status(
            entity_id="entity_id",
            sheet_id="sheet_id",
            status=True,
        )
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_status(self, client: Linkt) -> None:
        response = client.sheet.entity.with_raw_response.update_status(
            entity_id="entity_id",
            sheet_id="sheet_id",
            status=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_status(self, client: Linkt) -> None:
        with client.sheet.entity.with_streaming_response.update_status(
            entity_id="entity_id",
            sheet_id="sheet_id",
            status=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert entity is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_status(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.entity.with_raw_response.update_status(
                entity_id="entity_id",
                sheet_id="",
                status=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            client.sheet.entity.with_raw_response.update_status(
                entity_id="",
                sheet_id="sheet_id",
                status=True,
            )


class TestAsyncEntity:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncLinkt) -> None:
        entity = await async_client.sheet.entity.retrieve(
            entity_id="entity_id",
            sheet_id="sheet_id",
        )
        assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.entity.with_raw_response.retrieve(
            entity_id="entity_id",
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.entity.with_streaming_response.retrieve(
            entity_id="entity_id",
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.entity.with_raw_response.retrieve(
                entity_id="entity_id",
                sheet_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            await async_client.sheet.entity.with_raw_response.retrieve(
                entity_id="",
                sheet_id="sheet_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_comments(self, async_client: AsyncLinkt) -> None:
        entity = await async_client.sheet.entity.update_comments(
            entity_id="entity_id",
            sheet_id="sheet_id",
        )
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_comments_with_all_params(self, async_client: AsyncLinkt) -> None:
        entity = await async_client.sheet.entity.update_comments(
            entity_id="entity_id",
            sheet_id="sheet_id",
            comments="comments",
        )
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_comments(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.entity.with_raw_response.update_comments(
            entity_id="entity_id",
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_comments(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.entity.with_streaming_response.update_comments(
            entity_id="entity_id",
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert entity is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_comments(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.entity.with_raw_response.update_comments(
                entity_id="entity_id",
                sheet_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            await async_client.sheet.entity.with_raw_response.update_comments(
                entity_id="",
                sheet_id="sheet_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_status(self, async_client: AsyncLinkt) -> None:
        entity = await async_client.sheet.entity.update_status(
            entity_id="entity_id",
            sheet_id="sheet_id",
            status=True,
        )
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_status(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.entity.with_raw_response.update_status(
            entity_id="entity_id",
            sheet_id="sheet_id",
            status=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_status(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.entity.with_streaming_response.update_status(
            entity_id="entity_id",
            sheet_id="sheet_id",
            status=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert entity is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_status(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.entity.with_raw_response.update_status(
                entity_id="entity_id",
                sheet_id="",
                status=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            await async_client.sheet.entity.with_raw_response.update_status(
                entity_id="",
                sheet_id="sheet_id",
                status=True,
            )
