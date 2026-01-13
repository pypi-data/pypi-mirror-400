from typing import TypeAlias
from pydantic import Field
from ....._schemas import QueryBase
from ...._request_schemas import TimeEntryRequest
from ...._response_schemas import TimeEntry

    
PostTimeEntryRequest: TypeAlias = TimeEntryRequest

PostTimeEntryResponse: TypeAlias = TimeEntry

class PostTimeEntryQuery(QueryBase):
    meta: bool | None = Field(default=None)