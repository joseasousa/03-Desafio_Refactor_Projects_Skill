# Severity Rubric

Use these severity levels for MVC, SOLID, security, and maintainability findings.

## CRITICAL

Use for severe architecture or security failures that break correct behavior, expose sensitive data, or completely collapse separation of responsibilities.

Examples:

- hardcoded credentials, secrets, tokens, or private keys
- SQL injection or equivalent unsafe query/command construction
- god class, god module, or god method combining routing, persistence, complex business logic, validation, and formatting
- business-critical behavior that is untestable because all concerns are fused
- data exposure, authentication bypass, or authorization missing from protected operations

## HIGH

Use for strong MVC or SOLID violations that significantly harm maintainability, testability, or change safety.

Examples:

- heavy business logic embedded in controllers, routes, templates, or UI handlers
- strong coupling to concrete infrastructure without dependency injection or a composition root
- global mutable state used across request or domain flows
- duplicated domain rules across controllers, views, jobs, or handlers
- models directly formatting HTTP responses or views directly querying persistence

## MEDIUM

Use for standardization problems, moderate duplication, moderate performance risks, or missing boundary checks.

Examples:

- N+1 database access patterns
- validation missing or inconsistent at public boundaries
- middleware used for business rules instead of cross-cutting concerns
- repeated query fragments, mapping logic, or serializers
- inconsistent error handling that complicates clients or tests
- framework conventions partially followed in ways that confuse ownership

## LOW

Use for local readability and small maintainability improvements.

Examples:

- unclear variable, function, class, or file names
- magic numbers or magic strings with no domain explanation
- overlong local blocks that are still understandable
- comments that restate code or missing comments around non-obvious logic
- small formatting or organization issues not covered by tooling

## Classification Rules

- Classify by impact, not by how easy the fix is.
- Prefer the highest applicable severity when a finding spans multiple categories.
- Tie every finding to MVC/SOLID/security impact, not personal style.
- Include exact file and line references for every finding.
- Do not invent security findings; mark uncertainty as an open question only after inspection.
- Exclude generated, vendored, build, lock, and minified files unless they are the source of application behavior or secrets.
- Group repeated instances only when they share one root cause; still provide representative exact locations.
