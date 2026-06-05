# REVA C Tutor

**AI-powered Socratic teaching assistant for C programming � REVA University, School of CSE**

---

## Overview

REVA C Tutor is a VS Code�integrated system designed to help you master C programming. It assigns exercises, guides you through debugging via **Socratic questioning**, and grades your submissions based on a professional 10-point rubric.

The tutor's goal is to build your mental execution model. It will **never** give you the answer or write code for you�instead, it helps you find the bugs yourself.

---

## Prerequisites

Before starting, ensure you have the following tools installed and available in your system path:

### Windows Users (Crucial)
1.  **Git for Windows**: [Download here](https://git-scm.com/download/win). During installation, ensure "**Add Git to PATH**" is selected. This provides the `bash` environment required by the scripts.
2.  **Verify Bash**: Open PowerShell and type `bash --version`. If it fails, you must install Git for Windows.

### Required Tools (All Platforms)

| Tool | Install command (Ubuntu/WSL) | Windows Recommendation |
|---|---|---|
| GCC | `sudo apt install gcc` | [MinGW-w64](https://www.mingw-w64.org/) or [Choco](https://chocolatey.org/) |
| cppcheck | `sudo apt install cppcheck` | `choco install cppcheck` |
| jq | `sudo apt install jq` | `choco install jq` or [Download Binary](https://jqlang.github.io/jq/download/) |
| Python 3 | `sudo apt install python3` | [Python.org](https://www.python.org/downloads/windows/) |

After installing, make the scripts executable by running this in your terminal once:
```bash
chmod +x scripts/*.sh
```

---

## Getting Started

The recommended workflow uses VS Code Tasks. To run any task, press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS), type **Tasks: Run Task**, and select the task.

### 1. Register Yourself (Once)
Run the task **`REVA: Register Student`**. Follow the prompts to enter your Student ID, Full Name, Section, and your 1st semester C Programming grade. This creates your progress file and determines if you need catch-up exercises.

### 2. Get Your First Exercise
Run the task **`REVA: Next Exercise`**. This creates a `.c` file in the `student_data/` folder (e.g., `student_data/INTRO_L1_a_raj22cs045.c`). Open this file to see your assignment.

### 3. Write and Test Your Code
Implement your solution in the created `.c` file. Follow the [Coding Style Guide](docs/coding_style_guide.md) strictly, as it affects your grade.

### 4. Get Help (When Stuck)
If you encounter compiler errors or logical bugs:
1. Keep your exercise `.c` file open.
2. Run the task **`REVA: Get Help`**.
3. Attach the generated `student_data/help_context.txt` to your agent chat (`@help_context.txt`) and ask for guidance.

### 5. Submit for Grading
When you think your solution is ready:
1. Run the task **`REVA: Grade My Code`**.
2. Attach the generated `student_data/grade_context.txt` to your chat and ask the agent to grade your code.
3. If you score **7/10 or higher**, you can move to the next exercise.

---

## The Tutor's Principles

The agent is your guide, not your ghostwriter.

**The agent will NEVER:**
- Write code for you.
- Tell you exactly which line is wrong.
- Give you the corrected version of your code.

**The agent WILL:**
- Ask questions that lead you to the answer.
- Provide analogies and partial code traces.
- Give targeted feedback on your grade and style violations.

---

## Troubleshooting

- **File Naming**: Exercises must follow `TOPIC_Ln_variant_studentid.c`. If you rename them manually, scripts may fail.
- **Active File**: Always keep the exercise `.c` file active in your editor when running **Get Help** or **Grade My Code**.
- **Tool Errors**: If `help.sh` fails, ensure `gcc`, `cppcheck`, and `jq` are correctly installed.

---

## Professional Standards
Code quality is as important as correctness. Refer to the [Coding Style Guide](docs/coding_style_guide.md) for rules on indentation, naming conventions, and documentation.

---

For technical details, architecture, and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

*REVA University | School of Computer Science and Engineering | AY 2025-26*
