# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from ..types import identity_create_params, identity_update_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ..types.identity_create_response import IdentityCreateResponse
from ..types.identity_delete_response import IdentityDeleteResponse
from ..types.identity_update_response import IdentityUpdateResponse
from ..types.identity_retrieve_response import IdentityRetrieveResponse
from ..types.identity_retrieve_credentials_response import IdentityRetrieveCredentialsResponse

__all__ = ["IdentitiesResource", "AsyncIdentitiesResource"]


class IdentitiesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IdentitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return IdentitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IdentitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return IdentitiesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        credentials: Iterable[identity_create_params.Credential],
        source: str,
        validate_async: bool | Omit = omit,
        application_description: str | Omit = omit,
        application_name: str | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityCreateResponse:
        """Creates a new identity with credentials for authentication.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          credentials: Array of credentials for authentication

          source: The source URL for the identity (e.g., login page URL)

          validate_async: Whether to validate the identity asynchronously. Defaults to true.

          application_description: Optional application description

          application_name: Optional application name to associate with the identity

          metadata: Optional metadata for the identity

          name: Name of the identity. Defaults to "Unnamed Identity" if not provided.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/identities",
            body=maybe_transform(
                {
                    "credentials": credentials,
                    "source": source,
                    "application_description": application_description,
                    "application_name": application_name,
                    "metadata": metadata,
                    "name": name,
                },
                identity_create_params.IdentityCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"validate_async": validate_async}, identity_create_params.IdentityCreateParams),
            ),
            cast_to=IdentityCreateResponse,
        )

    def retrieve(
        self,
        identity_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityRetrieveResponse:
        """Retrieves details of a specific identity by its ID.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        return self._get(
            f"/v1/identities/{identity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityRetrieveResponse,
        )

    def update(
        self,
        identity_id: str,
        *,
        credentials: Iterable[identity_update_params.Credential] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityUpdateResponse:
        """
        Updates an existing identity's name, metadata, or credentials.

        **Beta** Capability. [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          credentials: Array of credentials for authentication

          metadata: Metadata for the identity

          name: Name of the identity

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        return self._put(
            f"/v1/identities/{identity_id}",
            body=maybe_transform(
                {
                    "credentials": credentials,
                    "metadata": metadata,
                    "name": name,
                },
                identity_update_params.IdentityUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityUpdateResponse,
        )

    def delete(
        self,
        identity_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityDeleteResponse:
        """Deletes an existing identity.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        return self._delete(
            f"/v1/identities/{identity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityDeleteResponse,
        )

    def retrieve_credentials(
        self,
        identity_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityRetrieveCredentialsResponse:
        """
        Retrieves the credentials for a specific identity.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        return self._get(
            f"/v1/identities/{identity_id}/credentials",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityRetrieveCredentialsResponse,
        )


class AsyncIdentitiesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIdentitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return AsyncIdentitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIdentitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return AsyncIdentitiesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        credentials: Iterable[identity_create_params.Credential],
        source: str,
        validate_async: bool | Omit = omit,
        application_description: str | Omit = omit,
        application_name: str | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityCreateResponse:
        """Creates a new identity with credentials for authentication.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          credentials: Array of credentials for authentication

          source: The source URL for the identity (e.g., login page URL)

          validate_async: Whether to validate the identity asynchronously. Defaults to true.

          application_description: Optional application description

          application_name: Optional application name to associate with the identity

          metadata: Optional metadata for the identity

          name: Name of the identity. Defaults to "Unnamed Identity" if not provided.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/identities",
            body=await async_maybe_transform(
                {
                    "credentials": credentials,
                    "source": source,
                    "application_description": application_description,
                    "application_name": application_name,
                    "metadata": metadata,
                    "name": name,
                },
                identity_create_params.IdentityCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"validate_async": validate_async}, identity_create_params.IdentityCreateParams
                ),
            ),
            cast_to=IdentityCreateResponse,
        )

    async def retrieve(
        self,
        identity_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityRetrieveResponse:
        """Retrieves details of a specific identity by its ID.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        return await self._get(
            f"/v1/identities/{identity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityRetrieveResponse,
        )

    async def update(
        self,
        identity_id: str,
        *,
        credentials: Iterable[identity_update_params.Credential] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityUpdateResponse:
        """
        Updates an existing identity's name, metadata, or credentials.

        **Beta** Capability. [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          credentials: Array of credentials for authentication

          metadata: Metadata for the identity

          name: Name of the identity

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        return await self._put(
            f"/v1/identities/{identity_id}",
            body=await async_maybe_transform(
                {
                    "credentials": credentials,
                    "metadata": metadata,
                    "name": name,
                },
                identity_update_params.IdentityUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityUpdateResponse,
        )

    async def delete(
        self,
        identity_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityDeleteResponse:
        """Deletes an existing identity.

        **Beta** Capability.

        [Contact support](mailto:support@anchorbrowser.io) to
        enable.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        return await self._delete(
            f"/v1/identities/{identity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityDeleteResponse,
        )

    async def retrieve_credentials(
        self,
        identity_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IdentityRetrieveCredentialsResponse:
        """
        Retrieves the credentials for a specific identity.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        return await self._get(
            f"/v1/identities/{identity_id}/credentials",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityRetrieveCredentialsResponse,
        )


class IdentitiesResourceWithRawResponse:
    def __init__(self, identities: IdentitiesResource) -> None:
        self._identities = identities

        self.create = to_raw_response_wrapper(
            identities.create,
        )
        self.retrieve = to_raw_response_wrapper(
            identities.retrieve,
        )
        self.update = to_raw_response_wrapper(
            identities.update,
        )
        self.delete = to_raw_response_wrapper(
            identities.delete,
        )
        self.retrieve_credentials = to_raw_response_wrapper(
            identities.retrieve_credentials,
        )


class AsyncIdentitiesResourceWithRawResponse:
    def __init__(self, identities: AsyncIdentitiesResource) -> None:
        self._identities = identities

        self.create = async_to_raw_response_wrapper(
            identities.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            identities.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            identities.update,
        )
        self.delete = async_to_raw_response_wrapper(
            identities.delete,
        )
        self.retrieve_credentials = async_to_raw_response_wrapper(
            identities.retrieve_credentials,
        )


class IdentitiesResourceWithStreamingResponse:
    def __init__(self, identities: IdentitiesResource) -> None:
        self._identities = identities

        self.create = to_streamed_response_wrapper(
            identities.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            identities.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            identities.update,
        )
        self.delete = to_streamed_response_wrapper(
            identities.delete,
        )
        self.retrieve_credentials = to_streamed_response_wrapper(
            identities.retrieve_credentials,
        )


class AsyncIdentitiesResourceWithStreamingResponse:
    def __init__(self, identities: AsyncIdentitiesResource) -> None:
        self._identities = identities

        self.create = async_to_streamed_response_wrapper(
            identities.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            identities.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            identities.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            identities.delete,
        )
        self.retrieve_credentials = async_to_streamed_response_wrapper(
            identities.retrieve_credentials,
        )
