from __future__ import annotations

import httpx

from .models import *


class SystemSystemAPI:
    """API endpoints for System."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def alerts_list(self, page: int | None = None, page_size: int | None = None, read: bool | None = None, type: str | None = None, workspace: str | None = None) -> list[PaginatedAlertList]:
        """
        List alerts with filters.
        """
        url = "/api/system/alerts/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "read": read if read is not None else None, "type": type if type is not None else None, "workspace": workspace if workspace is not None else None})
        response.raise_for_status()
        return PaginatedAlertList.model_validate(response.json())


    async def alerts_create(self, data: AlertCreateRequest) -> AlertCreate:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = "/api/system/alerts/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return AlertCreate.model_validate(response.json())


    async def alerts_retrieve(self, id: str) -> Alert:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = f"/api/system/alerts/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Alert.model_validate(response.json())


    async def alerts_update(self, id: str, data: AlertRequest) -> Alert:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = f"/api/system/alerts/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return Alert.model_validate(response.json())


    async def alerts_partial_update(self, id: str, data: PatchedAlertRequest | None = None) -> Alert:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = f"/api/system/alerts/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return Alert.model_validate(response.json())


    async def alerts_destroy(self, id: str) -> None:
        """
        ViewSet for Alert operations. System notifications for important events.
        """
        url = f"/api/system/alerts/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def alerts_mark_as_read_create(self, id: str) -> Alert:
        """
        Mark alert as read
        """
        url = f"/api/system/alerts/{id}/mark-as-read/"
        response = await self._client.post(url)
        response.raise_for_status()
        return Alert.model_validate(response.json())


    async def alerts_mark_all_as_read_create(self) -> None:
        """
        Mark all unread alerts as read for current workspace
        """
        url = "/api/system/alerts/mark-all-as-read/"
        response = await self._client.post(url)
        response.raise_for_status()
        return None


    async def api_keys_list(self, page: int | None = None, page_size: int | None = None, workspace: str | None = None) -> list[PaginatedApiKeyList]:
        """
        List API keys with filters.
        """
        url = "/api/system/api-keys/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "workspace": workspace if workspace is not None else None})
        response.raise_for_status()
        return PaginatedApiKeyList.model_validate(response.json())


    async def api_keys_create(self, data: ApiKeyCreateRequest) -> ApiKeyResponse:
        """
        Create new API key (raw key shown only once).
        """
        url = "/api/system/api-keys/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return ApiKeyResponse.model_validate(response.json())


    async def api_keys_retrieve(self, id: str) -> ApiKey:
        """
        ViewSet for ApiKey operations. Manage API keys for workspace
        integrations. Note: Raw key is only shown once during creation.
        """
        url = f"/api/system/api-keys/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return ApiKey.model_validate(response.json())


    async def api_keys_update(self, id: str) -> ApiKey:
        """
        ViewSet for ApiKey operations. Manage API keys for workspace
        integrations. Note: Raw key is only shown once during creation.
        """
        url = f"/api/system/api-keys/{id}/"
        response = await self._client.put(url)
        response.raise_for_status()
        return ApiKey.model_validate(response.json())


    async def api_keys_partial_update(self, id: str) -> ApiKey:
        """
        ViewSet for ApiKey operations. Manage API keys for workspace
        integrations. Note: Raw key is only shown once during creation.
        """
        url = f"/api/system/api-keys/{id}/"
        response = await self._client.patch(url)
        response.raise_for_status()
        return ApiKey.model_validate(response.json())


    async def api_keys_destroy(self, id: str) -> None:
        """
        ViewSet for ApiKey operations. Manage API keys for workspace
        integrations. Note: Raw key is only shown once during creation.
        """
        url = f"/api/system/api-keys/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def api_keys_regenerate_create(self, id: str) -> ApiKeyResponse:
        """
        Regenerate API key (deletes old key and creates new one)
        """
        url = f"/api/system/api-keys/{id}/regenerate/"
        response = await self._client.post(url)
        response.raise_for_status()
        return ApiKeyResponse.model_validate(response.json())


