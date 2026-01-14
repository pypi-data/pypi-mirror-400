<div align="center">

# ⚡ Task-NG

**Powerful task management for the command line**

[![pipeline](https://gitlab.com/mathias.ewald/task-ng/badges/main/pipeline.svg)](https://gitlab.com/mathias.ewald/task-ng/-/pipelines)
[![coverage](https://gitlab.com/mathias.ewald/task-ng/badges/main/coverage.svg?job=coverage)](https://gitlab.com/mathias.ewald/task-ng/-/graphs/main/charts)

[**User Guide**](docs/USER_GUIDE.md) • [**Architecture**](docs/ARCHITECTURE.md)

</div>

---

## Quick Installation

### PyPI (Recommended)

```bash
pipx install task-ng
```

Or with pip:

```bash
pip install task-ng
```

### From Source

```bash
curl -fsSL https://gitlab.com/mathias.ewald/task-ng/-/raw/main/scripts/install.sh | bash
```

or try this if you don't have `curl` installed:

```bash
wget -qO- https://gitlab.com/mathias.ewald/task-ng/-/raw/main/scripts/install.sh | bash
```

Refer to the [User Guide](./docs/USER_GUIDE.md) for other installation options.

---

## Screenshots

<table>
<tr>
<td align="center" width="50%"><img src="docs/screenshots/task-list.png" width="100%" /><br/><em>Task list with filters</em></td>
<td align="center" width="50%"><img src="docs/screenshots/task-show.png" width="100%" /><br/><em>Detailed task view</em></td>
</tr>
<tr>
<td align="center"><img src="docs/screenshots/board.png" width="100%" /><br/><em>Kanban board</em></td>
<td align="center"><img src="docs/screenshots/calendar-month.png" width="100%" /><br/><em>Monthly calendar</em></td>
</tr>
<tr>
<td align="center"><img src="docs/screenshots/report.png" width="100%" /><br/><em>Custom reports</em></td>
<td align="center"><img src="docs/screenshots/task-edit.png" width="100%" /><br/><em>Interactive editor</em></td>
</tr>
<tr>
<td align="center"><img src="docs/screenshots/calendar-week.png" width="100%" /><br/><em>Weekly calendar</em></td>
<td align="center"><img src="docs/screenshots/context.png" width="100%" /><br/><em>Context switching</em></td>
</tr>
</table>

---

## Highlights

<table>
<tr>
<td width="50%">

### 🗓️ Natural Language Dates
Schedule tasks the way you think—*"tomorrow"*, *"next friday"*, *"in 3 days"*, or *"end of month"*. No more mental date math.

</td>
<td width="50%">

### 🔍 Powerful Filtering
Find exactly what you need: `project:Work +urgent priority:H due:today`. Combine any attributes for precise task selection.

</td>
</tr>
<tr>
<td width="50%">

### 🔄 Recurring Tasks
Set it and forget it. Daily standups, weekly reviews, monthly reports—tasks automatically regenerate when completed.

</td>
<td width="50%">

### 📊 Visual Views
Kanban boards for workflow visualization. Calendar views for time-based planning. See your tasks the way that works for you.

</td>
</tr>
<tr>
<td width="50%">

### ⚡ Dependencies & Blocking
Chain tasks together. Task B waits until Task A is done. Perfect for projects with sequential steps.

</td>
<td width="50%">

### 🤖 Automation Ready
JSON output mode for scripting. Pipe to `jq`, integrate with CI/CD, or build your own dashboards.

</td>
</tr>
</table>

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by [Taskwarrior](https://taskwarrior.org/), a fantastic command-line task management tool.
