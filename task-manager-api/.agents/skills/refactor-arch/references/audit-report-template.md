# Audit Report Template

Use concise, structured output. Keep headings stable so users can compare runs.

## Phase 1: Project Analysis

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language and version if known>
Framework:     <framework and version if known>
Dependencies:  <important runtime dependencies>
Domain:        <inferred business domain>
Architecture:  <current architecture summary>
Source files:  <count> files analyzed
DB tables:     <tables/entities if found, or "Not detected">
Entrypoints:   <routes/apps/commands/jobs>
Validation:    <available test/build/boot commands>
================================
```

## Architecture Audit Report

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project name>
Stack: <language + framework>
Files: <count> analyzed | ~<lines> lines of code

## Summary

CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [<SEVERITY>] <finding title>

File: <path>:<line-or-range>
Description: <specific problem observed in the code>
Impact: <why this harms security, behavior, MVC, SOLID, tests, or maintenance>
Recommendation: <concrete MVC/SOLID-oriented correction>

================================
Total: <n> findings
================================
```

## Saved Phase 2 Artifact

For three-project challenge runs, save the full Phase 2 artifact exactly as emitted to:

```text
reports/audit-project-<n>.md
```

The saved file must include both sections in this order:

1. `PHASE 1: PROJECT ANALYSIS`
2. `ARCHITECTURE AUDIT REPORT`

It must also include the findings summary, all findings, the total count, and the Phase 3 confirmation gate. Do not save only a summary.

## Phase 3: Refactoring Complete

```markdown
================================
PHASE 3: REFACTORING COMPLETE
================================

## New Project Structure

<tree or compact list of important architecture changes>

## Resolved Findings

- [<SEVERITY>] <finding title> -> <what changed>

## Validation

✓ <successful command or smoke test>
! <skipped or partial validation with reason>
✗ <failed validation with brief cause, if any>

## Remaining Risks

- <risk or "None identified after focused re-scan">

## Acceptance Matrix

| Project     | Stack detected | Findings >= 5 | CRITICAL/HIGH found | App works after refactor |
| ----------- | -------------: | ------------: | ------------------: | -----------------------: |
| <project-1> |      PASS/FAIL |     PASS/FAIL |           PASS/FAIL |                PASS/FAIL |
| <project-2> |      PASS/FAIL |     PASS/FAIL |           PASS/FAIL |                PASS/FAIL |
| <project-3> |      PASS/FAIL |     PASS/FAIL |           PASS/FAIL |                PASS/FAIL |

================================
```

## Reporting Rules

- Sort findings by severity: CRITICAL, HIGH, MEDIUM, LOW.
- Use exact paths relative to the repository root.
- Use exact lines or ranges.
- Keep recommendations actionable and specific to the stack.
- If there are no findings for a severity, show `0` in the summary.
- Do not claim success without listing validation evidence.
- For single-project runs, omit the acceptance matrix unless the user asks for it.
- For three-project runs, include the acceptance matrix and the paths of all saved Phase 2 report files.
