from ....._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetTimeEntryQuery, GetTimeEntryResponse

class TimeEntry(SyncAPIResourceBase):
    def __init__(self, client, time_entry_id: int):
        super().__init__(client)
        self._time_entry_id = time_entry_id

    def get(self, query: GetTimeEntryQuery) -> GetTimeEntryResponse:
        return self._client.get(path=f"me/time_entries/{self._time_entry_id}", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetTimeEntryResponse)

class AsyncTimeEntry(AsyncAPIResourceBase):
    def __init__(self, client, time_entry_id: int):
        super().__init__(client)
        self._time_entry_id = time_entry_id

    async def get(self, query: GetTimeEntryQuery) -> GetTimeEntryResponse:
        return await self._client.get(path=f"me/time_entries/{self._time_entry_id}", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetTimeEntryResponse)