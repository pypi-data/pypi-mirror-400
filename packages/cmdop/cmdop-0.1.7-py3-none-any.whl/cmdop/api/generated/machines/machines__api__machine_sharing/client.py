from __future__ import annotations

import httpx

from .models import *


class MachinesMachineSharingAPI:
    """API endpoints for Machine Sharing."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def machines_machines_share_create(self, id: str, data: SharedMachineCreateRequest) -> SharedMachine:
        """
        Create share link for machine

        Create a public share link for read-only terminal viewing. Only
        workspace owner or admin can create shares.
        """
        url = f"/api/machines/machines/{id}/share/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return SharedMachine.model_validate(response.json())


    async def machines_machines_shares_list(self, id: str, page: int | None = None, page_size: int | None = None) -> list[PaginatedSharedMachineListList]:
        """
        List active shares for machine

        Get all active share links for this machine
        """
        url = f"/api/machines/machines/{id}/shares/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedSharedMachineListList.model_validate(response.json())


    async def machines_machines_unshare_destroy(self, id: str) -> None:
        """
        Remove all shares for machine

        Deactivate all share links for this machine. Only workspace owner or
        admin can remove shares.
        """
        url = f"/api/machines/machines/{id}/unshare/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


