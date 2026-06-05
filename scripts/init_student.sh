#!/bin/bash
# Usage: init_student.sh <student_id> <name> <section> <grade>
# Creates student_data/progress/<student_id>.json with all ACP topics locked
# (assigned_level: null) except FUNC (ACP Unit 1 entry point), which starts
# at assigned_level = 1 (unless grade is low, which triggers prerequisites).
# Topics are unlocked by next.sh when a full syllabus unit is mastered.
#
# Requires: bash, date, mkdir

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ── Dependency Check ──────────────────────────────────────────────────────────
for tool in jq python3 gcc cppcheck; do
    if ! command -v "$tool" &> /dev/null; then
        echo "WARNING: Tool '$tool' is not installed. You will need it for later steps."
        echo "         Please refer to the Prerequisites section in README.md"
    fi
done

STUDENT_ID="${1:-}"
NAME="${2:-}"
SECTION="${3:-}"
GRADE_ARG="${4:-}"

if [ -z "$STUDENT_ID" ] || [ -z "$NAME" ] || [ -z "$SECTION" ]; then
    echo "Usage: $0 <student_id> \"<Full Name>\" \"<Section>\" [<1st sem grade>]"
    echo "Example: $0 raj22cs045 \"Raj Kumar\" \"BTech-CS-2B\" \"A+\""
    exit 1
fi

GRADE=""
if [ -n "$GRADE_ARG" ]; then
    GRADE=$(echo "$GRADE_ARG" | tr '[:lower:]' '[:upper:]' | xargs)
    if [[ ! "$GRADE" =~ ^(O|A\+|A|B\+|B|C\+|C|F)$ ]]; then
        echo "Warning: Invalid grade '$GRADE_ARG' provided. Reverting to interactive prompt."
        GRADE=""
    fi
fi

if [ -z "$GRADE" ]; then
    if [ -t 0 ]; then
        while [ -z "$GRADE" ]; do
            echo -n "Enter your 1st sem C Programming grade (O/A+/A/B+/B/C+/C/F): "
            read -r GRADE
            GRADE=$(echo "$GRADE" | tr '[:lower:]' '[:upper:]' | xargs)
            if [[ ! "$GRADE" =~ ^(O|A\+|A|B\+|B|C\+|C|F)$ ]]; then
                echo "Invalid grade. Please enter O, A+, A, B+, B, C+, C, or F."
                GRADE=""
            fi
        done
    else
        # Default fallback for automated environments
        GRADE="B"
    fi
fi

UNLOCK_PREREQS="false"
if [[ "$GRADE" == "C+" || "$GRADE" == "C" || "$GRADE" == "F" ]]; then
    UNLOCK_PREREQS="true"
    echo "⚠️  Grade ($GRADE) indicates catch-up is needed. Unlocking prerequisite topics first!"
fi

FUNC_ASSIGNED="1"
PREREQ_ASSIGNED="null"
if [ "$UNLOCK_PREREQS" = "true" ]; then
    FUNC_ASSIGNED="null"
    PREREQ_ASSIGNED="1"
fi

STUDENT_DATA="$PROJECT_ROOT/student_data"
PROGRESS_DIR="$STUDENT_DATA/progress"
SESSIONS_DIR="$STUDENT_DATA/sessions/${STUDENT_ID}"
PROGRESS_FILE="$PROGRESS_DIR/${STUDENT_ID}.json"

if [ -f "$PROGRESS_FILE" ]; then
    echo "ERROR: Progress file already exists for '$STUDENT_ID'. Aborting."
    echo "       To reset a student, manually delete $PROGRESS_FILE first."
    exit 1
fi

mkdir -p "$PROGRESS_DIR"
mkdir -p "$SESSIONS_DIR"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# ── ACP topic registry ─────────────────────────────────────────────────────────
# Prerequisite topics (prior course): locked by default; unlocked on demand.
# ACP syllabus topics: FUNC is the entry point (assigned_level=1); all others
#   locked and unlocked as each ACP unit is mastered.
# Advanced topics: permanently locked until all CO1-CO5 reach Level 3.

cat > "$PROGRESS_FILE" << EOF
{
  "student_id": "$STUDENT_ID",
  "name": "$NAME",
  "section": "$SECTION",
  "c_grade_sem1": "$GRADE",
  "created": "$NOW",
  "last_active": "$NOW",
  "overall_level": 1,
  "topics": {
    "FUNC":        { "assigned_level": $FUNC_ASSIGNED,    "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO1"] },
    "SCOPE":       { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO1"] },
    "ARRAY":       { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO1"] },
    "STRUCT":      { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO1","CO2"] },
    "ARRAYSTRUCT": { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO2"] },
    "PTR":         { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO3"] },
    "PTRARR":      { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO3"] },
    "PTRF":        { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO1","CO3"] },
    "DYNMEM":      { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO3"] },
    "LINKEDLIST":  { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO3"] },
    "STRING":      { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO4"] },
    "STROP":       { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO4"] },
    "FILE":        { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": ["CO5"] },
    "_prereq_INTRO":  { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_prereq_DTYPES": { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_prereq_OPS":    { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_prereq_IO":     { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_prereq_COND":   { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_prereq_LOOP":   { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_prereq_JUMP":   { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_adv_RECUR":  { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_adv_UNION":  { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_adv_ENUM":   { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] },
    "_adv_FSEEK":  { "assigned_level": null, "demonstrated_level": 0, "exercises_completed": 0, "last_score": null, "co_mapping": [] }
  },
  "sessions": []
}
EOF

echo "✅ Student registered: $STUDENT_ID ($NAME) — $SECTION (Sem 1 Grade: $GRADE)"
echo "   Progress file: $PROGRESS_FILE"
echo "   Sessions dir:  $SESSIONS_DIR"
echo ""
echo "Next step: ./scripts/next.sh $STUDENT_ID"
