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

OPEN_ISSUES=$(gh issue list --label autonomous-claude --state open --json number 2>/dev/null | jq 'length' 2>/dev/null || echo "0")

if [ "$OPEN_ISSUES" = "0" ]; then
    rm -f "$STATE_FILE"
    exit 0
fi

echo "{\"decision\": \"block\", \"reason\": \"Iteration $ITERATION/$MAX_ITERATIONS. $OPEN_ISSUES issues remaining.\"}"
