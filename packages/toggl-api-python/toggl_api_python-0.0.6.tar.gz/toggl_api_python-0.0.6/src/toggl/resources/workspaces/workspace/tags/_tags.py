from __future__ import annotations
from typing import TYPE_CHECKING
from ....._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetTagsQuery, GetTagsResponse, PostTagRequest, PostTagResponse
from .tag import Tag, AsyncTag

if TYPE_CHECKING:
    from ....._client import TogglAPI, AsyncTogglAPI

class Tags(SyncAPIResourceBase):
    def __init__(self, client: TogglAPI, workspace_id: int):
        super().__init__(client)
        self.workspace_id = workspace_id
    
    def get(self, query: GetTagsQuery) -> GetTagsResponse:
        return self._client.get(f"workspaces/{self.workspace_id}/tags", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetTagsResponse)
    
    def post(self, request: PostTagRequest) -> PostTagResponse:
        return self._client.post(f"workspaces/{self.workspace_id}/tags", options={"params": {}, "body": request.model_dump(exclude_none=True)}, ResponseT=PostTagResponse)
    
    def __getitem__(self, tag_id: int) -> Tag:
        return Tag(self._client, workspace_id=self.workspace_id, tag_id=tag_id)

class AsyncTags(AsyncAPIResourceBase):
    def __init__(self, client: AsyncTogglAPI, workspace_id: int):
        super().__init__(client)
        self.workspace_id = workspace_id
    
    async def get(self, query: GetTagsQuery) -> GetTagsResponse:
        return await self._client.get(f"workspaces/{self.workspace_id}/tags", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetTagsResponse)
    
    async def post(self, request: PostTagRequest) -> PostTagResponse:
        return await self._client.post(f"workspaces/{self.workspace_id}/tags", options={"params": {}, "body": request.model_dump(exclude_none=True)}, ResponseT=PostTagResponse)
    
    def __getitem__(self, tag_id: int) -> AsyncTag:
        return AsyncTag(self._client, workspace_id=self.workspace_id, tag_id=tag_id)