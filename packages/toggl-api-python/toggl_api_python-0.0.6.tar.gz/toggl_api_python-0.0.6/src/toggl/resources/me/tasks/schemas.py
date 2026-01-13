from pydantic import Field
from typing import TypeAlias
from ...._schemas import QueryBase
from ..._response_schemas import Task

class GetMyTasksQuery(QueryBase):
    meta: bool | None = Field(default=None, description="Should the response contain data for meta entities")
    since: int | None = Field(default=None, description="Get tasks modified since this UNIX timestamp.")
    include_not_active: bool | None = Field(default=None, description="Include tasks marked as done.")
    offset: int | None = Field(default=None, description="Offset to resume the next pagination from.")
    per_page: int | None = Field(default=None, description="Number of items per page, default is all.")

GetMyTasksResponse: TypeAlias = list[Task]