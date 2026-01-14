#!/usr/bin/env bash
# Populate a task-ng database with demo tasks showcasing all features
# Usage: ./scripts/populate_demo.sh [--data-dir /path/to/data]

set -e

# Pass through any arguments (like --data-dir)
TASK_NG="task-ng $*"

echo "Populating task-ng database with demo tasks..."
echo ""

# ============================================================================
# Basic tasks with projects and priorities
# ============================================================================
echo "=== Creating basic tasks with projects and priorities ==="

$TASK_NG add "Review quarterly budget report" -p Finance -P H
$TASK_NG add "Update team wiki documentation" -p Engineering.Docs -P M
$TASK_NG add "Prepare presentation slides" -p Marketing -P H
$TASK_NG add "Code review for authentication module" -p Engineering.Backend -P H
$TASK_NG add "Design new landing page mockups" -p Engineering.Frontend -P M
$TASK_NG add "Write unit tests for API endpoints" -p Engineering.Backend -P M
$TASK_NG add "Organize team building event" -p HR -P L
$TASK_NG add "Update dependency versions" -p Engineering.DevOps -P L

# ============================================================================
# Tasks with tags
# ============================================================================
echo ""
echo "=== Creating tasks with tags ==="

$TASK_NG add "Fix critical login bug +urgent +bug" -p Engineering.Backend -P H
$TASK_NG add "Implement dark mode +feature +ui" -p Engineering.Frontend -P M
$TASK_NG add "Database migration script +devops +urgent" -p Engineering.DevOps -P H
$TASK_NG add "Customer feedback analysis +research +meeting" -p Marketing -P M
$TASK_NG add "Security audit preparation +security +compliance" -p Engineering -P H
$TASK_NG add "Performance optimization +optimization +backend" -p Engineering.Backend -P M

# ============================================================================
# Tasks with due dates
# ============================================================================
echo ""
echo "=== Creating tasks with due dates ==="

$TASK_NG add "Submit expense reports" -p Finance -P M --due "today"
$TASK_NG add "Weekly standup meeting notes" -p Engineering --due "tomorrow"
$TASK_NG add "Client presentation" -p Marketing -P H --due "friday"
$TASK_NG add "Sprint planning session" -p Engineering --due "next monday"
$TASK_NG add "Quarterly review preparation" -p HR -P M --due "end of month"
$TASK_NG add "Conference talk submission" -p Engineering -P L --due "2025-01-15"

# ============================================================================
# Tasks with wait and scheduled dates
# ============================================================================
echo ""
echo "=== Creating tasks with wait/scheduled dates ==="

$TASK_NG add "Follow up on proposal" -p Marketing --wait "3d" -P M
$TASK_NG add "Check deployment status" -p Engineering.DevOps --wait "tomorrow"
$TASK_NG add "Review pull requests" -p Engineering --scheduled "monday"
$TASK_NG add "Prepare monthly report" -p Finance --scheduled "2025-01-01" -P M

# ============================================================================
# Recurring tasks
# ============================================================================
echo ""
echo "=== Creating recurring tasks ==="

$TASK_NG add "Daily standup" -p Engineering --recur daily --due "tomorrow"
$TASK_NG add "Weekly team sync" -p Engineering --recur weekly --due "next monday"
$TASK_NG add "Backup verification" -p Engineering.DevOps --recur "2d" --due "tomorrow" -P M
$TASK_NG add "Monthly metrics review" -p Finance --recur monthly --due "end of month" -P H
$TASK_NG add "Quarterly security scan" -p Engineering --recur "3m" --due "2025-03-01" -P H

# ============================================================================
# Tasks with dependencies
# ============================================================================
echo ""
echo "=== Creating tasks with dependencies ==="

# First create the prerequisite tasks
$TASK_NG add "Design database schema" -p Engineering.Backend -P H
$TASK_NG add "Set up CI pipeline" -p Engineering.DevOps -P H
$TASK_NG add "Write API specification" -p Engineering.Backend -P M

