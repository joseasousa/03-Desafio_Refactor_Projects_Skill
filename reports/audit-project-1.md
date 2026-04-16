================================
PHASE 1: PROJECT ANALYSIS
================================
Language: Python 3.14.4 detected locally
Framework: Flask 3.1.1, flask-cors 5.0.1
Dependencies: Flask, Flask-CORS, sqlite3 stdlib
Domain: E-commerce API with products, users, orders, order items, sales report
Architecture: Thin Flask app wiring routes to a single controllers module; controllers mix HTTP, validation, notifications, and some persistence; models module mixes SQL access, domain rules, serialization, and transactions; database module owns schema creation, seed data, and a global SQLite connection
Source files: 6 files analyzed
DB tables: produtos, usuarios, pedidos, itens_pedido
Entrypoints: Flask routes `/`, `/produtos`, `/produtos/busca`, `/produtos/<id>`, `/usuarios`, `/usuarios/<id>`, `/login`, `/pedidos`, `/pedidos/usuario/<usuario_id>`, `/pedidos/<pedido_id>/status`, `/relatorios/vendas`, `/health`, `/admin/reset-db`, `/admin/query`
Validation: Available boot command: `python app.py`; install command: `pip install -r requirements.txt`; no tests/build/lint config detected
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack: Python + Flask + SQLite
Files: 6 analyzed | ~794 lines of code

## Summary

CRITICAL: 6 | HIGH: 4 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] Arbitrary SQL execution endpoint

File: app.py:59-78
Description: `/admin/query` accepts request JSON, reads `sql`, and executes it directly through `cursor.execute(query)`.
Impact: Any caller can run arbitrary SQL, including reads, deletes, updates, schema changes, or data exfiltration. This is both a security failure and a total collapse of controller/model boundaries.
Recommendation: Remove the endpoint or lock it behind real authentication/authorization and a constrained admin service. Do not execute request-provided SQL; expose explicit repository methods for supported maintenance actions.

### [CRITICAL] Unauthenticated destructive database reset

File: app.py:47-57
Description: `/admin/reset-db` deletes all rows from `itens_pedido`, `pedidos`, `produtos`, and `usuarios` without authentication, authorization, environment gating, or confirmation.
Impact: A public POST can destroy all application data. The route also embeds persistence logic directly in the Flask view.
Recommendation: Remove from runtime routes or restrict to a non-production maintenance command protected by environment checks and authorization. Move database maintenance logic out of `app.py`.

### [CRITICAL] Hardcoded secret key and debug mode enabled

File: app.py:7-8
Description: The Flask secret key is hardcoded and debug mode is enabled in application configuration.
Impact: Hardcoded secrets can be leaked through source control, reused across environments, and compromise signed Flask data. Debug mode can expose sensitive runtime behavior.
Recommendation: Load secrets and debug flags from environment/config, fail closed when missing in production, and keep defaults non-debug.

### [CRITICAL] Health endpoint exposes secret and sensitive runtime details

File: controllers.py:276-290
Description: `/health` returns `db_path`, `debug: True`, and the literal `secret_key`.
Impact: This leaks sensitive configuration to clients and confirms dangerous runtime settings.
Recommendation: Return only minimal health state, such as service/database availability. Never return secrets or internal paths.

### [CRITICAL] SQL injection through string-built queries

File: models.py:47-60
Description: Product create/update SQL is built by concatenating user-controlled `nome`, `descricao`, `categoria`, and numeric fields.
Impact: Malicious input can break query syntax, alter data, or execute unintended SQL depending on driver behavior. Persistence safety depends on every controller validating perfectly, which it does not.
Recommendation: Use parameterized SQL for every query and centralize query construction in repository/model functions.

### [CRITICAL] Plaintext passwords are stored and exposed

File: models.py:72-103
Description: User listing and lookup serialize the `senha` column into API responses. Passwords are also stored as normal text in the user table.
Impact: Anyone with access to user endpoints can retrieve passwords, and database compromise exposes credentials immediately.
Recommendation: Store password hashes only, never return password fields, and move authentication concerns into an auth/service layer.

