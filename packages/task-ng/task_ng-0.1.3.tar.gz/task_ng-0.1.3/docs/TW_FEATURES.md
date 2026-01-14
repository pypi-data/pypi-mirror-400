# Taskwarrior Features

**Version:** 3.4.2
**Description:** A command-line todo list manager

## Overview

Taskwarrior is a powerful command-line task management tool that helps you organize, track, and manage your tasks efficiently. At its core, it's a list processing program that becomes a comprehensive todo system through features like due dates, priorities, tags, and project organization.

---

## Core Task Management

### Basic Operations
- **Add tasks** - Create new pending tasks with rich metadata
- **Modify tasks** - Update any aspect of existing tasks
- **Delete tasks** - Remove tasks (soft delete, can be purged later)
- **Complete tasks** - Mark tasks as done
- **Log tasks** - Add tasks that are already completed
- **Duplicate tasks** - Clone existing tasks with modifications
- **Annotate tasks** - Add timestamped notes/comments to tasks
- **Edit tasks** - Direct editing of task data in a text editor
- **Undo operations** - Revert the most recent change

### Task Attributes
- **Description** - Main task text with annotation support
- **Project** - Hierarchical project organization (e.g., `Home.Garden`)
- **Priority** - H (High), M (Medium), L (Low), or none
- **Due date** - When the task should be completed
- **Scheduled date** - When work should begin
- **Until date** - Expiration date for recurring tasks
- **Wait date** - Hide task until specified date
- **Entry date** - When task was created (automatic)
- **Modified date** - Last modification timestamp (automatic)
- **Start/End dates** - Track when work began/completed
- **Status** - pending, completed, deleted, waiting, recurring
- **Tags** - Multiple word-based labels (e.g., `+home`, `+urgent`)
- **Dependencies** - Tasks that must be completed first
- **Recurrence** - Automatic task regeneration patterns
- **UUID** - Unique identifier for each task

---

## Advanced Features

### Filtering and Search
- **Powerful filter syntax** - Combine multiple criteria with logical operators
- **Attribute modifiers** - Refined filtering (contains, startswith, before, after, etc.)
- **Regex support** - Pattern matching in descriptions and attributes
- **Logical operators** - AND, OR, XOR with parentheses
- **ID and UUID targeting** - Select specific tasks or ranges (e.g., `1-5,10`)
- **Virtual tags** - System-generated tags like `+PENDING`, `+COMPLETED`, `+OVERDUE`

### Task Relationships
- **Dependencies** - Define tasks that block others
- **Blocking/Blocked reports** - View task dependency chains
- **Unblocked view** - Show actionable tasks only
- **Recurring tasks** - Automatic task regeneration on completion
- **Parent-child relationships** - Recurring task templates and instances

### Urgency and Prioritization
- **Urgency calculation** - Automatic scoring based on multiple factors:
  - Priority level
  - Due date proximity
  - Age of task
  - Tags
  - Annotations
  - Dependencies
  - Custom coefficients
- **Next report** - Shows most urgent tasks automatically
- **Ready report** - Most urgent actionable tasks (started or unscheduled)

### Context System
- **Define contexts** - Set default filters for different work environments
- **Switch contexts** - Quickly change focus (e.g., work vs. home)
- **Context filters** - Automatically applied to relevant commands
- **Multiple contexts** - Manage different areas of responsibility

### User Defined Attributes (UDAs)
- **Custom attributes** - Define your own task fields
- **Type support** - string, numeric, date, duration types
- **Validation** - Restrict values to allowed sets
- **Full integration** - Use UDAs in filters, reports, and sorting

---

## Reporting and Visualization

### Built-in Reports (28 Total)
- **list** - Most details of tasks
- **long** - All details of tasks
- **ls** - Few details of tasks
- **minimal** - Minimal details of tasks
- **next** - Most urgent tasks
- **ready** - Most urgent actionable tasks
- **active** - Currently started tasks
- **completed** - Finished tasks
- **all** - Everything including deleted
- **waiting** - Hidden/postponed tasks
- **recurring** - Repeating tasks
- **blocked** - Tasks waiting on dependencies
- **blocking** - Tasks that block others
- **unblocked** - Tasks with no blockers
- **overdue** - Past due date tasks
- **oldest/newest** - Sorted by age
- **projects** - List all projects with task counts
- **tags** - List all tags with usage counts
- **summary** - Task status aggregated by project
- **information** - Complete task details including history
- **timesheet** - Weekly summary of completed/started tasks

