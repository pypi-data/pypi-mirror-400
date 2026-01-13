from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetFeaturesResponse


class Features(SyncAPIResourceBase):
    def get(self) -> GetFeaturesResponse:
        return self._client.get(path="me/features", options={"params": {}}, ResponseT=GetFeaturesResponse)


class AsyncFeatures(AsyncAPIResourceBase):
    async def get(self) -> GetFeaturesResponse:
        return await self._client.get(path="me/features", options={"params": {}}, ResponseT=GetFeaturesResponse)

