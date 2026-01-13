from pydantic import ConfigDict
from typing import TypeAlias
from ...._schemas import ApiDataModel

class Feature(ApiDataModel):
    enabled: bool
    feature_id: str
    name: str
    
class WorkspaceFeatures(ApiDataModel):
    features: list[Feature]
    workspace_id: int

GetFeaturesResponse: TypeAlias = list[WorkspaceFeatures]