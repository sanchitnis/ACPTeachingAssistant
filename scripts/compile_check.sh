#!/bin/bash
# Usage: compile_check.sh <file.c>
# Outputs YAML-style compile_status block for inclusion in the context block.
# Requires: gcc

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: $0 <file.c>"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "ERROR: File '$FILE' not found."
    exit 1
fi

BIN="/tmp/reva_tutor_bin_$$"

OUTPUT=$(gcc -Wall -Wextra -Wpedantic -std=c99 -o "$BIN" "$FILE" 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "compile_status: OK"
    # Capture any warnings that appeared even on success
    WARNINGS=$(gcc -Wall -Wextra -std=c99 -fsyntax-only "$FILE" 2>&1)
    if [ -n "$WARNINGS" ]; then
        echo "compile_warnings: |"
        echo "$WARNINGS" | sed 's/^/  /'
    fi
    # Rename to the stable path expected by grade.sh
    mv "$BIN" /tmp/reva_tutor_bin 2>/dev/null
else
    echo "compile_status: ERROR"
    echo "compile_output: |"
    echo "$OUTPUT" | sed 's/^/  /'
    rm -f "$BIN"
fi
