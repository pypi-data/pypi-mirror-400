from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetWorkspacesQuery, GetWorkspacesResponse

class Workspaces(SyncAPIResourceBase):
    def get(self, query: GetWorkspacesQuery | None = None) -> GetWorkspacesResponse:
        query_params = query.model_dump(exclude_none=True) if query else {}
        return self._client.get(
            path="me/workspaces",
            options={"params": query_params},
            ResponseT=GetWorkspacesResponse,
        )


class AsyncWorkspaces(AsyncAPIResourceBase):
    async def get(self, query: GetWorkspacesQuery | None = None) -> GetWorkspacesResponse:
        query_params = query.model_dump(exclude_none=True) if query else {}
        return await self._client.get(
            path="me/workspaces",
            options={"params": query_params},
            ResponseT=GetWorkspacesResponse,
        )

