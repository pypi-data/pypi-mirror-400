from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetClientsQuery, GetClientsResponse

class Clients(SyncAPIResourceBase):
    def get(self, query: GetClientsQuery | None = None) -> GetClientsResponse:
        query_params = query.model_dump(exclude_none=True) if query else {}
        return self._client.get(
            path="me/clients",
            options={"params": query_params},
            ResponseT=GetClientsResponse,
        )


class AsyncClients(AsyncAPIResourceBase):
    async def get(self, query: GetClientsQuery | None = None) -> GetClientsResponse:
        query_params = query.model_dump(exclude_none=True) if query else {}
        return await self._client.get(
            path="me/clients",
            options={"params": query_params},
            ResponseT=GetClientsResponse,
        )