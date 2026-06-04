# REVA C Tutor — Student Quick-Start Guide

Welcome to the REVA C Programming Practice System. This guide gets you up and running in 5 minutes.

---

## Prerequisites

Install these tools before you start:

| Tool | Install command (Ubuntu/WSL) |
|---|---|
| GCC | `sudo apt install gcc` |
| cppcheck | `sudo apt install cppcheck` |
| jq | `sudo apt install jq` |
| Python 3 | `sudo apt install python3` |

Make all scripts executable (run once):
```bash
chmod +x scripts/*.sh
```

---

## Step 1 — Register Yourself (Once)

```bash
./scripts/init_student.sh raj22cs045 "Raj Kumar" "BTech-CS-2B"
```

This creates `student_data/progress/raj22cs045.json` which tracks your progress through all topics.

---

## Step 2 — Get Your First Exercise

```bash
./scripts/next.sh raj22cs045
```

This creates a `.c` file in the project root with your exercise embedded in the comments.  
Open it in VS Code:

```bash
code INTRO_L1_a_raj22cs045.c
```

---

## Step 3 — Write Your Solution

Edit the file. Your code goes inside `main()` (or in new functions above it).  
Read `docs/coding_style_guide.md` — style is graded from Day 1.

---

## Step 4 — Get Help (When Stuck)

Run:
```bash
./scripts/help.sh INTRO_L1_a_raj22cs045.c
```

This prints a **context block**. Copy the entire block (from `---REVA-TUTOR-CONTEXT---` to `---END-REVA-TUTOR-CONTEXT---`) and paste it into your Claude chat session.

The agent will ask you Socratic questions — it will **never** give you the answer, but it will guide you to find it yourself.

> **Each time you call `help.sh`, the help counter increments.**  
> At tier 5+, the agent may suggest a simpler warm-up exercise.

---

## Step 5 — Submit for Grading

When you are happy with your solution:

```bash
./scripts/grade.sh INTRO_L1_a_raj22cs045.c
```

Copy the grade context block and paste it into your Claude chat.  
The agent will return your score (out of 10) broken down by:

| Dimension | Marks |
|---|---|
| Correctness | /4 |
| Code Quality & Style | /2 |
| Robustness & Edge Cases | /2 |
| Documentation | /1 |
| Efficiency & Design | /1 |

---

## Step 6 — Get Your Next Exercise

After grading, call `next.sh` again for the next assigned exercise.

---

## Running with VS Code Tasks

If you are using VS Code, you can run all the scripts directly through VS Code's built-in Task runner without using the terminal manually. This is the recommended workflow.

### How to Run a Task

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS) to open the Command Palette.
2. Type `Tasks: Run Task` and press `Enter`.
3. Select the task you want to run from the dropdown list.

### Available Tasks

*   **`REVA: Register Student`**: Registers your profile. When run, VS Code will display prompts at the top of the window asking you to enter:
    1. Your **Student ID** (e.g., `raj22cs045`)
    2. Your **Full Name** (e.g., `Raj Kumar`)
    3. Your **Section** (e.g., `BTech-CS-2B`)
*   **`REVA: Next Exercise`**: Requests your next exercise. It will prompt you for your **Student ID** and automatically create the `.c` file template in the project root.
*   **`REVA: Get Help`**: Gathers compiler outputs, style checking results, and your code from the **currently active C file** in your editor, generating the help context block in the terminal panel.
*   **`REVA: Grade My Code`**: Compiles and runs tests against the **currently active C file**, producing the grading context block in the terminal panel.

> [!IMPORTANT]
> For **`REVA: Get Help`** and **`REVA: Grade My Code`** to work, you must have the exercise `.c` file open and active in your editor when you launch the task.

---

## The Tutor's Principles

The agent will **never**:
- Write code for you
- Tell you which line is wrong
- Give you the corrected version

It **will**:
- Ask you questions that lead you to the answer
- Provide analogies and partial traces
- Give you targeted feedback on your grade
- Tell you exactly which style rule you violated

This is intentional. You learn by figuring it out — the agent is your guide, not your ghostwriter.

---

## File Naming Convention

All exercise files must follow:
```
TOPIC_Ln_variant_studentid.c
```
Example: `LOOP_L2_a_raj22cs045.c`

If you rename a file incorrectly, the scripts will tell you what's wrong.

---

## Getting Help with the System

If `help.sh` fails with a tool error:
- Check that gcc, cppcheck, and jq are installed
- Run the script with `bash -x scripts/help.sh yourfile.c` for debug output
- Contact your instructor if a tool is unavailable on the lab machine

---

*REVA University | School of Computer Science and Engineering*
