from typing import TypeAlias
from pydantic import Field
from ....._schemas import QueryBase
from ...._response_schemas import TimeEntry

class GetTimeEntryQuery(QueryBase):
    meta: bool | None = Field(default=None, description="Should the response contain data for meta entities")
    include_sharing: bool | None = Field(default=None, description="Include sharing details in the response")

GetTimeEntryResponse: TypeAlias = TimeEntry