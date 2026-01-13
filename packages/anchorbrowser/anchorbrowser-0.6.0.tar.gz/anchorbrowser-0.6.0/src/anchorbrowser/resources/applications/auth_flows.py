# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.applications import auth_flow_create_params, auth_flow_update_params
from ...types.applications.auth_flow_list_response import AuthFlowListResponse
from ...types.applications.auth_flow_create_response import AuthFlowCreateResponse
from ...types.applications.auth_flow_delete_response import AuthFlowDeleteResponse
from ...types.applications.auth_flow_update_response import AuthFlowUpdateResponse

__all__ = ["AuthFlowsResource", "AsyncAuthFlowsResource"]


class AuthFlowsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AuthFlowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return AuthFlowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AuthFlowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return AuthFlowsResourceWithStreamingResponse(self)

    def create(
        self,
        application_id: str,
        *,
        methods: List[Literal["username_password", "authenticator", "custom"]],
        name: str,
        custom_fields: Iterable[auth_flow_create_params.CustomField] | Omit = omit,
        description: str | Omit = omit,
        is_recommended: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthFlowCreateResponse:
        """Creates a new authentication flow for an application.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          methods: Authentication methods in this flow

          name: Name of the authentication flow

          custom_fields: Custom fields for this authentication flow

          description: Description of the authentication flow

          is_recommended: Whether this is the recommended authentication flow

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        return self._post(
            f"/v1/applications/{application_id}/auth-flows",
            body=maybe_transform(
                {
                    "methods": methods,
                    "name": name,
                    "custom_fields": custom_fields,
                    "description": description,
                    "is_recommended": is_recommended,
                },
                auth_flow_create_params.AuthFlowCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthFlowCreateResponse,
        )

    def update(
        self,
        auth_flow_id: str,
        *,
        application_id: str,
        custom_fields: Iterable[auth_flow_update_params.CustomField] | Omit = omit,
        description: str | Omit = omit,
        is_recommended: bool | Omit = omit,
        methods: List[Literal["username_password", "authenticator", "custom"]] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthFlowUpdateResponse:
        """Updates an existing authentication flow.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          custom_fields: Custom fields for this authentication flow

          description: Description of the authentication flow

          is_recommended: Whether this is the recommended authentication flow

          methods: Authentication methods in this flow

          name: Name of the authentication flow

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        if not auth_flow_id:
            raise ValueError(f"Expected a non-empty value for `auth_flow_id` but received {auth_flow_id!r}")
        return self._patch(
            f"/v1/applications/{application_id}/auth-flows/{auth_flow_id}",
            body=maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "is_recommended": is_recommended,
                    "methods": methods,
                    "name": name,
                },
                auth_flow_update_params.AuthFlowUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthFlowUpdateResponse,
        )

    def list(
        self,
        application_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthFlowListResponse:
        """
        Retrieves all authentication flows for a specific application.

        **Beta** Capability. [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        return self._get(
            f"/v1/applications/{application_id}/auth-flows",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthFlowListResponse,
        )

    def delete(
        self,
        auth_flow_id: str,
        *,
        application_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthFlowDeleteResponse:
        """Deletes an existing authentication flow.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        if not auth_flow_id:
            raise ValueError(f"Expected a non-empty value for `auth_flow_id` but received {auth_flow_id!r}")
        return self._delete(
            f"/v1/applications/{application_id}/auth-flows/{auth_flow_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthFlowDeleteResponse,
        )


class AsyncAuthFlowsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAuthFlowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return AsyncAuthFlowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAuthFlowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return AsyncAuthFlowsResourceWithStreamingResponse(self)

    async def create(
        self,
        application_id: str,
        *,
        methods: List[Literal["username_password", "authenticator", "custom"]],
        name: str,
        custom_fields: Iterable[auth_flow_create_params.CustomField] | Omit = omit,
        description: str | Omit = omit,
        is_recommended: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthFlowCreateResponse:
        """Creates a new authentication flow for an application.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          methods: Authentication methods in this flow

          name: Name of the authentication flow

          custom_fields: Custom fields for this authentication flow

          description: Description of the authentication flow

          is_recommended: Whether this is the recommended authentication flow

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        return await self._post(
            f"/v1/applications/{application_id}/auth-flows",
            body=await async_maybe_transform(
                {
                    "methods": methods,
                    "name": name,
                    "custom_fields": custom_fields,
                    "description": description,
                    "is_recommended": is_recommended,
                },
                auth_flow_create_params.AuthFlowCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthFlowCreateResponse,
        )

    async def update(
        self,
        auth_flow_id: str,
        *,
        application_id: str,
        custom_fields: Iterable[auth_flow_update_params.CustomField] | Omit = omit,
        description: str | Omit = omit,
        is_recommended: bool | Omit = omit,
        methods: List[Literal["username_password", "authenticator", "custom"]] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthFlowUpdateResponse:
        """Updates an existing authentication flow.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          custom_fields: Custom fields for this authentication flow

          description: Description of the authentication flow

          is_recommended: Whether this is the recommended authentication flow

          methods: Authentication methods in this flow

          name: Name of the authentication flow

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        if not auth_flow_id:
            raise ValueError(f"Expected a non-empty value for `auth_flow_id` but received {auth_flow_id!r}")
        return await self._patch(
            f"/v1/applications/{application_id}/auth-flows/{auth_flow_id}",
            body=await async_maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "is_recommended": is_recommended,
                    "methods": methods,
                    "name": name,
                },
                auth_flow_update_params.AuthFlowUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthFlowUpdateResponse,
        )

    async def list(
        self,
        application_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthFlowListResponse:
        """
        Retrieves all authentication flows for a specific application.

        **Beta** Capability. [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        return await self._get(
            f"/v1/applications/{application_id}/auth-flows",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthFlowListResponse,
        )

    async def delete(
        self,
        auth_flow_id: str,
        *,
        application_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthFlowDeleteResponse:
        """Deletes an existing authentication flow.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        if not auth_flow_id:
            raise ValueError(f"Expected a non-empty value for `auth_flow_id` but received {auth_flow_id!r}")
        return await self._delete(
            f"/v1/applications/{application_id}/auth-flows/{auth_flow_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthFlowDeleteResponse,
        )


class AuthFlowsResourceWithRawResponse:
    def __init__(self, auth_flows: AuthFlowsResource) -> None:
        self._auth_flows = auth_flows

        self.create = to_raw_response_wrapper(
            auth_flows.create,
        )
        self.update = to_raw_response_wrapper(
            auth_flows.update,
        )
        self.list = to_raw_response_wrapper(
            auth_flows.list,
        )
        self.delete = to_raw_response_wrapper(
            auth_flows.delete,
        )


class AsyncAuthFlowsResourceWithRawResponse:
    def __init__(self, auth_flows: AsyncAuthFlowsResource) -> None:
        self._auth_flows = auth_flows

        self.create = async_to_raw_response_wrapper(
            auth_flows.create,
        )
        self.update = async_to_raw_response_wrapper(
            auth_flows.update,
        )
        self.list = async_to_raw_response_wrapper(
            auth_flows.list,
        )
        self.delete = async_to_raw_response_wrapper(
            auth_flows.delete,
        )


class AuthFlowsResourceWithStreamingResponse:
    def __init__(self, auth_flows: AuthFlowsResource) -> None:
        self._auth_flows = auth_flows

        self.create = to_streamed_response_wrapper(
            auth_flows.create,
        )
        self.update = to_streamed_response_wrapper(
            auth_flows.update,
        )
        self.list = to_streamed_response_wrapper(
            auth_flows.list,
        )
        self.delete = to_streamed_response_wrapper(
            auth_flows.delete,
        )


class AsyncAuthFlowsResourceWithStreamingResponse:
    def __init__(self, auth_flows: AsyncAuthFlowsResource) -> None:
        self._auth_flows = auth_flows

        self.create = async_to_streamed_response_wrapper(
            auth_flows.create,
        )
        self.update = async_to_streamed_response_wrapper(
            auth_flows.update,
        )
        self.list = async_to_streamed_response_wrapper(
            auth_flows.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            auth_flows.delete,
        )
