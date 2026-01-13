from __future__ import annotations
from typing import TYPE_CHECKING
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetOrganizationResponse

if TYPE_CHECKING:
    from ...._client import TogglAPI, AsyncTogglAPI
    

class Organization(SyncAPIResourceBase):
    def __init__(self, client: TogglAPI, organization_id: int):
        super().__init__(client)
        self._organization_id = organization_id

    def get(self) -> GetOrganizationResponse:
        return self._client.get(
            path=f"organizations/{self._organization_id}",
            options={"params": {}},
            ResponseT=GetOrganizationResponse,
        )

class AsyncOrganization(AsyncAPIResourceBase):
    def __init__(self, client: AsyncTogglAPI, organization_id: int):
        super().__init__(client)
        self._organization_id = organization_id

    async def get(self) -> GetOrganizationResponse:
        return await self._client.get(
            path=f"organizations/{self._organization_id}",
            options={"params": {}},
            ResponseT=GetOrganizationResponse,
        )