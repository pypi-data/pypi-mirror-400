from typing import TypeAlias
from pydantic import Field
from ..._response_schemas import Tag
from ...._schemas import QueryBase

class GetMyTagsQuery(QueryBase):
    since: int | None = Field(default=None, description="Retrieve tags modified/deleted since this date using UNIX timestamp.")

GetMyTagsResponse: TypeAlias = list[Tag]