from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetProjectsResponse

class Projects(SyncAPIResourceBase):
    def get(self) -> GetProjectsResponse:
        return self._client.get(
            path="me/projects",
            options={"params": {}},
            ResponseT=GetProjectsResponse,
        )


class AsyncProjects(AsyncAPIResourceBase):
    async def get(self) -> GetProjectsResponse:
        return await self._client.get(
            path="me/projects",
            options={"params": {}},
            ResponseT=GetProjectsResponse,
        )

