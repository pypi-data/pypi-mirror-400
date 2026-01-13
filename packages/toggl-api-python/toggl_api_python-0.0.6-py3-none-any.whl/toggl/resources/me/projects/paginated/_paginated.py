from __future__ import annotations
from typing import TYPE_CHECKING
from ....._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetPaginatedQuery, GetPaginatedResponse

class Paginated(SyncAPIResourceBase):
    def get(self, query: GetPaginatedQuery) -> GetPaginatedResponse:
        return self._client.get(
            path="me/projects",
            options={"params": query.model_dump(exclude_none=True)},
            ResponseT=GetPaginatedResponse,
        )

class AsyncPaginated(AsyncAPIResourceBase):
    async def get(self, query: GetPaginatedQuery) -> GetPaginatedResponse:
        return await self._client.get(
            path="me/projects",
            options={"params": query.model_dump(exclude_none=True)},
            ResponseT=GetPaginatedResponse,
        )