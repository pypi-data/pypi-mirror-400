from __future__ import annotations
from typing import TYPE_CHECKING
from ....._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetProjectsResponse, GetProjectsQuery
from .project import Project, AsyncProject

if TYPE_CHECKING:
    from ....._client import SyncAPIClient, AsyncAPIClient


class Projects(SyncAPIResourceBase):
    def __init__(self, client, workspace_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id

    def _base_path(self) -> str:
        return f"workspaces/{self._workspace_id}"

    def get(self, query: GetProjectsQuery) -> GetProjectsResponse:
        return self._client.get(
            path=f"{self._base_path()}/projects",
            options={"params": query.model_dump(exclude_none=True)},
            ResponseT=GetProjectsResponse,
        )
    
    def __getitem__(self, project_id: int) -> Project:
        return Project(self._client, self._workspace_id, project_id)


class AsyncProjects(AsyncAPIResourceBase):
    def __init__(self, client, workspace_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id

    def _base_path(self) -> str:
        return f"workspaces/{self._workspace_id}"

    async def get(self, query: GetProjectsQuery) -> GetProjectsResponse:
        return await self._client.get(
            path=f"{self._base_path()}/projects",
            options={"params": query.model_dump(exclude_none=True)},
            ResponseT=GetProjectsResponse,
        )
    
    def __getitem__(self, project_id: int) -> AsyncProject:
        return AsyncProject(self._client, self._workspace_id, project_id)
