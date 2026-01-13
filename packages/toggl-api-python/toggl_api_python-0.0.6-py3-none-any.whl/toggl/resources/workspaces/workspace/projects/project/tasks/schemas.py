from pydantic import Field
from typing import TypeAlias
from ......._schemas import QueryBase, ApiDataModel
from ......_response_schemas import Task

class GetTasksQuery(QueryBase):
    active: bool | None = Field(default=None, description="Return only active tasks. If true, returns only active tasks. If false or omitted, returns all tasks.")

GetTasksResponse: TypeAlias = list[Task]

class PostTaskRequest(ApiDataModel):
    active: bool | None = Field(description="Use false to mark the task as done", default=True)
    estimated_seconds: int | None = Field(description="Task estimation in seconds", default=None)
    external_reference: str | None = Field(description="Task external reference", default=None)
    name: str = Field(description="Name")
    user_id: int | None = Field(description="Creator ID, if omitted, will use requester user ID", default=None)

PostTaskResponse: TypeAlias = Task