from __future__ import annotations
from typing import Self, Any, Callable, TYPE_CHECKING, ClassVar
from pydantic import BaseModel, Field, model_validator, model_serializer, computed_field, field_serializer
from datetime import datetime, timedelta
from toggl import TogglAPI
from toggl.types import *
from toggl._schemas import ApiDataModel
from ._object_model_base import ObjectModel, queryable_property
from .find import FindMany
from .operators import Expr
from toggl.resources.schemas import TimeEntry as TimeEntryResource
from toggl.resources.me.time_entries.time_entry import TimeEntry as MeTimeEntry

if TYPE_CHECKING:
    from toggl._schemas import QueryBase, ResourceBase
class EventMetadata(BaseModel):
    origin_feature: str | None = Field(default=None)
    visible_goals_count: int | None = Field(default=None)
    
class TimeEntry(ObjectModel):
    billable: bool | None = Field(default=None)
    description: str | None = Field(default=None)
    duronly: bool | None = Field(default=None)
    expense_ids: list[int] | None = Field(default=None)
    project_id: int | None = Field(default=None)
    start: datetime = Field(description="Start time as a timezone-aware datetime.")
    stop: datetime | None = Field(default=None)
    tag_ids: list[int] = Field(default=[])
    task_id: int | None = Field(default=None)
    user_id: int | None = Field(descriptio="Time Entry creator ID, if omitted will use the requester user ID", default=None)
    workspace_id: int = Field(description="Workspace ID, required")
    
    @computed_field
    @queryable_property
    def duration(self) -> timedelta:
        if self.stop is None:
            return None
        return self.stop - self.start
    
    @duration.setter
    def duration(self, value: timedelta):
        if value is None:
            self.stop = None
        else:
            self.stop = self.start + value
    
    @computed_field
    @queryable_property
    def is_running(self) -> bool:
        return self.stop is None
    
    @classmethod
    def _get_api(cls) -> Callable[[QueryBase], ResourceBase]:
        return cls.__client__.me.time_entries.get(GetTimeEntriesQuery())
    
    def _get_by_id_api(self) -> ResourceBase:
        return self.__client__.me.time_entries[self.id].get(GetTimeEntryQuery())
    
    def _post_api(self) -> ResourceBase:
        return self.__client__.workspaces[self.workspace_id].time_entries.post(PostTimeEntryQuery(), self._to_request())
    
    def _put_api(self) -> ResourceBase:
        return self.__client__.workspaces[self.workspace_id].time_entries[self.id].put(PutTimeEntryQuery(), self._to_request())
    
    @field_serializer("duration")
    def _serialize_duration(self, v: timedelta):
        return int(v.total_seconds())
    
    @model_serializer(mode="wrap")
    def _serialize(self, handler, info):
        data = handler(self)
        if (info.context or {}).get("target") == "resource":
            data["uid"] = self.user_id
            data["wid"] = self.workspace_id
        elif (info.context or {}).get("target") == "request":
            data["created_with"] = "toggl-api-python"
        return data

    @classmethod
    def from_resource(cls: type[Self], resource: TimeEntryResource) -> Self:
        return cls.model_validate(resource)
    
    def _to_request(self):
        data = self.model_dump(context={"target": "request"})
        return TimeEntryRequest.model_validate(data)