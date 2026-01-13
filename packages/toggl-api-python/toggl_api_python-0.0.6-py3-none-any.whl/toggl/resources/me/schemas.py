from pydantic import BaseModel, Field
from typing import Any
from .._response_schemas import Tag, TimeEntry, Workspace, Project
from ..._schemas import ApiDataModel, ApiDataModel, QueryBase, ResourceBase


class PutMeRequest(ApiDataModel):
    beginning_of_week: int | None = Field(default=None)
    country_id: int | None = Field(default=None)
    current_password: str | None = Field(default=None)
    default_workspace_id: int | None = Field(default=None)
    email: str | None = Field(default=None)
    fullname: str | None = Field(default=None)
    password: str | None = Field(default=None)
    timezone: str | None = Field(default=None)

class GetMeQuery(QueryBase):
    with_related_data: bool | None = Field(description="Retrieve user related data (clients, projects, tasks, tags, workspaces, time entries, etc.)", default=None)

class MeResponseBase(ResourceBase):
    two_fa_enabled: bool = Field(alias="2fa_enabled")
    api_token: str | None = Field(default=None)
    beginning_of_week: int
    country_id: int
    created_at: str
    default_workspace_id: int
    email: str
    fullname: str
    has_password: bool
    image_url: str
    openid_email: str | None = Field(default=None)
    openid_enabled: bool
    options: Any | None = Field(default=None) # TODO: define options model
    timezone: str
    updated_at: str

class GetMeResponse(MeResponseBase):
    authorization_updated_at: str
    clients: Any | None = Field(default=None) # TODO: define clients model
    intercom_hash: str | None = Field(default=None)
    oauth_providers: list[str] | None = Field(default=None)
    projects: list[Project] | None = Field(default=None)
    tags: list[Tag] | None = Field(default=None)
    tasks: list[Any] | None = Field(default=None) # TODO: define tasks model
    time_entries: list[TimeEntry] | None = Field(default=None)
    workspaces: list[Workspace] | None = Field(default=None)

class PutMeResponse(MeResponseBase):
    pass