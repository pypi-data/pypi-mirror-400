from .clients._clients import Clients, AsyncClients
from .workspaces import Workspaces, AsyncWorkspaces
from .projects import Projects, AsyncProjects
from .tasks import Tasks, AsyncTasks
from .organizations import Organizations, AsyncOrganizations
from .web_timer import WebTimer, AsyncWebTimer
from .features import Features, AsyncFeatures
from .location import Location, AsyncLocation
from .logged import Logged, AsyncLogged
from .projects import Projects, AsyncProjects
from .quota import Quota, AsyncQuota
from .track_reminders import TrackReminders, AsyncTrackReminders
from functools import cached_property
from ..._resource import SyncAPIResourceBase, AsyncAPIResourceBase
from .schemas import GetMeResponse, PutMeResponse, PutMeRequest, GetMeQuery
from .time_entries._time_entries import TimeEntries, AsyncTimeEntries
from .preferences import Preferences, AsyncPreferences, AsyncPreferences

class Me(SyncAPIResourceBase):
    @cached_property
    def clients(self) -> Clients:
        return Clients(self._client)
    
    @cached_property
    def workspaces(self) -> Workspaces:
        return Workspaces(self._client)
    
    @cached_property
    def projects(self) -> Projects:
        return Projects(self._client)
    
    @cached_property
    def tasks(self) -> Tasks:
        return Tasks(self._client)
    
    @cached_property
    def organizations(self) -> Organizations:
        return Organizations(self._client)
    
    @cached_property
    def web_timer(self) -> WebTimer:
        return WebTimer(self._client)
    
    @cached_property
    def features(self) -> Features:
        return Features(self._client)
    
    @cached_property
    def location(self) -> Location:
        return Location(self._client)
    
    @cached_property
    def logged(self) -> Logged:
        return Logged(self._client)
    
    @cached_property
    def quota(self) -> Quota:
        return Quota(self._client)
    
    @cached_property
    def track_reminders(self) -> TrackReminders:
        return TrackReminders(self._client)
    
    @cached_property
    def time_entries(self) -> TimeEntries:
        return TimeEntries(self._client)
    
    @cached_property
    def preferences(self) -> Preferences:
        return Preferences(self._client)
    
    def get(self, query: GetMeQuery) -> GetMeResponse:
        return self._client.get(path="me", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetMeResponse)
    
    def put(self, data: PutMeRequest):
        return self._client.put(path="me", options={"body": data.model_dump(exclude_none=True)}, ResponseT=PutMeResponse)

class AsyncMe(AsyncAPIResourceBase):
    @cached_property
    def clients(self) -> AsyncClients:
        return AsyncClients(self._client)
    
    @cached_property
    def workspaces(self) -> AsyncWorkspaces:
        return AsyncWorkspaces(self._client)

    @cached_property
    def projects(self) -> AsyncProjects:
        return AsyncProjects(self._client)

    @cached_property
    def tasks(self) -> AsyncTasks:
        return AsyncTasks(self._client)

    @cached_property
    def organizations(self) -> AsyncOrganizations:
        return AsyncOrganizations(self._client)

    @cached_property
    def web_timer(self) -> AsyncWebTimer:
        return AsyncWebTimer(self._client)
    
    @cached_property
    def features(self) -> AsyncFeatures:
        return AsyncFeatures(self._client)
    
    @cached_property
    def location(self) -> AsyncLocation:
        return AsyncLocation(self._client)
    
    @cached_property
    def logged(self) -> AsyncLogged:
        return AsyncLogged(self._client)
    
    @cached_property
    def quota(self) -> AsyncQuota:
        return AsyncQuota(self._client)
    
    @cached_property
    def track_reminders(self) -> AsyncTrackReminders:
        return AsyncTrackReminders(self._client)
    
    @cached_property
    def preferences(self) -> AsyncPreferences:
        return AsyncPreferences(self._client)
    
    @cached_property
    def time_entries(self) -> AsyncTimeEntries:
        return AsyncTimeEntries(self._client)

    async def get(self, query: GetMeQuery) -> GetMeResponse:
        return await self._client.get(path="me", options={"params": query.model_dump(exclude_none=True)}, ResponseT=GetMeResponse)
    
    async def put(self, data: PutMeRequest):
        return await self._client.put(path="me", options={"body": data.model_dump(exclude_none=True)}, ResponseT=PutMeResponse)