# MVC Architecture Guidelines

Use these rules as the Phase 3 target. Adapt names to the framework, but preserve responsibilities.

## Models

- Own domain data access, repositories, ORM models, persistence adapters, and invariants close to data.
- Never expose secrets or internal credential fields in public serializers.
- Use parameterized queries or ORM-safe APIs for user-controlled input.
- Batch or eager-load related data when list/report endpoints would otherwise create N+1 access.

## Views or Routes

- Bind public interfaces: HTTP routes, CLI commands, jobs, event handlers, templates, or response DTOs.
- Extract request data and pass it to controllers/services.
- Keep route files thin; no direct SQL, long business branches, or domain calculations.
- Preserve existing public paths, methods, command names, flags, and response shapes unless fixing a documented critical risk.

## Controllers

- Orchestrate use cases and choose response/status outcomes.
- Coordinate validation, authorization, services, transaction boundaries, and serializers.
- Avoid direct persistence details unless the framework convention explicitly treats controllers as the model boundary.

## Supporting Layers

- Config: load environment-specific values in one module/object; avoid hardcoded secrets and production-like defaults.
- Services: hold workflows spanning multiple models, payment/email/adapters, reports, and domain policies.
- Validators/schemas: centralize public input validation and reusable domain constants.
- Error handling: normalize expected errors at the boundary and log unexpected failures without leaking sensitive details.

## Completion Rules

- Challenge projects must have MVC-equivalent directories for `models/`, `controllers/`, and `routes/` or `views/`.
- Flat files such as `models.py`, `controllers.py`, or `services.py` may remain only as documented compatibility shims.
- Do not claim Phase 3 completion unless boot/interface validation ran or a concrete blocker is documented.