### Graphical Reports
- **Calendar view** - Monthly calendar with due tasks marked
- **Burndown charts** - Progress visualization (daily, weekly, monthly)
- **History reports** - Task status over time (daily, weekly, monthly, annual)
- **Graphical history (ghistory)** - Visual task history charts

### Custom Reports
- **Define new reports** - Create custom views with specific columns
- **Column customization** - Choose which fields to display
- **Sort configuration** - Define custom sort orders
- **Filter defaults** - Set implicit filters for reports
- **Format control** - Control output formatting and colors

---

## Time Management

### Time Tracking
- **Start/Stop tasks** - Track active work periods
- **Active report** - View currently running tasks
- **Multiple timers** - Track several tasks simultaneously
- **Duration tracking** - Automatic calculation of time spent

### Scheduling
- **Due dates** - Set deadlines for tasks
- **Scheduled dates** - Plan when to start work
- **Wait dates** - Defer tasks until a specific time
- **Until dates** - Set expiration for recurring tasks
- **Recurring patterns** - daily, weekly, monthly, yearly, or custom intervals
- **Countdown display** - Show time remaining until due

---

## Data Management

### Import/Export
- **JSON export** - Full data export in JSON format
- **JSON import** - Import tasks from JSON
- **Bulk operations** - Modify multiple tasks at once
- **Migration tools** - Import from version 2.x format
- **Script integration** - Helper scripts for CSV, XML, YAML, HTML, iCal, SQL formats

### Synchronization
- **Multiple sync backends**:
  - **TaskChampion sync server** - Modern HTTP server for multi-user sync
  - **AWS S3** - Direct sync to S3 bucket with IAM policies
  - **Google Cloud Storage** - GCP bucket sync with service accounts
  - **Local sync** - On-disk sync for space savings without remote server
  - **Legacy Taskserver** - Original sync server (deprecated)
- **End-to-end encryption** - `sync.encryption_secret` encrypts all data; server never sees plaintext
- **Client ID based** - Each replica identified by UUID; independent user namespaces
- **Multi-device support** - Keep tasks in sync across computers
- **Conflict resolution** - Handle concurrent modifications
- **Sync status tracking** - Monitor pending changes
- **Disk space optimization** - Sync compresses and deduplicates task data

### Synchronization Limitations
- **Undo breaks after sync** - Cannot undo operations once synchronized
- **Recurring task duplication** - Must manually disable recurrence on secondary clients
- **No visual merge tool** - Conflicts require manual resolution
- **Manual client management** - Client IDs must be manually generated and tracked

### Data Integrity
- **UUID tracking** - Unique identifiers prevent conflicts
- **Change history** - Complete audit trail of modifications
- **Diagnostics** - Scan for data problems
- **Backup-friendly** - Plain text data files
- **Purge capability** - Permanently remove deleted tasks

---

## Customization and Configuration

Taskwarrior's power comes from its extensive configurability. With **298 configuration variables**, nearly every aspect of behavior, appearance, and functionality can be customized via the `.taskrc` file.

### Configuration System
- **Rich settings** - 298+ configuration variables covering all aspects
- **File-based config** - Simple `.taskrc` file in home directory (`~/.taskrc`)
- **Alternative locations** - Support for `TASKRC` env var or `XDG_CONFIG_HOME`
- **Include files** - Nest configuration files for organization
- **Runtime overrides** - Command-line config changes (`task rc.name:value ...`)
- **Config command** - Modify settings directly via CLI (`task config name value`)
- **Show command** - View all current settings with `task show`
- **Validation** - Automatic checking of configuration values
- **Comments** - Support for documentation within config files
- **Environment expansion** - Use environment variables in paths

