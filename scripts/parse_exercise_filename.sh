#!/bin/bash
# Usage: parse_exercise_filename.sh <filename.c>
# Outputs: KEY=value pairs (eval-able) or exits 1 with an error message.

if [ -z "$1" ]; then
    echo "Usage: $0 <filename.c>"
    exit 1
fi

if [[ "$1" != *.c ]]; then
    echo "ERROR: File '$1' is not a .c file. Please ensure you have an active C file open."
    exit 1
fi

FILE=$(basename "$1" .c)
IFS='_' read -r TOPIC LEVEL_STR VARIANT STUDENT_ID <<< "$FILE"

if [[ -z "$TOPIC" || -z "$LEVEL_STR" || -z "$VARIANT" || -z "$STUDENT_ID" ]]; then
    echo "ERROR: Filename '$1' does not match convention TOPIC_Ln_variant_studentid.c"
    exit 1
fi

LEVEL="${LEVEL_STR#L}"  # Strip leading 'L'

if ! [[ "$LEVEL" =~ ^[1-3]$ ]]; then
    echo "ERROR: Level must be 1, 2, or 3. Got: '$LEVEL' (from '$LEVEL_STR')"
    exit 1
fi

if ! [[ "$VARIANT" =~ ^[a-z]$ ]]; then
    echo "ERROR: Variant must be a single lowercase letter. Got: '$VARIANT'"
    exit 1
fi

echo "TOPIC=$TOPIC"
echo "LEVEL=$LEVEL"
echo "VARIANT=$VARIANT"
echo "STUDENT_ID=$STUDENT_ID"
