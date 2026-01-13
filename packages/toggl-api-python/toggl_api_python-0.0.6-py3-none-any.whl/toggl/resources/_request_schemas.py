from typing import Any, Literal
from datetime import datetime
from pydantic import Field, field_serializer
from .._schemas import ApiDataModel

class EventMetadata(ApiDataModel):
    origin_feature: str | None = Field(default=None, description="Origin feature")
    visible_goals_count: int | None = Field(default=None, description="Visible goals count")
    
class TimeEntryRequest(ApiDataModel):
    billable: bool | None = Field(default=None, description="Whether the time entry is marked as billable, optional, default false")
    created_with: str = Field(description="Must be provided when creating a time entry and should identify the service/application used to create it")
    description: str | None = Field(default=None, description="Time entry description, optional")
    duration : int | None = Field(default=None, description="Time entry duration. For running entries should be negative, preferable -1")
    duronly: bool | None = Field(default=None, description="Deprecated: Used to create a time entry with a duration but without a stop time. This parameter can be ignored.")
    event_metadata: EventMetadata | None = Field(default=None, description="Event metadata")
    expense_ids: list[int] | None = Field(default=None, description="Work Expenses associated with the Time Entry")
    pid: int | None = Field(default=None, description="Project ID, legacy field")
    project_id: int | None = Field(default=None, description="Project ID, optional")
    shared_with_user_ids: list[int] | None = Field(default=None, description="List of user IDs to share this time entry with")
    start: datetime | str = Field(description="Start time in UTC, required for creation. Format: 2006-01-02T15:04:05Z")
    start_date: str | None = Field(default=None, description="If provided during creation, the date part will take precedence over the date part of 'start'. Format: 2006-11-07")
    stop: datetime | str | None = Field(default=None, description="Stop time in UTC, can be omitted if it's still running or created with 'duration'. If 'stop' and 'duration' are provided, values must be consistent (start + duration == stop)")
    tag_action: Literal["add", "delete"] | None = Field(default=None, description="Can be 'add' or 'delete'. Used when updating an existing time entry")
    tag_ids: list[int] = Field(default=[], description="IDs of tags to add/remove")
    tags: list[str] | None = Field(default=None, description="Names of tags to add/remove. If name does not exist as tag, one will be created automatically")
    task_id: int | None = Field(default=None, description="Task ID, optional")
    tid: int | None = Field(default=None, description="Task ID, legacy field")
    uid: int | None = Field(default=None, description="Time Entry creator ID, legacy field")
    user_id: int | None = Field(default=None, description="Time Entry creator ID, if omitted will use the requester user ID")
    wid: int | None = Field(default=None, description="Workspace ID, legacy field")
    workspace_id: int | None = Field(default=None, description="Workspace ID, required")
    
    @field_serializer("start", "stop")
    def serialize_datetime(self, dt: datetime) -> str:
        return ApiDataModel.parse_tz_aware_datetime_to_iso_string(dt)