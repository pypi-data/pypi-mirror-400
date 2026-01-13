from pydantic import Field
from ....._schemas import QueryBase
from ...._response_schemas import Project
from typing import TypeAlias

class GetPaginatedQuery(QueryBase):
    start_project_id: int | None = Field(default=None, description="Project ID to resume the next pagination from.")
    since: int | None = Field(default=None, description="Retrieve projects created/modified/deleted since this date using UNIX timestamp.")
    per_page: int | None = Field(default=None, description="Number of items per page, default 201.")

GetPaginatedResponse : TypeAlias = list[Project]