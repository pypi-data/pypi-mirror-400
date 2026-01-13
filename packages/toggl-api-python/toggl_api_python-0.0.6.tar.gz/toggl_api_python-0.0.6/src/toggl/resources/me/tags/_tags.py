from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetMyTagsQuery, GetMyTagsResponse

class Tags(SyncAPIResourceBase):
    def get(self, query: GetMyTagsQuery) -> GetMyTagsResponse:
        return self._client.get(path="me/tags", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetMyTagsResponse)

class AsyncTags(AsyncAPIResourceBase):
    async def get(self, query: GetMyTagsQuery) -> GetMyTagsResponse:
        return await self._client.get(path="me/tags", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetMyTagsResponse)