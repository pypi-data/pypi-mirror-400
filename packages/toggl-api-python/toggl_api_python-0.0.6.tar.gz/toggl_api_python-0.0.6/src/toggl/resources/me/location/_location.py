from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetLocationResponse

class Location(SyncAPIResourceBase):
    def get(self) -> GetLocationResponse:
        return self._client.get(path="me/location", options={"params": {}}, ResponseT=GetLocationResponse)


class AsyncLocation(AsyncAPIResourceBase):
    async def get(self) -> GetLocationResponse:
        return await self._client.get(path="me/location", options={"params": {}}, ResponseT=GetLocationResponse)

