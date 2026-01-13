from typing import TypeAlias
from pydantic import Field
from ...._schemas import ApiDataModel

class Quota(ApiDataModel):
    organization_id: int | None = Field(default=None, description="ID of the organization for which the quota is reported. If null, represents the quota for requests that do not belong to any organization, such as the /me endpoints.")
    remaining: int = Field(description="Number of API calls remaining for the current window. Once this value reaches zero, no further requests will be accepted until the window resets. While the quota is not enforced, this value may go negative, indicating how much the user has exceeded the limit.")
    resets_in_secs: int = Field(description="Time until the window resets, in seconds. Once this value reaches zero, the window is reset and more requests will be accepted again.")
    total: int = Field(description="Total number of API calls allowed for the current window. This value depends on the organization's plan.")

GetQuotaResponse: TypeAlias = list[Quota]
