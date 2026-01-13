from typing import TypeAlias
from pydantic import Field
from ....._schemas import QueryBase, ApiDataModel
from ...._response_schemas import  Tag


class GetTagsQuery(QueryBase):
    page: int | None = Field(default=None, description="Page number")
    per_page: int | None = Field(default=None, description="Number of items per page")
    search: str | None = Field(default=None, description="Search by task name")

GetTagsResponse: TypeAlias = list[Tag]

class PostTagRequest(ApiDataModel):
    name: str = Field(description="Tag name")

PostTagResponse: TypeAlias = list[Tag]

