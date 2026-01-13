# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import task_list_params, task_create_params, task_search_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.task_list_response import TaskListResponse
from ..types.task_create_response import TaskCreateResponse
from ..types.task_search_response import TaskSearchResponse

__all__ = ["TaskResource", "AsyncTaskResource"]


class TaskResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/tembo/sdk-python#accessing-raw-response-data-eg-headers
        """
        return TaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/tembo/sdk-python#with_streaming_response
        """
        return TaskResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        agent: str | Omit = omit,
        branch: Optional[str] | Omit = omit,
        prompt: str | Omit = omit,
        queue_right_away: Optional[bool] | Omit = omit,
        repositories: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskCreateResponse:
        """
        Create a task for tembo to start working on in the background

        Args:
          agent: The agent to use for this task

          branch: Specific git branch to target for this task

          prompt: Description of the task to be performed. Supports tagging files.

          queue_right_away: Whether to immediately queue the task for processing (optional, defaults to
              true)

          repositories: Array of code repository urls that this task relates to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/task/create",
            body=maybe_transform(
                {
                    "agent": agent,
                    "branch": branch,
                    "prompt": prompt,
                    "queue_right_away": queue_right_away,
                    "repositories": repositories,
                },
                task_create_params.TaskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCreateResponse,
        )

    def list(
        self,
        *,
        limit: int | Omit = omit,
        page: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskListResponse:
        """
        Gets a paginated list of issues for the organization

        Args:
          limit: Number of items to return per page (max 100)

          page: Page number to retrieve (starts from 1)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/task/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            cast_to=TaskListResponse,
        )

    def search(
        self,
        *,
        q: str,
        limit: int | Omit = omit,
        page: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskSearchResponse:
        """
        Search issues for the organization with pagination

        Args:
          q: Search query to find issues by title or description

          limit: Number of items to return per page (max 100)

          page: Page number to retrieve (starts from 1)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/task/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "q": q,
                        "limit": limit,
                        "page": page,
                    },
                    task_search_params.TaskSearchParams,
                ),
            ),
            cast_to=TaskSearchResponse,
        )


class AsyncTaskResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/tembo/sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/tembo/sdk-python#with_streaming_response
        """
        return AsyncTaskResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        agent: str | Omit = omit,
        branch: Optional[str] | Omit = omit,
        prompt: str | Omit = omit,
        queue_right_away: Optional[bool] | Omit = omit,
        repositories: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskCreateResponse:
        """
        Create a task for tembo to start working on in the background

        Args:
          agent: The agent to use for this task

          branch: Specific git branch to target for this task

          prompt: Description of the task to be performed. Supports tagging files.

          queue_right_away: Whether to immediately queue the task for processing (optional, defaults to
              true)

          repositories: Array of code repository urls that this task relates to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/task/create",
            body=await async_maybe_transform(
                {
                    "agent": agent,
                    "branch": branch,
                    "prompt": prompt,
                    "queue_right_away": queue_right_away,
                    "repositories": repositories,
                },
                task_create_params.TaskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCreateResponse,
        )

    async def list(
        self,
        *,
        limit: int | Omit = omit,
        page: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskListResponse:
        """
        Gets a paginated list of issues for the organization

        Args:
          limit: Number of items to return per page (max 100)

          page: Page number to retrieve (starts from 1)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/task/list",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            cast_to=TaskListResponse,
        )

    async def search(
        self,
        *,
        q: str,
        limit: int | Omit = omit,
        page: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskSearchResponse:
        """
        Search issues for the organization with pagination

        Args:
          q: Search query to find issues by title or description

          limit: Number of items to return per page (max 100)

          page: Page number to retrieve (starts from 1)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/task/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "q": q,
                        "limit": limit,
                        "page": page,
                    },
                    task_search_params.TaskSearchParams,
                ),
            ),
            cast_to=TaskSearchResponse,
        )


class TaskResourceWithRawResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.create = to_raw_response_wrapper(
            task.create,
        )
        self.list = to_raw_response_wrapper(
            task.list,
        )
        self.search = to_raw_response_wrapper(
            task.search,
        )


class AsyncTaskResourceWithRawResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.create = async_to_raw_response_wrapper(
            task.create,
        )
        self.list = async_to_raw_response_wrapper(
            task.list,
        )
        self.search = async_to_raw_response_wrapper(
            task.search,
        )


class TaskResourceWithStreamingResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.create = to_streamed_response_wrapper(
            task.create,
        )
        self.list = to_streamed_response_wrapper(
            task.list,
        )
        self.search = to_streamed_response_wrapper(
            task.search,
        )


class AsyncTaskResourceWithStreamingResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.create = async_to_streamed_response_wrapper(
            task.create,
        )
        self.list = async_to_streamed_response_wrapper(
            task.list,
        )
        self.search = async_to_streamed_response_wrapper(
            task.search,
        )
