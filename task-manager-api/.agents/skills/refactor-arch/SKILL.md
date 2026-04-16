---
name: refactor-arch
description: Technology-agnostic architecture audit and MVC refactoring workflow. Use when Codex needs to analyze a codebase, detect language/framework/current architecture, identify MVC/SOLID anti-patterns and code smells with exact file and line references, produce a structured architecture audit report, refactor the project into Model-View-Controller after explicit confirmation, and validate that the application still works.
---

# Refactor Arch

## Overview

Use this skill to audit an existing project for MVC/SOLID architecture problems, report all findings with severity and exact locations, then refactor toward MVC while preserving behavior.

This skill is technology-agnostic. Adapt naming, folders, framework conventions, and validation commands to the stack discovered in the repository.

When the task covers the three challenge projects, run the full workflow independently for each project. Save the Phase 2 audit output for every project in the invoking workspace under:

- `reports/audit-project-1.md`

Map project numbers deterministically from the order requested by the user. If the user does not provide an order, sort project directories by name and document the mapping in the final response.

## Resources

Load these references only when needed:

- `references/severity-rubric.md`: severity definitions and classification rules.
- `references/audit-report-template.md`: required report structure and output sections.
- `references/mvc-refactor-playbook.md`: MVC mapping and refactoring strategy across stacks.

## Workflow

### 1. Analyze the project

Inspect the repository before changing anything. Prefer `rg`, manifests, entrypoints, configs, tests, migrations, route declarations, schema files, and dependency files.

Identify:

- language, framework, runtime, package manager, and key dependencies
- app entrypoints and public interfaces: routes, CLI commands, jobs, events, views, APIs
- domain concepts and persistent data models
- current architecture and layer boundaries
- test commands, build commands, boot commands, and validation strategy
- source file count and approximate lines analyzed

Print `PHASE 1: PROJECT ANALYSIS` using `references/audit-report-template.md`.

### 2. Audit architecture and code smells

Read `references/severity-rubric.md` before classifying findings.

Find MVC/SOLID and maintainability issues, including:

- mixed routing, persistence, validation, business logic, rendering, and formatting in one unit
- god files, god classes, god methods, fat controllers, anemic or leaky models
- hardcoded secrets, unsafe query construction, exposed sensitive data
- strong coupling, missing dependency injection, global mutable state
- duplicated business rules, missing validation, N+1 access patterns, inappropriate middleware
- unclear names, magic numbers, low-signal comments, and local readability issues

For every finding, include exact location. Use `path:line` for a single line or `path:start-end` for a range. If a precise line cannot be established, keep investigating until it can; only mark a location as approximate when generated code, minified files, or framework metadata make precision impractical.

Print `ARCHITECTURE AUDIT REPORT` using `references/audit-report-template.md`.

If running against one of the three challenge projects, immediately save the complete Phase 2 output, including `PHASE 1: PROJECT ANALYSIS`, `ARCHITECTURE AUDIT REPORT`, findings, totals, and the refactoring gate, to the matching `reports/audit-project-{1,2,3}.md` file before asking for confirmation. Create `reports/` if needed.

Acceptance minimum for Phase 2 on each challenge project:

- stack detection in Phase 1 must be correct
- at least 5 findings
- at least 1 finding classified as `CRITICAL` or `HIGH`

If any minimum is missed, do not proceed to Phase 3 for that project. Re-read the source, adjust the audit strategy or reference files when the miss is caused by weak skill instructions, and rerun Phase 1/2. Expect 2-4 iterations when tuning the skill.

### 3. Stop for confirmation

After the audit report, stop and ask whether to proceed with refactoring unless the user explicitly requested a fully automated end-to-end refactor in the current turn.

Do not edit files before the user confirms.

### 4. Refactor to MVC

After confirmation, read `references/mvc-refactor-playbook.md`.

Refactor incrementally:

- preserve public behavior, route paths, request/response shapes, CLI flags, schemas, and database compatibility
- keep framework idioms instead of forcing a generic folder layout when the framework already has MVC conventions
- move business rules out of routes/views and into controllers or application services as appropriate
- move persistence and domain data access into models, repositories, or adapters according to the stack
- keep views/presentation responsible for HTTP handlers, templates, serializers, response formatting, or UI presentation
- introduce dependency injection or composition roots where it reduces coupling without adding unnecessary framework complexity
- update imports, registration, tests, and startup wiring together

Work with any existing user changes in the worktree. Do not revert unrelated edits.

### 5. Validate

Run the strongest available validation that is practical for the project:

- package manager install status or dependency check when needed
- unit/integration tests
- type checks, linters, builds, or framework checks
- application boot command
- endpoint smoke tests, CLI smoke tests, or equivalent user-facing workflows
- a focused re-scan for the original findings

If a validation command cannot be run, state the reason and the residual risk. Do not claim that all anti-patterns are eliminated unless a focused re-scan supports that claim.

Acceptance minimum for Phase 3 on each challenge project:

- the application must still work after refactoring, proven by tests, build/type checks, boot checks, endpoint/CLI smoke tests, or the strongest practical equivalent for the discovered stack

If validation fails, fix the refactor and rerun validation. If failure is caused by missing dependencies or sandbox/network restrictions, request the required approval and continue when possible.

### 6. Report completion

Print `PHASE 3: REFACTORING COMPLETE` using `references/audit-report-template.md`.

Include:

- new architecture and important files/directories
- findings resolved and any intentionally deferred items
- validation commands and outcomes
- remaining risks or follow-up work

For three-project challenge runs, include a compact acceptance matrix in the final response showing each project against:

- Phase 1 stack detected correctly
- Phase 2 findings count is >= 5
- Phase 2 includes at least 1 `CRITICAL` or `HIGH`
- Phase 3 application works after refactoring

All four criteria must pass for all three projects. If any criterion fails, report the failed project and continue iterating unless blocked by user approval, environment restrictions, or missing project files.
