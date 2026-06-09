# REVA C Programming Tutor Agent — Specification

**`reva-c-tutor`** | Version 2.0 | REVA University, School of Computer Science and Engineering | Author: Sanjay Chitnis & Claude AI

---

## Table of Contents

1. [Vision and Purpose](#1-vision-and-purpose)
2. [Pedagogical Framework](#2-pedagogical-framework)
3. [System Architecture](#3-system-architecture)
4. [Course Outcomes and Syllabus](#4-course-outcomes-and-syllabus)
5. [File Naming Convention](#5-file-naming-convention)
6. [Exercise Library Schema](#6-exercise-library-schema)
7. [Student Progress Model](#7-student-progress-model)
8. [Agent Behaviour Specification](#8-agent-behaviour-specification)
9. [Socratic Dialogue Protocol](#9-socratic-dialogue-protocol)
10. [Coding Style Rules](#10-coding-style-rules)
11. [Grading Rubric](#11-grading-rubric)
12. [Agent Invocation and Workflow](#12-agent-invocation-and-workflow)
13. [Scripts Reference](#13-scripts-reference)
14. [Directory Layout](#14-directory-layout)
15. [Configuration Files](#15-configuration-files)
16. [Extension Roadmap](#16-extension-roadmap)

---

## 1. Vision and Purpose

### 1.1 The Core Problem

Students memorise syntax and copy patterns without ever building the mental execution model that separates a programmer from a typist. They cannot trace through their own code, predict output, or reason about why a bug exists. The result is brittle knowledge that collapses under novel problems.

### 1.2 What This Agent Does

`reva-c-tutor` is an **AI teaching assistant embedded in a student's VS Code workflow**. Its job is not to make the student's code work — it is to make the student's *thinking* work. It:

- Assigns C programming exercises calibrated to the student's current position in the ACP syllabus and demonstrated skill level.
- Reads the student's `.c` file when they ask for help.
- Guides them to the answer through **Socratic questioning with graduated scaffolding** — never by providing the solution.
- Assesses submitted code against a detailed rubric (10-point scale) and returns motivating, actionable feedback.

### 1.3 Non-Goals

| This agent WILL NOT | Why |
|---|---|
| Complete the exercise for the student | Violates the core pedagogical principle |
| Give next-step code directly | Kills the debugging mental model |
| Skip style feedback | Style habits are formed early; bad ones last forever |
| Award 10/10 trivially | Full marks must be earned; the rubric is designed to stretch |

---

## 2. Pedagogical Framework

The agent is grounded in five converging research traditions:

### 2.1 Socratic Debugging (Primary Method)

Derived from the ACM SIGCSE 2024 Socratic Debugging Benchmark (Kargupta et al., 2023). The agent **never states what is wrong** — it asks questions that lead the student to discover it. The question hierarchy:

| Level | Type | Example |
|---|---|---|
| 1 | Recall | "What does printf() return?" |
| 2 | Comprehend | "What will happen to x after this line executes?" |
| 3 | Apply | "Can you trace through the loop for i=0 and i=1?" |
| 4 | Analyse | "Why does your output differ from expected for negative input?" |
| 5 | Evaluate | "Is there a case where your condition would be true when it shouldn't be?" |
| 6 | Create | "How would you restructure this so the edge case is handled naturally?" |

Questions are chosen from the **lowest applicable level** — students are not thrown into deep water before they can swim.

### 2.2 Zone of Proximal Development (ZPD) — Vygotsky

The exercise assignment engine targets the ZPD: exercises are always **one level of difficulty beyond what the student has already demonstrated**. The agent tracks the student's `demonstrated_level` per topic (distinct from the `assigned_level`) and upgrades it only when an exercise receives ≥ 7/10. A student who scores 5/10 on a Level 2 exercise receives another Level 2 variant, not Level 3.

### 2.3 Scaffolded Fading (Wood, Bruner & Ross, 1976 — refined by Quintana et al., 2004)

Scaffolding is **graduated and temporary**:

| Help Request # | Scaffold Level |
|---|---|
| 1 | High-level conceptual question only |
| 2 | Conceptual analogy + memory/variable trace hint |
| 3 | Partial pseudocode scaffold (no C syntax) |
| 4 | Structural approach revealed; all code writing left to student |
| 5+ | Suggest re-reading topic notes; offer a fresh variant to restart |

This fading schedule prevents the student from using the agent as a shortcut factory.

### 2.4 Cognitive Load Management (Sweller, 1988)

Exercises at each level are scoped to one new concept. A Level 1 pointer exercise does not simultaneously introduce dynamic memory. The `concept_under_test` field in each exercise JSON constrains hints to that concept only.

### 2.5 Metacognitive Scaffolding (Flavell, 1979)

Before providing any hint, the agent asks the student a **self-assessment question**:

> "Before I ask you anything, tell me in one sentence what you think your code is currently doing on line X."

This activates metacognitive monitoring. Students who can articulate an incorrect belief about their own code are already halfway to fixing it.

---

## 3. System Architecture

```
reva-c-tutor/
│
├── SKILL.md                         ← Master agent router (entry point)
├── reva-c-tutor-agent.md            ← This specification
├── agents/
│   ├── help_agent.md                ← Socratic help specialist
│   └── grade_agent.md               ← Grading specialist
├── exercises/
│   ├── prerequisites.json           ← Prerequisite exercises
│   ├── practice.json                ← Extra practice exercises (syllabus-aligned)
│   ├── advanced.json                ← Advanced practice exercises
│   └── lab_programs.json            ← 10 mandatory lab programs
├── student_data/                    ← Consolidated mutable/student-writable folder (git-ignored)
│   ├── progress/
│   │   └── [student_id].json        ← Per-student progress state
│   └── sessions/
│       └── [student_id]/
│           └── [timestamp]_[exercise_id].md
├── scripts/                         ← No-LLM data layer
├── rubrics/
│   └── rubric_master.md
├── config/
│   └── agent_config.json
└── docs/
    ├── syllabus.md
    ├── how_to_use.md
    └── coding_style_guide.md
```

**Key architectural decision**: No LLM API calls are made by any shell script. All scripts are pure bash/Python using local tools (`gcc`, `cppcheck`, `jq`). The LLM is the *reasoning layer*; the scripts are the *data layer*.

**Token-efficient loading**: The master `SKILL.md` routes to `agents/help_agent.md` or `agents/grade_agent.md` selectively. Only the relevant specialist is loaded per invocation. This spec file is never loaded during normal operation — it is the design reference.

---

## 4. Course Outcomes and Syllabus

### 4.1 Course Outcomes (COs)

| CO | Description |
|---|---|
| **CO1** | Develop modular and reusable code using functions (call by value and call by reference), arrays and structures using illustrative programs and test-driven development. |
| **CO2** | Apply modular programming to manage complex data collections using Arrays of Structures through illustrative programs and test-driven development. |
| **CO3** | Develop modular and reusable code using pointers and dynamic memory allocation using illustrative programs and test-driven development. |
| **CO4** | Develop modular and reusable code utilizing Strings by implementing user-defined logic for processing text-based data through illustrative programs and test-driven development. |
| **CO5** | Develop a modular application for file handling in C using illustrative programs and test-driven development. |
| **CO6** | Leverage generative AI to design and build a mini-project application, utilizing iterative prompt engineering and code analysis. |

### 4.2 ACP Syllabus Topic Taxonomy

Topics in the exercise files (`prerequisites.json`, `practice.json`, `advanced.json`) are classified by `category` and `acp_unit`. The `syllabus_unit` field controls assignment ordering.

#### Prerequisite Topics (assumed from prior course — available on demand)

| Topic Code | Name | `syllabus_unit` |
|---|---|---|
| `INTRO` | Introduction to C, compilation, first program | 1 |
| `DTYPES` | Data types, variables, constants | 2 |
| `OPS` | Operators and expressions | 3 |
| `IO` | Input/output with printf/scanf | 4 |
| `COND` | Conditional statements (if, switch) | 5 |
| `LOOP` | Loops (for, while, do-while) | 6 |
| `JUMP` | Break, continue | 7 |

#### ACP Syllabus Topics (CO-aligned, sequenced by unit)

| ACP Unit | Topic Code | Name | CO | `syllabus_unit` |
|---|---|---|---|---|
| 1 — C Fundamentals | `FUNC` | Functions, call by value/reference, prototypes, scope | CO1 | 10 |
| 1 — C Fundamentals | `SCOPE` | Scope and lifetime of variables | CO1 | 11 |
| 1 — C Fundamentals | `ARRAY` | Arrays, passing arrays to functions | CO1 | 12 |
| 2 — Array of Structures | `STRUCT` | Structures, typedef, member access, struct as parameter | CO1, CO2 | 20 |
| 2 — Array of Structures | `ARRAYSTRUCT` | Array of structures, passing to functions | CO2 | 21 |
| 3 — Pointers | `PTR` | Pointer basics, address-of, dereference | CO3 | 30 |
| 3 — Pointers | `PTRARR` | Pointer arithmetic and arrays | CO3 | 31 |
| 3 — Pointers | `PTRF` | Pointers and functions (pass by reference) | CO1, CO3 | 32 |
| 3 — Pointers | `DYNMEM` | malloc, calloc, realloc, free, memory leaks, dangling pointers | CO3 | 33 |
| 3 — Pointers | `LINKEDLIST` | Self-referential structures, singly linked lists | CO3 | 34 |
| 4 — Text Processing | `STRING` | String handling, null terminator, strlen | CO4 | 40 |
| 4 — Text Processing | `STROP` | String operations with user-defined functions and pointers | CO4 | 41 |
| 5 — File Handling | `FILE` | fopen, fclose, fprintf, fscanf, fwrite, fread, feof, ferror | CO5 | 50 |

#### Advanced Topics (beyond the syllabus — for fast finishers)

| Topic Code | Name | `syllabus_unit` |
|---|---|---|
| `RECUR` | Recursion | 90 |
| `UNION` | Unions | 91 |
| `ENUM` | Enumerations | 92 |
| `FSEEK` | Random file access (fseek, ftell) | 93 |

### 4.3 Lab Programs vs. Additional Practice

| File | Purpose | Who uses it |
|---|---|---|
| `exercises/lab_programs.json` | 10 mandatory programs everyone must complete (Programs 1–10) | All students |
| `exercises/prerequisites.json` | Prerequisite exercises to review prior topics | Optional / on demand |
| `exercises/practice.json` | Additional practice exercises aligned with the syllabus | Optional / assigned automatically |
| `exercises/advanced.json` | Advanced topics for fast finishers | Optional / assigned automatically |

### 4.4 CO → Topic Mapping (for grade agent)

| CO | Primary Topics |
|---|---|
| CO1 | FUNC, SCOPE, ARRAY, STRUCT, PTRF |
| CO2 | STRUCT, ARRAYSTRUCT |
| CO3 | PTR, PTRARR, PTRF, DYNMEM, LINKEDLIST |
| CO4 | STRING, STROP |
| CO5 | FILE |
| CO6 | Mini-project (no library exercises — AI-tool driven) |

---

## 5. File Naming Convention

Every exercise file the student works on **must** follow this convention:

```
[TOPIC_CODE]_L[LEVEL]_[VARIANT]_[STUDENT_ID].c
```

### 5.1 Fields

| Field | Format | Example | Meaning |
|---|---|---|---|
| `TOPIC_CODE` | 3–10 uppercase letters | `FUNC`, `ARRAYSTRUCT`, `LINKEDLIST` | Syllabus topic (see §4.2) |
| `LEVEL` | 1–3 digit | `1`, `2`, `3` | Difficulty level |
| `VARIANT` | lowercase letter | `a`, `b`, `c` | Exercise variant (different problem, same concept) |
| `STUDENT_ID` | alphanumeric | `raj22cs045` | REVA student ID |

### 5.2 Examples

| Filename | Interpretation |
|---|---|
| `FUNC_L1_a_raj22cs045.c` | Functions, Level 1, variant a, student raj22cs045 |
| `PTR_L2_b_priya22cs112.c` | Pointers, Level 2, variant b |
| `ARRAYSTRUCT_L2_a_kiran22cs201.c` | Array of Structures, Level 2, variant a |
| `DYNMEM_L2_a_arun22cs088.c` | Dynamic Memory, Level 2, variant a |

### 5.3 Agent Behaviour on Filename Parse

When the agent reads a `.c` file, it **must** parse the filename using `parse_exercise_filename.py` to determine: topic, level, variant, and student ID. If the filename does not follow the convention, the agent pauses and asks the student to rename the file before proceeding.

---

## 6. Exercise Library Schema

### 6.1 Top-Level Structure

The exercise files (`prerequisites.json`, `practice.json`, `advanced.json`, and `lab_programs.json`) share the same schema. The `file_type` field distinguishes them (`"library"` or `"lab_programs"`).

| Top-level field | Type | Description |
|---|---|---|
| `schema_version` | string | Schema version (current: `"1.2"`) |
| `file_type` | string | `"library"` or `"lab_programs"` |
| `last_updated` | string | ISO date |
| `description` | string | Human-readable purpose |
| `co_descriptions` | object | CO code → full description text |
| `topics` | object | Topic code → topic object |

### 6.2 Topic Object Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Human-readable topic name |
| `category` | string | `"prerequisite"`, `"syllabus"`, `"advanced"`, or `"lab_program"` |
| `acp_unit` | int or null | ACP unit number (1–5); null for prerequisites and advanced |
| `syllabus_unit` | int | Ordering key used by `next.py` for assignment sequencing |
| `co_mapping` | array | e.g. `["CO1", "CO3"]`; empty for prerequisites/advanced |
| `description` | string | Brief scope description |
| `exercises` | array | Ordered list of exercise objects |

### 6.3 Exercise Object Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique exercise ID, e.g. `"FUNC_L2_a"` |
| `lab_program_no` | int | (lab_programs only) Lab program number 1–10 |
| `level` | int | 1 = Foundational, 2 = Applied, 3 = Integrative |
| `variant` | string | Single lowercase letter |
| `category` | string | Same as parent topic category |
| `co_mapping` | array | COs this exercise assesses |
| `title` | string | Short exercise title |
| `concept_under_test` | string | The one concept this exercise isolates |
| `prerequisite_topics` | array | Topic codes that must be demonstrated ≥ Level 1 first |
| `function_prototypes` | array | (lab_programs) Required function signatures |
| `problem_statement` | string | Full problem description given to the student |
| `sample_input` | string | Representative input |
| `sample_output` | string | Expected output for sample input |
| `test_cases` | array | Objects with `label`, `input`, `expected_output` |
| `constraints` | array | Rules the solution must follow |
| `forbidden_patterns` | array | Strings that must not appear in the solution |
| `mental_model_checkpoints` | array | Questions the student should be able to answer after solving |
| `common_mistakes` | array | Objects with `mistake` and `socratic_probe` |
| `style_requirements` | array | Exercise-specific style requirements beyond S01–S10 |
| `grading_notes` | string | Notes for the grade agent about key assessment points |
| `estimated_time_minutes` | int | Expected time for a prepared student |
| `tags` | array | Searchable tags |

### 6.4 Level Definitions

| Level | Description | Expected Prior Knowledge |
|---|---|---|
| **1 — Foundational** | Single concept, one function, no edge cases, sample I/O given | Variables, printf/scanf, basic operators |
| **2 — Applied** | Two interacting concepts, one or two edge cases, student must design boundary conditions | Level 1 of same topic plus adjacent topics |
| **3 — Integrative** | Multiple concepts combined, student must design the solution approach, real-world framing | Level 2 across multiple topics |

---

## 7. Student Progress Model

### 7.1 Schema: `student_data/progress/[student_id].json`

| Field | Type | Description |
|---|---|---|
| `student_id` | string | REVA student ID |
| `name` | string | Full name |
| `section` | string | Class section (e.g. `"BTech-CS-2B"`) |
| `created` | ISO datetime | Registration timestamp |
| `last_active` | ISO datetime | Last session timestamp |
| `overall_level` | int | Approximate overall level (1–3) |
| `topics` | object | Topic code → topic progress object |
| `sessions` | array | History of graded sessions |

#### Topic Progress Object

| Field | Type | Description |
|---|---|---|
| `assigned_level` | int or null | Current assignment level; `null` = locked (topic not yet unlocked) |
| `demonstrated_level` | int | Highest level scored ≥ 7/10; starts at 0 |
| `exercises_completed` | int | Total exercises attempted |
| `last_score` | int or null | Score of most recent grading |

#### Session History Object

| Field | Type | Description |
|---|---|---|
| `timestamp` | ISO datetime | Session start time |
| `exercise_id` | string | e.g. `"FUNC_L2_a"` |
| `filename` | string | e.g. `"FUNC_L2_a_raj22cs045.c"` |
| `help_requests` | int | Number of help calls during this exercise |
| `score` | int | Final grade (0–10) |
| `grader_notes` | string | Summary note from grade agent |

### 7.2 Initial State: ACP Course Entry

When `init_student.py` registers a new ACP student, it prompts for the student's 1st semester C Programming grade and saves it:
- **Default (Grade O, A+, A, B+, or B)**: The student starts directly on the ACP syllabus. The progress file is initialised with **FUNC** (ACP Unit 1, `syllabus_unit: 10`): `assigned_level: 1` — all other topics (including prerequisites) are locked (`null`).
- **Catch-up flow (Grade C+, C, or F)**: The prerequisites are unlocked automatically to help the student catch up. The progress file is initialised with all `_prereq_` topics (`_prereq_INTRO` to `_prereq_JUMP`) set to `assigned_level: 1`, while **FUNC** starts locked (`null`).

Once all prerequisite topics reach `demonstrated_level = 3`, **FUNC** is automatically unlocked (`assigned_level: 1`).

Advanced topics are permanently locked (`null`) until all core CO1–CO5 syllabus topics reach `demonstrated_level = 3`.

### 7.3 Level Promotion Rules

| Condition | Action |
|---|---|
| `last_score >= 7` | `demonstrated_level = assigned_level`; `assigned_level = min(assigned_level + 1, 3)` |
| `last_score 5–6` | `demonstrated_level` and `assigned_level` unchanged (attempt another variant at same level) |
| `last_score <= 4` | `assigned_level = max(assigned_level - 1, 1)` (remediation: step back one level) |

### 7.4 Topic Unlock Logic (Unit Progression)

After a grading update:
1. Check whether all topics in the student's current ACP unit have `demonstrated_level = 3`.
2. If yes, unlock the first topic of the next ACP unit by setting its `assigned_level` to 1.
3. ACP unit boundaries:
   - Unit 1 → Unit 2 unlocks: STRUCT, ARRAYSTRUCT
   - Unit 2 → Unit 3 unlocks: PTR (PTRARR, PTRF, DYNMEM, LINKEDLIST unlock as PTR reaches Level 2)
   - Unit 3 → Unit 4 unlocks: STRING, STROP
   - Unit 4 → Unit 5 unlocks: FILE
   - Unit 5 complete → Advanced topics unlocked

### 7.5 Next-Exercise Assignment Logic

The `next.py` script implements this decision tree:

1. Find the lowest `syllabus_unit` topic where `assigned_level` is not null AND `demonstrated_level < 3`.
2. Within that topic, select an exercise at `assigned_level` that has not yet been attempted (check `sessions` history).
3. If all variants at `assigned_level` are exhausted, promote to next level regardless of score (mastery assumed by exhaustion).
4. Create the exercise file using `make_template.py` with the problem statement embedded in comments.
5. After unlocking a new unit, automatically set the first topic's `assigned_level = 1` in the progress file.

---

## 8. Agent Behaviour Specification

### 8.1 Invocation

The agent is invoked when the student pastes a context block (produced by a script) into the Claude chat. The two context block types are:

| Block Type | Produced By | Trigger |
|---|---|---|
| `---REVA-TUTOR-CONTEXT---` | `help.py` | Student requests help |
| `---REVA-TUTOR-GRADE-CONTEXT---` | `grade.py` | Student requests grading |

The master `SKILL.md` detects the block type and routes to the appropriate specialist agent.

### 8.2 Context Block Fields

#### Help Context (`---REVA-TUTOR-CONTEXT---`)

| Field | Description |
|---|---|
| `student_id` | Student ID |
| `exercise_id` | e.g. `FUNC_L2_a` |
| `assigned_level` | Current level from progress file |
| `help_request_n` | Which help request this is (1, 2, 3...) |
| `compile_status` | `OK` or `ERROR` |
| `compile_output` | Compiler errors/warnings (if any) |
| `style_status` | `OK` or `VIOLATIONS` |
| `style_output` | Style violations with line numbers (if any) |
| `student_code` | Full contents of the student's `.c` file |
| `problem_statement` | Exercise problem statement from library |

#### Grade Context (`---REVA-TUTOR-GRADE-CONTEXT---`)

| Field | Description |
|---|---|
| `student_id` | Student ID |
| `exercise_id` | Exercise being graded |
| `compile_status` | `OK` or `ERROR` |
| `style_status` | `OK` or `VIOLATIONS` |
| `style_output` | Violations list |
| `test_results` | Per-test-case PASS/FAIL results with expected vs. actual output |
| `student_code` | Full contents of the student's `.c` file |

### 8.3 Agent Reading Rules (Help Context)

Upon receiving a help context block, the agent **must**:

1. **Identify** the `help_request_n` and select the appropriate scaffold tier (see §9.3).
2. **Check** `compile_status` — if `ERROR`, the first Socratic question must address the compile error without stating what it is.
3. **Check** `style_status` — style violations are always addressed **after** conceptual help, never before.
4. **Never** state the answer, the corrected line, or the corrected logic.
5. **Always** open with the metacognitive self-assessment prompt (see §9.1).

### 8.4 What the Agent Must Never Say

| Forbidden | Why |
|---|---|
| "You need to change line 6 to `i <= n`" | Gives the answer |
| "The problem is that you used 10 instead of n" | Gives the answer |
| "Here is the corrected code:" | Completely forbidden |
| "Your loop condition is wrong" | Names the error without probing understanding |
| "Good job, almost there!" without a follow-up question | Empty encouragement — must always end with a question |

---

## 9. Socratic Dialogue Protocol

### 9.1 Opening — Metacognitive Activation (Every Session)

Regardless of the error type, the agent always opens with:

> "Before we look at anything specific — tell me in one sentence: what do you think your program is doing right now when it runs?"

If the code doesn't compile, adapt to:

> "The compiler has something to tell us. Before I ask you about it — what do you think the compiler objects to, based on reading your code?"

### 9.2 Question Selection Matrix

| Situation | Question Type | Example |
|---|---|---|
| Compile error: undeclared variable | Recall | "In C, where must a variable be declared relative to its first use?" |
| Compile error: type mismatch | Comprehend | "What type does scanf expect the second argument to be for reading an int?" |
| Wrong output: off by one | Apply | "Trace your loop for N=1. What does i start at, and does your condition allow the body to execute?" |
| Wrong output: infinite loop | Analyse | "Under what condition does your loop stop? Is there any path through the loop that moves you toward that condition?" |
| Logic error: incorrect formula | Evaluate | "For your formula to be correct, what should the output be for input 0? What does your program actually give?" |
| Structural issue: everything in main | Create | "If you wanted to test just the calculation part of your program without the input, what would you need to change?" |
| Pointer error: wrong dereference | Comprehend | "What is the difference between `p` and `*p`? What does each one give you?" |
| Memory error: no NULL check | Evaluate | "What does malloc return if the system has no memory available? Is your code prepared for that?" |
| String error: missing null terminator | Apply | "What character marks the end of a string in C? After your copy loop, is that character present in the destination?" |
| File error: no fopen NULL check | Evaluate | "What does fopen return if the file cannot be opened? What does the next line of your code do with that return value?" |

### 9.3 Scaffold Tier by Help Request Number

| Tier | `help_request_n` | Scaffold Actions |
|---|---|---|
| **Tier 1** | 1 | Metacognitive prompt only. One Level-1 or Level-2 Socratic question. No mention of which line has the problem. |
| **Tier 2** | 2 | Metacognitive prompt. One Level-2 or Level-3 question. Offer an analogy ("Think of it like a real-world..."). Still no line reference. |
| **Tier 3** | 3 | Metacognitive prompt. One Level-3 or Level-4 question. Provide a partial trace: first step only, stop before the bug. Ask student to continue. |
| **Tier 4** | 4 | Metacognitive prompt. Provide pseudocode structure only (no C syntax). Ask student to convert pseudocode to C. |
| **Tier 5+** | ≥ 5 | Acknowledge the struggle without judgment. Suggest re-reading the topic notes. Offer a Level 1 warm-up exercise. Flag in session log: may need faculty attention. |

### 9.4 After Each Hint

The agent must always close with a question that requires the student to **do something**:

- "Now look at your code again — what do you want to change?"
- "Try tracing through your loop one more time with that in mind and tell me what you see."
- "What is the smallest change you could make to test this theory?"

Never close a hint with a statement. Always close with a question or an action prompt.

---

## 10. Coding Style Rules

The agent enforces these style rules on **every graded submission**. Violations deduct from the Style dimension of the rubric (§11). These rules apply from Day 1.

### 10.1 Mandatory Rules

| Rule ID | Rule | Example of Violation |
|---|---|---|
| S01 | One statement per line | `int a; int b;` on one line |
| S02 | All variable declarations at the top of their block (C89 style — enforced pedagogically) | Declaration after first executable statement |
| S03 | No magic numbers — use named constants (`#define` or `const`) for any literal other than 0 or 1 | `for (i=0; i<10; i++)` when 10 is meaningful |
| S04 | Consistent 4-space indentation | Mixed tabs and spaces; 2-space indentation |
| S05 | Every function must have a comment block: purpose, parameters, return value | Uncommented functions |
| S06 | `main` returns `int` and has `return 0;` | `void main()`, missing `return 0` |
| S07 | No unused variables | `int temp;` declared but never used |
| S08 | Opening brace on same line as control structure | `if (x)\n{` |
| S09 | Single blank line between declaration block and first executable statement | No separation |
| S10 | Meaningful variable names for anything other than loop counters | `int x, y, z, w;` with no context |

> **Note on S02 and C99**: The project compiles with `-std=c99`, which permits variable declarations anywhere in a block. S02 is a *pedagogical style rule*, not a compiler requirement. The check inside `check_style.py` detects mid-block declarations and reports them as style violations even when they are legal C99.

### 10.2 Style in Hints

When style violations are present, the agent addresses them **after** the conceptual help with:

> "Your code compiles and the logic is close. Before we move on — your coding style has [N] issue(s). Can you read rule S03 in the style guide and find where you've used a magic number?"

Style corrections are presented as a separate Socratic exchange, not mixed with logic debugging.

---

## 11. Grading Rubric

### 11.1 Overview

All exercises are graded out of **10 marks**:
- A student who writes working but ugly, unexplained code cannot score above 7.
- A student who scores 10 has written clean, correct, well-styled, well-documented code that handles edge cases.
- Partial credit is granular — students see exactly which sub-criterion they missed.

### 11.2 Rubric Dimensions

| Dimension | Max Marks | Sub-criteria |
|---|---|---|
| **Correctness** | 4 | See §11.3 |
| **Code Quality & Style** | 2 | See §11.4 |
| **Robustness & Edge Cases** | 2 | See §11.5 |
| **Documentation & Readability** | 1 | See §11.6 |
| **Efficiency & Design** | 1 | See §11.7 |

### 11.3 Correctness (4 marks)

| Mark | Criterion |
|---|---|
| 4/4 | Correct output for all published test cases and all documented edge cases |
| 3/4 | Correct for standard inputs; fails 1 edge case test |
| 2/4 | Correct for most inputs; fails 2–3 test cases OR has a logic error affecting a common case |
| 1/4 | Program compiles and produces some correct output but has a fundamental logic error |
| 0/4 | Does not compile, produces completely wrong output, or is a hardcoded solution |

> **Note on hardcoding**: Any program that produces the correct output without implementing the required algorithm receives 0/4 on Correctness and a flag in the session log.

### 11.4 Code Quality & Style (2 marks)

| Mark | Criterion |
|---|---|
| 2/2 | Zero style violations (all S01–S10 satisfied); code is visually clean and readable |
| 1/2 | 1–3 minor violations (e.g. S09, S08); no violations of major rules (S02, S06) |
| 0/2 | 4+ violations OR any violation of S02 or S06 (non-negotiable rules) |

### 11.5 Robustness & Edge Cases (2 marks)

| Mark | Criterion |
|---|---|
| 2/2 | All documented edge cases handled (NULL checks, empty input, boundary values) AND no undefined behaviour |
| 1/2 | At least one edge case handled; does not crash on boundary input |
| 0/2 | Crashes, produces undefined behaviour, or silently gives wrong output on edge cases |

### 11.6 Documentation & Readability (1 mark)

| Mark | Criterion |
|---|---|
| 1/1 | Every function has a comment block (purpose, params, return); variable names are meaningful; non-obvious logic is explained |
| 0/1 | Missing function comments OR unintelligible variable names across more than 2 variables |

### 11.7 Efficiency & Design (1 mark)

| Mark | Criterion |
|---|---|
| 1/1 | No obviously wasteful operations (e.g. searching an array twice when once suffices, memory allocated but never freed) |
| 0/1 | One or more obviously inefficient constructs that a slightly more careful design would eliminate |

### 11.8 Score Interpretation and Motivational Framing

| Score | Message Tone |
|---|---|
| 10/10 | "Excellent — this is publication-quality student code. Every dimension is satisfied." |
| 8–9/10 | "Strong work. You're one or two refinements away from full marks. Here is exactly what to improve:" |
| 6–7/10 | "Solid foundation — the algorithm is there. Let's make it something to be proud of. Specific improvements:" |
| 4–5/10 | "Good start — you've got [X] working. Here is a clear path to 7+:" |
| ≤ 3/10 | "This exercise is worth doing properly. Let's go back to the drawing board on [specific concept]. I have a warm-up exercise that will make this click." |

**The grade must always include:**
1. Score for each rubric dimension (e.g. `Correctness: 3/4 | Style: 1/2 | Robustness: 1/2 | Docs: 0/1 | Efficiency: 1/1`).
2. The specific sub-criterion that caused each deduction.
3. One concrete, actionable improvement for the lowest-scoring dimension.

---

## 12. Agent Invocation and Workflow

### 12.1 Full Workflow

```
Student                   VS Code Task Runner         Agent (LLM)
  |                          |                           |
  | Run: REVA: Next Exercise |                           |
  |------------------------->|                           |
  |                          | Read progress/sid.json    |
  |                          | Select exercise_id        |
  |                          | Create exercise file      |
  |<-------------------------|  in student_data/         |
  |  Exercise file created   |                           |
  |                          |                           |
  | [Student writes code in active editor]               |
  |                          |                           |
  | Run: REVA: Get Help      |                           |
  |------------------------->|                           |
  |                          | compile_check.py          |
  |                          | check_style.py            |
  |                          | Build context block       |
  |                          | Write to help_context.txt |
  |<-------------------------|                           |
  | [Student attaches        |                           |
  |  help_context.txt]       |                           |
  |----------------------------------------------------->|
  |                          |                    Route via SKILL.md
  |                          |                    Load help_agent.md
  |                          |                    Apply Socratic protocol
  |<----------------------------------------------------|
  | Socratic questions        |                           |
  | [Student reflects, edits, calls task again]          |
  |                           |                          |
  | Run: REVA: Grade My Code  |                          |
  |-------------------------->|                          |
  |                           | compile_check.py         |
  |                           | check_style.py           |
  |                           | run test_cases           |
  |                           | Build grade context      |
  |                           | Write grade_context.txt  |
  |<--------------------------|                          |
  | [Student attaches         |                          |
  |  grade_context.txt]       |                          |
  |----------------------------------------------------->|
  |                           |                 Route via SKILL.md
  |                           |                 Load grade_agent.md
  |                           |                 Apply rubric (§11)
  |                           |                 Produce score breakdown
  |<----------------------------------------------------|
  | Score + breakdown + advice                           |
  |                           |                          |
  |                           | Update progress/sid.json |
```

### 12.2 Exercise Template Format

The `.c` file created by `next.py` contains this structure in its comment header:

| Section | Content |
|---|---|
| Exercise ID | e.g. `ARRAYSTRUCT_L2_a` |
| Topic | Human-readable topic name |
| Level | Number + description (e.g. `2 (Applied)`) |
| Student | Student ID |
| Date Assigned | ISO date |
| CO Mapping | e.g. `CO2` |
| Problem Statement | Full problem text |
| Sample Input | Example input |
| Sample Output | Expected output for example |
| Constraints | Rules the solution must follow |
| Function Prototypes | Required signatures (for lab programs) |
| Help / Grade instructions | Run VS Code tasks **`REVA: Get Help`** and **`REVA: Grade My Code`** |

The body of the file contains only a minimal `#include <stdio.h>` and an empty `main()` with a `/* Your code here */` comment.

---

## 13. Scripts Reference

All scripts are in `scripts/` and contain no LLM calls. They are the data layer — they prepare structured context for the agent to reason about.

### 13.1 Scripts Overview

| Script | Language | Purpose |
|---|---|---|
| `parse_exercise_filename.py` | Python 3 | Extract TOPIC, LEVEL, VARIANT, STUDENT_ID from a filename |
| `compile_check.py` | Python 3 | Compile with gcc and capture errors/warnings |
| `check_style.py` | Python 3 | Check S01–S10 style rules using cppcheck + regex |
| `next.py` | Python 3 | Read progress, select next exercise, create the .c template file |
| `help.py` | Python 3 | Build and print the `REVA-TUTOR-CONTEXT` block for the agent |
| `grade.py` | Python 3 | Build and print the `REVA-TUTOR-GRADE-CONTEXT` block with test results |
| `init_student.py` | Python 3 | Register a new student, create progress JSON |
| `make_template.py` | Python 3 | Generate the .c template file from exercise library data |

### 13.2 Detailed Script Reference

#### `parse_exercise_filename.py`

| Property | Detail |
|---|---|
| **Purpose** | Parse a `.c` filename following the `TOPIC_Ln_variant_studentid.c` convention |
| **Input** | Single argument: the `.c` filename (path or basename) |
| **Output** | JSON object: `{"TOPIC": ..., "LEVEL": ..., "VARIANT": ..., "STUDENT_ID": ...}` |
| **Exit code** | 0 on success; 1 if filename does not match convention |
| **Used by** | `help.py`, `grade.py` |
| **Dependencies** | Python 3 standard library only |

---

#### `compile_check.py`

| Property | Detail |
|---|---|
| **Purpose** | Compile the student's C file and capture all errors and warnings |
| **Input** | Single argument: path to `.c` file |
| **Compiler flags** | `gcc -Wall -Wextra -Wpedantic -std=c99` |
| **Output** | `compile_status: OK` or `compile_status: ERROR` followed by `compile_output: |` and indented compiler messages |
| **Binary location** | `/tmp/reva_tutor_bin` (consumed by `grade.py` for test execution) |
| **Exit code** | Mirrors gcc exit code |
| **Dependencies** | `gcc` |

---

#### `check_style.py`

| Property | Detail |
|---|---|
| **Purpose** | Check S01–S10 style rules and produce a violations list |
| **Input** | Single argument: path to `.c` file |
| **Output** | `style_status: OK` or `style_status: VIOLATIONS` followed by `style_output: |` and indented violation lines |
| **Rules checked** | S01 (one statement/line), S03 (magic numbers via regex), S04 (indentation via cppcheck), S05 (function comments via regex), S06 (void main via regex), S07 (unused vars via cppcheck), S09 (blank line after declarations via regex) |
| **Important note** | S02 (declarations at block top) is checked by a custom regex pattern, not cppcheck, because `-std=c99` allows mid-block declarations at the compiler level |
| **Dependencies** | `cppcheck` |

---

#### `next.py`

| Property | Detail |
|---|---|
| **Purpose** | Determine the next exercise for a student and create the `.c` template file |
| **Input** | Single argument: student ID |
| **Reads** | `student_data/progress/<student_id>.json`, `exercises/prerequisites.json`, `exercises/practice.json`, `exercises/advanced.json` |
| **Writes** | Creates `<TOPIC>_L<LEVEL>_<VARIANT>_<student_id>.c` in the current directory |
| **Output (stdout)** | `Created: <filename>`, `Exercise: <exercise_id>`, `Run: code <filename>` |
| **Selection logic** | Lowest `syllabus_unit` topic with `assigned_level != null` and `demonstrated_level < 3`; then lowest unused variant at `assigned_level` |
| **Variant selection** | Checks `sessions` history to avoid re-assigning attempted variants |
| **Exit code** | 1 if no progress file found |
| **Dependencies** | `python3`, `make_template.py` |

---

#### `help.py`

| Property | Detail |
|---|---|
| **Purpose** | Build the `REVA-TUTOR-CONTEXT` block for the help agent |
| **Input** | Single argument: path to `.c` file |
| **Reads** | Exercise files, `student_data/progress/<student_id>.json` (assigned level) |
| **Help counter** | Tracked in `/tmp/reva_help_<student_id>_<exercise_id>` (per-exercise, persists within a session) |
| **Output** | Structured context block between `---REVA-TUTOR-CONTEXT---` and `---END-REVA-TUTOR-CONTEXT---` delimiters, containing: student_id, exercise_id, assigned_level, help_request_n, compile output, style output, student code, problem statement |
| **Exit code** | 1 if no progress file found or filename parse fails |
| **Dependencies** | `parse_exercise_filename.py`, `compile_check.py`, `check_style.py` |

---

#### `grade.py`

| Property | Detail |
|---|---|
| **Purpose** | Build the `REVA-TUTOR-GRADE-CONTEXT` block with test results for the grade agent |
| **Input** | Single argument: path to `.c` file |
| **Reads** | Exercise files (test_cases array), `/tmp/reva_tutor_bin` (compiled binary from compile_check.py) |
| **Test execution** | Iterates over all `test_cases` in the exercise JSON; pipes `input` via stdin to the compiled binary with `timeout 5` to prevent hanging |
| **Test result format** | `PASS: <label>` or `FAIL: <label>` with `Expected:` and `Got:` lines |
| **Output** | Structured block between `---REVA-TUTOR-GRADE-CONTEXT---` and `---END-REVA-TUTOR-GRADE-CONTEXT---` delimiters, containing: student_id, exercise_id, compile output, style output, test_results, student_code |
| **Exit code** | 1 if filename parse fails |
| **Dependencies** | `parse_exercise_filename.py`, `compile_check.py`, `check_style.py` |

---

#### `init_student.py`

| Property | Detail |
|---|---|
| **Purpose** | Register a new ACP student and create their progress JSON |
| **Input** | Four arguments: `student_id`, `name`, `section`, `grade` |
| **Writes** | `student_data/progress/<student_id>.json` |
| **Initial state** | `FUNC` (ACP Unit 1): `assigned_level: 1` (or `_prereq_INTRO`: `1` if grade is low); all other topics: `assigned_level: null` |
| **Error** | Aborts if progress file already exists |
| **Output** | Confirmation message with student name, section, and 1st sem grade |
| **Dependencies** | Python 3 standard library only |

---

#### `make_template.py`

| Property | Detail |
|---|---|
| **Purpose** | Generate a populated `.c` template file for a given exercise |
| **Input** | Three arguments: `filename`, `exercise_id`, `student_id` |
| **Reads** | `exercises/prerequisites.json`, `exercises/practice.json`, `exercises/advanced.json` (problem statement, constraints, sample I/O, CO mapping) and `exercises/lab_programs.json` (for lab program exercises) |
| **Writes** | The `.c` file specified by `filename` |
| **Template content** | Comment header with exercise metadata + problem statement + empty `main()` with `#include <stdio.h>` |
| **Called by** | `next.sh` |
| **Dependencies** | Python 3 standard library only (`json`, `datetime`, `pathlib`) |

---

### 13.3 VS Code Tasks

The `.vscode/tasks.json` exposes these tasks in the VS Code task runner (`Ctrl+Shift+P → Run Task`):

| Task Label | Command | Shortcut Use |
|---|---|---|
| REVA: Get Help | `python scripts/help.py ${file}` | Active `.c` file → help context |
| REVA: Grade My Code | `python scripts/grade.py ${file}` | Active `.c` file → grade context |
| REVA: Next Exercise | `python scripts/next.py ${input:studentId}` | Prompt for student ID → create exercise file |
| REVA: Register Student | `python scripts/init_student.py ...` | One-time student registration |

---

## 14. Directory Layout

```
reva-c-tutor/
│
├── SKILL.md                         ← Master router (agent entry point)
├── reva-c-tutor-agent.md            ← This specification
├── README.md                        ← Student-facing quick start
│
├── agents/
│   ├── help_agent.md                ← Socratic help specialist
│   └── grade_agent.md               ← Grading specialist
│
├── exercises/
│   ├── prerequisites.json           ← Prerequisite exercises
│   ├── practice.json                ← Extra practice exercises (syllabus-aligned)
│   ├── advanced.json                ← Advanced practice exercises
│   └── lab_programs.json            ← 10 mandatory lab programs
│
├── student_data/                    ← Consolidated folder for student runtime data (mutable, git-ignored)
│   ├── progress/
│   │   ├── .gitkeep
│   │   └── [student_id].json        ← One file per student
│   └── sessions/
│       ├── .gitkeep
│       └── [student_id]/
│           └── [ISO8601-timestamp]_[exercise_id].md
│
├── rubrics/
│   └── rubric_master.md             ← Full rubric (mirrors §11)
│
├── scripts/
│   ├── parse_exercise_filename.sh
│   ├── compile_check.sh
│   ├── check_style.sh
│   ├── make_template.py
│   ├── next.sh
│   ├── help.sh
│   ├── grade.sh
│   └── init_student.sh
│
├── config/
│   └── agent_config.json
│
└── docs/
    ├── syllabus.md                  ← ACP course syllabus
    ├── coding_style_guide.md        ← Student-facing S01–S10 with examples
    └── how_to_use.md                ← Student onboarding guide
```

---

## 15. Configuration Files

### 15.1 `config/agent_config.json` — Key Fields

| Field | Value | Description |
|---|---|---|
| `agent_version` | `"2.0"` | Spec version |
| `institution` | `"REVA University"` | Institution name |
| `department` | `"School of Computer Science and Engineering"` | Department |
| `course` | `"Advanced C Programming with Generative AI"` | Course name |
| `academic_year` | `"2025-26"` | Academic year |
| `scaffolding.max_help_tiers` | `5` | Number of help tiers before suggesting restart |
| `scaffolding.metacognitive_prompt_always` | `true` | Always open with self-assessment prompt |
| `scaffolding.style_after_logic` | `true` | Address style only after conceptual help |
| `scaffolding.never_give_direct_answer` | `true` | Core principle — always enforced |
| `grading.total_marks` | `10` | Total marks per exercise |
| `grading.dimensions` | Correctness: 4, Style: 2, Robustness: 2, Docs: 1, Efficiency: 1 | Rubric weights |
| `grading.promotion_threshold` | `7` | Minimum score to advance demonstrated_level |
| `grading.remediation_threshold` | `4` | Score below which assigned_level is reduced |
| `progress.min_score_to_advance` | `7` | Same as promotion_threshold |
| `progress.max_variants_per_level` | `5` | After 5 variants exhausted, advance regardless of score |

### 15.2 `.vscode/tasks.json` — Structure

The VS Code tasks file registers the four student-facing tasks (Get Help, Grade My Code, Next Exercise, Register Student) as shell commands in the VS Code task runner. It also registers a `studentId` input prompt so that the Next Exercise task can capture the student ID interactively.

---

## 16. Extension Roadmap

| Phase | Feature | Rationale |
|---|---|---|
| v2.1 | **Lab program support in next.sh**: `next.sh --lab` assigns the next unsubmitted lab program from `lab_programs.json` | Unified workflow for both mandatory and optional exercises |
| v2.2 | **CO progress summary**: grade agent appends per-CO progress summary to session log | Faculty can assess attainment against each CO |
| v2.3 | **Misconception database**: track which common mistakes recur per student and surface targeted review exercises | Personalised remediation |
| v2.4 | **Faculty dashboard**: aggregated view of class performance per topic/CO/level; flags students who have requested 5+ helps on the same exercise | Instructor oversight and early intervention |
| v3.0 | **Mental model verification questions**: after grading 8+, ask the student to predict output for a novel input without running the code | Direct test of mental execution model — the core goal |
| v3.1 | **Mini-project module (CO6)**: structured prompting workflow with AI tool, iterative refinement cycles, and code analysis | Addresses CO6 directly; prompt engineering as a taught skill |
| v3.2 | **C memory visualiser integration** (Valgrind output in plain English) | Makes pointer and dynamic memory mental models concrete |

---

*Specification authored for REVA University, School of Computer Science and Engineering*
*Pedagogical framework grounded in: Vygotsky (1978), Quintana et al. (2004), Kargupta et al. (2023/ACM SIGCSE), Sweller (1988), Flavell (1979).*
*This document is the design reference. The agent reads `SKILL.md` → `agents/help_agent.md` or `agents/grade_agent.md` on every invocation — not this file.*
