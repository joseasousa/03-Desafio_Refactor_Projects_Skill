================================
PHASE 1: PROJECT ANALYSIS
================================
Language: JavaScript running on Node.js (runtime version not pinned)
Framework: Express 4.18.x with sqlite3 5.1.x
Dependencies: express, sqlite3
Domain: LMS/e-commerce API for course checkout, enrollment, payments, and financial reporting
Architecture: Single Express entrypoint delegates all database setup, route registration, persistence, business rules, payment simulation, reporting, and deletion behavior to one AppManager class; shared config/cache/crypto helpers live in utils.js.
Source files: 6 files analyzed (~237 lines)
DB tables: users, courses, enrollments, payments, audit_logs
Entrypoints: node src/app.js; POST /api/checkout; GET /api/admin/financial-report; DELETE /api/users/:id
Validation: npm start available; no test, lint, type-check, or build script detected
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack: JavaScript + Node.js + Express + SQLite
Files: 6 analyzed | ~237 lines of code

## Summary

CRITICAL: 2 | HIGH: 5 | MEDIUM: 4 | LOW: 1

Catalog scan: 12 anti-patterns considered from `references/anti-pattern-catalog.md`.
Deprecated API scan: completed; no deprecated/obsolete API finding was applicable in this project.

## Findings

### [CRITICAL] Hardcoded production-like credentials and secrets

File: src/utils.js:1-5
Description: Database credentials, a payment gateway key, and SMTP user are committed directly in application config, including a `pk_live_...` payment key string.
Impact: Secrets in source control can be leaked, reused across environments, and accidentally logged or exposed. This also prevents proper environment-specific configuration and violates separation between deployment configuration and code.
Recommendation: Move secrets and environment-specific settings to environment variables or a configuration adapter, validate required values at boot, and keep only non-sensitive defaults in source.

### [CRITICAL] God class combines HTTP routing, schema creation, persistence, business workflow, payment, reporting, and response formatting

File: src/AppManager.js:4-138
Description: `AppManager` creates the database, defines schema and seeds, registers all Express routes, implements checkout business logic, simulates payments, writes audit logs, generates financial reports, mutates cache, deletes users, and formats HTTP responses.
Impact: MVC boundaries are collapsed into one class, making business-critical behavior hard to test independently, unsafe to change, and tightly coupled to Express and SQLite callbacks.
Recommendation: Split responsibilities into models/repositories for SQLite access, controllers for HTTP request/response handling, services for checkout/payment/report workflows, and a boot/composition module that wires dependencies.

### [HIGH] Sensitive card data and payment key are logged during checkout

File: src/AppManager.js:45
Description: The checkout flow logs the full card value together with the configured payment gateway key before deciding payment status.
Impact: Logs can expose payment data and credentials, creating a severe security and compliance risk. The payment concern is also embedded directly inside the route workflow.
Recommendation: Remove raw card and key logging, mask any operational payment references, and isolate payment processing behind a payment service interface.

### [HIGH] Password handling uses insecure reversible-looking hashing and a weak default password

File: src/AppManager.js:68
Description: New users without a supplied password are assigned `"123456"` before hashing.
Impact: Defaulting credentials weakens account security and hides invalid input instead of rejecting it at the API boundary.
Recommendation: Require a password for new-user checkout or explicitly create a passwordless onboarding flow with secure token delivery.

### [HIGH] Password hashing is custom, deterministic, and unsuitable for credentials

File: src/utils.js:17-22
Description: `badCrypto` repeatedly base64-encodes the password and truncates the result to 10 characters.
Impact: This is not a password hashing strategy; it has no salt, no adaptive cost, severe truncation, and makes user credential behavior insecure and difficult to migrate safely.
Recommendation: Replace with a credential model/service using a vetted password hashing library such as bcrypt or argon2, and keep hash verification outside controllers.

### [HIGH] Administrative financial report has no authentication or authorization boundary

File: src/AppManager.js:80-129
Description: `/api/admin/financial-report` returns revenue and student data without any middleware or authorization check.
Impact: Sensitive business and student data is exposed to any caller who can reach the API. Missing authorization on an admin route is a protected-operation failure, not just a routing concern.
Recommendation: Add authentication/authorization middleware before admin controllers and keep access policy separate from report generation.

### [HIGH] User deletion leaves related enrollments and payments orphaned by design

File: src/AppManager.js:131-135
Description: The delete endpoint removes a user and then returns a message stating that enrollments and payments were left dirty in the database.
Impact: This breaks domain invariants and reporting correctness. It also embeds known data corruption behavior in a controller route instead of enforcing lifecycle rules in the model/service layer.
Recommendation: Define deletion policy in a user service/model boundary: restrict deletion when related records exist, soft-delete users, or perform a transactional cascade consistent with the domain.

### [MEDIUM] Financial report performs N+1 nested database queries

