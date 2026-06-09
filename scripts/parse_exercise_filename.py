#!/usr/bin/env python3
"""
Usage: parse_exercise_filename.py <filename.c>
Outputs: JSON object with TOPIC, LEVEL, VARIANT, STUDENT_ID fields
"""

import sys
import os
import json
import re

def parse_exercise_filename(filepath):
    """Parse exercise filename and return components as JSON."""
    if not filepath:
        print(json.dumps({"error": "Usage: parse_exercise_filename.py <filename.c>"}), file=sys.stderr)
        sys.exit(1)
    
    if not filepath.endswith('.c'):
        print(json.dumps({"error": f"File '{filepath}' is not a .c file. Please ensure you have an active C file open."}), file=sys.stderr)
        sys.exit(1)
    
    # Extract filename without extension
    filename = os.path.splitext(os.path.basename(filepath))[0]
    
    # Split by underscore
    parts = filename.split('_')
    
    if len(parts) != 4:
        print(json.dumps({"error": f"Filename '{filepath}' does not match convention TOPIC_Ln_variant_studentid.c"}), file=sys.stderr)
        sys.exit(1)
    
    topic, level_str, variant, student_id = parts
    
    # Extract level number from Ln format
    level_match = re.match(r'^L(\d+)$', level_str)
    if not level_match:
        print(json.dumps({"error": f"Invalid level format: {level_str}. Expected L1, L2, or L3"}), file=sys.stderr)
        sys.exit(1)
    
    level = level_match.group(1)
    
    # Validate level is 1-3
    if level not in ('1', '2', '3'):
        print(json.dumps({"error": f"Level must be 1, 2, or 3. Got: '{level}' (from '{level_str}')"}), file=sys.stderr)
        sys.exit(1)
    
    # Validate variant is single lowercase letter
    if not re.match(r'^[a-z]$', variant):
        print(json.dumps({"error": f"Variant must be a single lowercase letter. Got: '{variant}'"}), file=sys.stderr)
        sys.exit(1)
    
    return {
        "TOPIC": topic,
        "LEVEL": level,
        "VARIANT": variant,
        "STUDENT_ID": student_id
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: parse_exercise_filename.py <filename.c>"}), file=sys.stderr)
        sys.exit(1)
    
    result = parse_exercise_filename(sys.argv[1])
    print(json.dumps(result))
