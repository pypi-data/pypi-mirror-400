#!/usr/bin/env bash
# Seed demo data for task-ng
# Usage: ./scripts/seed-demo-data.sh [--data-dir PATH]

set -e

# Pass through any arguments (like --data-dir)
ARGS="$@"

tn() {
    task-ng $ARGS "$@"
}

echo "Creating demo tasks..."

# Work tasks
tn add "Review quarterly report +urgent" -p Work -P H -d tomorrow
tn add "Update project documentation +docs" -p Work -P M -d friday
tn add "Prepare presentation slides +meeting" -p Work -P H -d monday
tn add "Plan team building event +team" -p Work -P L -w 3d

# Code tasks
tn add "Fix authentication bug +bug +backend" -p Code -P H -d today
tn add "Write unit tests for API +testing" -p Code -P M
tn add "Refactor database queries +performance" -p Code -P M -D 5
tn add "Review pull requests +review" -p Code -d today
tn add "Deploy feature to staging +deployment" -p Code -P H -d tomorrow

# Personal tasks
tn add "Buy groceries +shopping" -p Personal -P L -d saturday
tn add "Schedule dentist appointment +health" -p Personal
tn add "Call mom +family" -p Personal -d sunday

# Learning tasks
tn add "Read Clean Code chapter 5 +reading +learning" -p Learn
tn add "Complete Python course module +course" -p Learn -d "next week"
tn add "Practice typing speed +practice" -p Learn -r daily

# Add some annotations
tn annotate 1 "Received draft from finance team"
tn annotate 5 "Reported by user in issue #42"
tn annotate 9 "Feature branch created"

echo ""
echo "Demo data created successfully!"
echo "Run 'task-ng list' to see tasks"