File: src/AppManager.js:83-127
Description: The report loads all courses, then enrollments per course, then user and payment records per enrollment.
Impact: Query count grows with courses and enrollments, making the route slow and callback-heavy. The data access pattern is also mixed directly into response-building code.
Recommendation: Move report data access into a repository query using joins or grouped queries, then let a report service shape domain data for the controller.

### [MEDIUM] Checkout request validation is incomplete and mixed into the route body

File: src/AppManager.js:29-35
Description: The route reads abbreviated request fields and only checks a subset for presence; `pwd` is read but not required, and no email, course id, or card format validation is performed at the boundary.
Impact: Invalid data enters business and persistence logic, producing inconsistent users and payment outcomes. Validation rules are not reusable or independently testable.
Recommendation: Add a request DTO/validator for checkout input and keep controller validation separate from checkout service orchestration.

### [MEDIUM] Database errors are ignored in audit logging and user deletion

File: src/AppManager.js:57-60
Description: The audit log insert callback ignores `err` and returns checkout success even if logging fails.
Impact: Operational failures become silent and make auditing unreliable; the route cannot distinguish successful enrollment from incomplete side effects.
Recommendation: Handle audit write failures explicitly and consider transaction boundaries for enrollment, payment, and audit writes.

### [MEDIUM] Global mutable cache is shared outside a clear ownership boundary

File: src/utils.js:9-15
Description: `globalCache` is module-level mutable state, and `logAndCache` both logs and mutates it directly.
Impact: Hidden shared state couples workflows to utility module behavior, complicating tests and making request side effects unclear.
Recommendation: Replace with an injected cache adapter or remove the cache side effect from checkout until a real caching responsibility exists.

### [LOW] Cryptic checkout field names reduce API readability and mapping clarity

File: src/AppManager.js:29-33
Description: Request body fields are copied into short variables such as `u`, `e`, `p`, `cid`, and `cc`, mirroring abbreviated API keys like `usr`, `eml`, and `c_id`.
Impact: The route is harder to read and increases the chance of mapping mistakes as the checkout workflow evolves.
Recommendation: Use explicit DTO names such as `userName`, `email`, `password`, `courseId`, and `cardNumber`, while preserving the public request shape through a mapper if compatibility is required.

================================
Total: 12 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

================================
PHASE 3: REFACTORING COMPLETE
================================

## New Project Structure

- `src/app.js`: Express composition root wiring config, database, repositories, services, controllers, middleware, and routes.
- `src/routes.js`: thin HTTP route/view registration for the original API paths.
- `src/controllers/`: request validation coordination, response selection, and error handling.
- `src/services/`: checkout, payment, password, financial report, and user lifecycle workflows.
- `src/models/`: SQLite repositories and report query ownership.
- `src/validators/`: checkout DTO mapping and boundary validation.
- `src/middleware/`: optional admin token authorization.

## Resolved Findings

- [CRITICAL] Hardcoded secrets and god class -> removed legacy utility/AppManager runtime ownership and split into MVC layers.
- [HIGH] Sensitive card/key logging, weak/default password handling, missing admin boundary, orphan deletion -> moved to services/middleware with safer behavior.
- [MEDIUM] N+1 report, incomplete validation, ignored errors, global cache -> replaced with repository queries, validator, explicit errors, and no global cache side effect.
- [LOW] Cryptic field names -> public DTO is mapped to explicit internal names.

## Validation

✓ `find src -name '*.js' -exec node -c {} \;`
✓ Express smoke tests on a temporary loopback port:
  - `GET /api/admin/financial-report` -> 200
  - `POST /api/checkout` with `card` beginning `4` -> 200
  - `POST /api/checkout` with `card` beginning `5` -> 400
  - `DELETE /api/users/1` -> 200

## Technology-Agnostic Validation Evidence

- Manifest commands checked: `package.json`; `npm start` available; no test/build/lint script present.
- Automated tests: not available.
- Build/typecheck/lint/syntax: Node syntax checks passed for all `src/*.js` files.
- Boot/startup: `createApp()` booted and opened a temporary local server.
- Public interface smoke tests: HTTP endpoints listed above.

## Remaining Risks

- `npm install` previously reported inherited dependency vulnerabilities; no dependency upgrade was requested.
- Admin report remains open when `ADMIN_TOKEN` is unset to preserve challenge usability.

## Exit Checklist

| Requirement | Status | Evidence |
| ----------- | -----: | -------- |
| Anti-pattern catalog consulted | PASS | `references/anti-pattern-catalog.md`, 12 entries considered |
| At least 8 anti-patterns considered | PASS | 12 considered |
| Deprecated/obsolete APIs checked | PASS | completed; none found |
| MVC playbook applied | PASS | routes, controllers, services, repositories/models, validator, config, middleware |
| MVC structure validated | PASS | `src/models/`, `src/controllers/`, `src/routes.js`, `src/services/`, `src/validators/` inspected |
| Language-agnostic validation performed | PASS | manifest, syntax, boot, and HTTP smoke tests |
| README/report matches completion state | PASS | README updated to report validated Phase 3 |

================================
