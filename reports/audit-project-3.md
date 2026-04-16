================================
PHASE 1: PROJECT ANALYSIS
================================
Language: Python 3.14.4 detected locally
Framework: Flask 3.0.0 with Flask-SQLAlchemy 3.1.1 and Flask-CORS 4.0.0
Dependencies: flask, flask-sqlalchemy, flask-cors, marshmallow, requests, python-dotenv
Domain: Task Manager API for users, tasks, categories, reports, login, and notifications
Architecture: Blueprint-based Flask API with partial separation into routes/, models/, services/, and utils/. The current boundaries are leaky: route handlers contain validation, business rules, persistence, serialization, report calculation, and response formatting.
Source files: 17 files analyzed, including 15 Python source files and project metadata
DB tables: users, tasks, categories
Entrypoints: app.py Flask app; blueprints in routes/task_routes.py, routes/user_routes.py, routes/report_routes.py; seed.py data seeding command
Validation: Available manual commands: pip install -r requirements.txt, python seed.py, python app.py. No automated test suite detected.
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack: Python + Flask + Flask-SQLAlchemy
Files: 17 analyzed | ~1,158 Python LOC

## Summary

CRITICAL: 3 | HIGH: 4 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] Hardcoded application secret in Flask configuration

File: app.py:13
Description: The Flask `SECRET_KEY` is hardcoded as a literal value in source control.
Impact: This exposes session/signing material and prevents per-environment rotation. It is a direct security failure and couples runtime configuration to application code.
Recommendation: Load the secret from environment/configuration at startup, fail fast when it is missing outside development, and keep configuration in an application factory or config object.

### [CRITICAL] Hardcoded SMTP credentials in notification service

File: services/notification_service.py:7-10
Description: SMTP host, account, and password are embedded directly in the service constructor.
Impact: Credentials can leak through source control and the notification service is tightly coupled to a concrete email provider, making it unsafe and hard to test.
Recommendation: Inject email settings and the SMTP client through configuration/composition, move secrets to environment variables, and provide a test double for unit tests.

### [CRITICAL] User serialization exposes password hashes through API responses

File: models/user.py:16-25
Description: `User.to_dict()` includes the `password` field.
Impact: Every route that serializes a user can expose password hashes, including user detail, create/update responses, and login responses. This collapses the model/API boundary and leaks sensitive data.
Recommendation: Remove credentials from public serializers. Use explicit response serializers/schemas for public user data and keep credential fields internal.

### [HIGH] Weak password hashing and fake token generation in authentication flow

File: models/user.py:27-32
Description: Passwords are hashed with unsalted MD5, and authentication depends on comparing MD5 digests directly.
Impact: MD5 is inappropriate for password storage and makes credential compromise much easier if hashes leak. Combined with the fake token response in routes/user_routes.py:207-210, the auth boundary is not production-safe.
Recommendation: Use a password hashing function such as Werkzeug/PBKDF2, bcrypt, or Argon2, and move authentication/token generation into an auth service with explicit tests.

### [HIGH] Task routes are fat controllers combining validation, business rules, persistence, and presentation

File: routes/task_routes.py:85-223
Description: `create_task()` and `update_task()` parse request JSON, validate domain rules, query related models, mutate SQLAlchemy objects, parse dates, serialize responses, log side effects, and manage transactions.
Impact: The route layer is difficult to test without Flask and a database, and changes to task rules require editing HTTP handlers. This violates MVC/SOLID separation and increases regression risk.
Recommendation: Move task validation and mutation rules into a task service or controller layer, keep persistence in model/repository helpers, and let routes only translate HTTP requests/responses.

### [HIGH] Report route contains reporting/business aggregation logic and persistence access directly in the view layer

File: routes/report_routes.py:12-101
Description: `summary_report()` performs many counts, overdue calculations, recent activity rules, per-user productivity aggregation, and response shaping inline.
Impact: Reporting rules cannot be reused or unit tested cleanly and the HTTP layer owns domain calculations. The repeated queries also make performance behavior hard to reason about.
Recommendation: Extract report calculation into a report service/controller, centralize overdue and completion-rate rules, and expose a thin route that only calls the service and returns JSON.

### [HIGH] Protected mutations lack authentication and authorization boundaries

File: routes/user_routes.py:92-151
Description: User update/delete endpoints allow changing roles, active status, passwords, and deleting users without any authentication or authorization check.
Impact: Administrative behavior is publicly reachable if the API is exposed. This is a security and architecture boundary failure because authorization is not modeled at the controller/service boundary.
Recommendation: Add authentication middleware and explicit authorization checks around user, task, and category mutations. Keep permission decisions in a policy/service layer rather than duplicating them in routes.

### [MEDIUM] Repeated N+1 query patterns in list and report endpoints

File: routes/task_routes.py:14-59
Description: The task list loads all tasks, then queries `User` and `Category` separately inside the loop for each task.
Impact: The endpoint performs extra queries per row and will degrade as task volume grows. Data-access strategy is hidden inside presentation code.
Recommendation: Use SQLAlchemy relationships/eager loading or repository queries that fetch required related data in one planned query, then serialize from loaded objects.

### [MEDIUM] User and category list endpoints trigger per-row relationship/count queries

File: routes/user_routes.py:10-25
Description: `get_users()` calls `len(u.tasks)` for each user, causing relationship loading per row.
Impact: Query volume grows with user count and the route owns aggregation behavior that belongs in a query/repository layer.
Recommendation: Use aggregate queries or eager loading in a user repository/service and return DTOs to the route.

### [MEDIUM] Domain rules are duplicated instead of centralized

File: routes/task_routes.py:30-39
Description: Overdue calculation is implemented inline in the task list route and repeated elsewhere, including routes/task_routes.py:71-80, routes/task_routes.py:281-287, routes/user_routes.py:171-180, and routes/report_routes.py:132-135.
Impact: Rule changes require synchronized edits across multiple handlers, increasing the chance of inconsistent API behavior.
Recommendation: Centralize overdue logic on the Task domain model or a task policy/service and reuse it from serializers and reports.

### [MEDIUM] Public input validation is inconsistent and partially unused

File: utils/helpers.py:57-108
Description: `process_task_data()` centralizes task validation, but task routes reimplement similar validation inline instead of using it.
Impact: Validation rules drift between helper code and routes. Some inputs are also cast without error handling, such as `int(priority)` in routes/task_routes.py:260-264.
Recommendation: Adopt one validation path, preferably Marshmallow schemas already listed in dependencies, and use it consistently at route boundaries.

### [LOW] Unused imports and helpers obscure ownership

File: routes/report_routes.py:7-8
Description: `format_date`, `calculate_percentage`, and `json` are imported but unused.
Impact: Unused imports make module responsibilities less clear and suggest unfinished refactors.
Recommendation: Remove unused imports during the MVC refactor and keep helper modules focused on functions that are actually shared.

### [LOW] Magic domain values are repeated across models, routes, and helpers

File: routes/task_routes.py:110-114
Description: Status values, priority ranges, date formats, role values, and defaults are repeated as literals across route handlers and helpers.
Impact: Repeated literals make behavior harder to audit and change safely, even when each instance is locally simple.
Recommendation: Move domain constants to a single module or domain model and have validators/services reference that source.

================================
Total: 13 findings
================================
