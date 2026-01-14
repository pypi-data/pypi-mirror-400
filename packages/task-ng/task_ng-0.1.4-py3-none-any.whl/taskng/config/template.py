"""Configuration file template with full defaults and documentation."""


def get_default_config_template() -> str:
    """Generate a fully documented configuration template.

    Returns:
        Multi-line string containing complete TOML configuration with:
        - Section headers for organization
        - Inline comments explaining each option
        - All values commented out (user uncomments to customize)
        - Default values shown for reference
    """
    return """\
# Task-NG Configuration File
# This file contains all available configuration options with their default values.
# Uncomment and modify any setting to customize Task-NG behavior.

## =============================================================================
## Data Storage
## =============================================================================

[data]
# Location where Task-NG stores the database and state files
# Default: ~/.local/share/taskng
# location = "~/.local/share/taskng"


## =============================================================================
## Default Behavior
## =============================================================================

[default]
# Command to run when no command is given (e.g., just typing 'task-ng')
# Options: next, list, active, projects, calendar, board, etc.
# Default: next
# command = "next"

# Default project for new tasks (optional)
# Default: null (no default project)
# project = "Inbox"

# Default priority for new tasks (optional)
# Options: H (high), M (medium), L (low), or null
# Default: null (no default priority)
# priority = null


## =============================================================================
## Default Settings
## =============================================================================

[defaults]
# Default sort order for list and report commands
# Format: field+ (ascending) or field- (descending)
# Fields: urgency, priority, due, project, id, description, entry, modified
# Multiple keys: "priority-,due+"
# Default: urgency-
# sort = "urgency-"


## =============================================================================
## UI Settings
## =============================================================================

[ui]
# Enable colored output in terminal
# Default: true
# color = true

# Enable unicode symbols (✓, ⚠, etc.) in output
# Set to false for plain ASCII output
# Default: true
# unicode = true


## =============================================================================
## Editor Configuration
## =============================================================================

# Editor to use for 'task-ng edit' command
# Falls back to $VISUAL, then $EDITOR environment variables, then 'vi'
# Examples: "vim", "nano", "emacs", "code --wait"
# editor = "vim"


## =============================================================================
## Color Scheme
## =============================================================================

[color]
# Master switch for all color output
# Default: true
# enabled = true

# Color for blocked task indicator [B]
# Default: magenta
# blocked = "magenta"

# Color for annotation count indicator
# Default: cyan
# annotation = "cyan"


## -----------------------------------------------------------------------------
## Due Date Colors
## -----------------------------------------------------------------------------

[color.due]
# Color for overdue tasks
# Default: red bold
# overdue = "red bold"

# Color for tasks due today
# Default: yellow bold
# today = "yellow bold"

# Color for tasks due this week
# Default: cyan
# week = "cyan"

# Color for future tasks (due beyond this week)
# Default: green
# future = "green"


## -----------------------------------------------------------------------------
## Priority Colors
## -----------------------------------------------------------------------------

[color.priority]
# Color for high priority tasks
# Default: red bold
# H = "red bold"

# Color for medium priority tasks
# Default: yellow
# M = "yellow"

# Color for low priority tasks
# Default: blue
# L = "blue"


## -----------------------------------------------------------------------------
## Urgency Colors
## -----------------------------------------------------------------------------

[color.urgency]
# Color for high urgency tasks (urgency >= 10)
# Default: red bold
# high = "red bold"

# Color for medium urgency tasks (5 <= urgency < 10)
# Default: yellow
# medium = "yellow"

# Color for low urgency tasks (urgency < 5)
# Default: default
# low = "default"


## -----------------------------------------------------------------------------
## Table Row Colors
## -----------------------------------------------------------------------------

[color.row]
# Background color for alternating table rows
# Default: on grey11
# alternate = "on grey11"


## -----------------------------------------------------------------------------
## Calendar Colors
## -----------------------------------------------------------------------------

[color.calendar]
# Color for today's date in calendar view
# Default: black on white
# today = "black on white"


## =============================================================================
## Calendar Settings
## =============================================================================

[calendar]
# First day of the week for calendar display
# Options: monday, sunday, tuesday, wednesday, thursday, friday, saturday
# Default: monday
# weekstart = "monday"


## =============================================================================
## Urgency Calculation
## =============================================================================
## Urgency is calculated using weighted coefficients for various task attributes.
## The formula combines priority, due dates, age, tags, project, and blocking status.
## Higher values increase the importance of that factor.

[urgency]
# Weight for priority in urgency calculation
# Priority values: H=6.0, M=3.9, L=1.8 (multiplied by this coefficient)
# Default: 1.0
# priority = 1.0

# Weight for due dates (future tasks)
# Default: 0.5
# due = 0.5

# Weight multiplier for tasks due today
# Default: 1.0
# due_today = 1.0

# Weight multiplier for tasks due this week
# Default: 1.0
# due_week = 1.0

# Weight multiplier for overdue tasks
# Default: 1.0
# overdue = 1.0

# Weight for having a project assigned
# Default: 1.0
# project = 1.0

# Weight per tag (urgency increases by 0.5 * tag_count * coefficient)
# Default: 1.0
# tags = 1.0

# Multiplier when task is blocked by dependencies
# Reduces urgency by 50% (urgency * 0.5 * coefficient)
# Default: 1.0
# blocked = 1.0

# Weight for task age (older tasks get higher urgency, max 2.0 points)
# Default: 1.0
# age = 1.0


## =============================================================================
## Report Definitions
## =============================================================================
## Reports define how tasks are displayed with customizable columns, filters,
## sorting, and limits. You can override built-in reports or create new ones.
##
## To disable a built-in report, set enabled = false:
## [report.recurring]
## enabled = false  # Don't use recurring tasks, hide this report

## -----------------------------------------------------------------------------
## Built-in Report: list
## -----------------------------------------------------------------------------

# [report.list]
# description = "Default task list"
# columns = ["id", "priority", "project", "tags", "due", "description"]
# sort = ["urgency-"]
# # filter = ["status:pending"]  # Optional filter
# # limit = 100  # Optional limit


## -----------------------------------------------------------------------------
## Built-in Report: next
## -----------------------------------------------------------------------------

# [report.next]
# description = "Most urgent tasks"
# columns = ["id", "priority", "project", "tags", "due", "description"]
# sort = ["urgency-"]
# limit = 10
# # filter = ["status:pending"]


## -----------------------------------------------------------------------------
## Built-in Report: all
## -----------------------------------------------------------------------------

# [report.all]
# description = "All tasks"
# columns = ["id", "status", "priority", "project", "due", "description"]
# sort = ["status+", "urgency-"]
# # No status filter - shows all tasks


## -----------------------------------------------------------------------------
## Built-in Report: completed
## -----------------------------------------------------------------------------

# [report.completed]
# description = "Completed tasks"
# columns = ["id", "end", "project", "tags", "description"]
# sort = ["end-"]
# filter = ["status:completed"]


## -----------------------------------------------------------------------------
## Built-in Report: overdue
## -----------------------------------------------------------------------------

# [report.overdue]
# description = "Overdue tasks"
# columns = ["id", "priority", "project", "due", "description"]
# sort = ["due+"]
# filter = ["+OVERDUE"]


## -----------------------------------------------------------------------------
## Built-in Report: waiting
## -----------------------------------------------------------------------------

# [report.waiting]
# description = "Waiting tasks"
# columns = ["id", "wait", "project", "description"]
# sort = ["wait+"]
# filter = ["+WAITING"]


## -----------------------------------------------------------------------------
## Built-in Report: recurring
## -----------------------------------------------------------------------------

# [report.recurring]
# description = "Recurring tasks"
# columns = ["id", "priority", "recur", "due", "description"]
# sort = ["due+"]
# filter = ["+RECURRING"]


## -----------------------------------------------------------------------------
## Custom Reports
## -----------------------------------------------------------------------------
## Create your own reports by adding new [report.name] sections
## Available columns: id, uuid, status, priority, project, tags, due, wait,
##                   scheduled, recur, until, entry, modified, end, description
## Filter syntax: Same as command-line filters (project:Work, +urgent, priority:H, etc.)
## Set enabled = false to disable a custom report

# [report.mywork]
# description = "My work tasks"
# columns = ["id", "priority", "due", "description"]
# filter = ["project:Work", "status:pending"]
# sort = ["urgency-"]
# limit = 20
# # enabled = true  # Optional, defaults to true


## =============================================================================
## Board Definitions
## =============================================================================
## Boards provide a kanban-style view of tasks organized into columns.
## Each column can have its own filter, limit, and WIP limit.

## -----------------------------------------------------------------------------
## Built-in Board: default
## -----------------------------------------------------------------------------

# [board.default]
# description = "Task board by status"
# enabled = true
# sort = ["urgency-"]
# limit = 10  # Per-column limit
# column_width = 40
# card_fields = ["id", "priority", "description", "due"]
# # filter = []  # Global filter applied to all columns
#
# [[board.default.columns]]
# name = "Backlog"
# filter = ["status:pending", "-ACTIVE", "-BLOCKED"]
# # limit = 5  # Optional per-column limit override
# # wip_limit = 10  # Optional work-in-progress warning threshold
# # since = "7d"  # Optional time window filter
#
# [[board.default.columns]]
# name = "Blocked"
# filter = ["+BLOCKED"]
#
# [[board.default.columns]]
# name = "Active"
# filter = ["+ACTIVE"]
#
# [[board.default.columns]]
# name = "Done"
# filter = ["status:completed"]


## -----------------------------------------------------------------------------
## Built-in Board: priority
## -----------------------------------------------------------------------------

# [board.priority]
# description = "Tasks by priority"
# enabled = true
# sort = ["urgency-"]
# limit = 10
# column_width = 40
# card_fields = ["id", "description", "due", "project"]
#
# [[board.priority.columns]]
# name = "High"
# filter = ["priority:H"]
#
# [[board.priority.columns]]
# name = "Medium"
# filter = ["priority:M"]
#
# [[board.priority.columns]]
# name = "Low"
# filter = ["priority:L"]
#
# [[board.priority.columns]]
# name = "None"
# filter = ["priority.none:"]


## -----------------------------------------------------------------------------
## Custom Boards
## -----------------------------------------------------------------------------
## Create your own boards by adding new [board.name] sections

# [board.myboard]
# description = "My custom board"
# enabled = true
# sort = ["due+"]
# limit = 15
# column_width = 35
# card_fields = ["id", "description", "tags"]
# filter = ["project:Work"]  # Global filter
#
# [[board.myboard.columns]]
# name = "Todo"
# filter = ["status:pending"]
#
# [[board.myboard.columns]]
# name = "In Progress"
# filter = ["+wip"]
#
# [[board.myboard.columns]]
# name = "Review"
# filter = ["+review"]


## =============================================================================
## Context Definitions
## =============================================================================
## Contexts apply filters to all task views, allowing you to focus on specific
## subsets of tasks. Activate with: task-ng context <name>

## -----------------------------------------------------------------------------
## Example Contexts
## -----------------------------------------------------------------------------
## Uncomment and customize these examples or create your own

# [context.work]
# description = "Work tasks"
# filter = ["project:Work"]
# # OR use shorthand:
# # project = "Work"
# # tags = ["work"]  # Adds +work filter

# [context.home]
# description = "Home tasks"
# filter = ["project:Home"]

# [context.urgent]
# description = "Urgent high-priority tasks"
# filter = ["+urgent", "priority:H"]

# [context.today]
# description = "Tasks due today or overdue"
# filter = ["+OVERDUE", "+TODAY"]


## =============================================================================
## End of Configuration
## =============================================================================
"""
