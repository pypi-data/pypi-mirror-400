from __future__ import annotations

import httpx

from .models import *


class SyncMachinesMachinesAPI:
    """Synchronous API endpoints for Machines."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def logs_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedMachineLogList]:
        """
        ViewSet for MachineLog operations. Read-only except for creation. Logs
        are created by agents.
        """
        url = "/api/machines/logs/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedMachineLogList.model_validate(response.json())


    def logs_create(self, data: MachineLogRequest) -> MachineLog:
        """
        ViewSet for MachineLog operations. Read-only except for creation. Logs
        are created by agents.
        """
        url = "/api/machines/logs/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return MachineLog.model_validate(response.json())


    def logs_retrieve(self, id: str) -> MachineLog:
        """
        ViewSet for MachineLog operations. Read-only except for creation. Logs
        are created by agents.
        """
        url = f"/api/machines/logs/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return MachineLog.model_validate(response.json())


    def machines_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedMachineList]:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = "/api/machines/machines/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedMachineList.model_validate(response.json())


    def machines_create(self, data: MachineCreateRequest) -> MachineCreate:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = "/api/machines/machines/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return MachineCreate.model_validate(response.json())


    def machines_retrieve(self, id: str) -> Machine:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = f"/api/machines/machines/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Machine.model_validate(response.json())


    def machines_update(self, id: str, data: MachineRequest) -> Machine:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = f"/api/machines/machines/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Machine.model_validate(response.json())


    def machines_partial_update(self, id: str, data: PatchedMachineRequest | None = None) -> Machine:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = f"/api/machines/machines/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Machine.model_validate(response.json())


    def machines_destroy(self, id: str) -> None:
        """
        ViewSet for Machine operations. Provides CRUD operations for remote
        machines with monitoring capabilities.
        """
        url = f"/api/machines/machines/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def machines_logs_list(self, id: str, level: str | None = None, limit: int | None = None, page: int | None = None, page_size: int | None = None) -> list[PaginatedMachineLogList]:
        """
        Get machine logs

        Get logs for this machine.
        """
        url = f"/api/machines/machines/{id}/logs/"
        response = self._client.get(url, params={"level": level if level is not None else None, "limit": limit if limit is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedMachineLogList.model_validate(response.json())


    def machines_regenerate_token_create(self, id: str, data: MachineRequest) -> None:
        """
        Regenerate agent token

        Regenerate machine agent token.
        """
        url = f"/api/machines/machines/{id}/regenerate-token/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()


    def machines_stats_retrieve(self, id: str) -> None:
        """
        Get machine statistics

        Get machine statistics.
        """
        url = f"/api/machines/machines/{id}/stats/"
        response = self._client.get(url)
        response.raise_for_status()


    def machines_update_metrics_create(self, id: str, data: MachinesMachinesUpdateMetricsCreateRequest) -> Machine:
        """
        Update machine metrics

        Update machine metrics (called by agent).
        """
        url = f"/api/machines/machines/{id}/update-metrics/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Machine.model_validate(response.json())


