from typing import TypeAlias
from pydantic import Field
from ...._schemas import QueryBase
from ..._response_schemas import TimeEntry



class GetTimeEntriesQuery(QueryBase):
    since: int | None = Field(description="Get entries modified since this date using UNIX timestamp, including deleted ones.", default=None)
    before: str | None = Field(description="Get entries with start time, before given date (YYYY-MM-DD) or with time in RFC3339 format.", default=None)
    start_date: str | None = Field(description="Get entries with start time, from start_date YYYY-MM-DD or with time in RFC3339 format. To be used with end_date.", default=None)
    end_date: str | None = Field(description="Get entries with start time, until end_date YYYY-MM-DD or with time in RFC3339 format. To be used with start_date.", default=None)
    meta: bool | None = Field(description="Should the response contain data for meta entities", default=None)
    include_sharing: bool | None = Field(description="Include sharing details in the response", default=None)
    

GetTimeEntriesResponse: TypeAlias = list[TimeEntry]