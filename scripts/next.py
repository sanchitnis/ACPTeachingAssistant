#!/usr/bin/env python3
"""
Usage: next.py <student_id>
Reads student_data/progress/<student_id>.json, selects the next exercise,
creates the .c file from the template, and prints instructions.

Requires: python3
"""

import sys
import os
import json
import subprocess
from pathlib import Path

def get_next_exercise(student_id):
    """Get the next exercise for a student."""
    if not student_id:
        print("ERROR: Usage: next.py <student_id>")
        sys.exit(1)
    
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    progress_file = os.path.join(project_root, 'student_data', 'progress', f'{student_id}.json')
    library_file = os.path.join(project_root, 'exercises', 'practice.json')
    
    if not os.path.isfile(progress_file):
        print(f"ERROR: No progress file for '{student_id}'.")
        print(f"       Expected: student_data/progress/{student_id}.json")
        print(f"Run: python scripts/init_student.py {student_id} \"<Full Name>\" \"<Section>\" \"<1st Sem Grade>\"")
        sys.exit(1)
    
    # Load progress and library
    with open(progress_file, 'r') as f:
        progress = json.load(f)
    
    with open(library_file, 'r') as f:
        library = json.load(f)
    
    # Find next topic and level
    # Filter out locked topics and _prereq_/_adv_ prefixed topics
    candidates = []
    for topic_name, topic_data in progress['topics'].items():
        if topic_name.startswith('_'):
            continue
        
        assigned_level = topic_data.get('assigned_level')
        demonstrated_level = topic_data.get('demonstrated_level', 0)
        
        if assigned_level is not None and demonstrated_level < 3:
            syllabus_unit = library.get('topics', {}).get(topic_name, {}).get('syllabus_unit', 99)
            candidates.append({
                'name': topic_name,
                'assigned_level': assigned_level,
                'unit': syllabus_unit
            })
    
    if not candidates:
        print("🎉 Congratulations! All available topics are at Level 3 (demonstrated).")
        print("   Ask your faculty for advanced exercises.")
        sys.exit(0)
    
    # Sort by unit and get first
    candidates.sort(key=lambda x: x['unit'])
    next_topic = candidates[0]
    topic = next_topic['name']
    level = next_topic['assigned_level']
    
    # Find a variant not yet attempted at this topic+level
    attempted = set()
    for session in progress.get('sessions', []):
        exercise_id = session.get('exercise_id', '')
        if exercise_id.startswith(f"{topic}_L{level}_"):
            variant = exercise_id.split('_')[-1]
            attempted.add(variant)
    
    exercise_id = None
    variant = None
    for v in ['a', 'b', 'c', 'd', 'e']:
        if v not in attempted:
            exercise_id = f"{topic}_L{level}_{v}"
            variant = v
            break
    
    if not exercise_id:
        print(f"All variants at {topic} Level {level} attempted. Promoting level...")
        level += 1
        if level > 3:
            print(f"Topic {topic} fully mastered. Moving to next topic.")
            sys.exit(0)
        exercise_id = f"{topic}_L{level}_a"
        variant = 'a'
    
    # Verify exercise exists in library
    exercise_exists = False
    if topic in library.get('topics', {}):
        for exercise in library['topics'][topic].get('exercises', []):
            if exercise.get('id') == exercise_id:
                exercise_exists = True
                break
    
    if not exercise_exists:
        print(f"ERROR: Exercise '{exercise_id}' not found in library.json.")
        print("       Ask your instructor to add it, or choose a different variant.")
        sys.exit(1)
    
    # Get problem statement
    problem_statement = ""
    if topic in library.get('topics', {}):
        for exercise in library['topics'][topic].get('exercises', []):
            if exercise.get('id') == exercise_id:
                problem_statement = exercise.get('problem_statement', '')
                break
    
    # Create exercise file from template
    filename = f"{topic}_L{level}_{variant}_{student_id}.c"
    filepath = os.path.join(project_root, 'student_data', filename)
    
    # Call make_template.py to create the file
    try:
        result = subprocess.run(
            ['python', os.path.join(script_dir, 'make_template.py'), filepath, exercise_id, student_id],
            input=problem_statement,
            capture_output=True,
            text=True
        )
    except Exception as e:
        print(f"ERROR: Failed to create exercise file: {e}")
        sys.exit(1)
    
    print()
    print(f"📝 Exercise assigned: {exercise_id}")
    print(f"   File created:      student_data/{filename}")
    print(f"   Open in VS Code:   code student_data/{filename}")
    print()
    print("Use the VS Code Tasks runner (REVA: Get Help / REVA: Grade My Code) to get support.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Usage: next.py <student_id>")
        sys.exit(1)
    
    get_next_exercise(sys.argv[1])
