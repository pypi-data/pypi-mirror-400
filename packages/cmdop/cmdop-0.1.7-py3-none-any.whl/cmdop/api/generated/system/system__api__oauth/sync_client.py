from __future__ import annotations

import httpx

from .models import *


class SyncSystemOauthAPI:
    """Synchronous API endpoints for Oauth."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def system_oauth_authorize_create(self, data: DeviceAuthorizeRequest) -> DeviceAuthorizeResponse:
        """
        Authorize device

        User approves or denies device code in browser (requires
        authentication).
        """
        url = "/api/system/oauth/authorize/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return DeviceAuthorizeResponse.model_validate(response.json())


    def system_oauth_device_create(self, data: DeviceCodeRequestRequest) -> DeviceCodeResponse:
        """
        Request device code

        CLI initiates OAuth flow by requesting a device code and user code.
        """
        url = "/api/system/oauth/device/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return DeviceCodeResponse.model_validate(response.json())


    def system_oauth_revoke_create(self, data: TokenRevokeRequest) -> None:
        """
        Revoke token

        Revoke access token or refresh token.
        """
        url = "/api/system/oauth/revoke/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()


    def system_oauth_token_create(self, data: TokenRequestRequest) -> TokenResponse:
        """
        Request access token

        CLI polls for token (device flow) or refreshes expired token.
        """
        url = "/api/system/oauth/token/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return TokenResponse.model_validate(response.json())


    def system_oauth_token_info_retrieve(self) -> TokenInfo:
        """
        Get token info

        Get information about current access token (requires authentication).
        """
        url = "/api/system/oauth/token/info/"
        response = self._client.get(url)
        response.raise_for_status()
        return TokenInfo.model_validate(response.json())


    def system_oauth_tokens_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedTokenListList]:
        """
        List user tokens

        List all CLI tokens for authenticated user.
        """
        url = "/api/system/oauth/tokens/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedTokenListList.model_validate(response.json())