# Now create dependent tasks (assuming IDs 27, 28, 29 for the above)
$TASK_NG add "Implement user service" -p Engineering.Backend -P H --depends 27,29
$TASK_NG add "Deploy to staging" -p Engineering.DevOps -P M --depends 28
$TASK_NG add "Integration testing" -p Engineering -P H --depends 30,31

# ============================================================================
# Tasks with UDAs (User Defined Attributes)
# ============================================================================
echo ""
echo "=== Creating tasks with custom attributes ==="

$TASK_NG add "Customer support ticket ticket:12345 severity:high" -p Support -P H
$TASK_NG add "Bug investigation ticket:12346 severity:medium component:auth" -p Engineering -P M
$TASK_NG add "Feature request ticket:12347 votes:42 component:ui" -p Engineering.Frontend -P L
$TASK_NG add "Infrastructure upgrade cost:5000 vendor:aws" -p Engineering.DevOps -P M
$TASK_NG add "Training session duration:2h attendees:15" -p HR -P M

# ============================================================================
# Add annotations to some tasks
# ============================================================================
echo ""
echo "=== Adding annotations to tasks ==="

$TASK_NG annotate 1 "Discussed with CFO - need by EOD Friday"
$TASK_NG annotate 1 "Include Q3 projections"
$TASK_NG annotate 9 "Reproducible on Chrome and Firefox"
$TASK_NG annotate 9 "Possibly related to session timeout"
$TASK_NG annotate 13 "Client prefers morning slot"
$TASK_NG annotate 27 "Use PostgreSQL with partitioning"

# ============================================================================
# Complete some tasks
# ============================================================================
echo ""
echo "=== Completing some tasks ==="

$TASK_NG done 7  # Organize team building event
$TASK_NG done 8  # Update dependency versions

# ============================================================================
# Start time tracking on a task
# ============================================================================
echo ""
echo "=== Starting time tracking ==="

$TASK_NG start 4  # Code review for authentication module

# ============================================================================
# Create contexts in config (informational)
# ============================================================================
echo ""
echo "=== Summary ==="
echo ""
echo "Demo database populated successfully!"
echo ""
echo "Tasks created:"
echo "  - Basic tasks with projects and priorities"
echo "  - Tasks with tags (+urgent, +bug, +feature, etc.)"
echo "  - Tasks with due dates (today, tomorrow, friday, etc.)"
echo "  - Tasks with wait/scheduled dates"
echo "  - Recurring tasks (daily, weekly, monthly)"
echo "  - Tasks with dependencies"
echo "  - Tasks with custom attributes (UDAs)"
echo "  - Tasks with annotations"
echo "  - Completed tasks"
echo "  - Active task (time tracking)"
echo ""
echo "Try these commands:"
echo "  task-ng list                    # List all pending tasks"
echo "  task-ng list +urgent            # Filter by tag"
echo "  task-ng list project:Engineering# Filter by project"
echo "  task-ng list project.not:HR     # Exclude project"
echo "  task-ng list +OVERDUE           # Virtual tag for overdue"
echo "  task-ng list +DUE               # Tasks with due dates"
echo "  task-ng list +BLOCKED           # Blocked by dependencies"
echo "  task-ng report next             # Most urgent tasks"
echo "  task-ng report overdue          # Overdue tasks"
echo "  task-ng stats                   # Task statistics"
echo "  task-ng projects                # List all projects"
echo "  task-ng tags                    # List all tags"
echo "  task-ng show 1                  # Show task details"
echo "  task-ng active                  # Show active task"
echo ""
echo "To set up contexts, add to ~/.config/taskng/config.toml:"
echo ""
echo '  [context.work]'
echo '  description = "Work tasks only"'
echo '  project = "Engineering"'
echo ""
echo '  [context.urgent]'
echo '  description = "Urgent tasks"'
echo '  tags = ["urgent"]'
