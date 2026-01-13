from ...._schemas import ApiDataModel
from typing import TypeAlias


class TrackReminder(ApiDataModel):
    craeted_at: str
    frequency: str
    group_ids: list[int]
    reminder_id: int
    threshold: int
    user_ids: list[int]
    workspace_id: int

GetTrackRemindersResponse: TypeAlias = list[TrackReminder]