### [HIGH] Login is vulnerable to SQL injection and plaintext credential comparison

File: models.py:105-120
Description: Login concatenates `email` and `senha` into SQL and compares plaintext password values in the database.
Impact: Authentication can be bypassed or manipulated, and the model owns auth policy directly instead of a dedicated service.
Recommendation: Parameterize the query, look up by email, verify a password hash in an authentication service, and return a safe user DTO.

### [HIGH] Single `models.py` module mixes persistence, domain rules, serialization, and reporting

File: models.py:4-314
Description: The file contains product repositories, user repositories, order creation business rules, stock mutation, order serialization, and sales report calculations.
Impact: This is a god module. Changes to one domain area risk unrelated behavior, and business rules are tightly coupled to SQLite row shape.
Recommendation: Split by domain responsibility, for example product/user/order repositories plus services for order creation and reporting.

### [HIGH] Controllers contain business rules and side effects

File: controllers.py:24-62
Description: `criar_produto` performs required-field checks, price/stock/name constraints, category policy, model call, logging, and response formatting in one handler.
Impact: Validation and domain policy are hard to test outside HTTP and are duplicated or missing in other flows.
Recommendation: Keep controllers focused on request/response orchestration. Move product validation and creation rules into a service or domain function.

### [HIGH] Global mutable database connection without dependency injection

File: database.py:4-11
Description: A module-level `db_connection` is shared globally with `check_same_thread=False`.
Impact: Request handling, tests, and services are coupled to one concrete SQLite connection and path. Cross-request state and transaction behavior become difficult to reason about.
Recommendation: Introduce an app factory/composition root and per-request or injectable database connection/repository dependencies.

### [MEDIUM] Order creation can leave partial state without rollback

File: models.py:133-169
Description: `criar_pedido` validates stock, inserts an order, inserts items, updates stock, and commits once, but has no explicit transaction rollback on errors after partial writes.
Impact: Exceptions during item insert or stock update can leave the connection in an inconsistent transaction state and make recovery unclear.
Recommendation: Wrap order creation in an explicit transaction boundary with rollback on failure, and keep stock/order mutation in an order service.

### [MEDIUM] N+1 query pattern when loading orders and items

File: models.py:171-201
Description: `get_pedidos_usuario` queries orders, then queries items per order, then queries product names per item.
Impact: The number of queries grows with orders and items, degrading performance and complicating persistence behavior.
Recommendation: Use joined queries or batched lookups and map rows into order DTOs in one repository method.

### [MEDIUM] N+1 query pattern when listing all orders

File: models.py:203-233
Description: `get_todos_pedidos` repeats the same per-order and per-item query pattern for the global order list.
Impact: A common list endpoint can become slow as data grows and can pressure SQLite unnecessarily.
Recommendation: Replace nested queries with joins or batched item/product queries.

### [MEDIUM] Inconsistent and incomplete public-boundary validation

File: controllers.py:167-186
Description: `login` calls `request.get_json()` and immediately reads `.get()` without checking whether the body exists or is an object. Similar type assumptions appear in search and order creation.
Impact: Malformed requests can become 500 responses instead of stable 400 responses, complicating clients and tests.
Recommendation: Normalize request parsing and validation in controller helpers or service input schemas.

### [LOW] Magic domain constants are scattered in controllers

File: controllers.py:52
Description: Valid product categories are embedded as a local list in the controller.
Impact: Category policy is not reusable by services, tests, seeds, or future validation paths.
Recommendation: Move category constants to a product domain module or service validator.

### [LOW] Sales discount thresholds are unexplained magic numbers

File: models.py:256-262
Description: Report discount thresholds and percentages are hardcoded inline.
Impact: Business policy is hidden inside persistence/reporting code and is hard to change or test independently.
Recommendation: Extract named constants or a reporting service policy function with focused tests.

================================
Total: 16 findings
================================
