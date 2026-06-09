#!/usr/bin/env python3
"""
Usage: help.py <file.c>
Compiles and style-checks the file, then prints the REVA-TUTOR-CONTEXT
block that the student pastes into the agent chat.
help_request_n is tracked in temp dir so student_data/progress/ is not mutated mid-session.

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

def get_help(filepath):
    """Generate help context block."""
    if not filepath:
        print("ERROR: Usage: help.py <file.c>")
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
        # parse_exercise_filename calls sys.exit() on error
        raise
    
    topic = parsed['TOPIC']
    level = parsed['LEVEL']
    variant = parsed['VARIANT']
    student_id = parsed['STUDENT_ID']
    exercise_id = f"{topic}_L{level}_{variant}"
    
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    progress_file = os.path.join(project_root, 'student_data', 'progress', f'{student_id}.json')
    
    if not os.path.isfile(progress_file):
        print(f"ERROR: No progress file for '{student_id}'.")
        print(f"       Expected: student_data/progress/{student_id}.json")
        print(f"Run: python scripts/init_student.py {student_id} \"<Full Name>\" \"<Section>\" \"<1st Sem Grade>\"")
        sys.exit(1)
    
    # Increment help_request_n
    temp_dir = tempfile.gettempdir()
    help_count_file = os.path.join(temp_dir, f'reva_help_{student_id}_{exercise_id}')
    
    help_n = 1
    if os.path.isfile(help_count_file):
        try:
            with open(help_count_file, 'r') as f:
                help_n = int(f.read().strip()) + 1
        except:
            pass
    
    with open(help_count_file, 'w') as f:
        f.write(str(help_n))
    
    # Run compile and style checks
    compile_out = compile_check(filepath)
    style_out = check_style(filepath)
    
    # Load problem statement from library
    problem = "NOT_FOUND"
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
                        problem = exercise.get('problem_statement', 'NOT_FOUND')
                        break
            
            if problem != "NOT_FOUND":
                break
        except:
            continue
    
    if problem == "NOT_FOUND":
        print(f"ERROR: Exercise '{exercise_id}' not found in libraries.")
        print("       Check your filename: TOPIC_Ln_variant_studentid.c")
        sys.exit(1)
    
    # Load assigned_level from progress
    try:
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        assigned_level = progress.get('topics', {}).get(topic, {}).get('assigned_level', '?')
    except:
        assigned_level = '?'
    
    # Save context block
    context_file = os.path.join(project_root, 'student_data', 'help_context.txt')
    
    with open(context_file, 'w') as f:
        f.write("---REVA-TUTOR-CONTEXT---\n")
        f.write(f"student_id:        {student_id}\n")
        f.write(f"exercise_id:       {exercise_id}\n")
        f.write(f"assigned_level:    {assigned_level}\n")
        f.write(f"help_request_n:    {help_n}\n")
        f.write(f"{compile_out}\n")
        f.write(f"{style_out}\n")
        f.write("student_code: |\n")
        
        with open(filepath, 'r') as src:
            for line in src:
                f.write(f"  {line}")
        
        f.write("problem_statement: |\n")
        for line in problem.split('\n'):
            f.write(f"  {line}\n")
        
        f.write("---END-REVA-TUTOR-CONTEXT---\n")
    
    print()
    print("✅ Help context successfully saved to: student_data/help_context.txt")
    print("👉 In the agent/chat window, attach this file (type '@help_context.txt' or click '+') and ask the agent for help!")
    print(f"   Help request #{help_n} for {exercise_id}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Usage: help.py <file.c>")
        sys.exit(1)
    
    get_help(sys.argv[1])
