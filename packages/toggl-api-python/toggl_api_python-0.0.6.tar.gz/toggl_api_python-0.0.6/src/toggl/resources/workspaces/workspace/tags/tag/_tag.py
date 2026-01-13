from __future__ import annotations
from typing import TYPE_CHECKING
from ......_resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import PutTagRequest, PutTagResponse

if TYPE_CHECKING:
    from ......_client import TogglAPI, AsyncTogglAPI

class Tag(SyncAPIResourceBase):
    def __init__(self, client: TogglAPI, workspace_id: int, tag_id: int):
        super().__init__(client)
        self.workspace_id = workspace_id
        self.tag_id = tag_id

    def put(self, request: PutTagRequest) -> PutTagResponse:
        return self._client.put(f"workspaces/{self.workspace_id}/tags/{self.tag_id}", options={"params": {}, "body": request.model_dump(exclude_none=True)}, ResponseT=PutTagResponse)
    
    def delete(self) -> None:
        return self._client.delete(f"workspaces/{self.workspace_id}/tags/{self.tag_id}", options={"params": {}}, ResponseT=None)

class AsyncTag(AsyncAPIResourceBase):
    def __init__(self, client: AsyncTogglAPI, workspace_id: int, tag_id: int):
        super().__init__(client)
        self.workspace_id = workspace_id
        self.tag_id = tag_id

    async def put(self, request: PutTagRequest) -> PutTagResponse:
        return await self._client.put(f"workspaces/{self.workspace_id}/tags/{self.tag_id}", options={"params": {}, "body": request.model_dump(exclude_none=True)}, ResponseT=PutTagResponse)
    
    async def delete(self) -> None:
        return await self._client.delete(f"workspaces/{self.workspace_id}/tags/{self.tag_id}", options={"params": {}}, ResponseT=None)