### File and Directory Configuration
- **data.location** - Path to task database (default: `~/.task`)
- **hooks.location** - Path to hook scripts directory
- **TASKDATA** - Environment variable override for data location
- **gc** - Control garbage collection and ID rebuilding
- **purge.on-sync** - Automatic purge of old tasks after sync

### Report Customization (183+ report-related settings)
Each of the 28 built-in reports can be customized:
- **report.X.columns** - Define which columns to display
- **report.X.labels** - Customize column headers
- **report.X.sort** - Set sort order (multi-field with +/- for asc/desc)
- **report.X.filter** - Default filter applied to report
- **report.X.description** - Report description text
- **report.X.context** - Whether report respects active context

Example report configuration:
```
report.list.columns=id,start.age,entry.age,depends.indicator,priority,project,tags,recur.indicator,scheduled.countdown,due,until.remaining,description.count,urgency
report.list.labels=ID,Active,Age,D,P,Project,Tags,R,Sch,Due,Until,Description,Urg
report.list.sort=start-,due+,project+,urgency-
report.list.filter=status:pending -WAITING
```

### Custom Reports
- **Create new reports** - Define entirely new report types
- **Clone existing reports** - Start from built-in reports and modify
- **Combine filters** - Complex default filters for specialized views
- **Custom formatting** - Control every aspect of output

### Urgency Calculation (15 urgency coefficients)
Fine-tune the urgency algorithm by adjusting coefficients:
- **urgency.active.coefficient** - Weight for started tasks (default: 4.0)
- **urgency.age.coefficient** - Weight for task age (default: 2.0)
- **urgency.age.max** - Maximum age considered (default: 365 days)
- **urgency.annotations.coefficient** - Weight for annotations (default: 1.0)
- **urgency.blocked.coefficient** - Weight for blocked tasks (default: -5.0)
- **urgency.blocking.coefficient** - Weight for blocking tasks (default: 8.0)
- **urgency.due.coefficient** - Weight for due date (default: 12.0)
- **urgency.scheduled.coefficient** - Weight for scheduled tasks (default: 5.0)
- **urgency.tags.coefficient** - Weight per tag (default: 1.0)
- **urgency.project.coefficient** - Weight for project membership (default: 1.0)
- **urgency.waiting.coefficient** - Weight for waiting tasks (default: -3.0)
- **urgency.uda.priority.H.coefficient** - High priority weight (default: 6.0)
- **urgency.uda.priority.M.coefficient** - Medium priority weight (default: 3.9)
- **urgency.uda.priority.L.coefficient** - Low priority weight (default: 1.8)
- **urgency.user.tag.X.coefficient** - Custom tag-specific weights
- **urgency.inherit** - Whether child tasks inherit parent urgency

### Color Customization (80+ color settings)
Full control over terminal colors with 256-color support:

**Color Categories:**
- **Task status colors** - Different colors for pending, completed, deleted, active
- **Attribute colors** - Color by priority, project, tags
- **Due date colors** - Overdue, due today, due soon
- **Report colors** - Headers, labels, footers, alternate rows
- **Calendar colors** - Due dates, holidays, today, weekends
- **Chart colors** - Burndown, history graphs, summary bars
- **Special indicators** - Blocking, blocked, recurring, scheduled
- **Sync status** - Added, changed, rejected
- **System colors** - Errors, warnings, debug output

**Color Configuration Examples:**
```
color.active=rgb045 on rgb015
color.due.today=color252
color.overdue=color255
color.blocked=white on rgb001
color.tagged=rgb031
color.uda.priority.H=rgb035
```

**Color Features:**
- **RGB notation** - Use `rgb###` for 256-color support
- **Named colors** - Use color names like `red`, `blue`, `white`
- **Background colors** - Set with `on <color>`
- **Underline/bold** - Text decoration support
- **Theme files** - Include predefined themes (dark-16, dark-256, light-16, etc.)
- **Color legend** - View with `task colors`
- **Conditional coloring** - Rule-based color application
- **Custom rules** - Define your own color.rule.X settings

