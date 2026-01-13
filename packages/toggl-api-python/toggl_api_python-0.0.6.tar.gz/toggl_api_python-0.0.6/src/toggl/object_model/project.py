from datetime import datetime
from pydantic import Field, field_serializer
from ._object_model_base import ObjectModel

class Project(ObjectModel):
    active: bool = Field(description="Whether the project is active or archived")
    name: str = Field(description="Project Name")
    description: str | None = Field(default=None)
    end_date: datetime
    is_private: bool = Field(description="Whether the project is private")
    workspace_id: int = Field(description="Workspace ID")
    start_date: datetime
