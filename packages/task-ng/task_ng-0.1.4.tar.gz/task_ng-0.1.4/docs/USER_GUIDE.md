# Task-NG User Guide

A comprehensive guide to using Task-NG, a modern Python reimagining of Taskwarrior.

- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
- [Basic Task Management](#basic-task-management)
  - [Adding Tasks](#adding-tasks)
  - [Listing Tasks](#listing-tasks)
  - [Viewing Task Details](#viewing-task-details)
  - [Modifying Tasks](#modifying-tasks)
  - [Completing Tasks](#completing-tasks)
  - [Deleting Tasks](#deleting-tasks)
  - [Bulk Operations](#bulk-operations)
- [Task Organization](#task-organization)
  - [Projects](#projects)
  - [Tags](#tags)
  - [Priorities](#priorities)
- [Scheduling & Time](#scheduling--time)
  - [Due Dates](#due-dates)
  - [Wait and Scheduled Dates](#wait-and-scheduled-dates)
  - [Recurring Tasks](#recurring-tasks)
  - [Time Tracking](#time-tracking)
- [Advanced Features](#advanced-features)
  - [Task Dependencies](#task-dependencies)
  - [Annotations](#annotations)
  - [Custom Attributes (UDAs)](#custom-attributes-udas)
  - [Filtering](#filtering)
  - [Contexts](#contexts)
- [Views & Reports](#views--reports)
  - [Reports](#reports)
  - [Statistics](#statistics)
  - [Kanban Boards](#kanban-boards)
  - [Calendar View](#calendar-view)
- [Configuration & Customization](#configuration--customization)
  - [Configuration](#configuration)
  - [Hooks](#hooks)
  - [Shell Completion](#shell-completion)
- [Import & Export](#import--export)
  - [Import from Taskwarrior](#import-from-taskwarrior)
  - [JSON Output](#json-output)
- [Synchronization](#synchronization)
  - [Overview](#sync-overview)
  - [Setting Up Sync](#setting-up-sync)
  - [Sync Commands](#sync-commands)
  - [Conflict Resolution](#conflict-resolution)
  - [Sync Configuration](#sync-configuration)
- [Reference](#reference)
  - [Command Reference](#command-reference)
  - [Tips and Best Practices](#tips-and-best-practices)
  - [Getting Help](#getting-help)


---

## Getting Started

### Installation

#### PyPI (Recommended)

```bash
pipx install task-ng
```

Or with pip:

```bash
pip install task-ng
```

#### From Source (Git)

```bash
curl -fsSL https://gitlab.com/mathias.ewald/task-ng/-/raw/main/scripts/install.sh | bash
```

Or clone and install:

```bash
git clone https://gitlab.com/mathias.ewald/task-ng.git
cd task-ng
pip install -e .
```

### Quick Start

```bash
# Add your first task
task-ng add "Learn task-ng"

# Show most urgent tasks (runs default "next" report)
task-ng

# List all pending tasks
task-ng list

# Complete a task
task-ng done 1

# View task details
task-ng show 1
```

Running `task-ng` without any subcommand executes the default command, which is the "next" report by default. This shows your most urgent pending tasks. You can [configure the default command](#default-command) to use any command or report.

---

## Basic Task Management

### Adding Tasks

#### Basic Usage

```bash
task-ng add "Task description"
```

#### With Options

```bash
# With project
task-ng add "Fix login bug" --project Work

# With priority (H=High, M=Medium, L=Low)
task-ng add "Urgent fix" --priority H

# With due date
task-ng add "Submit report" --due tomorrow

# With multiple options
task-ng add "Client meeting" --project Work --priority H --due "next friday"
```

#### Inline Tags

Add tags directly in the description using `+tagname`:

```bash
task-ng add "Review PR +urgent +code-review"
```

#### Inline Custom Attributes

Add custom attributes using `key:value` syntax:

```bash
task-ng add "Feature work client:Acme estimate:4h"
```

### Listing Tasks

#### Basic List

```bash
task-ng list
```

#### Filtered List

```bash
# By project
task-ng list project:Work

# By status
task-ng list status:pending

# By tag
task-ng list +urgent

# Exclude tag
task-ng list -waiting

# By priority
task-ng list priority:H

# By custom attribute
task-ng list client:Acme

# Multiple filters
task-ng list project:Work +urgent priority:H
```

#### Show All Tasks (Including Waiting)

```bash
task-ng list --all
```

### Viewing Task Details

```bash
task-ng show 1
```

This displays:
- Task ID and UUID
- Description
- Status
- Priority
- Project
- Tags
- Dates (created, modified, due, scheduled)
- Dependencies
- Annotations
- Custom attributes

### Modifying Tasks

#### Change Description

```bash
task-ng modify 1 --description "New description"
```

#### Change Project

```bash
task-ng modify 1 --project "NewProject"
```

#### Change Priority

```bash
task-ng modify 1 --priority M
```

#### Change Due Date

```bash
task-ng modify 1 --due "next week"
```

#### Add/Remove Tags

```bash
# Add tag
task-ng modify 1 --tag urgent

# Remove tag
task-ng modify 1 --remove-tag waiting
```

#### Add/Remove Dependencies

```bash
# Add dependency
task-ng modify 3 --depends 1

# Remove dependency
task-ng modify 3 --remove-depends 1
```

#### Set Wait Date

```bash
task-ng modify 1 --wait "next monday"
```

#### Set Scheduled Date

```bash
task-ng modify 1 --scheduled "friday 9am"
```

### Completing Tasks

#### Complete Single Task

```bash
task-ng done 1
```

#### Complete Multiple Tasks

```bash
task-ng done 1 2 3
```

#### Complete Range of Tasks

```bash
task-ng done 1-5
```

#### Note on Dependencies

Tasks with pending dependencies cannot be completed. Complete the dependencies first:

```bash
# If task 3 depends on task 1
task-ng done 3
# Error: Task 3 blocked by: 1

task-ng done 1
task-ng done 3  # Now works
```

### Deleting Tasks

#### Soft Delete (Can Be Undone)

```bash
task-ng delete 1
```

#### Delete Multiple Tasks

```bash
task-ng delete 1 2 3
```

#### Force Delete (Skip Confirmation)

```bash
task-ng delete 1 --force
```

### Bulk Operations

Perform operations on multiple tasks using filters instead of individual IDs.

#### Complete Tasks by Filter

```bash
# Complete all tasks with a tag
task-ng done +work --force

# Complete tasks in a project
task-ng done project:Work --force

# Preview without making changes
task-ng done +old --dry-run
```

#### Delete Tasks by Filter

```bash
# Delete all tasks with a tag
task-ng delete +cancelled --force

# Delete tasks in a project
task-ng delete project:Archive --force

# Preview deletion
task-ng delete +cleanup --dry-run
```

#### Modify Tasks by Filter

```bash
# Add priority to all work tasks
task-ng modify +work --priority H --force

# Change project for tagged tasks
task-ng modify +migrate --project NewProject --force

# Add tag to project tasks
task-ng modify project:Work --tag urgent --force

# Preview modifications
task-ng modify +work --priority H --dry-run
```

#### Options

- `--force` / `-f`: Skip confirmation prompt
- `--dry-run` / `-n`: Preview changes without applying them

#### Undo Last Operation

```bash
task-ng undo
```

---

## Task Organization

### Projects

Projects group related tasks together. Task-NG supports hierarchical projects using dot notation.

#### Setting Project

```bash
# When adding
task-ng add "Task" --project Work

# Hierarchical project
task-ng add "API task" --project Work.Backend.API

# When modifying
task-ng modify 1 --project Home
```

#### Listing All Projects

View all projects as a tree with task counts:

```bash
task-ng project list
```

Output shows projects in a tree structure with counts:
```
Work (2/5)
├── Backend (1/3)
│   └── API (2)
└── Frontend (0)
Home (3)
```

The counts show (direct/total) where total includes all child projects.

Use `--all` to include completed and waiting tasks in counts:

```bash
task-ng project list --all
```

**Filtering Projects**

The `project list` command supports filter expressions and respects active context:

```bash
# Show only projects with urgent tasks
task-ng project list +urgent

# Show only projects with high priority tasks
task-ng project list priority:H

# Show specific project hierarchy
task-ng project list project:Work

# Combine multiple filters
task-ng project list priority:H +urgent

# Respects active context
task-ng context set work project:Work
task-ng project list  # Only shows Work projects
```

This allows you to answer questions like "which projects have urgent tasks?" or "show me projects in my current context."

#### Renaming Projects

Rename a project and all its subprojects:

```bash
# Rename "Work" to "GitLab" (includes Work.Backend -> GitLab.Backend, etc.)
task-ng project rename Work GitLab

# Preview changes without applying
task-ng project rename Work GitLab --dry-run

# Skip confirmation prompt
task-ng project rename Work GitLab --force
```

#### Filtering by Project

Filtering by a parent project includes all children:

```bash
# Match Work, Work.Backend, Work.Backend.API, etc.
task-ng list project:Work

# Match only Work.Backend and its children
task-ng list project:Work.Backend
```

#### Clearing Project

```bash
task-ng modify 1 --project ""
```

### Tags

Tags help categorize and filter tasks.

#### Adding Tags

```bash
# Inline with description
task-ng add "Task +urgent +review"

# Via modify
task-ng modify 1 --tag urgent
```

#### Removing Tags

```bash
task-ng modify 1 --remove-tag urgent
```

#### Filtering by Tags

```bash
# Include tag
task-ng list +urgent

# Exclude tag
task-ng list -waiting

# Multiple tags
task-ng list +urgent +review
```

#### Listing All Tags

View all tags with usage counts:

```bash
# Show all tags
task-ng tags

# Include virtual tags
task-ng tags --virtual
```

Output shows tags sorted by usage count (most used first).

**Filtering Tags**

The `tags` command supports filter expressions and respects active context:

```bash
# Show tags used in Work project
task-ng tags project:Work

# Show tags used on high priority tasks
task-ng tags priority:H

# Show tags on urgent tasks (see what other tags they have)
task-ng tags +urgent

# Combine multiple filters
task-ng tags project:Work priority:H

# Respects active context
task-ng context set work project:Work
task-ng tags  # Only shows tags from Work project
```

This allows you to answer questions like "what tags are used in my current project?" or "what tags are on high priority tasks?"

### Priorities

Three priority levels are available:

- **H** - High (displayed in red)
- **M** - Medium (displayed in yellow)
- **L** - Low (displayed in green)

#### Setting Priority

```bash
# When adding
task-ng add "Urgent task" --priority H

# When modifying
task-ng modify 1 --priority M
```

#### Filtering by Priority

```bash
task-ng list priority:H
```

---

## Scheduling & Time

### Due Dates

#### Natural Language Dates

Task-NG understands natural language dates:

```bash
task-ng add "Task" --due tomorrow
task-ng add "Task" --due "next friday"
task-ng add "Task" --due "in 3 days"
task-ng add "Task" --due "end of month"
task-ng add "Task" --due "december 25"
```

#### Specific Dates

```bash
task-ng add "Task" --due "2024-12-25"
task-ng add "Task" --due "2024-12-25 14:00"
```

#### Relative Dates

```bash
task-ng add "Task" --due "monday"
task-ng add "Task" --due "next week"
task-ng add "Task" --due "in 2 weeks"
```

### Wait and Scheduled Dates

#### Wait Date

Tasks with a wait date are hidden from the default list until that date:

```bash
# Wait for 3 days
task-ng add "Follow up" --wait 3d

# Wait until specific date
task-ng add "Check status" --wait "next monday"
```

To see waiting tasks:

```bash
task-ng list --all
```

#### Scheduled Date

The scheduled date indicates when you plan to start working on a task:

```bash
task-ng add "Weekly review" --scheduled "friday 9am"
```

#### Duration Syntax

Both wait and scheduled support duration syntax:

- `3d` - 3 days
- `2w` - 2 weeks
- `1m` - 1 month
- `4h` - 4 hours

### Recurring Tasks

Create tasks that repeat automatically when completed.

#### Named Patterns

```bash
task-ng add "Daily standup" --recur daily --due "9am"
task-ng add "Weekly review" --recur weekly --due friday
task-ng add "Monthly report" --recur monthly --due "1st"
task-ng add "Annual review" --recur yearly --due "january 1"
task-ng add "Biweekly sync" --recur biweekly --due monday
task-ng add "Quarterly review" --recur quarterly --due "1st"
```

#### Interval Patterns

```bash
task-ng add "Water plants" --recur 3d --due tomorrow
task-ng add "Team sync" --recur 2w --due monday
task-ng add "Review goals" --recur 6m --due "january 1"
```

#### With End Date

```bash
task-ng add "Sprint task" --recur weekly --due friday --until "2024-12-31"
```

#### How It Works

When you complete a recurring task, the next occurrence is automatically created:

```bash
task-ng done 1
# Completed 1 task(s)
#   ✓ 1: Daily standup
#   Created next occurrence 2 due 2024-01-16
```

### Time Tracking

Track time spent on tasks with start and stop commands.

#### Start Tracking

```bash
# Start tracking time on a task
task-ng start 1
```

#### Stop Tracking

```bash
# Stop the specified task
task-ng stop 1

# Stop the currently active task (no ID needed)
task-ng stop
```

#### View Active Task

```bash
# Show currently active task with elapsed time
task-ng active
```

#### Force Start

If another task is already active, use `--force` to stop it and start the new one:

```bash
task-ng start 2 --force
```

#### Viewing Elapsed Time

When you view a task with `task-ng show`, it displays the elapsed time:

```bash
task-ng show 1
# Shows: Started: 2024-01-15 09:30
#        Elapsed: 2h 15m
```

#### Filtering Active Tasks

The `active` command supports filter expressions to show only specific active tasks:

```bash
# Show all active tasks
task-ng active

# Show active tasks in Work project
task-ng active project:Work

# Show high priority active tasks
task-ng active priority:H

# Show active tasks with urgent tag
task-ng active +urgent

# Combine multiple filters
task-ng active project:Work priority:H
```

**Context Integration**: The active command respects the active context. If you have a context active, it will automatically filter active tasks to match the context filters.

```bash
# Set context for Work project
task-ng context set work project:Work

# Active now shows only Work active tasks
task-ng active

# Add additional filters on top of context
task-ng active priority:H  # Shows only high priority Work active tasks
```

You can also use the `+ACTIVE` virtual tag with the list command:

```bash
task-ng list +ACTIVE
```

---

## Advanced Features

### Task Dependencies

Create relationships between tasks where one task must be completed before another.

#### Adding Dependencies

```bash
# When creating task
task-ng add "Deploy to production" --depends 1 --depends 2

# When modifying task
task-ng modify 3 --depends 1
```

#### Removing Dependencies

```bash
task-ng modify 3 --remove-depends 1
```

#### Viewing Dependencies

```bash
task-ng show 3
# Shows: Dependencies: [1] Write tests
```

#### Completing Dependent Tasks

Tasks with pending dependencies cannot be completed:

```bash
task-ng done 3
# Task 3 blocked by: 1, 2
```

Complete dependencies first, then complete the dependent task.

#### Circular Dependencies

Task-NG prevents circular dependencies:

```bash
task-ng add "Task A"
task-ng add "Task B" --depends 1
task-ng modify 1 --depends 2
# Error: Circular dependency detected
```

### Annotations

Add timestamped notes to tasks to track progress or context.

#### Adding Annotations

```bash
task-ng annotate 1 "Waiting for client response"
task-ng annotate 1 "Called, left voicemail"
task-ng annotate 1 "Client confirmed, proceeding"
```

#### Viewing Annotations

```bash
task-ng show 1
# Annotations:
#   [1] 2024-01-15 10:30: Waiting for client response
#   [2] 2024-01-16 14:00: Called, left voicemail
#   [3] 2024-01-17 09:15: Client confirmed, proceeding
```

#### Removing Annotations

Remove by index (1-based):

```bash
task-ng denotate 1 2  # Removes "Called, left voicemail"
```

### Custom Attributes (UDAs)

User Defined Attributes allow you to add custom fields to tasks.

#### Adding UDAs

Use `key:value` syntax in the description:

```bash
task-ng add "Feature implementation client:Acme estimate:4h size:L"
task-ng add "Bug fix client:Globex sprint:5"
```

#### Viewing UDAs

```bash
task-ng show 1
# Custom Attributes:
#   client: Acme
#   estimate: 4h
#   size: L
```

#### Filtering by UDAs

```bash
task-ng list client:Acme
task-ng list size:L
task-ng list client:Acme size:L
```

#### Common UDA Examples

- `client:Name` - Client or customer name
- `estimate:4h` - Time estimate
- `sprint:5` - Sprint number
- `size:L` - T-shirt sizing (S/M/L/XL)
- `story_points:8` - Story points
- `component:frontend` - Component or module

### Filtering

#### Filter Syntax

| Filter | Description | Example |
|--------|-------------|---------|
| `project:Name` | Match project | `project:Work` |
| `project.not:Name` | Exclude project | `project.not:Work` |
| `priority:X` | Match priority | `priority:H` |
| `priority.not:X` | Exclude priority | `priority.not:L` |
| `status:X` | Match status | `status:pending` |
| `status.not:X` | Exclude status | `status.not:deleted` |
| `+tag` | Include tag | `+urgent` |
| `-tag` | Exclude tag | `-waiting` |
| `key:value` | Filter by UDA | `client:Acme` |

#### Exclusion Filters

Use `.not:` suffix to exclude tasks matching an attribute:

```bash
# Exclude tasks from Work project
task-ng list project.not:Work

# Exclude low priority tasks
task-ng list priority.not:L

# Exclude deleted tasks (useful with status override)
task-ng list status.not:deleted

# Combine exclusions
task-ng list project.not:Work priority.not:L
```

#### Combining Filters

All filters are combined with AND logic:

```bash
# Tasks in Work project with urgent tag and high priority
task-ng list project:Work +urgent priority:H

# Tasks for Acme client that are large
task-ng list client:Acme size:L
```

#### Virtual Tags

Virtual tags are computed based on task state, not explicitly set:

```bash
# Time-based
task-ng list +OVERDUE       # Due date passed
task-ng list +TODAY         # Due today
task-ng list +WEEK          # Due within 7 days
task-ng list +MONTH         # Due within 30 days

# Status-based
task-ng list +BLOCKED       # Has incomplete dependencies
task-ng list +WAITING       # Wait date in future

# Attribute-based
task-ng list +H             # High priority
task-ng list +PROJECT       # Has a project
task-ng list +TAGGED        # Has tags
task-ng list +DUE           # Has due date
task-ng list +RECURRING     # Is recurring

# Exclude virtual tags
task-ng list -OVERDUE       # Not overdue
task-ng list -BLOCKED       # Not blocked
```

Virtual tags must be uppercase to distinguish from regular tags.

### Contexts

Contexts apply automatic filters to narrow your task view. Useful for focusing on specific areas like "work" or "home".

#### Defining Contexts

Add contexts to `~/.config/taskng/config.toml`:

```toml
[context.work]
description = "Work tasks"
project = "Work"

[context.home]
description = "Home tasks"
project = "Home"
tags = ["personal"]

[context.urgent]
description = "Urgent tasks only"
filter = ["+urgent", "+OVERDUE"]

# Using exclusion filters
[context.not-work]
description = "Everything except work"
filter = ["project.not:Work"]

[context.focus]
description = "High priority, exclude waiting"
filter = ["priority.not:L", "-waiting"]
```

The `filter` key accepts full filter expressions including exclusions. Tags in the `tags` array can use `+` or `-` prefixes for inclusion/exclusion.

#### Using Contexts

```bash
# Show current context
task-ng context show

# Set context
task-ng context set work

# Clear context
task-ng context clear

# List available contexts
task-ng context list
# Or use shortcut
task-ng contexts
```

#### Context Filter Options

- `project` - Filter by project (includes children)
- `tags` - Filter by tags (list or single)
- `filter` - Raw filter strings (list or single)

When a context is active, its filters are automatically applied to all list commands.

---

## Views & Reports

### Reports

Reports are named views with configurable columns, filters, and sorting.

#### Running Reports

```bash
# Run a report
task-ng report run next
task-ng report run completed
task-ng report run overdue

# Add extra filters
task-ng report run next project:Work

# List available reports
task-ng report list
# Or use shortcut
task-ng reports
```

#### Default Reports

| Report | Description |
|--------|-------------|
| `list` | Default task list |
| `next` | Most urgent tasks (limit 10) |
| `all` | All tasks regardless of status |
| `completed` | Completed tasks |
| `overdue` | Overdue tasks (uses `+OVERDUE` virtual tag) |
| `waiting` | Waiting tasks |
| `recurring` | Recurring tasks (uses `+RECURRING` virtual tag) |

**Note**: The `overdue` and `recurring` reports use virtual tags (`+OVERDUE` and `+RECURRING`) for filtering, which provides consistent behavior with the rest of the filter system.

#### Custom Reports

Define custom reports in `~/.config/taskng/config.toml`:

```toml
[report.standup]
description = "Tasks for daily standup"
columns = ["id", "project", "description", "due"]
filter = ["status:pending", "+work"]
sort = ["project+", "urgency-"]
limit = 20

[report.review]
description = "Tasks needing review"
columns = ["id", "description", "priority"]
filter = ["+review", "status:pending"]
sort = ["priority-"]

# Custom report using virtual tags
[report.urgent_overdue]
description = "Urgent overdue tasks"
columns = ["id", "priority", "due", "description"]
filter = ["status:pending", "+OVERDUE", "priority:H"]
sort = ["due+"]
```

#### Report Options

- **columns**: Fields to display (id, uuid, description, status, priority, project, tags, due, scheduled, wait, end, entry, recur, depends, urgency)
- **filter**: List of filter expressions (including virtual tags like `+OVERDUE`, `+ACTIVE`, `+RECURRING`)
- **sort**: Sort order (`field+` ascending, `field-` descending)
- **limit**: Maximum tasks to show

### Statistics

View task statistics:

```bash
task-ng stats
```

Shows counts, completion rates, and distributions by project/priority/tag.

**Filtering Statistics**

The `stats` command supports filter expressions and respects active context:

```bash
# Show stats for Work project only
task-ng stats project:Work

# Show stats for high priority tasks
task-ng stats priority:H

# Show stats for urgent tasks
task-ng stats +urgent

# Combine multiple filters
task-ng stats project:Work priority:H

# Respects active context
task-ng context set work project:Work
task-ng stats  # Only shows statistics for Work project
```

This allows you to answer questions like "what's my completion rate for Work tasks?" or "how many high priority tasks are overdue?"

### Kanban Boards

Visualize tasks in a Kanban-style board with configurable columns.

#### Basic Usage

```bash
# Show default board
task-ng board show

# Show named board
task-ng board show priority

# Show board with additional filter
task-ng board show default +urgent

# List available boards
task-ng board list
# Or use shortcut
task-ng boards
```

#### Default Boards

Task-ng includes two default boards:

**default** - Task board by status:
- Backlog: Pending tasks (not active or blocked)
- Blocked: Tasks blocked by dependencies
- Active: Currently active tasks
- Done: Completed tasks

**priority** - Tasks by priority:
- High, Medium, Low, None

#### Custom Boards

Define custom boards in your config file (`~/.config/taskng/config.toml`):

```toml
[board.sprint]
description = "Current sprint"
filter = ["project:Engineering"]
columns = [
    { name = "To Do", filter = ["+sprint", "-ACTIVE"] },
    { name = "In Progress", filter = ["+sprint", "+ACTIVE"] },
    { name = "Review", filter = ["+sprint", "+review"] },
    { name = "Done", filter = ["+sprint", "status:completed"] }
]
card_fields = ["id", "description", "tags"]
sort = ["due+", "urgency-"]
limit = 8
column_width = 30
```

#### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `description` | string | `""` | Board description shown in title |
| `columns` | list | required | Column definitions |
| `filter` | list | `[]` | Global filter for all columns |
| `card_fields` | list | `["id", "priority", "description", "due"]` | Fields shown on cards |
| `sort` | list | `["urgency-"]` | Sort order within columns |
| `limit` | int | `10` | Max cards per column |
| `column_width` | int | `25` | Column width in characters |
| `enabled` | bool | `true` | Set to false to disable/hide board |

#### Overriding and Disabling Boards

**Partial override** - change specific properties while keeping defaults:

```toml
[board.default]
description = "My custom description"
limit = 5
```

This keeps the default columns (Backlog, Blocked, Active, Done) but changes the description and limit.

**Full override** - redefine the entire board including columns:

```toml
[board.default]
description = "My custom default"
columns = [
    { name = "Todo", filter = ["status:pending"] },
    { name = "Done", filter = ["status:completed"] }
]
```

Note: If you specify `columns`, they completely replace the default columns.

**Disable a default board** to hide it from the boards list:

```toml
[board.priority]
enabled = false
```

Disabled boards won't appear in `task-ng boards` and will show an error if accessed directly.

#### Column Definition

Each column has:
- `name` - Column header
- `filter` - Filter expressions for this column
- `limit` - Optional per-column card limit
- `wip_limit` - WIP limit with warning when exceeded
- `since` - Time window for completed tasks (e.g., "7d", "2w")

#### Available Card Fields

- `id` - Task ID
- `priority` - Priority indicator [H/M/L]
- `description` - Task description
- `due` - Due date
- `tags` - Task tags
- `project` - Project name

#### Examples

**Work-only board:**
```toml
[board.work]
description = "Work tasks only"
filter = ["project:Work"]
columns = [
    { name = "Todo", filter = ["status:pending", "-ACTIVE"] },
    { name = "Active", filter = ["+ACTIVE"] },
    { name = "Done", filter = ["status:completed"] }
]
```

**Tagged sprint board:**
```toml
[board.sprint]
description = "Sprint board"
columns = [
    { name = "Sprint", filter = ["+sprint"] },
    { name = "Backlog", filter = ["-sprint", "status:pending"] }
]
card_fields = ["id", "description", "due", "tags"]
```

**Limited board with wide columns:**
```toml
[board.focused]
description = "Top priorities"
columns = [
    { name = "High", filter = ["priority:H"], limit = 3 },
    { name = "Medium", filter = ["priority:M"], limit = 5 }
]
column_width = 35
limit = 5
```

#### Color Coding

Cards are color-coded:
- **Red** - Overdue tasks
- **Yellow** - High priority tasks
- **Cyan** - Medium priority tasks

#### Advanced Features

##### WIP Limits

Set Work-In-Progress limits to warn when columns are overloaded:

```toml
[board.kanban]
columns = [
    { name = "In Progress", filter = ["+ACTIVE"], wip_limit = 3 }
]
```

When exceeded, the column header shows a warning: `In Progress (4) [WIP:3]`

##### Time Windows

Show only recently completed tasks using the `since` option:

```toml
[board.recent]
columns = [
    { name = "Done This Week", filter = ["status:completed"], since = "7d" }
]
```

##### JSON Output

Export board data as JSON for integration with other tools:

```bash
task-ng --json board
task-ng --json board priority
```

Output includes board name, description, columns with task counts, WIP limits, and full task details.

### Calendar View

View tasks organized by due date in a monthly calendar format.

#### Basic Usage

```bash
# Show current month
task-ng calendar

# Show specific month
task-ng calendar --month 3

# Show specific month and year
task-ng calendar --month 12 --year 2024
```

#### Display

The calendar shows:
- Day numbers with tasks listed below
- **Today** highlighted with inverted colors
- Task indicators:
  - `!` Red - Overdue task
  - `*` Yellow - High priority task
  - `-` Cyan - Normal task

#### Task Display

Each day shows up to 3 tasks with truncated descriptions. If more tasks are due, a "+N more" indicator appears.

#### Navigation

```bash
# Previous month
task-ng calendar --month 10

# Next year
task-ng calendar --year 2025

# Specific date
task-ng calendar --month 6 --year 2024
```

#### Filtering Calendar

The calendar view supports filter expressions to show only tasks matching specific criteria.

```bash
# Show only Work project tasks
task-ng calendar project:Work

# Show only high priority tasks
task-ng calendar priority:H

# Show only tasks with specific tag
task-ng calendar +urgent

# Combine multiple filters
task-ng calendar project:Work priority:H

# Show completed tasks (by default only pending shown)
task-ng calendar status:completed
```

**Context Integration**: The calendar command respects the active context. If you have a context active, it will automatically filter the calendar view to match the context filters.

```bash
# Set context for Work project
task-ng context set work project:Work

# Calendar now shows only Work tasks
task-ng calendar

# Add additional filters on top of context
task-ng calendar priority:H  # Shows only high priority Work tasks
```

---

## Configuration & Customization

### Configuration

#### Default Command

When you run `task-ng` without any subcommand, it executes the default command. By default, this runs the "next" report which shows your most urgent tasks.

```bash
# These are equivalent (when default.command = "next")
task-ng
task-ng report run next
```

##### Configuring the Default Command

Set the default command in your config file:

```toml
[default]
command = "list"
```

Or via command line:

```bash
task-ng config default.command list
```

##### Available Default Commands

You can set `default.command` to any of these:

**Built-in commands:**
- `list` - List all pending tasks
- `active` - Show currently active task
- `projects` - Show project tree (alias for `project list`)
- `tags` - Show all tags
- `stats` - Show statistics
- `calendar` - Show calendar view

**Reports (any report name):**
- `next` - Most urgent tasks (default)
- `all` - All tasks regardless of status
- `completed` - Completed tasks
- `overdue` - Overdue tasks
- `waiting` - Waiting tasks
- `recurring` - Recurring tasks
- Any custom report you've defined

##### Examples

```toml
# Use list command as default
[default]
command = "list"

# Use a custom report as default
[default]
command = "standup"
```

#### View Configuration

```bash
# View all config
task-ng config

# View specific key
task-ng config dateformat
```

#### Set Configuration

```bash
task-ng config dateformat "%Y-%m-%d"
task-ng config default.project Work
```

#### Unset Configuration

```bash
task-ng config --unset dateformat
```

#### Configuration File

Configuration is stored in `~/.config/taskng/config.toml` by default.

#### Global Options

Override config and data locations with global CLI options:

```bash
# Use custom config file
task-ng --config /path/to/config.toml list

# Use custom data directory
task-ng --data-dir /path/to/data list

# Combine both
task-ng --config ./project.toml --data-dir ./data add "Project task"
```

#### Local Project Configuration

Task-NG automatically detects a `./.taskng` directory in the current working directory. This allows you to have project-specific task databases and configurations.

**Using the init command (recommended):**

```bash
# Initialize task-ng in current directory
task-ng init

# This creates:
# .taskng/
# ├── config.toml    # Comprehensive documented configuration
# └── task.db        # Local task database
```

The generated `config.toml` file contains:
- All available configuration options with descriptions
- Default values shown as commented-out settings
- Section headers organizing related options
- Inline comments explaining each setting
- Examples for reports, boards, and contexts

**To customize**, simply uncomment any line and modify its value:

```toml
# Before (default):
# [ui]
# color = true

# After (customized):
[ui]
color = false  # Disable colors
```

**Continue using task-ng:**

```bash
# Now all task-ng commands in this directory use local database
task-ng add "Project task"
task-ng list
```

**Manual setup:**

```bash
# Create project-local config manually
mkdir -p ./.taskng
cat > ./.taskng/config.toml << 'EOF'
[data]
location = "./.taskng"

[context.project]
project = "MyProject"
EOF

# Now task-ng commands in this directory use local config
task-ng add "Project task"
```

#### Configuration and Data Directory Precedence

Understanding how Task-NG determines which configuration file and data directory to use:

**Config File Location (highest to lowest priority):**

1. **`--config` CLI option** - Explicit path on command line
2. **Local `./.taskng/config.toml`** - Auto-detected in current directory
3. **`TASKNG_CONFIG_FILE` environment variable** - Set in your shell
4. **Default `~/.config/taskng/config.toml`** - User config directory

**Data Directory Location (highest to lowest priority):**

1. **`--data-dir` CLI option** - Explicit path on command line
2. **`TASKNG_DATA_DIR` environment variable** - Set in your shell
3. **`data.location` from config file** - Specified in active config
4. **Default `~/.local/share/taskng`** - User data directory

#### Configuration Examples

**Example 1: Global configuration with custom data location**

```toml
# ~/.config/taskng/config.toml
[data]
location = "/home/user/my-tasks"

[ui]
color = true

[default]
command = "next"
```

**Example 2: Project-local configuration**

```toml
# /path/to/project/.taskng/config.toml
[data]
location = "./.taskng"

[context.work]
description = "Work tasks for this project"
project = "ProjectName"

[default]
command = "list"
```

**Example 3: Using environment variables**

```bash
# Set custom config location
export TASKNG_CONFIG_FILE="/path/to/custom-config.toml"

# Set custom data directory
export TASKNG_DATA_DIR="/path/to/task-data"

# These will be used by all task-ng commands
task-ng list
```

**Example 4: CLI options (highest priority)**

```bash
# Override everything with CLI options
task-ng --config ./project.toml --data-dir ./data list

# Useful for one-off operations
task-ng --data-dir /backup/tasks export --all > backup.json
```

#### Environment Variables

Task-NG supports the following environment variables:

- **`TASKNG_CONFIG_FILE`** - Path to config file
- **`TASKNG_DATA_DIR`** - Path to data directory
- **`TASKNG_*`** - Set config values (e.g., `TASKNG_UI__COLOR=false`)
  - Double underscore (`__`) represents nesting (e.g., `TASKNG_UI__COLOR` sets `ui.color`)
  - Supported values: `true`, `yes`, `1` for boolean true; `false`, `no`, `0` for boolean false; numbers; strings

### Hooks

Hooks allow you to run custom scripts when tasks are added, modified, or completed.

#### Hook Directory

Create hook scripts in `~/.config/taskng/hooks/`:

```
~/.config/taskng/hooks/
├── on-add/       # Scripts run when tasks are added
├── on-modify/    # Scripts run when tasks are modified
└── on-complete/  # Scripts run when tasks are completed
```

#### Creating a Hook

1. Create the hooks directory:

```bash
mkdir -p ~/.config/taskng/hooks/on-add
```

2. Create an executable script:

```bash
#!/bin/bash
# ~/.config/taskng/hooks/on-add/notify.sh

# Read task JSON from stdin
task=$(cat)

# Extract description
desc=$(echo "$task" | jq -r '.task.description')

# Send notification
notify-send "Task Added" "$desc"

exit 0
```

3. Make it executable:

```bash
chmod +x ~/.config/taskng/hooks/on-add/notify.sh
```

#### Hook Input

Hooks receive task data as JSON on stdin:

**on-add and on-complete:**
```json
{
  "task": {
    "uuid": "abc-123",
    "description": "Task description",
    "status": "pending",
    "priority": "H",
    ...
  }
}
```

**on-modify:**
```json
{
  "task": {
    "description": "New description",
    ...
  },
  "old": {
    "description": "Old description",
    ...
  }
}
```

#### Hook Output

- Exit code 0: Success
- Non-zero exit: Failure (warning displayed)
- stdout: Message displayed to user
- stderr: Error message on failure

#### Example Hooks

**Log all task additions:**
```bash
#!/bin/bash
# on-add/log.sh
cat >> ~/.config/taskng/task-log.json
echo "Logged task"
```

**Prevent high-priority tasks without due dates:**
```python
#!/usr/bin/env python3
# on-add/require-due.py
import json
import sys

data = json.load(sys.stdin)
task = data['task']

if task.get('priority') == 'H' and not task.get('due'):
    print("High priority tasks require a due date", file=sys.stderr)
    sys.exit(1)
```

**Send notification on completion:**
```bash
#!/bin/bash
# on-complete/notify.sh
task=$(cat)
desc=$(echo "$task" | jq -r '.task.description')
notify-send "Task Completed" "$desc"
```

#### Hook Execution

- Hooks run in alphabetical order (use `01-`, `02-` prefixes to control order)
- Only executable files are run
- Hooks timeout after 30 seconds
- If any hook fails, a warning is displayed but the operation continues

### Shell Completion

#### Bash

```bash
task-ng completion bash > ~/.local/share/bash-completion/completions/task-ng
```

#### Zsh

```bash
task-ng completion zsh > ~/.zfunc/_task-ng
```

#### Fish

```bash
task-ng completion fish > ~/.config/fish/completions/task-ng.fish
```

---

## Import & Export

### Export Tasks

Export tasks to JSON for backup or transfer:

```bash
# Export pending tasks to stdout
task-ng export

# Export to file
task-ng export tasks.json

# Export with filter
task-ng export tasks.json --filter project:Work

# Include completed and deleted tasks
task-ng export tasks.json --all

# Create full backup with metadata
task-ng export backup.json --backup
```

The backup format includes version info and timestamp:
```json
{
  "version": "1.0",
  "exported": "2024-01-15T10:30:00",
  "task_count": 42,
  "tasks": [...]
}
```

### Import Tasks

Import tasks from Taskwarrior or Task-NG exports:

```bash
# Import from Taskwarrior
task export > tasks.json
task-ng import tasks.json

# Import from Task-NG backup
task-ng import backup.json

# Preview import (dry run)
task-ng import tasks.json --dry-run
```

Supported formats (auto-detected):
- Taskwarrior array format
- Taskwarrior NDJSON (newline-delimited)
- Task-NG export (plain array)
- Task-NG backup (with metadata)

### JSON Output

Get output in JSON format for scripting:

```bash
# List as JSON
task-ng --json list

# Show as JSON
task-ng --json show 1
```

---

## Synchronization

Task-NG supports multi-device synchronization, allowing you to keep your tasks in sync across multiple computers.

### Sync Overview

The sync system uses a **pluggable backend architecture**, with Git as the default sync mechanism. Tasks are stored as individual JSON files in a Git repository, enabling:

- **Offline-first operation**: Work freely without network access, sync when ready
- **Conflict resolution**: Field-level merging when the same task is modified on multiple devices
- **Version history**: Git provides full history of all changes
- **Privacy**: Use your own Git repository (GitHub, GitLab, self-hosted)

**How it works:**
1. Each task is stored as a JSON file (`tasks/{uuid}.json`) in a sync repository
2. Changes are tracked in your local task database
3. `sync push` exports local changes to the Git repository
4. `sync pull` imports remote changes from the repository
5. Conflicts are resolved automatically or flagged for manual resolution

### Setting Up Sync

#### Initialize Sync (Local Only)

For local-only sync (backup without remote):

```bash
# Initialize sync repository
task-ng sync init
```

This creates a sync repository at `~/.local/share/taskng/sync/`.

#### Initialize Sync with Remote

To sync across devices, set up a Git remote:

```bash
# Initialize with a remote repository
task-ng sync init --remote git@github.com:username/tasks.git

# Or add a remote later
task-ng sync init
cd ~/.local/share/taskng/sync
git remote add origin git@github.com:username/tasks.git
```

**Recommended repository setup:**
1. Create a **private** repository on GitHub, GitLab, or your Git server
2. Use SSH authentication for seamless sync operations
3. Don't share the repository—it's designed for single-user multi-device sync

#### Setting Up Additional Devices

On each additional device:

```bash
# Clone your sync repository first
git clone git@github.com:username/tasks.git ~/.local/share/taskng/sync

# Initialize task-ng sync (detects existing repo)
task-ng sync init

# Pull tasks from remote
task-ng sync pull
```

### Sync Commands

#### Full Sync

Perform a complete bidirectional sync:

```bash
task-ng sync
```

This runs `push` followed by `pull`, handling any conflicts.

#### Push Local Changes

Export and push local changes to the remote:

```bash
task-ng sync push
```

#### Pull Remote Changes

Pull and import changes from the remote:

```bash
task-ng sync pull
```

#### Check Sync Status

View the current sync status:

```bash
task-ng sync status
```

Output includes:
- Sync enabled/disabled
- Backend type (git)
- Last sync timestamp
- Pending push/pull counts
- Remote URL
- Device ID

#### View Conflicts

List any unresolved conflicts:

```bash
task-ng sync conflicts
```

### Conflict Resolution

When the same task is modified on multiple devices, Task-NG uses **field-level merging** to resolve conflicts automatically when possible.

#### Automatic Resolution

Most conflicts resolve automatically:

| Scenario | Resolution |
|----------|------------|
| Different fields modified | Both changes preserved |
| Same field, same value | No conflict |
| Only local changed | Keep local value |
| Only remote changed | Keep remote value |
| Lists (tags, depends) | Union of both lists |

**Example:**
```
Device A: Changes due date to Dec 18
Device B: Changes priority to High

Result: Both changes merged—due=Dec 18, priority=High
```

#### True Conflicts

When the same field is modified differently on both devices, the **last-write-wins** strategy is used by default (based on `modified` timestamp).

You can configure the default resolution strategy:

```bash
# Use last-write-wins (default)
task-ng config set sync.conflict_resolution last_write_wins

# Always keep local changes
task-ng config set sync.conflict_resolution keep_local

# Always keep remote changes
task-ng config set sync.conflict_resolution keep_remote
```

#### Delete Conflicts

When a task is deleted on one device and modified on another:
- The conflict is flagged for review
- Use `task-ng sync conflicts` to view and resolve

### Sync Configuration

Configure sync in your `~/.config/taskng/config.toml`:

```toml
[sync]
enabled = true
backend = "git"
conflict_resolution = "last_write_wins"  # or "keep_local", "keep_remote"

[sync.git]
directory = "~/.local/share/taskng/sync"
# remote is set via git commands
```

#### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `sync.enabled` | `true` | Enable/disable sync functionality |
| `sync.backend` | `"git"` | Sync backend (currently only "git") |
| `sync.conflict_resolution` | `"last_write_wins"` | Default conflict resolution strategy |
| `sync.git.directory` | `~/.local/share/taskng/sync` | Sync repository location |

### Sync Best Practices

1. **Sync regularly**: Run `task-ng sync` frequently to minimize conflicts
2. **Use SSH keys**: Set up SSH authentication for seamless Git operations
3. **Private repositories**: Keep your task repository private
4. **Check status**: Run `task-ng sync status` to verify sync is working
5. **Resolve conflicts promptly**: Don't let conflicts accumulate

### Troubleshooting

#### "Sync not initialized"

Run `task-ng sync init` to set up the sync repository.

#### Git authentication errors

Ensure your SSH key is configured:
```bash
ssh -T git@github.com  # Test GitHub connection
```

#### Merge conflicts in Git

If Git shows merge conflicts (not task field conflicts):
```bash
cd ~/.local/share/taskng/sync
git status  # See conflicting files
# Resolve manually or:
git checkout --theirs tasks/  # Accept remote
git checkout --ours tasks/    # Keep local
git add -A && git commit
```

#### Reset sync state

To reset sync completely:
```bash
rm -rf ~/.local/share/taskng/sync
task-ng sync init --remote <your-remote>
task-ng sync push  # Re-push all tasks
```

---

## Reference

### Command Reference

| Command | Description |
|---------|-------------|
| `add` | Add a new task |
| `list` | List tasks |
| `show` | Show task details |
| `modify` | Modify a task |
| `done` | Complete task(s) |
| `delete` | Delete task(s) |
| `undo` | Undo last operation |
| `annotate` | Add annotation |
| `denotate` | Remove annotation |
| `report` | Run a named report |
| `reports` | List available reports |
| `stats` | Show task statistics |
| `calendar` | Show calendar view |
| `config` | View/set configuration |
| `import` | Import from JSON (Taskwarrior or Task-NG) |
| `export` | Export tasks to JSON |
| `sync` | Full bidirectional sync (push + pull) |
| `sync init` | Initialize sync repository |
| `sync push` | Push local changes to remote |
| `sync pull` | Pull remote changes |
| `sync status` | Show sync status |
| `sync conflicts` | View unresolved conflicts |

#### Global Options

| Option | Description |
|--------|-------------|
| `--version`, `-v` | Show version |
| `--json` | Output in JSON format |
| `--debug` | Show debug info on errors |
| `--help` | Show help |

### Tips and Best Practices

#### Use Projects for Organization

Group related tasks into projects:

```bash
task-ng add "Design mockups" --project "Website Redesign"
task-ng add "Implement frontend" --project "Website Redesign"
task-ng add "Write tests" --project "Website Redesign"
```

#### Use Tags for Cross-Cutting Concerns

Tags work across projects:

```bash
task-ng list +blocked      # All blocked tasks
task-ng list +waiting      # All waiting tasks
task-ng list +next         # Next actions
```

#### Use Dependencies for Workflows

Model task dependencies:

```bash
task-ng add "Write code"
task-ng add "Write tests" --depends 1
task-ng add "Code review" --depends 2
task-ng add "Deploy" --depends 3
```

#### Use Annotations for Context

Track progress and decisions:

```bash
task-ng annotate 1 "Started implementation"
task-ng annotate 1 "Blocked on API response format"
task-ng annotate 1 "Resolved - using JSON format"
```

#### Use UDAs for Domain-Specific Data

Track custom fields:

```bash
task-ng add "Fix bug client:Acme priority_level:critical"
task-ng list client:Acme
```

### Getting Help

```bash
# General help
task-ng --help

# Command-specific help
task-ng add --help
task-ng list --help
```
