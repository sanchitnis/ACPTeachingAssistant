#!/bin/bash
# Usage: check_style.sh <file.c>
# Checks S01–S10 style rules. Outputs YAML-compatible style_status block.
# Requires: cppcheck, awk, grep

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: $0 <file.c>"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "ERROR: File '$FILE' not found."
    exit 1
fi

VIOLATIONS=()

# ── cppcheck (covers unused vars, uninitialised vars, style issues) ───────────
CPPCHECK_OUT=$(cppcheck --enable=style,warning \
    --suppress=missingIncludeSystem \
    --suppress=checkersReport \
    "$FILE" 2>&1)

if [ -n "$CPPCHECK_OUT" ]; then
    while IFS= read -r line; do
        VIOLATIONS+=("$line")
    done <<< "$CPPCHECK_OUT"
fi

# ── S06: void main ────────────────────────────────────────────────────────────
if grep -qP 'void\s+main\s*\(' "$FILE"; then
    VIOLATIONS+=("S06: void main() found — main must return int")
fi

# ── S06: missing return 0 in main ────────────────────────────────────────────
if ! grep -q 'return\s*0\s*;' "$FILE"; then
    VIOLATIONS+=("S06: No 'return 0;' found in file")
fi

# ── S03: Magic numbers (literals > 1, not in comments or strings) ─────────────
MAGIC=$(grep -nP '(?<![0-9a-zA-Z_"])[2-9][0-9]{0,5}(?![0-9a-zA-Z_"])' "$FILE" \
        | grep -vP '^\s*(//|/\*)' \
        | grep -vP '"[^"]*[2-9][^"]*"')
if [ -n "$MAGIC" ]; then
    VIOLATIONS+=("S03: Possible magic number(s) — use named constants:")
    # Process substitution avoids subshell; array appends are preserved.
    while IFS= read -r mline; do
        VIOLATIONS+=("  $mline")
    done < <(echo "$MAGIC" | head -5)
fi

# ── S02: Declaration after first executable statement (C89 rule, awk check) ──
# Strategy: inside a function body (brace depth ≥ 1), once we see an executable
# statement, any subsequent type-keyword declaration is a violation.
S02_VIOLATIONS=$(awk '
BEGIN { depth=0; saw_exec=0; }
{
    # Track brace depth
    n = split($0, chars, "")
    for (i = 1; i <= n; i++) {
        if (chars[i] == "{") depth++
        if (chars[i] == "}") { depth--; if (depth == 0) saw_exec = 0 }
    }
    # Skip comments and blank lines
    if (/^[[:space:]]*(\/\/|\/\*|\*|$)/) next
    # Skip preprocessor
    if (/^[[:space:]]*#/) next

    if (depth >= 1) {
        # Is this line a type declaration?
        is_decl = /^[[:space:]]*(int|char|float|double|long|short|unsigned|signed|struct|union|enum|void|const|static|extern|auto|register)[[:space:]]+[a-zA-Z_]/
        if (is_decl && saw_exec) {
            print "S02: L" NR ": Declaration after executable statement"
        }
        if (!is_decl) saw_exec = 1
    }
}
' "$FILE")

if [ -n "$S02_VIOLATIONS" ]; then
    while IFS= read -r vline; do
        VIOLATIONS+=("$vline")
    done <<< "$S02_VIOLATIONS"
fi

# ── S08: Opening brace on new line ────────────────────────────────────────────
S08_VIOLATIONS=$(grep -nP '^\s*(if|else|for|while|do|switch)\b[^{]*$' "$FILE" \
    | grep -v '//')
if [ -n "$S08_VIOLATIONS" ]; then
    while IFS= read -r vline; do
        VIOLATIONS+=("S08: Control structure without opening brace on same line — L${vline%%:*}")
    done < <(echo "$S08_VIOLATIONS" | head -5)
fi

# ── Output ────────────────────────────────────────────────────────────────────
if [ ${#VIOLATIONS[@]} -eq 0 ]; then
    echo "style_status: OK"
else
    echo "style_status: VIOLATIONS"
    echo "style_output: |"
    for v in "${VIOLATIONS[@]}"; do
        echo "  $v"
    done
fi
