from typing import Any
from datetime import datetime
from pydantic import Field
from .._schemas import ApiDataModel, ResourceBase


class TrialInfo(ApiDataModel):
    can_have_trial: bool = Field(description="CanHaveInitialTrial is true if neither the organization nor the owner has never had a trial before")
    last_pricing_plan_id: int | None = Field(default=None)
    next_payment_date: str | None = Field(default=None)
    trial: bool = Field(description="Whether the organization's subscription is currently on trial")
    trial_available: bool = Field(description="When a trial is available for this organization Deprecated: TrialAvailable - use CanHaveInitialTrial instead. Retained for front-end compatibility.")
    trial_end_date: str | None = Field(default=None)
    trial_plan_id: int | None = Field(default=None)


class Organization(ResourceBase):
    admin: bool = Field(description="Whether the requester is an admin of the organization")
    created_at: str = Field(description="Organization's creation date")
    is_multi_workspace_enabled: bool = Field(description="Is true when the organization option is_multi_workspace_enabled is set")
    is_unified: bool
    max_data_retention_days: Any | None = Field(default=None, description="How far back free workspaces in this org can access data.")
    max_workspaces: int = Field(description="Maximum number of workspaces allowed for the organization")
    name: str = Field(description="Organization Name")
    owner: bool = Field(description="Whether the requester is a the owner of the organization")
    permissions: list[str] | None = Field(default=None, description="Array of string")
    pricing_plan_enterprise: bool = Field(description="The subscription plan is an enterprise plan")
    pricing_plan_id: int = Field(description="Organization plan ID")
    pricing_plan_name: str = Field(description="The subscription plan name the org is currently on. Free or any plan name coming from payment provider")
    suspended_at: str | None = Field(default=None, description="Whether the organization is currently suspended")
    trial_info: TrialInfo | None = Field(default=None, description="Trial information")
    user_count: int = Field(description="Number of organization users")

class RecurringParameter(ApiDataModel):
    custom_period: int | None = Field(default=None, description="Custom period, used when 'period' field is 'custom'")
    estimated_seconds: int | None = Field(default=None, description="Estimated seconds")
    parameter_end_date: str | None = Field(default=None)
    parameter_start_date: str | None = Field(default=None, description="Recurring start date")
    period: str | None = Field(default=None, description="Period")
    project_start_date: str | None = Field(default=None, description="Project start date")

class Project(ResourceBase):
    active: bool
    actual_hours: int | None = Field(default=None)
    actual_seconds: int | None = Field(default=None)
    auto_estimates: bool | None = Field(default=None)
    billable: bool | None = Field(default=None)
    can_track_time: bool | None = Field(default=None)
    cid: int | None = Field(default=None)
    client_id: int | None = Field(default=None)
    client_name: str | None = Field(default=None)
    color: str | None = Field(default=None)
    created_at: str
    currency: str | None = Field(default=None)
    current_period: Any | None = Field(default=None) # TODO: define current_period model
    end_date: str | None = Field(default=None)
    estimated_hours: int | None = Field(default=None)
    estimated_seconds: int | None = Field(default=None)
    external_reference: str | None = Field(default=None)
    fixed_fee: int | None = Field(default=None)
    integration_ext_id: str | None = Field(default=None)
    integration_ext_type: str | None = Field(default=None)
    integration_provider: str | None = Field(default=None)
    is_private: bool
    name: str
    permissions: list[str] | None = Field(default=None)
    pinned: bool | None = Field(default=None)
    rate: int = Field(description="Hourly rate")
    rate_last_updated: str | None = Field(default=None)
    recurring: bool | None = Field(default=None, description="Whether the project is recurring, premium feature")
    recurring_parameters: list[RecurringParameter] | None = Field(default=None, description="Project recurring parameters, premium feature")
    start_date: str | None = Field(default=None, description="Start date")
    status: str | None = Field(default=None, description="Status of the project (upcoming, active, ended, archived, deleted)")
    template: bool | None = Field(default=None)
    template_id: int | None = Field(default=None)
    total_count: int | None = Field(default=None, description="Total number of projects found")
    wid: int | None = Field(default=None, description="Workspace ID legacy field")
    workspace_id: int | None = Field(default=None, description="Workspace ID")


class Workspace(ResourceBase):
    admin: bool | None = Field(default=None) # Deprecated
    api_token: str | None = Field(default=None) # deprecated
    business_ws: bool # Workspace on Premium subscription
    csv_upload: Any # CSV upload data
    default_currency: str # Default currency, premium feature, optional, only for existing WS, will be 'USD' initially
    default_hourly_rate: int | None = Field(default=None) # The default hourly rate, premium feature, optional, only for existing WS, will be 0.0 initially
    disable_approvals: bool # Disable approvals in the workspace
    disable_expenses: bool # Disable expenses in the workspace
    disable_timesheet_view: bool # Disable timesheet view in the workspace
    hide_start_end_times: bool # -
    ical_enabled: bool # Calendar integration enabled
    ical_url: str # URL of calendars
    last_modified: str # Last modification of data in the workspace
    limit_public_project_data: bool # Limit public projects data in reports to admins.
    logo_url: str # URL of workspace logo
    max_data_retention_days: Any | None = Field(default=None) # How far back free workspaces can access data.
    name: str # Name of the workspace
    only_admins_may_create_projects: bool # Only admins will be able to create projects, optional, only for existing WS, will be false initially
    only_admins_may_create_tags: bool # Only admins will be able to create tags, optional, only for existing WS, will be false initially
    only_admins_see_team_dashboard: bool # Only admins will be able to see the team dashboard, optional, only for existing WS, will be false initially
    organization_id: int # Identifier of the organization
    permissions: list[str] | None = Field(default=None) # Permissions list
    premium: bool # Workspace on Starter subscription
    projects_billable_by_default: bool # New projects billable by default
    projects_enforce_billable: bool # Whether tracking time to projects will enforce billable setting to be respected.
    projects_private_by_default: bool # Workspace setting for default project visbility.
    rate_last_updated: str | None = Field(default=None) # Timestamp of last workspace rate update
    reports_collapse: bool | None = Field(default=None) # Whether reports should be collapsed by default, optional, only for existing WS, will be true initially
    role: str | None = Field(default=None) # Role of the current user in the workspace
    rounding: int | None = Field(default=None) # Default rounding, premium feature, optional, only for existing WS. 0 - nearest, 1 - round up, -1 - round down
    rounding_minutes: int | None = Field(default=None) # Default rounding in minutes, premium feature, optional, only for existing WS
    subscription: Any | None = Field(default=None) # deprecated
    suspended_at: str | None = Field(default=None) # Timestamp of suspension
    te_constraints: Any | None = Field(default=None) # Time entry constraints setting
    working_hours_in_minutes: int | None = Field(default=None) # Working hours in minutes


