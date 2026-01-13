from pydantic import ConfigDict
from ...._schemas import ApiDataModel


class GetWebTimerResponse(ApiDataModel):
    # The web timer payload contains various fields; allow passthrough.
    model_config = ConfigDict(extra="allow")

