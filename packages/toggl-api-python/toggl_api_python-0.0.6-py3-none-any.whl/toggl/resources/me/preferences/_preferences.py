from .schemas import GetPreferencesResponse, PostPreferencesRequest
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase

class Preferences(SyncAPIResourceBase):
    def get(self) -> GetPreferencesResponse:
        return self._client.get(path="me/preferences", options={"params": {}}, ResponseT=GetPreferencesResponse)
    
    def post(self, request: PostPreferencesRequest) -> None:
        return self._client.post(path="me/preferences", options={"params": {}, "body": request.model_dump(exclude_none=True)})

class AsyncPreferences(AsyncAPIResourceBase):
    async def get(self) -> GetPreferencesResponse:
        return await self._client.get(path="me/preferences", options={"params": {}}, ResponseT=GetPreferencesResponse)
    
    async def post(self, request: PostPreferencesRequest) -> None:
        return await self._client.post(path="me/preferences", options={"params": {}, "body": request.model_dump(exclude_none=True)})