# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.v2.integrations.wellsky import patient_add_params, patient_search_params

__all__ = ["PatientsResource", "AsyncPatientsResource"]


class PatientsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return PatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return PatientsResourceWithStreamingResponse(self)

    def add(
        self,
        slug: str,
        *,
        data: Dict[str, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Add a patient to WellSky.

        Args:
          data: The data to add the patient to WellSky.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._post(
            f"/api/v2/integrations/wellsky/{slug}/patients",
            body=maybe_transform({"data": data}, patient_add_params.PatientAddParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def search(
        self,
        slug: str,
        *,
        reqdelete: str | Omit = omit,
        reqdispin: str | Omit = omit,
        reqlvl6_in: str | Omit = omit,
        reqnamein: str | Omit = omit,
        reqnonprosp: str | Omit = omit,
        reqprosp: str | Omit = omit,
        reqsortin: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Search for patients in WellSky.

        Args:
          reqdelete: Delete flag (Y/N)

          reqdispin: Disposition filter

          reqlvl6_in: Facility ID

          reqnamein: Patient name to search

          reqnonprosp: Non-prospect flag (Y/N)

          reqprosp: Prospect flag (Y/N)

          reqsortin: Sort field

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._get(
            f"/api/v2/integrations/wellsky/{slug}/patients",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "reqdelete": reqdelete,
                        "reqdispin": reqdispin,
                        "reqlvl6_in": reqlvl6_in,
                        "reqnamein": reqnamein,
                        "reqnonprosp": reqnonprosp,
                        "reqprosp": reqprosp,
                        "reqsortin": reqsortin,
                    },
                    patient_search_params.PatientSearchParams,
                ),
            ),
            cast_to=object,
        )


class AsyncPatientsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncPatientsResourceWithStreamingResponse(self)

    async def add(
        self,
        slug: str,
        *,
        data: Dict[str, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Add a patient to WellSky.

        Args:
          data: The data to add the patient to WellSky.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._post(
            f"/api/v2/integrations/wellsky/{slug}/patients",
            body=await async_maybe_transform({"data": data}, patient_add_params.PatientAddParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def search(
        self,
        slug: str,
        *,
        reqdelete: str | Omit = omit,
        reqdispin: str | Omit = omit,
        reqlvl6_in: str | Omit = omit,
        reqnamein: str | Omit = omit,
        reqnonprosp: str | Omit = omit,
        reqprosp: str | Omit = omit,
        reqsortin: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Search for patients in WellSky.

        Args:
          reqdelete: Delete flag (Y/N)

          reqdispin: Disposition filter

          reqlvl6_in: Facility ID

          reqnamein: Patient name to search

          reqnonprosp: Non-prospect flag (Y/N)

          reqprosp: Prospect flag (Y/N)

          reqsortin: Sort field

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._get(
            f"/api/v2/integrations/wellsky/{slug}/patients",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "reqdelete": reqdelete,
                        "reqdispin": reqdispin,
                        "reqlvl6_in": reqlvl6_in,
                        "reqnamein": reqnamein,
                        "reqnonprosp": reqnonprosp,
                        "reqprosp": reqprosp,
                        "reqsortin": reqsortin,
                    },
                    patient_search_params.PatientSearchParams,
                ),
            ),
            cast_to=object,
        )


class PatientsResourceWithRawResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.add = to_raw_response_wrapper(
            patients.add,
        )
        self.search = to_raw_response_wrapper(
            patients.search,
        )


class AsyncPatientsResourceWithRawResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.add = async_to_raw_response_wrapper(
            patients.add,
        )
        self.search = async_to_raw_response_wrapper(
            patients.search,
        )


class PatientsResourceWithStreamingResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.add = to_streamed_response_wrapper(
            patients.add,
        )
        self.search = to_streamed_response_wrapper(
            patients.search,
        )


class AsyncPatientsResourceWithStreamingResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.add = async_to_streamed_response_wrapper(
            patients.add,
        )
        self.search = async_to_streamed_response_wrapper(
            patients.search,
        )