class Task(ResourceBase):
    active: bool = Field(description="False when the task has been done")
    avatar_url: str | None = Field(default=None, description="Avatar URL")
    client_id: int | None = Field(default=None, description="Client ID")
    client_name: str | None = Field(default=None, description="Client name")
    estimated_seconds: int | None = Field(default=None, description="Estimated seconds")
    external_reference: str | None = Field(default=None, description="ExternalReference can be used to store an external reference to the Track Task Entity.")
    integration_ext_id: str | None = Field(default=None, description="The external ID of the linked entity in the external system (e.g. JIRA/SalesForce)")
    integration_ext_type: str | None = Field(default=None, description="The external type of the linked entity in the external system (e.g. JIRA/SalesForce)")
    integration_provider: Any | None = Field(default=None, description="The provider (e.g. JIRA/SalesForce) that has an entity linked to this Toggl Track entity")
    name: str = Field(description="Task Name")
    permissions: list[str] | None = Field(default=None, description="Array of string")
    project_billable: bool | None = Field(default=None, description="-")
    project_color: str | None = Field(default=None, description="Metadata")
    project_id: int | None = Field(default=None, description="Project ID")
    project_is_private: bool | None = Field(default=None, description="null")
    project_name: str | None = Field(default=None, description="-")
    rate: float | None = Field(default=None, description="Rate for this task")
    rate_last_updated: str | None = Field(default=None, description="null")
    recurring: bool | None = Field(default=None, description="Whether this is a recurring task")
    toggl_accounts_id: str | None = Field(default=None, description="null")
    tracked_seconds: int | None = Field(default=None, description="The value tracked_seconds is in milliseconds, not in seconds.")
    user_id: int | None = Field(default=None, description="null")
    user_name: str | None = Field(default=None, description="null")
    workspace_id: int | None = Field(default=None, description="Workspace ID")

class SharedWith(ApiDataModel):
    accepted: bool
    user_id: int
    user_name: str | None = Field(default=None)


class Tag(ResourceBase):
    creator_id: int = Field(description="CreatorID the user who created the tag")
    deleted_at: str | None = Field(description="When was deleted", default=None)
    integration_ext_id: str | None = Field(description="The external ID of the linked entity in the external system (e.g. JIRA/SalesForce)", default=None)
    integration_ext_type: str | None = Field(description="The external type of the linked entity in the external system (e.g. JIRA/SalesForce)", default=None)
    integration_provider: str | None = Field(description="The provider (e.g. JIRA/SalesForce) that has an entity linked to this Toggl Track entity", default=None)
    name: str = Field(description="Tag name")
    permissions: list[str] | None = Field(description="Array of string", default=None)
    workspace_id: int = Field(description="Workspace ID")

    
class TimeEntry(ResourceBase):
    billable: bool = Field(description="Whether the time entry is billable")
    client_name: str | None = Field(default=None, description="Related entities meta fields - if requested")
    description: str | None = Field(default=None)
    duration: int = Field(description="Time entry duration. For running entries should be negative, preferable -1")
    duronly: bool = Field(description="Used to create a TE with a duration but without a stop time, this field is deprecated for GET endpoints where the value will always be true.")
    expense_ids: list[int] | None = Field(default=None, description="Work expenses")
    permissions: list[str] | None = Field(default=None, description="Permission list")
    pid: int | None = Field(default=None, description="Project ID, legacy field")
    project_active: bool | None = Field(default=None)
    project_billable: bool | None = Field(default=None)
    project_color: str | None = Field(default=None)
    project_id: int | None = Field(default=None)
    project_name: str | None = Field(default=None)
    shared_with: list[SharedWith] | None = Field(default=None, description="Indicates who the time entry has been shared with")
    start: datetime = Field(description="Start time as a timezone-aware datetime.")
    stop: str | None = Field(default=None, descriptio="Stop time in UTC, can be null if it's still running or created with 'duration' and 'duronly' fields")
    tag_ids: list[int] = Field(description="Tag IDs, null if tags were not provided or were later deleted")
    tags: list[str] | None = Field(default=None, description="Tag names, null if tags were not provided or were later deleted")
    task_id: int | None = Field(default=None)
    task_name: str | None = Field(default=None)
    tid: int | None = Field(default=None)
    uid: int | None = Field(default=None)
    user_avatar_url: str | None = Field(default=None)
    user_id: int | None = Field(default=None)
    user_name: str | None = Field(default=None)
    wid: int | None = Field(default=None)
    workspace_id: int