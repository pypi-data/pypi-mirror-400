from ..._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import PostOrganizationRequest, PostOrganizationResponse
from .organization import Organization

class Organizations(SyncAPIResourceBase):
    def post(self, data: PostOrganizationRequest) -> PostOrganizationResponse:
        return self._client.post(path="organizations", options={"body": data}, ResponseT=PostOrganizationResponse)
    
    def __getitem__(self, organization_id: int):
        return Organization(self._client, organization_id)
        

class AsyncOrganizations(AsyncAPIResourceBase):
    async def post(self, data: PostOrganizationRequest) -> PostOrganizationResponse:
        return await self._client.post(path="organizations", options={"body": data}, ResponseT=PostOrganizationResponse)
    
    def __getitem__(self, organization_id: int):
        return Organization(self._client, organization_id)