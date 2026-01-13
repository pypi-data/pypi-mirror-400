from __future__ import annotations
from functools import cached_property
from ......_resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .stop import Stop, AsyncStop
from .schemas import PutTimeEntryQuery, PutTimeEntryRequest, PutTimeEntryResponse

class TimeEntry(SyncAPIResourceBase):
    def __init__(self, client, workspace_id: int, time_entry_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._time_entry_id = time_entry_id

    def _path(self) -> str:
        return f"workspaces/{self._workspace_id}/time_entries/{self._time_entry_id}"

    @cached_property
    def stop(self) -> Stop:
        return Stop(self._client, workspace_id=self._workspace_id, time_entry_id=self._time_entry_id)

    def put(self, query: PutTimeEntryQuery, data: PutTimeEntryRequest) -> PutTimeEntryResponse:
        return self._client.put(f"{self._path()}", options={"params": query.model_dump(exclude_none=True), "body": data.model_dump(exclude_none=True)}, ResponseT=PutTimeEntryResponse)
    
    
class AsyncTimeEntry(AsyncAPIResourceBase):
    def __init__(self, client, workspace_id: int, time_entry_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._time_entry_id = time_entry_id

    def _path(self) -> str:
        return f"workspaces/{self._workspace_id}/time_entries/{self._time_entry_id}"

    @cached_property
    def stop(self) -> AsyncStop:
        return AsyncStop(self._client, workspace_id=self._workspace_id, time_entry_id=self._time_entry_id)
    
    async def put(self, query: PutTimeEntryQuery, data: PutTimeEntryRequest) -> PutTimeEntryResponse:
        return await self._client.put(f"{self._path()}", options={"params": query.model_dump(exclude_none=True), "body": data.model_dump(exclude_none=True)}, ResponseT=PutTimeEntryResponse)