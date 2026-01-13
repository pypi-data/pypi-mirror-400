from __future__ import annotations
from typing import TYPE_CHECKING
from ....._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .time_entry_collection import TimeEntryCollection, AsyncTimeEntryCollection
from .time_entry import TimeEntry, AsyncTimeEntry
from .schemas import PostTimeEntryQuery, PostTimeEntryResponse, PostTimeEntryRequest

if TYPE_CHECKING:
    from ....._client import SyncAPIClient, AsyncAPIClient


class TimeEntries(SyncAPIResourceBase):
    def __init__(self, client, workspace_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id

    def _base_path(self) -> str:
        return f"workspaces/{self._workspace_id}"

    def post(self, query: PostTimeEntryQuery, data: PostTimeEntryRequest) -> PostTimeEntryResponse:
        return self._client.post(
            path=f"{self._base_path()}/time_entries",
            options={"params": query.model_dump(exclude_none=True), "body": data.model_dump(exclude_none=True)},
            ResponseT=PostTimeEntryResponse,
        )
    
    def items(self, time_entry_ids: list[int]) -> TimeEntryCollection:
        return TimeEntryCollection(self._client, workspace_id=self._workspace_id, time_entry_ids=time_entry_ids)
    
    def __getitem__(self, time_entry_id: int) -> TimeEntry:
        return TimeEntry(self._client, workspace_id=self._workspace_id, time_entry_id=time_entry_id)
    

class AsyncTimeEntries(AsyncAPIResourceBase):
    def __init__(self, client, workspace_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id

    def _base_path(self) -> str:
        return f"workspaces/{self._workspace_id}"

    async def post(self, query: PostTimeEntryQuery, data: PostTimeEntryRequest) -> PostTimeEntryResponse:
        return await self._client.post(
            path=f"{self._base_path()}/time_entries",
            options={"params": query.model_dump(exclude_none=True), "body": data.model_dump(exclude_none=True)},
            ResponseT=PostTimeEntryResponse,
        )
    
    def items(self, time_entry_ids: list[int]) -> TimeEntryCollection:
        return AsyncTimeEntryCollection(self._client, workspace_id=self._workspace_id, time_entry_ids=time_entry_ids)
    
    def __getitem__(self, time_entry_id: int) -> TimeEntry:
        return AsyncTimeEntry(self._client, workspace_id=self._workspace_id, time_entry_id=time_entry_id)