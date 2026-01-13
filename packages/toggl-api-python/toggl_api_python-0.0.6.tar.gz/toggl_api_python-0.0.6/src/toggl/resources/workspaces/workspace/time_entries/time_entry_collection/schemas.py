from pydantic import BaseModel, Field
from typing import Any, Literal
from ......_schemas import ApiDataModel, ApiDataModel
from ..schemas import PostTimeEntryQuery


class PatchTimeEntry(BaseModel):
    op: Literal["add", "remove", "replace"]
    path: str = Field(description="The path to the entity to patch (e.g. /description)")
    value: Any = Field(description="The new value for the entity in path.")
    
type PatchTimeEntriesRequest = list[PatchTimeEntry]

class PatchTimeEntriesFailure(BaseModel):
    id: int = Field(description="The ID for which the patch operation failed.")
    message: str = Field(description="The operation failure reason.")


class PatchTimeEntriesResponse(ApiDataModel):
    failure: list[PatchTimeEntriesFailure]
    success: list[int] = Field(description="The IDs for which the patch was succesful.")

PatchTimeEntryQuery = PostTimeEntryQuery

class GetTimeEntriesQuery(BaseModel):
    since: int | None = Field(description="Get entries modified since this date using UNIX timestamp, including deleted ones.", default=None)
    before: str | None = Field(description="Get entries with start time, before given date (YYYY-MM-DD) or with time in RFC3339 format.", default=None)
    start_date: str | None = Field(description="Get entries with start time, from start_date YYYY-MM-DD or with time in RFC3339 format. To be used with end_date.", default=None)
    end_date: str | None = Field(description="Get entries with start time, until end_date YYYY-MM-DD or with time in RFC3339 format. To be used with start_date.", default=None)
    meta: bool | None = Field(description="Should the response contain data for meta entities", default=None)
    include_sharing: bool | None = Field(description="Include sharing details in the response", default=None)