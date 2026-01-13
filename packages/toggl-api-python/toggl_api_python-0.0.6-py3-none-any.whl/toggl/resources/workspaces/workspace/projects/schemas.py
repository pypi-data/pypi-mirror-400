from typing import TypeAlias
from pydantic import Field
from ....._schemas import QueryBase
from ...._response_schemas import Project

class GetProjectsQuery(QueryBase):
    active: bool | None = Field(default=None, description="Return active or inactive project. You can pass 'both' to get both active and inactive projects.")
    since: int | None = Field(default=None, description="Retrieve projects created/modified/deleted since this date using UNIX timestamp.")
    billable: bool | None = Field(default=None, description="billable")
    user_ids: list[int] | None = Field(default=None, description="user_ids")
    client_ids: list[int] | None = Field(default=None, description="client_ids")
    group_ids: list[int] | None = Field(default=None, description="group_ids")
    project_ids: list[int] | None = Field(default=None, description="Numeric IDs of the projects")
    statuses: list[str] | None = Field(default=None, description="statuses")
    name: str = Field(description="name")
    page: int = Field(description="page")
    sort_field: str = Field(description="sort_field")
    sort_order: str = Field(description="sort_order")
    only_templates: bool = Field(description="only_templates")
    only_me: bool | None = Field(default=None, description="get only projects assigned to the current user")
    per_page: int | None = Field(default=None, description="Number of items per page, default 151. Cannot exceed 200.")
    sort_pinned: bool = Field(description="Place pinned projects at top of response")
    search: str | None = Field(default=None, description="search")

GetProjectsResponse: TypeAlias = list[Project]

