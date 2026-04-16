================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
- `src/app.js`: composition root that creates Express, SQLite, repositories, services, controllers, middleware, and route registration.
- `src/database.js`: SQLite connection, promise helpers, schema creation, and seed data.
- `src/routes.js`: thin route/view declarations for the public API paths.
- `src/controllers/`: HTTP request validation coordination, response status selection, and error handling.
- `src/services/`: checkout, payment, password hashing, financial reporting, and user lifecycle workflows.
- `src/models/`: SQLite repositories for users, courses, enrollments, payments, audit logs, and financial report data access.
- `src/validators/`: checkout request DTO mapping and boundary validation.
- `src/middleware/`: optional admin token middleware using `ADMIN_TOKEN` when configured.

## Resolved Findings
- [CRITICAL] Hardcoded production-like credentials and secrets -> removed `src/utils.js`; runtime config now reads non-secret `PORT` and optional `ADMIN_TOKEN` from environment.
- [CRITICAL] God class combines HTTP routing, schema creation, persistence, business workflow, payment, reporting, and response formatting -> removed `src/AppManager.js`; responsibilities are split across routes, controllers, services, repositories, and database bootstrapping.
- [HIGH] Sensitive card data and payment key are logged during checkout -> removed payment/card logging and removed the hardcoded payment key.
- [HIGH] Password handling uses insecure reversible-looking hashing and a weak default password -> checkout validation now requires `pwd`; no default password is assigned.
- [HIGH] Password hashing is custom, deterministic, and unsuitable for credentials -> replaced `badCrypto` with PBKDF2-SHA256 hashing in `PasswordService`.
- [HIGH] Administrative financial report has no authentication or authorization boundary -> added optional `ADMIN_TOKEN` middleware for the admin report route.
- [HIGH] User deletion leaves related enrollments and payments orphaned by design -> user deletion now removes related payments/enrollments inside a transaction before deleting the user.
- [MEDIUM] Financial report performs N+1 nested database queries -> report data now comes from one joined repository query and is shaped in `FinancialReportService`.
- [MEDIUM] Checkout request validation is incomplete and mixed into the route body -> checkout validation moved into `src/validators/checkoutValidator.js`.
- [MEDIUM] Database errors are ignored in audit logging and user deletion -> controllers now catch service errors; audit write failures prevent false checkout success; user deletion rolls back on failure.
- [MEDIUM] Global mutable cache is shared outside a clear ownership boundary -> removed the module-level cache side effect.
- [LOW] Cryptic checkout field names reduce API readability and mapping clarity -> public fields are mapped to explicit internal DTO names.

## Validation
  ✓ `npm install` completed and installed lockfile dependencies.
  ✓ `find src -name '*.js' -exec node -c {} \;` passed.
  ✓ HTTP smoke test passed on a temporary loopback port:
    - `GET /api/admin/financial-report` -> 200 with seeded course report.
    - `POST /api/checkout` with card beginning `4` -> 200 `{"msg":"Sucesso","enrollment_id":2}`.
    - `POST /api/checkout` with card beginning `5` -> 400 `Pagamento recusado`.
    - `DELETE /api/users/1` -> 200 `Usuário deletado.`
  ✓ Focused source scan found no runtime occurrences of `admin_master`, `senha_super`, `pk_live`, `paymentGatewayKey`, `badCrypto`, `globalCache`, `Processando cartão`, `AppManager`, or `SELECT *`.
  ! `npm install` reported 9 dependency vulnerabilities from the existing dependency tree: 2 low, 1 moderate, 6 high.

## Remaining Risks
- The admin route remains open by default to preserve local challenge usability; set `ADMIN_TOKEN` to enforce `x-admin-token` authorization.
- There is still no formal unit/integration test suite in `package.json`; behavior was validated with syntax checks and HTTP smoke tests.
================================