### Date and Time Formatting
- **dateformat** - Default date format (e.g., `Y-M-D`, `m/d/Y`)
- **dateformat.report** - Format for report display
- **dateformat.info** - Format for detailed info command
- **dateformat.edit** - Format when editing tasks
- **dateformat.annotation** - Format for annotation timestamps
- **dateformat.holiday** - Format for holiday dates
- **Date format tokens** - Y, M, D, H, N, S and many more
- **ISO-8601 support** - International date standard
- **Relative dates** - Age, remaining time displays

### Default Behaviors
- **default.command** - Command run when none specified (default: `next`)
- **default.timesheet.filter** - Default filter for timesheet report
- **default.due** - Default due date for new tasks
- **default.scheduled** - Default scheduled date
- **default.project** - Default project for new tasks
- **default.priority** - Default priority level

### Recurrence Settings
- **recurrence.confirmation** - Control confirmation prompts (yes/no/prompt)
- **recurrence.indicator** - Character to show recurring tasks (default: R)
- **recurrence.limit** - Number of future instances to generate
- **recurrence** - Enable/disable recurrence processing

### Search and Filter Configuration
- **search.case.sensitive** - Case-sensitive searches (default: yes)
- **regex** - Enable regular expression support
- **abbreviation.minimum** - Minimum characters for command abbreviation
- **allow.empty.filter** - Allow commands affecting all tasks

### Aliases (Command Shortcuts)
Define custom command aliases:
- **alias.rm** - Shortcut for delete (default: `alias.rm=delete`)
- **alias.burndown** - Default burndown report
- **alias.history** - Default history report
- **Custom aliases** - Create your own shortcuts

Example aliases:
```
alias.rm=delete
alias.h=history.monthly
alias.bd=burndown.weekly
alias.overdue=list due.before:today
```

### User Defined Attributes (UDAs)
Create completely custom task attributes:
```
uda.estimate.type=numeric
uda.estimate.label=Est
uda.estimate.values=1,2,3,5,8,13
uda.reviewed.type=date
uda.reviewed.label=Reviewed
urgency.uda.estimate.coefficient=2.0
```

**UDA Features:**
- **Type definition** - string, numeric, date, duration
- **Label customization** - Display name in reports
- **Value restrictions** - Limit to specific allowed values
- **Urgency integration** - Add UDA-based urgency weights
- **Report integration** - Use in any report or filter
- **Sort capability** - Sort by UDA values

### Calendar Configuration
- **calendar.details** - Level of detail (full/sparse)
- **calendar.details.report** - Which report to use for details
- **calendar.holidays** - Holiday location (full/sparse/none)
- **calendar.legend** - Show calendar legend
- **calendar.offset** - Months before/after current
- **calendar.offset.value** - Number of months offset
- **weekstart** - First day of week (Sunday/Monday)
- **displayweeknumber** - Show ISO week numbers
- **monthsperline** - Calendar layout width

### Display and Output
- **verbose** - Control output verbosity (off/nothing/blank/footnote/new-id/affected/edit/special/project/sync/unwait/recur)
- **confirmation** - Require confirmation for operations
- **bulk** - Threshold for bulk operation warnings
- **avoidlastcolumn** - Avoid using last terminal column
- **hyphenate** - Break long words in output
- **truncate.mode** - How to truncate long fields
- **truncate.lines** - Maximum lines in truncated fields
- **obfuscate** - Hide task data (for screenshots)

### Context Configuration
Define and manage contexts for filtering:
```
context.work.read=project:Work
context.work.write=project:Work
context.home.read=-work
context.home.write=project:Home
```

**Context Features:**
- **Read filters** - Applied when viewing tasks
- **Write filters** - Applied when creating tasks
- **Multiple contexts** - Switch between work environments
- **Hierarchical** - Combine with other filters

### Hook System
- **hooks** - Master switch to enable/disable hooks (default: on)
- **Hook scripts** - Execute on task events:
  - `on-add` - Before task creation
  - `on-modify` - Before task modification
  - `on-launch` - Before Taskwarrior starts
  - `on-exit` - After Taskwarrior exits
- **Hook directory** - Configured via `hooks.location`
- **Hook language** - Any executable script (Python, Bash, etc.)
- **Hook API** - JSON-based input/output
- **Hook chaining** - Multiple hooks per event

