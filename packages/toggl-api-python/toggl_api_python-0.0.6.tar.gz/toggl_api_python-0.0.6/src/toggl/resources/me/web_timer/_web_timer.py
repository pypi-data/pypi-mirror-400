from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetWebTimerResponse

class WebTimer(SyncAPIResourceBase):
    def get(self) -> GetWebTimerResponse:
        return self._client.get(path="me/web-timer", options={"params": {}}, ResponseT=GetWebTimerResponse)


class AsyncWebTimer(AsyncAPIResourceBase):
    async def get(self) -> GetWebTimerResponse:
        return await self._client.get(path="me/web-timer", options={"params": {}}, ResponseT=GetWebTimerResponse)

