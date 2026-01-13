from pydantic import Field
from typing import Any, TypeAlias
from ...._schemas import QueryBase, ApiDataModel


class GetClientsQuery(QueryBase):
    since: int | None = Field(default=None, description="Retrieve clients modified since this UNIX timestamp.")


class Client(ApiDataModel):
    archived: bool = Field(description="IsArchived is true if the client is archived")
    at: str = Field(description="When was the last update")
    creator_id: int = Field(description="CreatorID is the ID of the user who created the client")
    external_reference: str = Field(description="ExternalReference can be used to store an external reference to the Track Client entity.")
    id: int = Field(description="Client ID")
    integration_ext_id: str = Field(description="The external ID of the linked entity in the external system (e.g. JIRA/SalesForce)")
    integration_ext_type: str = Field(description="The external type of the linked entity in the external system (e.g. JIRA/SalesForce)")
    integration_provider: Any = Field(description="The provider (e.g. JIRA/SalesForce) that has an entity linked to this Toggl Track entity")
    name: str = Field(description="Name of the client")
    notes: str = Field(description="-")
    permissions: list[str] = Field(description="Array of string")
    total_count: int = Field(description="Total field to store the total count")
    wid: int = Field(description="Workspace ID")

GetClientsResponse: TypeAlias = list[Client]