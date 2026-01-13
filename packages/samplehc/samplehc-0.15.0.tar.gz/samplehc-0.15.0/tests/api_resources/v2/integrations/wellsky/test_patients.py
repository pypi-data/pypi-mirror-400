# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatients:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_add(self, client: SampleHealthcare) -> None:
        patient = client.v2.integrations.wellsky.patients.add(
            slug="slug",
            data={"foo": "bar"},
        )
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_add(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.wellsky.patients.with_raw_response.add(
            slug="slug",
            data={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_add(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.wellsky.patients.with_streaming_response.add(
            slug="slug",
            data={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(object, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_add(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.wellsky.patients.with_raw_response.add(
                slug="",
                data={"foo": "bar"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search(self, client: SampleHealthcare) -> None:
        patient = client.v2.integrations.wellsky.patients.search(
            slug="slug",
        )
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search_with_all_params(self, client: SampleHealthcare) -> None:
        patient = client.v2.integrations.wellsky.patients.search(
            slug="slug",
            reqdelete="REQDELETE",
            reqdispin="REQDISPIN",
            reqlvl6_in="REQLVL6IN",
            reqnamein="REQNAMEIN",
            reqnonprosp="REQNONPROSP",
            reqprosp="REQPROSP",
            reqsortin="REQSORTIN",
        )
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_search(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.wellsky.patients.with_raw_response.search(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_search(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.wellsky.patients.with_streaming_response.search(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(object, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_search(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.wellsky.patients.with_raw_response.search(
                slug="",
            )


class TestAsyncPatients:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_add(self, async_client: AsyncSampleHealthcare) -> None:
        patient = await async_client.v2.integrations.wellsky.patients.add(
            slug="slug",
            data={"foo": "bar"},
        )
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_add(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.wellsky.patients.with_raw_response.add(
            slug="slug",
            data={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_add(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.wellsky.patients.with_streaming_response.add(
            slug="slug",
            data={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(object, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_add(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.wellsky.patients.with_raw_response.add(
                slug="",
                data={"foo": "bar"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search(self, async_client: AsyncSampleHealthcare) -> None:
        patient = await async_client.v2.integrations.wellsky.patients.search(
            slug="slug",
        )
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        patient = await async_client.v2.integrations.wellsky.patients.search(
            slug="slug",
            reqdelete="REQDELETE",
            reqdispin="REQDISPIN",
            reqlvl6_in="REQLVL6IN",
            reqnamein="REQNAMEIN",
            reqnonprosp="REQNONPROSP",
            reqprosp="REQPROSP",
            reqsortin="REQSORTIN",
        )
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.wellsky.patients.with_raw_response.search(
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(object, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.wellsky.patients.with_streaming_response.search(
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(object, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_search(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.wellsky.patients.with_raw_response.search(
                slug="",
            )
