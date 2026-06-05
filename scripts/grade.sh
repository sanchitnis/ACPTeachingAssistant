#!/bin/bash
# Usage: grade.sh <file.c>
# Compiles, runs all test_cases from exercises/ JSON files, checks style,
# and outputs the REVA-TUTOR-GRADE-CONTEXT block for the agent to grade.
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

if [ ! -f "$FILE" ]; then
    echo "ERROR: File '$FILE' not found."
    exit 1
fi

# Parse filename → TOPIC, LEVEL, VARIANT, STUDENT_ID
PARSED=$(bash "$SCRIPT_DIR/parse_exercise_filename.sh" "$FILE")
if [ $? -ne 0 ]; then echo "$PARSED"; exit 1; fi
eval "$PARSED"

EXERCISE_ID="${TOPIC}_L${LEVEL}_${VARIANT}"

# ── Compile and style ─────────────────────────────────────────────────────────
COMPILE_OUT=$(bash "$SCRIPT_DIR/compile_check.sh" "$FILE")
STYLE_OUT=$(bash "$SCRIPT_DIR/check_style.sh" "$FILE")

# ── Run test cases ────────────────────────────────────────────────────────────
TEST_RESULTS_LINES=()
PASS_COUNT=0
FAIL_COUNT=0

# Pre-fetch test cases to check if exercise exists
TEST_CASES_BLOCK=$(
    jq -c --arg eid "$EXERCISE_ID" \
        '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .test_cases[]' \
        "$PROJECT_ROOT/exercises/practice.json" 2>/dev/null \
    || jq -c --arg eid "$EXERCISE_ID" \
        '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .test_cases[]' \
        "$PROJECT_ROOT/exercises/prerequisites.json" 2>/dev/null \
    || jq -c --arg eid "$EXERCISE_ID" \
        '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .test_cases[]' \
        "$PROJECT_ROOT/exercises/advanced.json" 2>/dev/null \
    || jq -c --arg eid "$EXERCISE_ID" \
        '.topics[$eid | split("_")[0]].exercises[] | select(.id == $eid) | .test_cases[]' \
        "$PROJECT_ROOT/exercises/lab_programs.json" 2>/dev/null
)

if [ -z "$TEST_CASES_BLOCK" ]; then
    echo "ERROR: Exercise '$EXERCISE_ID' not found in libraries."
    echo "       Check your filename: TOPIC_Ln_variant_studentid.c"
    exit 1
fi

if [ -f /tmp/reva_tutor_bin ]; then
    # Read test_cases array as newline-separated JSON objects
    while IFS= read -r tc; do
        [ -z "$tc" ] && continue
        INPUT_VAL=$(printf '%s' "$tc" | jq -r '.input')
        # Convert JSON \n escape to real newlines for comparison
        EXPECTED=$(printf '%s' "$tc" | jq -r '.expected_output' | sed 's/\\n/\n/g')
        CASE_LABEL=$(printf '%s' "$tc" | jq -r '.label // ("input=" + (.input | @json))')

        ACTUAL=$(printf '%s\n' "$INPUT_VAL" | timeout 5 /tmp/reva_tutor_bin 2>/dev/null || echo "__TIMEOUT_OR_CRASH__")

        if [ "$ACTUAL" = "$EXPECTED" ]; then
            TEST_RESULTS_LINES+=("  PASS: $CASE_LABEL")
            PASS_COUNT=$((PASS_COUNT + 1))
        else
            TEST_RESULTS_LINES+=("  FAIL: $CASE_LABEL")
            TEST_RESULTS_LINES+=("    Expected: $(printf '%s' "$EXPECTED" | head -3 | tr '\n' '|')")
            TEST_RESULTS_LINES+=("    Got:      $(printf '%s' "$ACTUAL"   | head -3 | tr '\n' '|')")
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    done <<< "$TEST_CASES_BLOCK"
    TEST_RESULTS_LINES+=("  Summary: $PASS_COUNT passed, $FAIL_COUNT failed")
else
    TEST_RESULTS_LINES+=("  (binary not available — compile failed)")
fi

# ── Save grade context block to student_data/grade_context.txt ─────────────────
CONTEXT_FILE="$PROJECT_ROOT/student_data/grade_context.txt"
{
  printf '%s\n'  "---REVA-TUTOR-GRADE-CONTEXT---"
  printf 'student_id:    %s\n' "$STUDENT_ID"
  printf 'exercise_id:   %s\n' "$EXERCISE_ID"
  printf '%s\n' "$COMPILE_OUT"
  printf '%s\n' "$STYLE_OUT"
  printf 'test_results: |\n'
  for line in "${TEST_RESULTS_LINES[@]}"; do
      printf '%s\n' "$line"
  done
  printf 'student_code: |\n'
  sed 's/^/  /' "$FILE"
  printf '%s\n'  "---END-REVA-TUTOR-GRADE-CONTEXT---"
} > "$CONTEXT_FILE"

echo ""
echo "✅ Grade context successfully saved to: student_data/grade_context.txt"
echo "👉 In the agent/chat window, attach this file (type '@grade_context.txt' or click '+') and ask the agent to grade your code!"
