from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import TogglAPI, AsyncTogglAPI


class SyncAPIResourceBase:
    _client: TogglAPI
    def __init__(self, client: TogglAPI):
        self._client = client


class AsyncAPIResourceBase:
    _client: AsyncTogglAPI
    
    def __init__(self, client: AsyncTogglAPI):
        self._client = client