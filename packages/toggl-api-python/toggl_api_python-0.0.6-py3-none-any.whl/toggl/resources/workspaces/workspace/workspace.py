from __future__ import annotations
from functools import cached_property
from ...._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .time_entries import TimeEntries, AsyncTimeEntries
from .projects import Projects, AsyncProjects
from .tags import Tags, AsyncTags

class Workspace(SyncAPIResourceBase):
    def __init__(self, client, workspace_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id

    @cached_property
    def time_entries(self) -> TimeEntries:
        return TimeEntries(self._client, workspace_id=self._workspace_id)

    @cached_property
    def projects(self) -> Projects:
        return Projects(self._client, workspace_id=self._workspace_id)

    @cached_property
    def tags(self) -> Tags:
        return Tags(self._client, workspace_id=self._workspace_id)


class AsyncWorkspace(AsyncAPIResourceBase):
    def __init__(self, client, workspace_id: int):
        super().__init__(client)
        self._workspace_id = workspace_id

    @cached_property
    def time_entries(self) -> AsyncTimeEntries:
        return AsyncTimeEntries(self._client, workspace_id=self._workspace_id)

    @cached_property
    def projects(self) -> AsyncProjects:
        return AsyncProjects(self._client, workspace_id=self._workspace_id)

    @cached_property
    def tags(self) -> AsyncTags:
        return AsyncTags(self._client, workspace_id=self._workspace_id)