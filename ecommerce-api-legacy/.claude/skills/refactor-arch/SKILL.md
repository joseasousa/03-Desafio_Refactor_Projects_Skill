---
name: refactor-arch
description: Technology-agnostic architecture audit and MVC refactoring workflow. Use when Codex needs to analyze a codebase, detect language/framework/database/current architecture, audit MVC/SOLID anti-patterns including deprecated APIs with exact file and line references, save a structured audit report, pause for confirmation, refactor into MVC-compatible layers, and validate the result through tests/build/boot plus public interfaces for any stack.
---

# Refactor Arch

Use this skill to audit an existing project, report architecture/code-smell findings, then refactor toward MVC after explicit confirmation while preserving public behavior.

The workflow is technology-agnostic. Always infer the project stack from files in the repository before choosing commands, folder names, or validation strategy.

## References

Load only what is needed for the current phase:

- `references/project-analysis-heuristics.md`: stack, framework, database, domain, architecture, and validation discovery.
- `references/anti-pattern-catalog.md`: required catalog scan with severity guidance and deprecated/obsolete API detection.
- `references/audit-report-template.md`: exact report format for Phase 1, Phase 2, Phase 3, and challenge acceptance.
- `references/mvc-architecture-guidelines.md`: MVC target responsibilities for Models, Views/Routes, Controllers, services, serializers, config, and error handling.
- `references/mvc-refactor-playbook.md`: concrete before/after transformations to apply during Phase 3.
- `references/severity-rubric.md`: severity definitions and classification rules.

For the three challenge projects, map report numbers exactly:

- `code-smells-project/` -> `reports/audit-project-1.md`
- `ecommerce-api-legacy/` -> `reports/audit-project-2.md`
- `task-manager-api/` -> `reports/audit-project-3.md`

## Phase 1 - Analysis

Inspect the repository before editing anything. Read `project-analysis-heuristics.md` and identify:

- language/runtime, framework, package manager, database/storage, and key dependencies
- domain, public interfaces, entrypoints, routes, CLI commands, jobs, events, or handlers
- current architecture, layer boundaries, source file count, and approximate lines analyzed
- available validation commands from manifests and framework conventions

Print `PHASE 1: PROJECT ANALYSIS` using `audit-report-template.md`. The summary must describe the domain and architecture in stack-specific terms.

## Phase 2 - Audit

Before scanning, read `severity-rubric.md`, `anti-pattern-catalog.md`, and `audit-report-template.md`.

Audit every relevant source file against the catalog. Consider at least 8 anti-patterns and always run a deprecated/obsolete API scan. For each finding include:

- severity ordered as `CRITICAL`, `HIGH`, `MEDIUM`, then `LOW`
- exact `path:line` or `path:start-end`
- description, impact, and concrete MVC/SOLID-oriented recommendation
- deprecated API name and modern equivalent when applicable

For challenge projects, the Phase 2 report must contain at least 5 findings, including at least 1 `CRITICAL` or `HIGH`, and must save the full artifact to the mapped `reports/audit-project-<n>.md` path.

After saving the report, stop and ask for confirmation before Phase 3 unless the current user request explicitly asks for end-to-end implementation. Do not modify repo-tracked files during Phase 1 or Phase 2.

## Phase 3 - Refactor and Validate

After confirmation, read `mvc-architecture-guidelines.md` and `mvc-refactor-playbook.md`. Apply the playbook as a checklist: consider at least 8 transformations and mark each as applied, rejected, or not applicable with a stack-specific reason.

Refactor incrementally:

- preserve route paths, request/response shapes, CLI flags, schemas, and database compatibility
- create or validate MVC-equivalent `models/`, `controllers/`, and `routes/` or `views/` unless the framework has a stronger native convention
- move config to a config module/object and avoid hardcoded secrets/defaults that imply production safety
- keep routes/views thin, controllers focused on orchestration, and models/repositories responsible for persistence/domain data
- centralize validation, serialization, and error handling according to the stack
- keep flat compatibility files only as documented shims that import from the new architecture

Validate technology-agnostically. Detect commands from manifests such as `package.json`, `pyproject.toml`, `requirements.txt`, `pom.xml`, `build.gradle`, `Cargo.toml`, `go.mod`, `composer.json`, and framework files. Prefer automated tests, then build/typecheck/lint/syntax checks, then boot commands, then public-interface smoke tests. Public interfaces may be HTTP endpoints, CLI commands, jobs, message handlers, functions, or equivalent user-facing workflows.

Print `PHASE 3: REFACTORING COMPLETE` using `audit-report-template.md`, including validation evidence, unresolved risks, MVC structure evidence, deprecated API scan evidence, and the challenge acceptance matrix when all three projects are in scope.
