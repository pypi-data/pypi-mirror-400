from ...._schemas import ApiDataModel
from pydantic import Field
from typing import Any, TypeAlias

class AlphaFeatures(ApiDataModel):
    alpha_feature_id: int | None = Field(description="Feature ID", default=None)
    code: str = Field(description="Feature code")
    deleted_at: str | None = Field(description="Time of deletion, omitted if empty", default=None)
    description: str | None = Field(description="Feature description, omitted if empty", default=None)
    enabled: bool = Field(description="Whether the feature is enabled")
    product_id: int | None = Field(description="Product ID for which this Feature belong", default=None)

class DefaultProjectTask(ApiDataModel):
    project_id: int = Field(description="Project ID")
    task_id: int | None = Field(description="Task ID", default=None)
    workspace_id: int = Field(description="Workspace ID")

class MacOSAutoTrackingRules(ApiDataModel):
    id: str
    keyword: str
    project_id: int
    task_id: int
    workspace_id: int

class MacOSShowHideTogglKeyboardShortcut(ApiDataModel):
    key: int
    modifiers: int
    
class MacOSStopContinueKeyboardShortcut(ApiDataModel):
    key: int
    modifiers: int

class PomodoroBreakProject(ApiDataModel):
    id: int
    workspace_id: int


class PomodoroBreakTag(ApiDataModel):
    id: int
    workspace_id: int

class WindowsAutoTrackingRules(ApiDataModel):
    billable: bool
    description: str
    enabled: bool
    id: str
    parameters: object
    project_id: int
    skip_when_timer_is_running: bool
    start_without_confirmation: bool
    tag_ids: list[int]
    task_id: int
    type: int
    workspace_id: int

class Parameters(ApiDataModel):
    duration: str
    keyword: str
    keyword_mode: str
    time_of_day: str
    week_days: str

class WindowsShowHideTogglKeyboardShortcut(ApiDataModel):
    key: int
    modifiers: int
    
class WindowsStopContinueKeyboardShortcut(ApiDataModel):
    key: int
    modifiers: int

class WindowsStopStartKeyboardShortcut(ApiDataModel):
    key: int
    modifiers: int

class WorkoutDefaultProject(ApiDataModel):
    id: int
    workspace_id: int


class WorkoutDefaultTag(ApiDataModel):
    id: int
    workspace_id: int


