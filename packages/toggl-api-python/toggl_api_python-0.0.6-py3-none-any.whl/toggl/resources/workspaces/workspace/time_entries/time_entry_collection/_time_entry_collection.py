from __future__ import annotations
from ......_resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import PatchTimeEntriesResponse, PatchTimeEntryQuery, PatchTimeEntriesRequest


class TimeEntryCollection(SyncAPIResourceBase):
    def __init__(self, client, workspace_id: int, time_entry_ids: list[int]):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._time_entry_ids = time_entry_ids
        joined_ids = ",".join(str(i) for i in time_entry_ids)
        self._path = f"workspaces/{workspace_id}/time_entries/{joined_ids}"

    def patch(self, query_params: PatchTimeEntryQuery, data: PatchTimeEntriesRequest) -> PatchTimeEntriesResponse:
        return self._client.patch(path=self._path, options={"params": query_params.model_dump(), "body": [item.model_dump() for item in data]}, ResponseT=PatchTimeEntriesResponse)

class AsyncTimeEntryCollection(AsyncAPIResourceBase):
    def __init__(self, client, workspace_id: int, time_entry_ids: list[int]):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._time_entry_ids = time_entry_ids
        joined_ids = ",".join(str(i) for i in time_entry_ids)
        self._path = f"workspaces/{workspace_id}/time_entries/{joined_ids}"

    async def patch(self, query_params: PatchTimeEntryQuery, data: PatchTimeEntriesRequest) -> PatchTimeEntriesResponse:
        return await self._client.patch(path=self._path, options={"params": query_params.model_dump(), "body": [item.model_dump() for item in data]}, ResponseT=PatchTimeEntriesResponse)