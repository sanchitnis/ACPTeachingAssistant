#!/usr/bin/env python3
"""
Usage: grade.py <file.c>
Compiles, runs all test_cases from exercises/ JSON files, checks style,
and outputs the REVA-TUTOR-GRADE-CONTEXT block for the agent to grade.

Requires: gcc, cppcheck
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path

# Import helper scripts
sys.path.insert(0, os.path.dirname(__file__))
from parse_exercise_filename import parse_exercise_filename
from compile_check import compile_check
from check_style import check_style

def grade_code(filepath):
    """Generate grade context block."""
    if not filepath:
        print("ERROR: Usage: grade.py <file.c>")
        sys.exit(1)
    
    # Check file extension
    if not filepath.endswith('.c'):
        print("ERROR: The active file is not a C programming file (.c).")
        print("       Please open your active exercise file (e.g., student_data/FUNC_L1_a_raj22cs045.c) in the editor and run this task again.")
        sys.exit(1)
    
    if not os.path.isfile(filepath):
        print(f"ERROR: File '{filepath}' not found.")
        sys.exit(1)
    
    # Parse filename
    try:
        parsed = parse_exercise_filename(filepath)
    except SystemExit as e:
        raise
    
    topic = parsed['TOPIC']
    level = parsed['LEVEL']
    variant = parsed['VARIANT']
    student_id = parsed['STUDENT_ID']
    exercise_id = f"{topic}_L{level}_{variant}"
    
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Run compile and style checks
    compile_out = compile_check(filepath)
    style_out = check_style(filepath)
    
    # Run test cases
    test_results_lines = []
    pass_count = 0
    fail_count = 0
    
    # Fetch test cases
    test_cases = []
    for lib_file in ['practice.json', 'prerequisites.json', 'advanced.json', 'lab_programs.json']:
        lib_path = os.path.join(project_root, 'exercises', lib_file)
        if not os.path.isfile(lib_path):
            continue
        
        try:
            with open(lib_path, 'r') as f:
                library = json.load(f)
            
            # Find exercise
            topic_name = exercise_id.split('_')[0]
            if topic_name in library.get('topics', {}):
                for exercise in library['topics'][topic_name].get('exercises', []):
                    if exercise.get('id') == exercise_id:
                        test_cases = exercise.get('test_cases', [])
                        break
            
            if test_cases:
                break
        except:
            continue
    
    if not test_cases:
        print(f"ERROR: Exercise '{exercise_id}' not found in libraries.")
        print("       Check your filename: TOPIC_Ln_variant_studentid.c")
        sys.exit(1)
    
    # Try to run tests if binary exists
    temp_dir = tempfile.gettempdir()
    binary_path = os.path.join(temp_dir, 'reva_tutor_bin')
    
    if os.path.isfile(binary_path) and os.access(binary_path, os.X_OK):
        for tc in test_cases:
            input_val = tc.get('input', '')
            expected_output = tc.get('expected_output', '')
            case_label = tc.get('label', f"input={json.dumps(input_val)}")
            
            try:
                result = subprocess.run(
                    [binary_path],
                    input=input_val,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                actual = result.stdout
            except subprocess.TimeoutExpired:
                actual = "__TIMEOUT_OR_CRASH__"
            except:
                actual = "__ERROR__"
            
            # Normalize expected output (convert \n escape to actual newlines)
            expected_output = expected_output.replace('\\n', '\n')
            
            if actual.strip() == expected_output.strip():
                test_results_lines.append(f"  PASS: {case_label}")
                pass_count += 1
            else:
                test_results_lines.append(f"  FAIL: {case_label}")
                exp_preview = ' | '.join(expected_output.split('\n')[:3])
                act_preview = ' | '.join(actual.split('\n')[:3])
                test_results_lines.append(f"    Expected: {exp_preview}")
                test_results_lines.append(f"    Got:      {act_preview}")
                fail_count += 1
        
        test_results_lines.append(f"  Summary: {pass_count} passed, {fail_count} failed")
    else:
        test_results_lines.append("  (binary not available — compile failed)")
    
    # Save grade context block
    context_file = os.path.join(project_root, 'student_data', 'grade_context.txt')
    
    with open(context_file, 'w') as f:
        f.write("---REVA-TUTOR-GRADE-CONTEXT---\n")
        f.write(f"student_id:    {student_id}\n")
        f.write(f"exercise_id:   {exercise_id}\n")
        f.write(f"{compile_out}\n")
        f.write(f"{style_out}\n")
        f.write("test_results: |\n")
        
        for line in test_results_lines:
            f.write(f"{line}\n")
        
        f.write("student_code: |\n")
        with open(filepath, 'r') as src:
            for line in src:
                f.write(f"  {line}")
        
        f.write("---END-REVA-TUTOR-GRADE-CONTEXT---\n")
    
    print()
    print("✅ Grade context successfully saved to: student_data/grade_context.txt")
    print("👉 In the agent/chat window, attach this file (type '@grade_context.txt' or click '+') and ask the agent to grade your code!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Usage: grade.py <file.c>")
        sys.exit(1)
    
    grade_code(sys.argv[1])
