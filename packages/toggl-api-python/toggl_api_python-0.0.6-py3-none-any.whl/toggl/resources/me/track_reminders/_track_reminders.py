from __future__ import annotations
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetTrackRemindersResponse


class TrackReminders(SyncAPIResourceBase):
    def get(self) -> GetTrackRemindersResponse:
        return self._client.get(path="me/track_reminders", options={"params": {}}, ResponseT=GetTrackRemindersResponse)


class AsyncTrackReminders(AsyncAPIResourceBase):
    async def get(self) -> GetTrackRemindersResponse:
        return await self._client.get(path="me/track_reminders", options={"params": {}}, ResponseT=GetTrackRemindersResponse)

