#!/bin/bash
set -e

MAX_ITERATIONS="${RALPH_MAX_ITERATIONS:-10}"
STATE_FILE=".autonomous-claude/.ralph-state"

mkdir -p "$(dirname "$STATE_FILE")"

if [ -f "$STATE_FILE" ]; then
    ITERATION=$(cat "$STATE_FILE")
else
    ITERATION=0
fi

ITERATION=$((ITERATION + 1))
echo "$ITERATION" > "$STATE_FILE"

if [ "$ITERATION" -ge "$MAX_ITERATIONS" ]; then
    rm -f "$STATE_FILE"
    exit 0
fi

# Count actionable issues (excludes 'needs-info' which are awaiting human response)
ACTIONABLE_ISSUES=$(gh issue list --state open --json number,labels 2>/dev/null | jq '[.[] | select(.labels | map(.name) | index("needs-info") | not)] | length' 2>/dev/null || echo "0")

if [ "$ACTIONABLE_ISSUES" = "0" ]; then
    rm -f "$STATE_FILE"
    exit 0
fi

echo "{\"decision\": \"block\", \"reason\": \"Iteration $ITERATION/$MAX_ITERATIONS. $ACTIONABLE_ISSUES actionable issues remaining.\"}"
