# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...types import (
    application_list_params,
    application_create_params,
    application_list_identities_params,
    application_create_identity_token_params,
)
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from .auth_flows import (
    AuthFlowsResource,
    AsyncAuthFlowsResource,
    AuthFlowsResourceWithRawResponse,
    AsyncAuthFlowsResourceWithRawResponse,
    AuthFlowsResourceWithStreamingResponse,
    AsyncAuthFlowsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.application_list_response import ApplicationListResponse
from ...types.application_create_response import ApplicationCreateResponse
from ...types.application_delete_response import ApplicationDeleteResponse
from ...types.application_retrieve_response import ApplicationRetrieveResponse
from ...types.application_list_identities_response import ApplicationListIdentitiesResponse
from ...types.application_create_identity_token_response import ApplicationCreateIdentityTokenResponse

__all__ = ["ApplicationsResource", "AsyncApplicationsResource"]


class ApplicationsResource(SyncAPIResource):
    @cached_property
    def auth_flows(self) -> AuthFlowsResource:
        return AuthFlowsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ApplicationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return ApplicationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApplicationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return ApplicationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        source: str,
        description: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationCreateResponse:
        """Creates a new application for identity management.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          source: The source URL of the application

          description: Description of the application

          name: Name of the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/applications",
            body=maybe_transform(
                {
                    "source": source,
                    "description": description,
                    "name": name,
                },
                application_create_params.ApplicationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationCreateResponse,
        )

    def retrieve(
        self,
        application_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationRetrieveResponse:
        """Retrieves details of a specific application by its ID.

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
        return self._get(
            f"/v1/applications/{application_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationRetrieveResponse,
        )

    def list(
        self,
        *,
        search: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationListResponse:
        """Retrieves all applications for the authenticated team.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          search: Search query to filter applications by name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/applications",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"search": search}, application_list_params.ApplicationListParams),
            ),
            cast_to=ApplicationListResponse,
        )

    def delete(
        self,
        application_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationDeleteResponse:
        """Deletes an existing application.

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
        return self._delete(
            f"/v1/applications/{application_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationDeleteResponse,
        )

    def create_identity_token(
        self,
        application_id: str,
        *,
        callback_url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationCreateIdentityTokenResponse:
        """Creates an identity token for a specific application.

        This token is used to
        initiate an authentication flow for linking user identities to the application.

        The callback URL must use HTTPS and is where the user will be redirected after
        authentication.

        Args:
          callback_url: The HTTPS URL where the user will be redirected after authentication. Must use
              HTTPS protocol.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        return self._post(
            f"/v1/applications/{application_id}/tokens",
            body=maybe_transform(
                {"callback_url": callback_url},
                application_create_identity_token_params.ApplicationCreateIdentityTokenParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationCreateIdentityTokenResponse,
        )

    def list_identities(
        self,
        application_id: str,
        *,
        search: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationListIdentitiesResponse:
        """
        Retrieves all identities associated with a specific application.

        **Beta** Capability. [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          search: Search query to filter identities by name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        return self._get(
            f"/v1/applications/{application_id}/identities",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"search": search}, application_list_identities_params.ApplicationListIdentitiesParams
                ),
            ),
            cast_to=ApplicationListIdentitiesResponse,
        )


class AsyncApplicationsResource(AsyncAPIResource):
    @cached_property
    def auth_flows(self) -> AsyncAuthFlowsResource:
        return AsyncAuthFlowsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncApplicationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return AsyncApplicationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApplicationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return AsyncApplicationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        source: str,
        description: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationCreateResponse:
        """Creates a new application for identity management.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          source: The source URL of the application

          description: Description of the application

          name: Name of the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/applications",
            body=await async_maybe_transform(
                {
                    "source": source,
                    "description": description,
                    "name": name,
                },
                application_create_params.ApplicationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationCreateResponse,
        )

    async def retrieve(
        self,
        application_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationRetrieveResponse:
        """Retrieves details of a specific application by its ID.

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
        return await self._get(
            f"/v1/applications/{application_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationRetrieveResponse,
        )

    async def list(
        self,
        *,
        search: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationListResponse:
        """Retrieves all applications for the authenticated team.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          search: Search query to filter applications by name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/applications",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"search": search}, application_list_params.ApplicationListParams),
            ),
            cast_to=ApplicationListResponse,
        )

    async def delete(
        self,
        application_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationDeleteResponse:
        """Deletes an existing application.

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
        return await self._delete(
            f"/v1/applications/{application_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationDeleteResponse,
        )

    async def create_identity_token(
        self,
        application_id: str,
        *,
        callback_url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationCreateIdentityTokenResponse:
        """Creates an identity token for a specific application.

        This token is used to
        initiate an authentication flow for linking user identities to the application.

        The callback URL must use HTTPS and is where the user will be redirected after
        authentication.

        Args:
          callback_url: The HTTPS URL where the user will be redirected after authentication. Must use
              HTTPS protocol.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        return await self._post(
            f"/v1/applications/{application_id}/tokens",
            body=await async_maybe_transform(
                {"callback_url": callback_url},
                application_create_identity_token_params.ApplicationCreateIdentityTokenParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationCreateIdentityTokenResponse,
        )

    async def list_identities(
        self,
        application_id: str,
        *,
        search: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationListIdentitiesResponse:
        """
        Retrieves all identities associated with a specific application.

        **Beta** Capability. [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          search: Search query to filter identities by name

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not application_id:
            raise ValueError(f"Expected a non-empty value for `application_id` but received {application_id!r}")
        return await self._get(
            f"/v1/applications/{application_id}/identities",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"search": search}, application_list_identities_params.ApplicationListIdentitiesParams
                ),
            ),
            cast_to=ApplicationListIdentitiesResponse,
        )


class ApplicationsResourceWithRawResponse:
    def __init__(self, applications: ApplicationsResource) -> None:
        self._applications = applications

        self.create = to_raw_response_wrapper(
            applications.create,
        )
        self.retrieve = to_raw_response_wrapper(
            applications.retrieve,
        )
        self.list = to_raw_response_wrapper(
            applications.list,
        )
        self.delete = to_raw_response_wrapper(
            applications.delete,
        )
        self.create_identity_token = to_raw_response_wrapper(
            applications.create_identity_token,
        )
        self.list_identities = to_raw_response_wrapper(
            applications.list_identities,
        )

    @cached_property
    def auth_flows(self) -> AuthFlowsResourceWithRawResponse:
        return AuthFlowsResourceWithRawResponse(self._applications.auth_flows)


class AsyncApplicationsResourceWithRawResponse:
    def __init__(self, applications: AsyncApplicationsResource) -> None:
        self._applications = applications

        self.create = async_to_raw_response_wrapper(
            applications.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            applications.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            applications.list,
        )
        self.delete = async_to_raw_response_wrapper(
            applications.delete,
        )
        self.create_identity_token = async_to_raw_response_wrapper(
            applications.create_identity_token,
        )
        self.list_identities = async_to_raw_response_wrapper(
            applications.list_identities,
        )

    @cached_property
    def auth_flows(self) -> AsyncAuthFlowsResourceWithRawResponse:
        return AsyncAuthFlowsResourceWithRawResponse(self._applications.auth_flows)


class ApplicationsResourceWithStreamingResponse:
    def __init__(self, applications: ApplicationsResource) -> None:
        self._applications = applications

        self.create = to_streamed_response_wrapper(
            applications.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            applications.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            applications.list,
        )
        self.delete = to_streamed_response_wrapper(
            applications.delete,
        )
        self.create_identity_token = to_streamed_response_wrapper(
            applications.create_identity_token,
        )
        self.list_identities = to_streamed_response_wrapper(
            applications.list_identities,
        )

    @cached_property
    def auth_flows(self) -> AuthFlowsResourceWithStreamingResponse:
        return AuthFlowsResourceWithStreamingResponse(self._applications.auth_flows)


class AsyncApplicationsResourceWithStreamingResponse:
    def __init__(self, applications: AsyncApplicationsResource) -> None:
        self._applications = applications

        self.create = async_to_streamed_response_wrapper(
            applications.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            applications.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            applications.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            applications.delete,
        )
        self.create_identity_token = async_to_streamed_response_wrapper(
            applications.create_identity_token,
        )
        self.list_identities = async_to_streamed_response_wrapper(
            applications.list_identities,
        )

    @cached_property
    def auth_flows(self) -> AsyncAuthFlowsResourceWithStreamingResponse:
        return AsyncAuthFlowsResourceWithStreamingResponse(self._applications.auth_flows)
