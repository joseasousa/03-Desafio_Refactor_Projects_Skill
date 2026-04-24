# Anti-Pattern Catalog

Use this catalog during Phase 2 before classifying audit findings. Treat every entry as a required scan item. Findings still need exact file and line references and must be classified with `severity-rubric.md`.

## Required Scan Checklist

- Consider at least 8 anti-patterns from this catalog on every run.
- Always scan for deprecated or obsolete APIs.
- When an anti-pattern is not present, do not create a finding; mention the completed scan in the audit summary or completion checklist when relevant.
- When a deprecated API is found, name the old API and recommend the modern equivalent.

## 1. God Module or God Class

- Description: One module/class owns routing, validation, persistence, business rules, and response formatting.
- Detection signal: A single file or class imports framework routing, database clients/ORM models, validation helpers, and formatting/serialization code while also containing complex business branches.
- Suggested severity: CRITICAL when behavior is business-critical or security-sensitive; otherwise HIGH.
- Recommendation: Split responsibilities into route/view, controller/use-case, model/repository, serializer/view, and service modules.
- Example: `app.py` defines routes, opens database connections, validates request bodies, calculates totals, and returns HTTP responses.

## 2. Fat Route or Fat Controller

- Description: Boundary handlers contain business decisions that should live in controllers, services, or domain models.
- Detection signal: Route/controller functions exceed simple request extraction and orchestration, or contain loops, pricing rules, authorization branches, persistence queries, and response formatting together.
- Suggested severity: HIGH.
- Recommendation: Keep route declarations thin, move orchestration to controllers, and move reusable domain rules to services or models.
- Example: A Flask route calculates discounts, updates stock, writes orders, and builds JSON directly.

## 3. Persistence in Presentation Boundary

- Description: Routes, views, UI handlers, serializers, or templates directly query or mutate storage.
- Detection signal: SQL strings, ORM queries, repository calls, filesystem writes, or external persistence clients appear inside presentation boundary code.
- Suggested severity: HIGH for write paths or sensitive data; MEDIUM for simple reads.
- Recommendation: Move persistence behind models, repositories, adapters, or data services with explicit methods.
- Example: `GET /users` handler executes `SELECT * FROM users` and maps database rows itself.

## 4. Deprecated or Obsolete API Usage

- Description: Code depends on an API that the runtime, framework, or library has deprecated, replaced, or marked obsolete.
- Detection signal: Deprecated decorators or annotations, compiler/runtime warnings, changelog notes, docs marked "deprecated", legacy imports, renamed methods, removed aliases, or comments such as `TODO migrate from old API`.
- Suggested severity: HIGH when the API is removed or security-relevant; MEDIUM when supported but discouraged; LOW for cosmetic rename-only migrations.
- Recommendation: Replace the obsolete API with the documented modern equivalent while preserving public behavior. Report the old API, the line, and the recommended replacement.
- Examples:
  - Flask: replace `before_first_request` startup initialization with an application factory or explicit startup setup compatible with current Flask versions.
  - SQLAlchemy: replace legacy `Query.get()` usage with `Session.get(Model, id)`.
  - Python: replace deprecated `datetime.utcnow()` timestamp creation with timezone-aware `datetime.now(timezone.utc)` when UTC awareness is required.
  - Node.js: replace deprecated `new Buffer(value)` with `Buffer.from(value)` or `Buffer.alloc(size)`.

## 5. Duplicated Domain Rule

- Description: The same business rule is implemented in multiple routes, controllers, jobs, serializers, or UI handlers.
- Detection signal: Repeated conditionals, constants, calculations, validation messages, or status transitions across unrelated files.
- Suggested severity: HIGH when divergence can affect money, authorization, or data integrity; otherwise MEDIUM.
- Recommendation: Extract the rule into a domain service, model invariant, validator, or policy module and reuse it from boundaries.
- Example: Discount eligibility is calculated separately in checkout, reporting, and admin update handlers.

## 6. Anemic or Leaky Model

- Description: Models are only passive dictionaries/data containers while domain invariants live elsewhere, or models expose persistence details to higher layers.
- Detection signal: Model files contain only fields while controllers mutate internal fields directly, or callers build raw SQL/filter fragments using model internals.
- Suggested severity: MEDIUM to HIGH depending on invariant risk.
- Recommendation: Move invariants and data-access operations close to the model/repository boundary and expose intention-revealing methods.
- Example: Controllers manually set order status transitions instead of calling `order.cancel()` or an `OrderService.cancel_order()`.

## 7. Global Mutable State Across Requests or Workflows

- Description: Shared mutable variables hold request, user, transaction, cache, or domain state without lifecycle control.
- Detection signal: Module-level lists/dicts/singletons are mutated by handlers, controllers, or services and read by unrelated flows.
- Suggested severity: HIGH for request/user/security data; MEDIUM for local caches with correctness risk.
- Recommendation: Use request-scoped context, dependency injection, framework-managed services, explicit repositories, or concurrency-safe storage.
- Example: A global `current_user` or `cart_items` object changes during request handling.

## 8. Unsafe Query or Command Construction

- Description: User-controlled data is interpolated into SQL, shell commands, file paths, URLs, or templates without safe parameterization.
- Detection signal: String concatenation, f-strings, template strings, or format calls combine request input with SQL/commands/path traversal-sensitive operations.
- Suggested severity: CRITICAL.
- Recommendation: Use parameterized queries, command argument arrays, safe path joins with allowlists, and framework escaping.
- Example: `f"SELECT * FROM users WHERE email = '{email}'"` in a route or repository.

## 9. Missing Boundary Validation

- Description: Public interfaces accept data without schema, type, range, authorization, or invariant checks.
- Detection signal: Request bodies, query params, CLI args, event payloads, or form data are used directly in business logic or persistence.
- Suggested severity: HIGH for write/security flows; MEDIUM otherwise.
- Recommendation: Add boundary validators or serializers and keep model-level invariants for rules that must hold regardless of entrypoint.
- Example: A create-order endpoint trusts `price`, `role`, or `status` fields from the client.

## 10. Middleware or Interceptor with Domain Branching

- Description: Middleware performs business-specific decisions instead of cross-cutting concerns.
- Detection signal: Middleware branches on product/order/user domain states, mutates domain records, or chooses business outcomes.
- Suggested severity: MEDIUM to HIGH.
- Recommendation: Keep middleware for authentication, parsing, CORS, logging, and error normalization; move domain decisions to controllers/services.
- Example: Auth middleware also cancels unpaid orders based on age.

## 11. N+1 Data Access Pattern

- Description: Code performs repeated queries or external calls inside loops where batching or eager loading is appropriate.
- Detection signal: ORM queries, repository calls, HTTP calls, or filesystem reads occur inside loops over records.
- Suggested severity: MEDIUM; HIGH when it affects critical paths or large datasets.
- Recommendation: Batch queries, eager load relations, introduce repository methods that load the required graph, or cache safe immutable data.
- Example: For every order in a report, code separately queries the user and payment.

## 12. Compatibility Shim Masquerading as Final Architecture

- Description: A flat file remains as the main implementation while the reported architecture claims MVC completion.
- Detection signal: Files such as `models.py`, `controllers.py`, `routes.py`, or `services.py` still contain primary logic after a supposed migration to packages/directories.
- Suggested severity: HIGH for challenge acceptance; MEDIUM otherwise.
- Recommendation: Move primary logic into MVC packages/directories or native framework equivalents. Keep flat files only as thin documented shims that import/re-export from the new structure.
- Example: `controllers.py` still defines all handlers instead of delegating to `controllers/user_controller.py` or equivalent modules.