class Preferences(ApiDataModel):
    activity_timeline_display_activity: bool | None = Field(default=None)
    activity_timeline_grouping_interval: str | None = Field(default=None)
    activity_timeline_grouping_method: str | None = Field(default=None)
    activity_timeline_recording_level: str | None = Field(default=None)
    activity_timeline_sync_events: bool | None = Field(default=None)
    alpha_features: list[AlphaFeatures] | None = Field(default=None)
    analyticsAdvancedFilters: bool | None = Field(default=None)
    auto_tracker_delay_enabled: bool | None = Field(default=None)
    auto_tracker_delay_in_seconds: int | None = Field(default=None)
    auto_tracker_stop_on_no_rule_match_enabled: bool | None = Field(default=None)
    automatic_tagging: bool | None = Field(default=None)
    autotracking_enabled: bool | None = Field(default=None)
    beginningOfWeek: int | None = Field(default=None)
    calendar_snap_duration: str | None = Field(default=None)
    calendar_snap_initial_location: str | None = Field(default=None)
    calendar_visible_hours_end: int | None = Field(default=None)
    calendar_visible_hours_start: int | None = Field(default=None)
    calendar_zoom_level: str | None = Field(default=None)
    cell_swipe_actions_enabled: bool | None = Field(default=None)
    charts_view_type: str | None = Field(default=None)
    collapseDetailedReportEntries: bool | None = Field(default=None)
    collapseTimeEntries: bool | None = Field(default=None)
    dashboards_view_type: str | None = Field(default=None)
    date_format: str | None = Field(default=None)
    decimal_separator: object | None = Field(default=None)
    default_project_id: int | None = Field(default=None)
    default_project_task: DefaultProjectTask | None = Field(default=None)
    default_task_id: int | None = Field(default=None)
    displayDensity: str | None = Field(default=None)
    distinctRates: str | None = Field(default=None)
    duration_format: str | None = Field(default=None)
    duration_format_on_timer_duration_field: bool | None = Field(default=None)
    edit_popup_integration_timer: bool | None = Field(default=None)
    extension_send_error_reports: bool | None = Field(default=None)
    extension_send_usage_statistics: bool | None = Field(default=None)
    firstSeenBusinessPromo: int | None = Field(default=None)
    focus_app_on_time_entry_started: bool | None = Field(default=None)
    focus_app_on_time_entry_stopped: bool | None = Field(default=None)
    haptic_feedback_enabled: bool | None = Field(default=None)
    hide_keyboard_shortcut: bool | None = Field(default=None)
    hide_sidebar_right: bool | None = Field(default=None)
    idle_detection_enabled: bool | None = Field(default=None)
    idle_detection_interval_in_minutes: int | None = Field(default=None)
    inactivity_behavior: str | None = Field(default=None)
    ios_is_goals_view_shown: bool | None = Field(default=None)
    is_goals_view_expanded: bool | None = Field(default=None)
    is_goals_view_shown: bool | None = Field(default=None)
    is_summary_total_view_visible: bool | None = Field(default=None)
    keep_mini_timer_on_top: bool | None = Field(default=None)
    keep_window_on_top: bool | None = Field(default=None)
    keyboard_increment_timer_page: int | None = Field(default=None)
    keyboard_shortcuts_enabled: bool | None = Field(description="Will be omitted if empty", default=None)
    keyboard_shortcuts_share_time_entries: bool | None = Field(default=None)
    mac_is_goals_view_shown: bool | None = Field(default=None)
    macos_auto_tracking_rules: list[MacOSAutoTrackingRules] | None = Field(default=None)
    macos_show_hide_toggl_keyboard_shortcut: MacOSShowHideTogglKeyboardShortcut | None = Field(default=None)
    macos_stop_continue_keyboard_shortcut: MacOSStopContinueKeyboardShortcut | None = Field(default=None)
    manualEntryMode: str | None = Field(description="Will be omitted if empty", default=None)
    manualMode: bool | None = Field(description="Will be omitted if empty", default=None)
    manualModeOverlaySeen: bool | None = Field(description="Will be omitted if empty", default=None)
    modify_on_start_time_change: str | None = Field(description="Will be omitted if empty", default=None)
    offlineMode: str | None = Field(description="Will be omitted if empty", default=None)
    pg_time_zone_name: str | None = Field(description="Will be omitted if empty", default=None)
    pomodoro_auto_start_break: bool | None = Field(default=None)
    pomodoro_auto_start_focus: bool | None = Field(default=None)
    pomodoro_break_interval_in_minutes: int | None = Field(default=None)
    pomodoro_break_project: PomodoroBreakProject | None = Field(default=None)
    pomodoro_break_project_id: int | None = Field(default=None)
    pomodoro_break_start_sound_enabled: bool | None = Field(default=None)
    pomodoro_break_tag: PomodoroBreakTag | None = Field(default=None)
    pomodoro_break_tag_id: int | None = Field(default=None)
    pomodoro_countdown_timer: bool | None = Field(default=None)
    pomodoro_enabled: bool | None = Field(default=None)
    pomodoro_focus_interval_in_minutes: int | None = Field(default=None)
    pomodoro_focus_sound: str | None = Field(default=None)
    pomodoro_global_sound_enabled: bool | None = Field(default=None)
    pomodoro_interval_end_sound: bool | None = Field(default=None)
    pomodoro_interval_end_volume: int | None = Field(default=None)
    pomodoro_longer_break_duration_in_minutes: int | None = Field(default=None)
    pomodoro_prevent_screen_lock: bool | None = Field(default=None)
    pomodoro_rounds_before_longer_break: int | None = Field(default=None)
    pomodoro_session_start_sound_enabled: bool | None = Field(default=None)
    pomodoro_show_notifications: bool | None = Field(default=None)
    pomodoro_stop_timer_at_interval_end: bool | None = Field(default=None)
    pomodoro_track_breaks_as_time_entries: bool | None = Field(default=None)
    projectDashboardActivityMode: str | None = Field(description="Will be omitted if empty", default=None)
    project_shortcut_enabled: bool | None = Field(default=None)
    record_timeline: bool | None = Field(default=None)
    remember_last_project: str | None = Field(default=None)
    reminder_days: str | None = Field(default=None)
    reminder_enabled: bool | None = Field(default=None)
    reminder_interval_in_minutes: int | None = Field(default=None)
    reminder_period: str | None = Field(default=None)
    reminder_snoozing_in_minutes: int | None = Field(default=None)
    reportRounding: bool | None = Field(description="Will be omitted if empty", default=None)
    reportRoundingDirection: str | None = Field(description="Will be omitted if empty", default=None)
    reportRoundingStepInMinutes: int | None = Field(description="Will be omitted if empty", default=None)
    reportsHideWeekends: bool | None = Field(description="Will be omitted if empty", default=None)
    run_app_on_startup: bool | None = Field(default=None)
    running_entry_warning: str | None = Field(default=None)
    running_timer_notification_enabled: bool | None = Field(default=None)
    seenFollowModal: bool | None = Field(description="Will be omitted if empty", default=None)
    seenFooterPopup: bool | None = Field(description="Will be omitted if empty", default=None)
    seenProjectDashboardOverlay: bool | None = Field(description="Will be omitted if empty", default=None)
    seenTogglButtonModal: bool | None = Field(description="Will be omitted if empty", default=None)
    send_added_to_project_notification: bool | None = Field(default=None)
    send_daily_project_invites: bool | None = Field(default=None)
    send_product_emails: bool | None = Field(default=None)
    send_product_release_notification: bool | None = Field(default=None)
    send_system_message_notification: bool | None = Field(default=None)
    send_timer_notifications: bool | None = Field(default=None)
    send_weekly_report: bool | None = Field(default=None)
    sharing_shortcut_enabled: bool | None = Field(default=None)
    showTimeInTitle: bool | None = Field(description="Will be omitted if empty", default=None)
    show_all_entries: bool | None = Field(default=None)
    show_changelog: bool | None = Field(default=None)
    show_description_in_menu_bar: bool | None = Field(default=None)
    show_dock_icon: bool | None = Field(default=None)
    show_events_in_calendar: bool | None = Field(default=None)
    show_project_in_menu_bar: bool | None = Field(default=None)
    show_qr_scanner: bool | None = Field(default=None)
    show_seconds_in_menu_bar: bool | None = Field(default=None)
    show_timeline_in_day_view: bool | None = Field(description="Will be omitted if empty", default=None)
    show_timer_in_menu_bar: bool | None = Field(default=None)
    show_today_total_in_menu_bar: bool | None = Field(default=None)
    show_total_billable_hours: bool | None = Field(description="Will be omitted if empty", default=None)
    show_weekend_on_timer_page: bool | None = Field(description="Will be omitted if empty", default=None)
    show_workouts_in_calendar: bool | None = Field(default=None)
    sleep_behaviour: str | None = Field(default=None)
    smart_alerts_option: str | None = Field(default=None)
    snowballReportRounding: str | None = Field(description="Will be omitted if empty", default=None)
    stack_times_on_manual_mode_after: str | None = Field(default=None)
    start_automatically: bool | None = Field(default=None)
    start_shortcut_mode: str | None = Field(default=None)
    stop_at_specific_time: bool | None = Field(default=None)
    stop_automatically: bool | None = Field(default=None)
    stop_entry_on_shutdown: bool | None = Field(default=None)
    stop_specified_time: str | None = Field(default=None)
    stopped_timer_notification_enabled: bool | None = Field(default=None)
    suggestions_enabled: bool | None = Field(default=None)
    summaryReportAmounts: str | None = Field(description="Will be omitted if empty", default=None)
    summaryReportDistinctRates: bool | None = Field(description="Will be omitted if empty", default=None)
    summaryReportGrouping: str | None = Field(description="Will be omitted if empty", default=None)
    summaryReportSortAsc: bool | None = Field(description="Will be omitted if empty", default=None)
    summaryReportSortField: str | None = Field(description="Will be omitted if empty", default=None)
    summaryReportSubGrouping: str | None = Field(description="Will be omitted if empty", default=None)
    summary_total_mode: str | None = Field(default=None)
    tags_shortcut_enabled: bool | None = Field(default=None)
    time_entry_display_mode: str | None = Field(default=None)
    time_entry_ghost_suggestions_enabled: bool | None = Field(default=None)
    time_entry_invitations_notification_enabled: bool | None = Field(default=None)
    time_entry_start_stop_input_mode: str | None = Field(default=None)
    timeofday_format: str | None = Field(default=None)
    timerView: str | None = Field(description="Will be omitted if empty", default=None)
    timerViewMobile: str | None = Field(description="Will be omitted if empty", default=None)
    toSAcceptNeeded: bool | None = Field(description="ToSAcceptNeeded represents the trigger for new ToS accept dialog", default=None)
    use_mini_timer: bool | None = Field(default=None)
    visibleFooter: str | None = Field(description="Will be omitted if empty", default=None)
    webTimeEntryStarted: bool | None = Field(description="Will be omitted if empty", default=None)
    webTimeEntryStopped: bool | None = Field(description="Will be omitted if empty", default=None)
    weeklyReportGrouping: str | None = Field(description="Will be omitted if empty", default=None)
    weeklyReportValueToShow: str | None = Field(description="Will be omitted if empty", default=None)
    windows_auto_tracking_rules: list[WindowsAutoTrackingRules] | None = Field(default=None)
    windows_show_hide_toggl_keyboard_shortcut: WindowsShowHideTogglKeyboardShortcut | None = Field(default=None)
    windows_stop_continue_keyboard_shortcut: WindowsStopContinueKeyboardShortcut | None = Field(default=None)
    windows_stop_start_keyboard_shortcut: WindowsStopStartKeyboardShortcut | None = Field(default=None)
    windows_theme: str | None = Field(default=None)
    workout_default_project: WorkoutDefaultProject | None = Field(default=None)
    workout_default_project_id: int | None = Field(default=None)
    workout_default_tag: WorkoutDefaultTag | None = Field(default=None)
    workout_default_tag_id: int | None = Field(default=None)

GetPreferencesResponse: TypeAlias = Preferences

PostPreferencesRequest: TypeAlias = Preferences