### Synchronization Configuration
- **sync.server.url** - Taskserver URL
- **sync.server.certificate** - Client certificate path
- **sync.server.key** - Client key path
- **sync.server.ca** - CA certificate path
- **sync.encryption_secret** - Encryption key for sync

### Performance Tuning
- **gc** - Garbage collection enable/disable
- **locking** - File locking for concurrent access
- **exit.on.missing.db** - Behavior when database missing
- **allow.empty.filter** - Safety for broad operations

### Terminal and Display
- **detection** - Auto-detect terminal capabilities
- **avoidlastcolumn** - Work around terminal quirks
- **_forcecolor** - Force color output
- **defaultwidth** - Default column width
- **defaultheight** - Default terminal height

### Advanced Configuration
- **json.array** - JSON output as array
- **json.depends.array** - Dependencies as JSON array
- **json.tags.array** - Tags as JSON array
- **expressions** - Enable algebraic expressions
- **dom** - Enable DOM reference access
- **debug** - Enable debug output
- **debug.hooks** - Debug hook execution

### Extensibility
- **External commands** - Execute system commands via `task execute`
- **DOM access** - Query internal data structures (`task _get rc.name`)
- **Helper commands** - Shell completion support (bash, zsh)
- **API access** - Programmatic access to task data
- **Script integration** - Machine-readable output modes

### Theme Support
Include pre-configured color themes:
```
include dark-16.theme
include dark-256.theme
include light-16.theme
include light-256.theme
include dark-red-256.theme
include dark-green-256.theme
include dark-blue-256.theme
include dark-violets-256.theme
include dark-yellow-green.theme
include dark-gray-256.theme
include dark-gray-blue-256.theme
include solarized-dark-256.theme
include solarized-light-256.theme
```

### Holiday Files
Include regional holiday calendars:
```
include holidays.en-US.rc
include holidays.en-GB.rc
include holidays.de-DE.rc
include holidays.fr-FR.rc
```

### Configuration Best Practices
- **Backup .taskrc** - Keep version control
- **Use includes** - Organize by category (colors.rc, reports.rc, etc.)
- **Test overrides** - Use command-line overrides before making permanent
- **Comment liberally** - Document custom settings
- **Start minimal** - Add customizations as needed
- **Review defaults** - Use `task show` to understand current settings

---

## Command-Line Interface

### User Experience
- **Flexible syntax** - Natural command ordering
- **Confirmation prompts** - Safety for destructive operations
- **Abbreviated commands** - Smart command matching
- **ID persistence** - Stable IDs within work sessions
- **Verbose control** - Adjust output detail level
- **Help system** - Comprehensive documentation access

### Output Formatting
- **Table views** - Clean columnar output
- **Sorting control** - Multi-field sort specifications
- **Column alignment** - Left, right, center alignment
- **Truncation** - Smart text truncation for long fields
- **Word wrap** - Terminal width-aware formatting
- **Count indicators** - Show number of annotations/dependencies

### Metadata Access
- **count** - Number of matching tasks
- **ids** - Extract task IDs
- **uuids** - Extract task UUIDs
- **stats** - Database statistics
- **_get** - Access internal data (DOM references)
- **_unique** - Extract unique attribute values

---

## Query and Filter Features

### Attribute Modifiers
- **equals** - Exact match
- **not** - Negation
- **contains** - Substring match
- **startswith/endswith** - Prefix/suffix matching
- **word** - Whole word match
- **noword** - Absence of word
- **before/after** - Date comparisons
- **under/over** - Numeric comparisons
- **isnt** - Case-sensitive non-match
- **has/hasnt** - Attribute presence

### Special Filters
- **Date expressions** - Natural language dates (today, tomorrow, eom, eoy, etc.)
- **Duration math** - Date arithmetic (now+8d, due-2w)
- **Relative dates** - Context-aware date parsing
- **Tag wildcards** - Pattern matching in tags
- **Project hierarchy** - Filter by project tree

---

## Collaboration Features

### Task Sharing
- **UUID-based identity** - Globally unique task identifiers
- **Export/Import** - Share task lists via JSON
- **Taskserver** - Central server for team synchronization
- **Conflict handling** - Merge changes from multiple sources

