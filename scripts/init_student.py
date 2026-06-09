#!/usr/bin/env python3
"""
Usage: init_student.py <student_id> <name> <section> [<1st sem grade>]
Creates student_data/progress/<student_id>.json with all ACP topics locked
(assigned_level: null) except FUNC (ACP Unit 1 entry point), which starts
at assigned_level = 1 (unless grade is low, which triggers prerequisites).
Topics are unlocked by next.py when a full syllabus unit is mastered.
"""

import sys
import os
import json
from datetime import datetime
import re

def init_student(student_id, name, section, grade_arg=None):
    """Initialize a new student."""
    if not student_id or not name or not section:
        print("ERROR: Usage: init_student.py <student_id> \"<Full Name>\" \"<Section>\" [<1st sem grade>]")
        print("Example: init_student.py raj22cs045 \"Raj Kumar\" \"BTech-CS-2B\" \"A+\"")
        sys.exit(1)
    
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Validate and normalize grade
    grade = None
    if grade_arg:
        grade = grade_arg.strip().upper()
        if not re.match(r'^(O|A\+|A|B\+|B|C\+|C|F)$', grade):
            print(f"Warning: Invalid grade '{grade_arg}' provided. Reverting to interactive prompt.")
            grade = None
    
    if not grade:
        try:
            while True:
                grade = input("Enter your 1st sem C Programming grade (O/A+/A/B+/B/C+/C/F): ").strip().upper()
                if re.match(r'^(O|A\+|A|B\+|B|C\+|C|F)$', grade):
                    break
                print("Invalid grade. Please enter O, A+, A, B+, B, C+, C, or F.")
        except EOFError:
            # Default fallback for automated environments
            grade = "B"
    
    unlock_prereqs = False
    if grade in ['C+', 'C', 'F']:
        unlock_prereqs = True
        print(f"⚠️  Grade ({grade}) indicates catch-up is needed. Unlocking prerequisite topics first!")
    
    func_assigned = 1 if not unlock_prereqs else None
    prereq_assigned = 1 if unlock_prereqs else None
    
    student_data_dir = os.path.join(project_root, 'student_data')
    progress_dir = os.path.join(student_data_dir, 'progress')
    sessions_dir = os.path.join(student_data_dir, 'sessions', student_id)
    progress_file = os.path.join(progress_dir, f'{student_id}.json')
    
    if os.path.isfile(progress_file):
        print(f"ERROR: Progress file already exists for '{student_id}'. Aborting.")
        print(f"       To reset a student, manually delete {progress_file} first.")
        sys.exit(1)
    
    # Create directories
    os.makedirs(progress_dir, exist_ok=True)
    os.makedirs(sessions_dir, exist_ok=True)
    
    now = datetime.utcnow().isoformat() + 'Z'
    
    # ACP topic registry
    progress_data = {
        "student_id": student_id,
        "name": name,
        "section": section,
        "c_grade_sem1": grade,
        "created": now,
        "last_active": now,
        "overall_level": 1,
        "topics": {
            "FUNC":        {"assigned_level": func_assigned, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO1"]},
            "SCOPE":       {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO1"]},
            "ARRAY":       {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO1"]},
            "STRUCT":      {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO1","CO2"]},
            "ARRAYSTRUCT": {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO2"]},
            "PTR":         {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO3"]},
            "PTRARR":      {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO3"]},
            "PTRF":        {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO1","CO3"]},
            "DYNMEM":      {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO3"]},
            "LINKEDLIST":  {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO3"]},
            "STRING":      {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO4"]},
            "STROP":       {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO4"]},
            "FILE":        {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": ["CO5"]},
            "_prereq_INTRO":  {"assigned_level": prereq_assigned, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_prereq_DTYPES": {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_prereq_OPS":    {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_prereq_IO":     {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_prereq_COND":   {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_prereq_LOOP":   {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_prereq_JUMP":   {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_adv_RECUR":  {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_adv_UNION":  {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_adv_ENUM":   {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
            "_adv_FSEEK":  {"assigned_level": None, "demonstrated_level": 0, "exercises_completed": 0, "last_score": None, "co_mapping": []},
        },
        "sessions": []
    }
    
    # Write progress file
    with open(progress_file, 'w') as f:
        json.dump(progress_data, f, indent=2)
    
    print(f"✅ Student registered: {student_id} ({name}) — {section} (Sem 1 Grade: {grade})")
    print(f"   Progress file: {progress_file}")
    print(f"   Sessions dir:  {sessions_dir}")
    print()
    print(f"Next step: python scripts/next.py {student_id}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("ERROR: Usage: init_student.py <student_id> \"<Full Name>\" \"<Section>\" [<1st sem grade>]")
        print("Example: init_student.py raj22cs045 \"Raj Kumar\" \"BTech-CS-2B\" \"A+\"")
        sys.exit(1)
    
    student_id = sys.argv[1]
    name = sys.argv[2]
    section = sys.argv[3]
    grade_arg = sys.argv[4] if len(sys.argv) > 4 else None
    
    init_student(student_id, name, section, grade_arg)
