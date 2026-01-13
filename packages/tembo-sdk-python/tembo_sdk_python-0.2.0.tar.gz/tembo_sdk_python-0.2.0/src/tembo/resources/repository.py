# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import Body, Query, Headers, NotGiven, not_given
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.repository_list_response import RepositoryListResponse

__all__ = ["RepositoryResource", "AsyncRepositoryResource"]


class RepositoryResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RepositoryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/tembo/sdk-python#accessing-raw-response-data-eg-headers
        """
        return RepositoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RepositoryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/tembo/sdk-python#with_streaming_response
        """
        return RepositoryResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepositoryListResponse:
        """Gets a list of enabled repositories for the organization"""
        return self._get(
            "/repository/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepositoryListResponse,
        )


class AsyncRepositoryResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRepositoryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/tembo/sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRepositoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRepositoryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/tembo/sdk-python#with_streaming_response
        """
        return AsyncRepositoryResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepositoryListResponse:
        """Gets a list of enabled repositories for the organization"""
        return await self._get(
            "/repository/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepositoryListResponse,
        )


class RepositoryResourceWithRawResponse:
    def __init__(self, repository: RepositoryResource) -> None:
        self._repository = repository

        self.list = to_raw_response_wrapper(
            repository.list,
        )


class AsyncRepositoryResourceWithRawResponse:
    def __init__(self, repository: AsyncRepositoryResource) -> None:
        self._repository = repository

        self.list = async_to_raw_response_wrapper(
            repository.list,
        )


class RepositoryResourceWithStreamingResponse:
    def __init__(self, repository: RepositoryResource) -> None:
        self._repository = repository

        self.list = to_streamed_response_wrapper(
            repository.list,
        )


class AsyncRepositoryResourceWithStreamingResponse:
    def __init__(self, repository: AsyncRepositoryResource) -> None:
        self._repository = repository

        self.list = async_to_streamed_response_wrapper(
            repository.list,
        )