### Team Management
- **Annotations** - Team communication via task notes
- **Project organization** - Shared project structures
- **Tag conventions** - Collaborative tagging schemes
- **Dependency tracking** - Coordinate dependent work

---

## Advanced Capabilities

### Calculation and Evaluation
- **calc command** - Algebraic expression evaluation
- **Date math** - Complex date calculations
- **Urgency formulas** - Customizable urgency coefficients
- **Duration parsing** - Human-friendly duration input (1h, 30min, 2d)

### Automation Support
- **Helper commands** - Machine-readable output (_commands, _columns, etc.)
- **Script-friendly modes** - Minimal output for automation
- **Exit codes** - Reliable success/failure indication
- **Batch operations** - Process multiple tasks efficiently
- **Piping support** - Chain commands with shell pipes

### Platform Support
- **Cross-platform** - Linux, macOS, BSD, Windows (WSL)
- **UTF-8 support** - International character handling
- **Terminal adaptation** - Auto-detect terminal capabilities
- **Shell integration** - Completion for bash, zsh, and others

---

## Documentation and Support

### Built-in Help
- **help command** - Usage guide
- **man pages** - Comprehensive manual (task, taskrc, task-color, task-sync)
- **commands list** - All available commands with details
- **columns list** - Supported columns and formats
- **news command** - Release notes and migration guides

### Diagnostic Tools
- **diagnostics** - System and configuration analysis
- **version info** - Build and platform details
- **logo** - Taskwarrior branding
- **show command** - View current configuration

---

## Security and Privacy

### Data Protection
- **Local storage** - Data stays on your machine by default
- **Optional sync** - Choose whether to use Taskserver
- **Encrypted sync** - Secure data transmission
- **File permissions** - Standard filesystem security

### Audit Trail
- **Modification history** - Complete change tracking
- **Undo capability** - Revert accidental changes
- **Information command** - View full task history
- **Timestamps** - All changes are timestamped

---

## Performance Features

### Efficiency
- **Fast filtering** - Optimized query processing
- **Minimal overhead** - Lightweight command execution
- **Lazy evaluation** - Efficient handling of large task lists
- **Index support** - Quick ID-based lookups

### Scalability
- **Handles thousands of tasks** - Efficient data structures
- **Archive old tasks** - Maintain performance
- **GC support** - Garbage collection for completed/deleted tasks
- **Purge capability** - Remove old deleted tasks

---

## Special Features

### Waiting Tasks
- **wait attribute** - Hide tasks until a date
- **waiting report** - View postponed tasks
- **Automatic unhiding** - Tasks appear when wait date passes

### Recurring Tasks
- **Flexible patterns** - daily, weekly, monthly, yearly, or custom (e.g., "3days")
- **Template management** - Parent tasks define recurrence
- **Instance generation** - Automatic creation of task instances
- **Until date** - Set recurrence end date
- **Modification propagation** - Changes can affect future instances

### Virtual Tags
- **PENDING** - Active tasks
- **COMPLETED** - Finished tasks
- **DELETED** - Removed tasks
- **BLOCKING** - Tasks that block others
- **BLOCKED** - Tasks with dependencies
- **UNBLOCKED** - Tasks ready to work
- **OVERDUE** - Past due date
- **ACTIVE** - Currently started tasks
- **TODAY** - Due today
- **TOMORROW** - Due tomorrow
- **WEEK/MONTH/QUARTER/YEAR** - Due within period
- **READY** - Actionable tasks
- **PARENT** - Recurring task templates
- **CHILD** - Recurring task instances
- **UNTIL** - Tasks with until date
- **WAITING** - Tasks with wait date
- **ANNOTATED** - Tasks with annotations
- **TAGGED** - Tasks with any tag
- **LATEST** - Most recently added task
- **ORPHAN** - Tasks with invalid dependencies

---

## Summary

Taskwarrior is a feature-rich, extensible task management system designed for power users who prefer the command line. It combines simple basic operations with sophisticated features like urgency calculations, dependency tracking, recurring tasks, and extensive customization options. Whether managing personal todos or coordinating team projects, Taskwarrior provides the flexibility and power to adapt to your workflow.
