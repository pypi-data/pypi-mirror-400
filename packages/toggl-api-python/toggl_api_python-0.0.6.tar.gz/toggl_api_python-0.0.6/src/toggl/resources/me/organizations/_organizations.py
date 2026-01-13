from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetOrganizationsResponse

class Organizations(SyncAPIResourceBase):
    def get(self) -> GetOrganizationsResponse:
        return self._client.get(
            path="me/organizations",
            options={"params": {}},
            ResponseT=GetOrganizationsResponse,
        )


class AsyncOrganizations(AsyncAPIResourceBase):
    async def get(self) -> GetOrganizationsResponse:
        return await self._client.get(
            path="me/organizations",
            options={"params": {}},
            ResponseT=GetOrganizationsResponse,
        )

