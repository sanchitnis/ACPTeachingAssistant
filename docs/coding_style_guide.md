# REVA C Coding Style Guide
**Rules S01–S10 — Effective from Day 1**

All student code submitted through the REVA C Tutor must satisfy these rules.
Violations are checked automatically by `scripts/check_style.py` and deduct from your grade.

---

## S01 — One Statement Per Line

**Rule**: Every C statement ends with `;` and occupies its own line.

❌ Violation:
```c
int a; int b; int c;
```
✅ Correct:
```c
int a;
int b;
int c;
```

---

## S02 — All Declarations at the Top of the Block (C89 Style)

**Rule**: Declare all variables at the beginning of their enclosing `{}` block, before any executable statements.

> *Why enforced despite C99?* Early declaration grouping makes it easy to see all variables a function uses at a glance — a habit that pays dividends when debugging.

❌ Violation:
```c
int main(void) {
    int n;
    scanf("%d", &n);
    int i;          /* ← declaration after executable statement */
    ...
}
```
✅ Correct:
```c
int main(void) {
    int n;
    int i;

    scanf("%d", &n);
    ...
}
```

---

## S03 — No Magic Numbers

**Rule**: Any numeric literal that is not `0` or `1` must be named. Use `#define` for constants.

❌ Violation:
```c
for (i = 0; i < 100; i++)   /* What does 100 mean? */
```
✅ Correct:
```c
#define MAX_SIZE 100

for (i = 0; i < MAX_SIZE; i++)
```

---

## S04 — 4-Space Indentation, No Tabs

**Rule**: Use exactly 4 spaces per indent level. Configure your editor to insert spaces, not tabs.

❌ Violation:
```c
if (x > 0) {
  printf("positive");   /* 2-space indent */
}
```
✅ Correct:
```c
if (x > 0) {
    printf("positive");   /* 4-space indent */
}
```

---

## S05 — Every Function Must Have a Comment Block

**Rule**: Every function (including `main`) must have a block comment directly above it stating:
- **Function**: name
- **Purpose**: what it does in one sentence
- **Params**: each parameter, type, and meaning
- **Returns**: what the return value means

✅ Correct:
```c
/*
 * Function : factorial
 * Purpose  : Computes n! iteratively for 0 <= n <= 20.
 * Params   : n (int) — the non-negative integer
 * Returns  : n! as a long long
 */
long long factorial(int n) {
    ...
}
```

---

## S06 — `main` Returns `int` with `return 0`

**Rule**: Always declare `main` as `int main(void)` or `int main(int argc, char *argv[])`.  
Always end `main` with `return 0;`.

❌ Violations:
```c
void main()        /* wrong return type */
int main()         /* missing return 0 at end */
```
✅ Correct:
```c
int main(void) {
    ...
    return 0;
}
```

---

## S07 — No Unused Variables

**Rule**: Every declared variable must be used. Remove variables you no longer need.

❌ Violation:
```c
int temp;   /* declared but never read */
int n;
scanf("%d", &n);
```

---

## S08 — Opening Brace on Same Line as Control Structure

**Rule**: Put `{` on the same line as `if`, `else`, `for`, `while`, `do`, `switch`, and function headers.

❌ Violation:
```c
if (x > 0)
{
    printf("positive");
}
```
✅ Correct:
```c
if (x > 0) {
    printf("positive");
}
```

---

## S09 — Single Blank Line Between Declarations and Statements

**Rule**: Leave exactly one blank line between the variable declaration block and the first executable statement in a function body.

✅ Correct:
```c
int main(void) {
    int n;
    int i;
    int sum;

    scanf("%d", &n);   /* ← one blank line above this */
    ...
}
```

---

## S10 — Meaningful Variable Names

**Rule**: Variables must have descriptive names. Single-letter names are acceptable only for:
- Loop counters: `i`, `j`, `k`
- Mathematical coordinates: `x`, `y`, `z`

❌ Violation:
```c
int a, b, c, d;   /* what do these hold? */
```
✅ Correct:
```c
int total_marks;
int num_students;
int passing_score;
```

---

## Quick Reference Table

| ID | Rule | Checked By |
|---|---|---|
| S01 | One statement per line | cppcheck |
| S02 | Declarations at top of block | custom awk |
| S03 | No magic numbers | custom grep |
| S04 | 4-space indentation | cppcheck |
| S05 | Function comment blocks | cppcheck |
| S06 | `int main` + `return 0` | grep |
| S07 | No unused variables | cppcheck |
| S08 | Opening brace same line | grep |
| S09 | Blank line after declarations | cppcheck |
| S10 | Meaningful variable names | agent review |
