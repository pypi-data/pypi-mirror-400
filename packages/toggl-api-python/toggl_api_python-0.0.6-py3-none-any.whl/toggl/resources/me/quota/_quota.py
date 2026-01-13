from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetQuotaResponse

class Quota(SyncAPIResourceBase):
    def get(self) -> GetQuotaResponse:
        return self._client.get(path="me/quota", options={"params": {}}, ResponseT=GetQuotaResponse)


class AsyncQuota(AsyncAPIResourceBase):
    async def get(self) -> GetQuotaResponse:
        return await self._client.get(path="me/quota", options={"params": {}}, ResponseT=GetQuotaResponse)

