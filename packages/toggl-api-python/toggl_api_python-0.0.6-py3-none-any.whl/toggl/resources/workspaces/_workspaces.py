from ..._resource import AsyncAPIResourceBase, SyncAPIResourceBase
from .workspace import Workspace, AsyncWorkspace


class Workspaces(SyncAPIResourceBase):      
    def workspace(self, workspace_id: int) -> Workspace:
        return Workspace(self._client, workspace_id)
    
    def __getitem__(self, workspace_id: int) -> Workspace:
        return Workspace(self._client, workspace_id)


class AsyncWorkspaces(AsyncAPIResourceBase):
    def workspace(self, workspace_id: int) -> AsyncWorkspace:
        return AsyncWorkspace(self._client, workspace_id)
    
    def __getitem__(self, workspace_id: int) -> AsyncWorkspace:
        return AsyncWorkspace(self._client, workspace_id)