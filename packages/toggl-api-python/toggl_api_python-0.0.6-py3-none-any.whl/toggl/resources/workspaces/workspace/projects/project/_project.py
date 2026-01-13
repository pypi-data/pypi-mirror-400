from __future__ import annotations
from functools import cached_property
from typing import TYPE_CHECKING
from ......_resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .tasks import Tasks, AsyncTasks

if TYPE_CHECKING:
    from ......_client import SyncAPIClient, AsyncAPIClient

class Project(SyncAPIResourceBase):
    def __init__(self, client: SyncAPIClient, workspace_id: int, project_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._project_id = project_id

    @cached_property
    def tasks(self) -> Tasks:
        return Tasks(self._client, self._workspace_id, self._project_id)

class AsyncProject(AsyncAPIResourceBase):
    def __init__(self, client: AsyncAPIClient, workspace_id: int, project_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id
        self._project_id = project_id

    @cached_property
    def tasks(self) -> AsyncTasks:
        return AsyncTasks(self._client, self._workspace_id, self._project_id)