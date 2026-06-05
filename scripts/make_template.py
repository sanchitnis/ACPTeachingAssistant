#!/usr/bin/env python3
"""
Usage: python3 make_template.py <output_filepath> <exercise_id> <student_id>

Searches exercises/library.json then exercises/lab_programs.json for the
exercise record and writes a populated .c template to <output_filepath>.

Called from next.sh.
"""

import sys
import json
import datetime
from pathlib import Path


LEVEL_NAMES = {
    "1": "Foundational",
    "2": "Applied",
    "3": "Integrative",
}


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: make_template.py <output_filepath> <exercise_id> <student_id>", file=sys.stderr)
        sys.exit(1)

    output_path  = Path(sys.argv[1])
    exercise_id  = sys.argv[2]
    student_id   = sys.argv[3]

    if not exercise_id or "_" not in exercise_id:
        print(f"ERROR: Invalid exercise_id '{exercise_id}'", file=sys.stderr)
        sys.exit(1)

    # Derive paths relative to this script's location
    script_dir   = Path(__file__).parent
    project_root = script_dir.parent

    # Search exercise files
    EXERCISE_FILES = [
        project_root / "exercises" / "prerequisites.json",
        project_root / "exercises" / "practice.json",
        project_root / "exercises" / "advanced.json",
        project_root / "exercises" / "lab_programs.json",
    ]

    lib = None
    ex  = None
    found_topic_key = None
    for lib_path in EXERCISE_FILES:
        if not lib_path.exists():
            continue
        candidate = json.loads(lib_path.read_text(encoding="utf-8"))
        for t_key, t_val in candidate.get("topics", {}).items():
            found = next((e for e in t_val.get("exercises", []) if e["id"] == exercise_id), None)
            if found:
                lib = candidate
                ex  = found
                found_topic_key = t_key
                break
        if ex:
            break

    if lib is None or ex is None:
        sys.exit(f"ERROR: Exercise '{exercise_id}' not found in exercise files.")

    topic_name   = lib["topics"][found_topic_key]["name"]
    level_num    = ex.get("level", 1)
    level_name   = LEVEL_NAMES.get(str(level_num), "Unknown")
    problem      = ex["problem_statement"]
    sample_in    = ex.get("sample_input", "(none)")
    sample_out   = ex.get("sample_output", "(none)")
    constraints  = "\n".join(
        f" *   - {c}" for c in ex.get("constraints", [])
    ) or " *   (none)"
    filename     = output_path.name
    today        = datetime.date.today().isoformat()

    content = f"""\
/*
 * ============================================================
 * REVA University \u2014 C Programming Practice
 * ============================================================
 * Exercise ID   : {exercise_id}
 * Topic         : {topic_name}
 * Level         : {level_num} ({level_name})
 * Student       : {student_id}
 * Date Assigned : {today}
 * ============================================================
 *
 * PROBLEM STATEMENT:
 * {problem}
 *
 * SAMPLE INPUT:
 *   {sample_in}
 *
 * SAMPLE OUTPUT:
 *   {sample_out}
 *
 * CONSTRAINTS:
{constraints}
 *
 * HELP:  Run VS Code Task "REVA: Get Help" to prepare context
 * GRADE: Run VS Code Task "REVA: Grade My Code" to check correctness
 * ============================================================
 */

#include <stdio.h>

/*
 * Function : main
 * Purpose  : Entry point \u2014 implement your solution here.
 * Params   : none
 * Returns  : 0 on success
 */
int main(void) {{
    /* TODO: Write your solution below.
     * Follow the REVA C Coding Style Guide (docs/coding_style_guide.md).
     */

    return 0;
}}
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"Template written: {output_path}")


if __name__ == "__main__":
    main()
