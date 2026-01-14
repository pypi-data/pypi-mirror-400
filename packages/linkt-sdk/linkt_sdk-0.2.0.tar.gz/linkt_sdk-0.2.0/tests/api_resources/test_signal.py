# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from linkt import Linkt, AsyncLinkt
from linkt.types import SignalResponse, SignalListResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSignal:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Linkt) -> None:
        signal = client.signal.retrieve(
            "signal_id",
        )
        assert_matches_type(SignalResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Linkt) -> None:
        response = client.signal.with_raw_response.retrieve(
            "signal_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signal = response.parse()
        assert_matches_type(SignalResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Linkt) -> None:
        with client.signal.with_streaming_response.retrieve(
            "signal_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signal = response.parse()
            assert_matches_type(SignalResponse, signal, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Linkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signal_id` but received ''"):
            client.signal.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Linkt) -> None:
        signal = client.signal.list()
        assert_matches_type(SignalListResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Linkt) -> None:
        signal = client.signal.list(
            days=1,
            entity_id="entity_id",
            icp_id="icp_id",
            order=0,
            page=1,
            page_size=1,
            search_term="search_term",
            signal_type="signal_type",
            sort_by="sort_by",
            strength="strength",
        )
        assert_matches_type(SignalListResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Linkt) -> None:
        response = client.signal.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signal = response.parse()
        assert_matches_type(SignalListResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Linkt) -> None:
        with client.signal.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signal = response.parse()
            assert_matches_type(SignalListResponse, signal, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSignal:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncLinkt) -> None:
        signal = await async_client.signal.retrieve(
            "signal_id",
        )
        assert_matches_type(SignalResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncLinkt) -> None:
        response = await async_client.signal.with_raw_response.retrieve(
            "signal_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signal = await response.parse()
        assert_matches_type(SignalResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncLinkt) -> None:
        async with async_client.signal.with_streaming_response.retrieve(
            "signal_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signal = await response.parse()
            assert_matches_type(SignalResponse, signal, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncLinkt) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signal_id` but received ''"):
            await async_client.signal.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncLinkt) -> None:
        signal = await async_client.signal.list()
        assert_matches_type(SignalListResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLinkt) -> None:
        signal = await async_client.signal.list(
            days=1,
            entity_id="entity_id",
            icp_id="icp_id",
            order=0,
            page=1,
            page_size=1,
            search_term="search_term",
            signal_type="signal_type",
            sort_by="sort_by",
            strength="strength",
        )
        assert_matches_type(SignalListResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLinkt) -> None:
        response = await async_client.signal.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signal = await response.parse()
        assert_matches_type(SignalListResponse, signal, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLinkt) -> None:
        async with async_client.signal.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signal = await response.parse()
            assert_matches_type(SignalListResponse, signal, path=["response"])

        assert cast(Any, response.is_closed) is True
