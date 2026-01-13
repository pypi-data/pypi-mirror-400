from __future__ import annotations
from typing import TYPE_CHECKING
from ......._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetTasksQuery, GetTasksResponse, PostTaskRequest, PostTaskResponse

if TYPE_CHECKING:
    from ......._client import SyncAPIClient, AsyncAPIClient

class Tasks(SyncAPIResourceBase):
    def __init__(self, client: SyncAPIClient, workspace_id: int, project_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._project_id = project_id

    def get(self, query: GetTasksQuery) -> GetTasksResponse:
        return self._client.get(f"workspaces/{self._workspace_id}/projects/{self._project_id}/tasks", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetTasksResponse)
    
    def post(self, data: PostTaskRequest) -> PostTaskResponse:
        return self._client.post(f"workspaces/{self._workspace_id}/projects/{self._project_id}/tasks", options={"params": {}, "body": data.model_dump(exclude_none=True)}, ResponseT=PostTaskResponse)

class AsyncTasks(AsyncAPIResourceBase):
    def __init__(self, client: AsyncAPIClient, workspace_id: int, project_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._project_id = project_id

    async def get(self, query: GetTasksQuery) -> GetTasksResponse:
        return await self._client.get(f"workspaces/{self._workspace_id}/projects/{self._project_id}/tasks", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetTasksResponse)
    
    async def post(self, data: PostTaskRequest) -> PostTaskResponse:
        return await self._client.post(f"workspaces/{self._workspace_id}/projects/{self._project_id}/tasks", options={"params": {}, "body": data.model_dump(exclude_none=True)}, ResponseT=PostTaskResponse)