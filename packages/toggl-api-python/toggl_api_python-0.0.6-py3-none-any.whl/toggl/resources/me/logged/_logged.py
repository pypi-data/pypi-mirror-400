from __future__ import annotations
from typing import TYPE_CHECKING
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase

if TYPE_CHECKING:
    from ...._client import SyncAPIClient, AsyncAPIClient


class Logged(SyncAPIResourceBase):
    def get(self) -> None:
        return self._client.get(path="me/logged", options={"params": {}})


class AsyncLogged(AsyncAPIResourceBase):
    async def get(self) -> None:
        return await self._client.get(path="me/logged", options={"params": {}})

