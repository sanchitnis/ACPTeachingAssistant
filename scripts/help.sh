#!/bin/bash
# Usage: help.sh <file.c>
# Compiles and style-checks the file, then prints the REVA-TUTOR-CONTEXT
# block that the student pastes into the agent chat.
# help_request_n is tracked in /tmp so student_data/progress/ is not mutated mid-session.
#
# Requires: gcc, cppcheck, jq

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ── Dependency Check ──────────────────────────────────────────────────────────
for tool in gcc cppcheck jq; do
    if ! command -v "$tool" &> /dev/null; then
        echo "ERROR: Tool '$tool' is not installed or not in PATH."
        echo "       Please refer to the Prerequisites section in README.md"
        exit 1
    fi
done

FILE="${1:-}"
if [ -z "$FILE" ]; then
    echo "Usage: $0 <file.c>"
    exit 1
fi

# Check file extension
if [[ "$FILE" != *.c ]]; then
    echo "ERROR: The active file is not a C programming file (.c)."
    echo "       Please open your active exercise file (e.g., student_data/FUNC_L1_a_raj22cs045.c) in the editor and run this task again."
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "ERROR: File '$FILE' not found."
    exit 1
fi

# Parse filename → TOPIC, LEVEL, VARIANT, STUDENT_ID
PARSED=$(bash "$SCRIPT_DIR/parse_exercise_filename.sh" "$FILE")
if [ $? -ne 0 ]; then echo "$PARSED"; exit 1; fi
eval "$PARSED"

EXERCISE_ID="${TOPIC}_L${LEVEL}_${VARIANT}"
PROGRESS_FILE="$PROJECT_ROOT/student_data/progress/${STUDENT_ID}.json"

if [ ! -f "$PROGRESS_FILE" ]; then
    echo "ERROR: No progress file for '$STUDENT_ID'."
    echo "       Expected: student_data/progress/${STUDENT_ID}.json"
    echo "Run: ./scripts/init_student.sh $STUDENT_ID \"<Full Name>\" \"<Section>\" \"<1st Sem Grade>\""
    exit 1
fi

# ── Increment help_request_n ──────────────────────────────────────────────────
# Stored in a temp file per (student, exercise) — survives between shell
# invocations within the same working session.
HELP_COUNT_FILE="/tmp/reva_help_${STUDENT_ID}_${EXERCISE_ID}"
HELP_N=1
if [ -f "$HELP_COUNT_FILE" ]; then
    HELP_N=$(( $(cat "$HELP_COUNT_FILE") + 1 ))
fi
echo "$HELP_N" > "$HELP_COUNT_FILE"

# ── Run compile and style checks ──────────────────────────────────────────────
COMPILE_OUT=$(bash "$SCRIPT_DIR/compile_check.sh" "$FILE")
STYLE_OUT=$(bash "$SCRIPT_DIR/check_style.sh" "$FILE")

# ── Load problem statement from library ───────────────────────────────────────
PROBLEM=$(jq -r --arg eid "$EXERCISE_ID" \
    '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .problem_statement' \
    "$PROJECT_ROOT/exercises/practice.json" 2>/dev/null \
  || jq -r --arg eid "$EXERCISE_ID" \
    '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .problem_statement' \
    "$PROJECT_ROOT/exercises/prerequisites.json" 2>/dev/null \
  || jq -r --arg eid "$EXERCISE_ID" \
    '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .problem_statement' \
    "$PROJECT_ROOT/exercises/advanced.json" 2>/dev/null \
  || jq -r --arg eid "$EXERCISE_ID" \
    '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .problem_statement' \
    "$PROJECT_ROOT/exercises/lab_programs.json" 2>/dev/null \
  || echo "NOT_FOUND")

if [ "$PROBLEM" = "NOT_FOUND" ]; then
    echo "ERROR: Exercise '$EXERCISE_ID' not found in libraries."
    echo "       Check your filename: TOPIC_Ln_variant_studentid.c"
    exit 1
fi

# ── Load assigned_level from progress ─────────────────────────────────────────
ASSIGNED_LEVEL=$(jq -r --arg t "$TOPIC" \
    '.topics[$t].assigned_level // "?"' \
    "$PROGRESS_FILE")

# ── Save context block to student_data/help_context.txt ────────────────────────
CONTEXT_FILE="$PROJECT_ROOT/student_data/help_context.txt"
{
  printf '%s\n'   "---REVA-TUTOR-CONTEXT---"
  printf 'student_id:        %s\n' "$STUDENT_ID"
  printf 'exercise_id:       %s\n' "$EXERCISE_ID"
  printf 'assigned_level:    %s\n' "$ASSIGNED_LEVEL"
  printf 'help_request_n:    %s\n' "$HELP_N"
  printf '%s\n' "$COMPILE_OUT"
  printf '%s\n' "$STYLE_OUT"
  printf 'student_code: |\n'
  sed 's/^/  /' "$FILE"
  printf 'problem_statement: |\n'
  echo "$PROBLEM" | sed 's/^/  /'
  printf '%s\n'   "---END-REVA-TUTOR-CONTEXT---"
} > "$CONTEXT_FILE"

echo ""
echo "✅ Help context successfully saved to: student_data/help_context.txt"
echo "👉 In the agent/chat window, attach this file (type '@help_context.txt' or click '+') and ask the agent for help!"
echo "   Help request #${HELP_N} for ${EXERCISE_ID}"
