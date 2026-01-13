from typing import TypeAlias
from pydantic import Field
from ......_schemas import QueryBase
from ....._response_schemas import TimeEntry
from ....._request_schemas import TimeEntryRequest

class PutTimeEntryQuery(QueryBase):
    meta: bool | None = Field(description="Should the response contain data for meta entities", default=False)
    include_sharing: bool | None = Field(description="Should the response contain time entry sharing details", default=False)

PutTimeEntryRequest: TypeAlias = TimeEntryRequest
PutTimeEntryResponse: TypeAlias = TimeEntry

