# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from linkt import Linkt, AsyncLinkt
from linkt.types import (
    IcpResponse,
    IcpListResponse,
    IcpGetActiveRunsResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIcp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Linkt) -> None:
        icp = client.icp.create(
            description="x",
            entity_targets=[
                {
                    "description": "description",
                    "entity_type": "entity_type",
                }
            ],
            name="x",
        )
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Linkt) -> None:
        response = client.icp.with_raw_response.create(
            description="x",
            entity_targets=[
                {
                    "description": "description",
                    "entity_type": "entity_type",
                }
            ],
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = response.parse()
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Linkt) -> None:
        with client.icp.with_streaming_response.create(
            description="x",
            entity_targets=[
                {
                    "description": "description",
                    "entity_type": "entity_type",
                }
            ],
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = response.parse()
            assert_matches_type(IcpResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Linkt) -> None:
        icp = client.icp.retrieve(
            "icp_id",
        )
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Linkt) -> None:
        response = client.icp.with_raw_response.retrieve(
            "icp_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = response.parse()
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Linkt) -> None:
        with client.icp.with_streaming_response.retrieve(
            "icp_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = response.parse()
            assert_matches_type(IcpResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `icp_id` but received ''"):
            client.icp.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Linkt) -> None:
        icp = client.icp.update(
            icp_id="icp_id",
        )
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Linkt) -> None:
        icp = client.icp.update(
            icp_id="icp_id",
            description="x",
            entity_targets=[
                {
                    "description": "description",
                    "entity_type": "entity_type",
                    "filters": ["string"],
                }
            ],
            name="x",
        )
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Linkt) -> None:
        response = client.icp.with_raw_response.update(
            icp_id="icp_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = response.parse()
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Linkt) -> None:
        with client.icp.with_streaming_response.update(
            icp_id="icp_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = response.parse()
            assert_matches_type(IcpResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `icp_id` but received ''"):
            client.icp.with_raw_response.update(
                icp_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Linkt) -> None:
        icp = client.icp.list()
        assert_matches_type(IcpListResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Linkt) -> None:
        icp = client.icp.list(
            mode="discovery",
            order=0,
            page=1,
            page_size=1,
            sort_by="sort_by",
        )
        assert_matches_type(IcpListResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Linkt) -> None:
        response = client.icp.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = response.parse()
        assert_matches_type(IcpListResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Linkt) -> None:
        with client.icp.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = response.parse()
            assert_matches_type(IcpListResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Linkt) -> None:
        icp = client.icp.delete(
            "icp_id",
        )
        assert icp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Linkt) -> None:
        response = client.icp.with_raw_response.delete(
            "icp_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = response.parse()
        assert icp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Linkt) -> None:
        with client.icp.with_streaming_response.delete(
            "icp_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = response.parse()
            assert icp is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `icp_id` but received ''"):
            client.icp.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_active_runs(self, client: Linkt) -> None:
        icp = client.icp.get_active_runs(
            "icp_id",
        )
        assert_matches_type(IcpGetActiveRunsResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_active_runs(self, client: Linkt) -> None:
        response = client.icp.with_raw_response.get_active_runs(
            "icp_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = response.parse()
        assert_matches_type(IcpGetActiveRunsResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_active_runs(self, client: Linkt) -> None:
        with client.icp.with_streaming_response.get_active_runs(
            "icp_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = response.parse()
            assert_matches_type(IcpGetActiveRunsResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_active_runs(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `icp_id` but received ''"):
            client.icp.with_raw_response.get_active_runs(
                "",
            )


class TestAsyncIcp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncLinkt) -> None:
        icp = await async_client.icp.create(
            description="x",
            entity_targets=[
                {
                    "description": "description",
                    "entity_type": "entity_type",
                }
            ],
            name="x",
        )
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLinkt) -> None:
        response = await async_client.icp.with_raw_response.create(
            description="x",
            entity_targets=[
                {
                    "description": "description",
                    "entity_type": "entity_type",
                }
            ],
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = await response.parse()
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLinkt) -> None:
        async with async_client.icp.with_streaming_response.create(
            description="x",
            entity_targets=[
                {
                    "description": "description",
                    "entity_type": "entity_type",
                }
            ],
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = await response.parse()
            assert_matches_type(IcpResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncLinkt) -> None:
        icp = await async_client.icp.retrieve(
            "icp_id",
        )
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncLinkt) -> None:
        response = await async_client.icp.with_raw_response.retrieve(
            "icp_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = await response.parse()
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncLinkt) -> None:
        async with async_client.icp.with_streaming_response.retrieve(
            "icp_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = await response.parse()
            assert_matches_type(IcpResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `icp_id` but received ''"):
            await async_client.icp.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncLinkt) -> None:
        icp = await async_client.icp.update(
            icp_id="icp_id",
        )
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncLinkt) -> None:
        icp = await async_client.icp.update(
            icp_id="icp_id",
            description="x",
            entity_targets=[
                {
                    "description": "description",
                    "entity_type": "entity_type",
                    "filters": ["string"],
                }
            ],
            name="x",
        )
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncLinkt) -> None:
        response = await async_client.icp.with_raw_response.update(
            icp_id="icp_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = await response.parse()
        assert_matches_type(IcpResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncLinkt) -> None:
        async with async_client.icp.with_streaming_response.update(
            icp_id="icp_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = await response.parse()
            assert_matches_type(IcpResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `icp_id` but received ''"):
            await async_client.icp.with_raw_response.update(
                icp_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncLinkt) -> None:
        icp = await async_client.icp.list()
        assert_matches_type(IcpListResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLinkt) -> None:
        icp = await async_client.icp.list(
            mode="discovery",
            order=0,
            page=1,
            page_size=1,
            sort_by="sort_by",
        )
        assert_matches_type(IcpListResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLinkt) -> None:
        response = await async_client.icp.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = await response.parse()
        assert_matches_type(IcpListResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLinkt) -> None:
        async with async_client.icp.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = await response.parse()
            assert_matches_type(IcpListResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncLinkt) -> None:
        icp = await async_client.icp.delete(
            "icp_id",
        )
        assert icp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncLinkt) -> None:
        response = await async_client.icp.with_raw_response.delete(
            "icp_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = await response.parse()
        assert icp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncLinkt) -> None:
        async with async_client.icp.with_streaming_response.delete(
            "icp_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = await response.parse()
            assert icp is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `icp_id` but received ''"):
            await async_client.icp.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_active_runs(self, async_client: AsyncLinkt) -> None:
        icp = await async_client.icp.get_active_runs(
            "icp_id",
        )
        assert_matches_type(IcpGetActiveRunsResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_active_runs(self, async_client: AsyncLinkt) -> None:
        response = await async_client.icp.with_raw_response.get_active_runs(
            "icp_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        icp = await response.parse()
        assert_matches_type(IcpGetActiveRunsResponse, icp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_active_runs(self, async_client: AsyncLinkt) -> None:
        async with async_client.icp.with_streaming_response.get_active_runs(
            "icp_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            icp = await response.parse()
            assert_matches_type(IcpGetActiveRunsResponse, icp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_active_runs(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `icp_id` but received ''"):
            await async_client.icp.with_raw_response.get_active_runs(
                "",
            )
