# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .patients import (
    PatientsResource,
    AsyncPatientsResource,
    PatientsResourceWithRawResponse,
    AsyncPatientsResourceWithRawResponse,
    PatientsResourceWithStreamingResponse,
    AsyncPatientsResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["WellskyResource", "AsyncWellskyResource"]


class WellskyResource(SyncAPIResource):
    @cached_property
    def patients(self) -> PatientsResource:
        return PatientsResource(self._client)

    @cached_property
    def with_raw_response(self) -> WellskyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return WellskyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WellskyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return WellskyResourceWithStreamingResponse(self)


class AsyncWellskyResource(AsyncAPIResource):
    @cached_property
    def patients(self) -> AsyncPatientsResource:
        return AsyncPatientsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncWellskyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWellskyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWellskyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncWellskyResourceWithStreamingResponse(self)


class WellskyResourceWithRawResponse:
    def __init__(self, wellsky: WellskyResource) -> None:
        self._wellsky = wellsky

    @cached_property
    def patients(self) -> PatientsResourceWithRawResponse:
        return PatientsResourceWithRawResponse(self._wellsky.patients)


class AsyncWellskyResourceWithRawResponse:
    def __init__(self, wellsky: AsyncWellskyResource) -> None:
        self._wellsky = wellsky

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithRawResponse:
        return AsyncPatientsResourceWithRawResponse(self._wellsky.patients)


class WellskyResourceWithStreamingResponse:
    def __init__(self, wellsky: WellskyResource) -> None:
        self._wellsky = wellsky

    @cached_property
    def patients(self) -> PatientsResourceWithStreamingResponse:
        return PatientsResourceWithStreamingResponse(self._wellsky.patients)


class AsyncWellskyResourceWithStreamingResponse:
    def __init__(self, wellsky: AsyncWellskyResource) -> None:
        self._wellsky = wellsky

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithStreamingResponse:
        return AsyncPatientsResourceWithStreamingResponse(self._wellsky.patients)
