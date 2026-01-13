from __future__ import annotations
from ......._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import PatchStopResponse


class Stop(SyncAPIResourceBase):
    def __init__(self, client, workspace_id: int, time_entry_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._time_entry_id = time_entry_id

    def _path(self) -> str:
        return f"workspaces/{self._workspace_id}/time_entries/{self._time_entry_id}"

    def patch(self) -> PatchStopResponse:
        return self._client.patch(path=f"{self._path()}/stop", options={"params": {}}, ResponseT=PatchStopResponse)


class AsyncStop(AsyncAPIResourceBase):
    def __init__(self, client, workspace_id: int, time_entry_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._time_entry_id = time_entry_id

    def _path(self) -> str:
        return f"workspaces/{self._workspace_id}/time_entries/{self._time_entry_id}"

    async def patch(self) -> PatchStopResponse:
        return await self._client.patch(path=f"{self._path()}/stop", options={"params": {}, "body": {}}, ResponseT=PatchStopResponse)