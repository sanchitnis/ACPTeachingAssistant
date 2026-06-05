#!/bin/bash
# Usage: next.sh <student_id>
# Reads student_data/progress/<student_id>.json, selects the next exercise,
# creates the .c file from the template, and prints instructions.
#
# Requires: jq, python3

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ── Dependency Check ──────────────────────────────────────────────────────────
for tool in jq python3; do
    if ! command -v "$tool" &> /dev/null; then
        echo "ERROR: Tool '$tool' is not installed or not in PATH."
        echo "       Please refer to the Prerequisites section in README.md"
        exit 1
    fi
done

STUDENT_ID="${1:-}"
if [ -z "$STUDENT_ID" ]; then
    echo "Usage: $0 <student_id>"
    exit 1
fi

PROGRESS_FILE="$PROJECT_ROOT/student_data/progress/${STUDENT_ID}.json"
LIBRARY_FILE="$PROJECT_ROOT/exercises/practice.json"

if [ ! -f "$PROGRESS_FILE" ]; then
    echo "ERROR: No progress file for '$STUDENT_ID'."
    echo "       Expected: student_data/progress/${STUDENT_ID}.json"
    echo "Run: ./scripts/init_student.sh $STUDENT_ID \"<Full Name>\" \"<Section>\" \"<1st Sem Grade>\""
    exit 1
fi

# ── Find the next topic and level ─────────────────────────────────────────────
# Cross-reference library.json for syllabus_unit (not stored in progress.json).
# Filter out locked topics (assigned_level == null) and _prereq_/_adv_ prefixed
# topics (those are not sequenced by next.sh — they are unlocked manually).
NEXT=$(jq -r --slurpfile lib "$LIBRARY_FILE" '
  .topics | to_entries
  | map(select(
      (.key | startswith("_") | not)
      and .value.assigned_level != null
      and .value.demonstrated_level < 3
    ))
  | map(. + { unit: ($lib[0].topics[.key].syllabus_unit // 99) })
  | sort_by(.unit)
  | .[0]
  | "\(.key) \(.value.assigned_level)"
' "$PROGRESS_FILE")

if [ -z "$NEXT" ] || [ "$NEXT" = "null null" ]; then
    echo "🎉 Congratulations! All available topics are at Level 3 (demonstrated)."
    echo "   Ask your faculty for advanced exercises."
    exit 0
fi

TOPIC=$(echo "$NEXT" | cut -d' ' -f1)
LEVEL=$(echo "$NEXT" | cut -d' ' -f2)

# ── Find a variant not yet attempted at this topic+level ──────────────────────
ATTEMPTED=$(jq -r --arg t "$TOPIC" --arg l "$LEVEL" '
  .sessions
  | map(select(.exercise_id | startswith($t + "_L" + $l)))
  | .[].exercise_id
' "$PROGRESS_FILE" 2>/dev/null | grep -oP '(?<=_L[0-9]_)[a-z]' || true)

EXERCISE_ID=""
for VARIANT in a b c d e; do
    if ! echo "$ATTEMPTED" | grep -qx "$VARIANT"; then
        EXERCISE_ID="${TOPIC}_L${LEVEL}_${VARIANT}"
        break
    fi
done

if [ -z "$EXERCISE_ID" ]; then
    echo "All variants at ${TOPIC} Level ${LEVEL} attempted. Promoting level..."
    # Force-promote: mastery assumed by exhaustion (§8.3 step 3)
    LEVEL=$(( LEVEL + 1 ))
    if [ "$LEVEL" -gt 3 ]; then
        echo "Topic $TOPIC fully mastered. Moving to next topic."
        # Let the agent handle the unlock; next run will pick a new topic.
        exit 0
    fi
    EXERCISE_ID="${TOPIC}_L${LEVEL}_a"
fi

# ── Verify exercise exists in library ─────────────────────────────────────────
EXERCISE_EXISTS=$(jq -r --arg eid "$EXERCISE_ID" \
    '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .id' \
    "$LIBRARY_FILE" 2>/dev/null || echo "")

if [ -z "$EXERCISE_EXISTS" ]; then
    echo "ERROR: Exercise '$EXERCISE_ID' not found in library.json."
    echo "       Ask your instructor to add it, or choose a different variant."
    exit 1
fi

# ── Create the exercise file from template ────────────────────────────────────
FILENAME="${TOPIC}_L${LEVEL}_${VARIANT}_${STUDENT_ID}.c"
FILEPATH="$PROJECT_ROOT/student_data/$FILENAME"

jq -r --arg eid "$EXERCISE_ID" \
    '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .problem_statement' \
    "$LIBRARY_FILE" | \
    python3 "$SCRIPT_DIR/make_template.py" "$FILEPATH" "$EXERCISE_ID" "$STUDENT_ID"

echo ""
echo "📝 Exercise assigned: $EXERCISE_ID"
echo "   File created:      student_data/$FILENAME"
echo "   Open in VS Code:   code student_data/$FILENAME"
echo ""
echo "Use the VS Code Tasks runner (REVA: Get Help / REVA: Grade My Code) to get support."
