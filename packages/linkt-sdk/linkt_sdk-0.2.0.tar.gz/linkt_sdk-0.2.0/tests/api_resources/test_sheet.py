# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from linkt import Linkt, AsyncLinkt
from linkt.types import (
    SheetListResponse,
    SheetGetEntitiesResponse,
)
from tests.utils import assert_matches_type
from linkt._utils import parse_datetime
from linkt.types.sheet import Sheet

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSheet:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Linkt) -> None:
        sheet = client.sheet.create(
            description="x",
            entity_type="company",
            icp_id="icp_id",
            name="x",
        )
        assert_matches_type(Sheet, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Linkt) -> None:
        response = client.sheet.with_raw_response.create(
            description="x",
            entity_type="company",
            icp_id="icp_id",
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = response.parse()
        assert_matches_type(Sheet, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Linkt) -> None:
        with client.sheet.with_streaming_response.create(
            description="x",
            entity_type="company",
            icp_id="icp_id",
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = response.parse()
            assert_matches_type(Sheet, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Linkt) -> None:
        sheet = client.sheet.retrieve(
            "sheet_id",
        )
        assert_matches_type(Sheet, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Linkt) -> None:
        response = client.sheet.with_raw_response.retrieve(
            "sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = response.parse()
        assert_matches_type(Sheet, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Linkt) -> None:
        with client.sheet.with_streaming_response.retrieve(
            "sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = response.parse()
            assert_matches_type(Sheet, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Linkt) -> None:
        sheet = client.sheet.update(
            sheet_id="sheet_id",
        )
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Linkt) -> None:
        sheet = client.sheet.update(
            sheet_id="sheet_id",
            description="x",
            icp_id="5eb7cf5a86d9755df3a6c593",
            name="x",
        )
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Linkt) -> None:
        response = client.sheet.with_raw_response.update(
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = response.parse()
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Linkt) -> None:
        with client.sheet.with_streaming_response.update(
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = response.parse()
            assert sheet is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.with_raw_response.update(
                sheet_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Linkt) -> None:
        sheet = client.sheet.list()
        assert_matches_type(SheetListResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Linkt) -> None:
        sheet = client.sheet.list(
            entity_type="entity_type",
            icp_id="icp_id",
            order=0,
            page=0,
            page_size=0,
            sort_by="sort_by",
        )
        assert_matches_type(SheetListResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Linkt) -> None:
        response = client.sheet.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = response.parse()
        assert_matches_type(SheetListResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Linkt) -> None:
        with client.sheet.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = response.parse()
            assert_matches_type(SheetListResponse, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Linkt) -> None:
        sheet = client.sheet.delete(
            "sheet_id",
        )
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Linkt) -> None:
        response = client.sheet.with_raw_response.delete(
            "sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = response.parse()
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Linkt) -> None:
        with client.sheet.with_streaming_response.delete(
            "sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = response.parse()
            assert sheet is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_export_csv(self, client: Linkt) -> None:
        sheet = client.sheet.export_csv(
            sheet_id="sheet_id",
        )
        assert_matches_type(object, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_export_csv_with_all_params(self, client: Linkt) -> None:
        sheet = client.sheet.export_csv(
            sheet_id="sheet_id",
            entity_ids=["string"],
        )
        assert_matches_type(object, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_export_csv(self, client: Linkt) -> None:
        response = client.sheet.with_raw_response.export_csv(
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = response.parse()
        assert_matches_type(object, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_export_csv(self, client: Linkt) -> None:
        with client.sheet.with_streaming_response.export_csv(
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = response.parse()
            assert_matches_type(object, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_export_csv(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.with_raw_response.export_csv(
                sheet_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_entities(self, client: Linkt) -> None:
        sheet = client.sheet.get_entities(
            sheet_id="sheet_id",
        )
        assert_matches_type(SheetGetEntitiesResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_entities_with_all_params(self, client: Linkt) -> None:
        sheet = client.sheet.get_entities(
            sheet_id="sheet_id",
            created_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            has_comments=True,
            order=0,
            page=1,
            page_size=1,
            search="search",
            sort_by="sort_by",
            status=True,
            updated_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            updated_before=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(SheetGetEntitiesResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_entities(self, client: Linkt) -> None:
        response = client.sheet.with_raw_response.get_entities(
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = response.parse()
        assert_matches_type(SheetGetEntitiesResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_entities(self, client: Linkt) -> None:
        with client.sheet.with_streaming_response.get_entities(
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = response.parse()
            assert_matches_type(SheetGetEntitiesResponse, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_entities(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            client.sheet.with_raw_response.get_entities(
                sheet_id="",
            )


class TestAsyncSheet:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.create(
            description="x",
            entity_type="company",
            icp_id="icp_id",
            name="x",
        )
        assert_matches_type(Sheet, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.with_raw_response.create(
            description="x",
            entity_type="company",
            icp_id="icp_id",
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = await response.parse()
        assert_matches_type(Sheet, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.with_streaming_response.create(
            description="x",
            entity_type="company",
            icp_id="icp_id",
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = await response.parse()
            assert_matches_type(Sheet, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.retrieve(
            "sheet_id",
        )
        assert_matches_type(Sheet, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.with_raw_response.retrieve(
            "sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = await response.parse()
        assert_matches_type(Sheet, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.with_streaming_response.retrieve(
            "sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = await response.parse()
            assert_matches_type(Sheet, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.update(
            sheet_id="sheet_id",
        )
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.update(
            sheet_id="sheet_id",
            description="x",
            icp_id="5eb7cf5a86d9755df3a6c593",
            name="x",
        )
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.with_raw_response.update(
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = await response.parse()
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.with_streaming_response.update(
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = await response.parse()
            assert sheet is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.with_raw_response.update(
                sheet_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.list()
        assert_matches_type(SheetListResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.list(
            entity_type="entity_type",
            icp_id="icp_id",
            order=0,
            page=0,
            page_size=0,
            sort_by="sort_by",
        )
        assert_matches_type(SheetListResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = await response.parse()
        assert_matches_type(SheetListResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = await response.parse()
            assert_matches_type(SheetListResponse, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.delete(
            "sheet_id",
        )
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.with_raw_response.delete(
            "sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = await response.parse()
        assert sheet is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.with_streaming_response.delete(
            "sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = await response.parse()
            assert sheet is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_export_csv(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.export_csv(
            sheet_id="sheet_id",
        )
        assert_matches_type(object, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_export_csv_with_all_params(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.export_csv(
            sheet_id="sheet_id",
            entity_ids=["string"],
        )
        assert_matches_type(object, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_export_csv(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.with_raw_response.export_csv(
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = await response.parse()
        assert_matches_type(object, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_export_csv(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.with_streaming_response.export_csv(
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = await response.parse()
            assert_matches_type(object, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_export_csv(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.with_raw_response.export_csv(
                sheet_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_entities(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.get_entities(
            sheet_id="sheet_id",
        )
        assert_matches_type(SheetGetEntitiesResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_entities_with_all_params(self, async_client: AsyncLinkt) -> None:
        sheet = await async_client.sheet.get_entities(
            sheet_id="sheet_id",
            created_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            has_comments=True,
            order=0,
            page=1,
            page_size=1,
            search="search",
            sort_by="sort_by",
            status=True,
            updated_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            updated_before=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(SheetGetEntitiesResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_entities(self, async_client: AsyncLinkt) -> None:
        response = await async_client.sheet.with_raw_response.get_entities(
            sheet_id="sheet_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sheet = await response.parse()
        assert_matches_type(SheetGetEntitiesResponse, sheet, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_entities(self, async_client: AsyncLinkt) -> None:
        async with async_client.sheet.with_streaming_response.get_entities(
            sheet_id="sheet_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sheet = await response.parse()
            assert_matches_type(SheetGetEntitiesResponse, sheet, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_entities(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sheet_id` but received ''"):
            await async_client.sheet.with_raw_response.get_entities(
                sheet_id="",
            )
