from __future__ import annotations
from typing import TYPE_CHECKING
from ....._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetCurrentResponse

if TYPE_CHECKING:
    from ....._client import SyncAPIClient, AsyncAPIClient

class Current(SyncAPIResourceBase):
    def get(self) -> GetCurrentResponse:
        return self._client.get(path="me/time_entries/current", options={"params": {}}, ResponseT=GetCurrentResponse)

class AsyncCurrent(AsyncAPIResourceBase):
    async def get(self) -> GetCurrentResponse:
        return await self._client.get(path="me/time_entries/current", options={"params": {}}, ResponseT=GetCurrentResponse)