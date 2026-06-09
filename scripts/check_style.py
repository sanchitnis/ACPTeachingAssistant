#!/usr/bin/env python3
"""
Usage: check_style.py <file.c>
Checks S01–S10 style rules. Outputs YAML-compatible style_status block.
Requires: cppcheck
"""

import sys
import os
import subprocess
import re

def check_style(filepath):
    """Check C file style and return YAML-formatted violations."""
    if not filepath:
        print("ERROR: Usage: check_style.py <file.c>")
        sys.exit(1)
    
    if not os.path.isfile(filepath):
        print(f"ERROR: File '{filepath}' not found.")
        sys.exit(1)
    
    violations = []
    
    # ── cppcheck (covers unused vars, uninitialised vars, style issues) ───────
    try:
        result = subprocess.run(
            ['cppcheck', '--enable=style,warning',
             '--suppress=missingIncludeSystem',
             '--suppress=checkersReport',
             filepath],
            capture_output=True,
            text=True
        )
        if result.stderr:
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    violations.append(line.strip())
    except FileNotFoundError:
        violations.append("WARNING: cppcheck not found in PATH")
    
    # Read file for pattern-based checks
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    # ── S06: void main ─────────────────────────────────────────────────────────
    if re.search(r'void\s+main\s*\(', content):
        violations.append("S06: void main() found — main must return int")
    
    # ── S06: missing return 0 in main ──────────────────────────────────────────
    if not re.search(r'return\s*0\s*;', content):
        violations.append("S06: No 'return 0;' found in file")
    
    # ── S03: Magic numbers (literals > 1, not in comments or strings) ──────────
    magic_violations = []
    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('//') or line.strip().startswith('/*'):
            continue
        
        # Remove string content and comments from line
        clean_line = re.sub(r'"[^"]*"', '""', line)  # Remove strings
        clean_line = re.sub(r'//.*', '', clean_line)  # Remove line comments
        
        # Find magic numbers (2-9 followed by 0-5 digits, not part of identifiers)
        matches = re.finditer(r'(?<![0-9a-zA-Z_"])([2-9][0-9]{0,5})(?![0-9a-zA-Z_"])', clean_line)
        for match in matches:
            magic_violations.append(f"  L{i}: {line.rstrip()}")
            break  # Only report once per line
    
    if magic_violations and len(magic_violations) <= 5:
        violations.append("S03: Possible magic number(s) — use named constants:")
        violations.extend(magic_violations)
    elif magic_violations:
        violations.append("S03: Possible magic number(s) — use named constants:")
        violations.extend(magic_violations[:5])
    
    # ── S02: Declaration after first executable statement (C89 rule) ──────────
    brace_depth = 0
    saw_exec = False
    s02_violations = []
    
    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('//') or line.strip().startswith('/*'):
            continue
        
        # Track brace depth
        brace_depth += line.count('{') - line.count('}')
        
        # Reset when exiting function
        if brace_depth == 0:
            saw_exec = False
        
        # Skip preprocessor
        if line.strip().startswith('#'):
            continue
        
        if brace_depth >= 1:
            # Check if this is a type declaration
            decl_pattern = r'^\s*(int|char|float|double|long|short|unsigned|signed|struct|union|enum|void|const|static|extern|auto|register)\s+[a-zA-Z_]'
            is_decl = bool(re.match(decl_pattern, line))
            
            if is_decl and saw_exec:
                s02_violations.append(f"S02: L{i}: Declaration after executable statement")
            
            if not is_decl and line.strip() and not line.strip().startswith('}'):
                saw_exec = True
    
    violations.extend(s02_violations)
    
    # ── S08: Opening brace on new line ─────────────────────────────────────────
    s08_violations = []
    for i, line in enumerate(lines, 1):
        # Skip comments
        if '//' in line:
            line = line[:line.index('//')]
        
        # Check for control structures without opening brace on same line
        if re.match(r'^\s*(if|else|for|while|do|switch)\b', line):
            if not '{' in line:
                s08_violations.append(f"S08: Control structure without opening brace on same line — L{i}")
    
    if s08_violations and len(s08_violations) <= 5:
        violations.extend(s08_violations)
    elif s08_violations:
        violations.extend(s08_violations[:5])
    
    # ── Output ────────────────────────────────────────────────────────────────
    if not violations:
        return "style_status: OK"
    else:
        output = ["style_status: VIOLATIONS", "style_output: |"]
        for v in violations:
            output.append(f"  {v}")
        return '\n'.join(output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Usage: check_style.py <file.c>")
        sys.exit(1)
    
    result = check_style(sys.argv[1])
    print(result)
