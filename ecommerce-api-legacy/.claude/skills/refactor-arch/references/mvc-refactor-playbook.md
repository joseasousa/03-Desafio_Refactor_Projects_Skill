# MVC Refactor Playbook

Use this playbook after the audit gate is approved. The playbook is mandatory for Phase 3: consider every transformation pattern below and document which ones were applied, rejected, or not applicable.

## Layer Mapping

Map MVC to the project's stack instead of forcing one folder convention.

- Model: domain entities, data access, repositories, ORM models, persistence adapters, schema-aware data operations, and domain invariants close to data.
- View: presentation layer, HTTP route declarations, templates, serializers, response DTOs, UI components, CLI output formatting, or API representation code.
- Controller: request/use-case orchestration, input validation coordination, transaction boundaries, calls into models/services, and response selection.

Some frameworks use alternative names:

- API-only backends may use routes/handlers as views and controllers/use-cases as orchestration.
- Frontend apps may map views to components/pages, controllers to hooks/actions/state coordinators, and models to domain/data modules.
- Rails/Laravel/Django-style apps may already have MVC; refactor toward their native conventions.
- Clean Architecture or hexagonal projects do not need to be flattened into classic MVC; align MVC responsibilities with existing boundaries.

## Refactoring Strategy

1. Freeze behavior by identifying public routes, commands, tests, schemas, fixtures, and key examples.
2. Move one domain flow at a time, starting with the highest-severity finding.
3. Extract pure business rules before moving persistence or routing.
4. Keep adapters thin and place framework-specific code near boundaries.
5. Introduce a composition root for dependency wiring when concrete dependencies are scattered.
6. Preserve database schemas and migration history unless the user explicitly asks for data model changes.
7. Update imports and registration immediately after each move.
8. Run focused validation after each meaningful slice when feasible.

## Required Completion Gate

- For challenge projects and for stacks without a stronger native convention, validate MVC-equivalent directories for `models/`, `controllers/`, and `routes/` or `views/`.
- Flat files such as `models.py`, `controllers.py`, `routes.py`, or `services.py` may remain only as thin compatibility shims with no primary business logic.
- Reject Phase 3 completion when primary implementation remains in flat files after the report claims MVC completion.
- README and completion reports must match reality: do not say "complete" if the refactor is partial or validation did not run.
- Validation must be stack-aware and language-agnostic: discover tests/build/boot commands from manifests, then prove the original public interfaces still work through HTTP, CLI, job, event, handler, or equivalent smoke checks.

## Common Transformations

### 1. Flat Model File to `models/` Package

Move primary domain entities and repository/data-access code out of a single flat model file into model modules grouped by domain concept.

Before:

```python
# models.py
class User:
    pass

class Order:
    pass
```

After:

```python
# models/user.py
class User:
    pass

# models/order.py
class Order:
    pass
```

### 2. Flat Controller File to `controllers/` Package

Move orchestration functions from a single controller file into controller modules by domain or use case.

Before:

```python
# controllers.py
def create_user(request):
    user = User(name=request.json["name"])
    user.save()
    return {"id": user.id}
```

After:

```python
# controllers/user_controller.py
def create_user(payload, user_service):
    user = user_service.create_user(payload["name"])
    return {"id": user.id}
```

### 3. Inline Route Declarations to `routes/` Package

Keep route files focused on URL/framework binding and delegate work to controllers.

Before:

```python
# app.py
@app.post("/users")
def create_user():
    user = User(name=request.json["name"])
    user.save()
    return jsonify({"id": user.id})
```

After:

```python
# routes/user_routes.py
@blueprint.post("/users")
def create_user_route():
    return jsonify(user_controller.create_user(request.get_json()))
```

### 4. Business Logic to `services/`

Extract reusable domain workflows from routes/controllers into services when the behavior spans multiple models or external adapters.

Before:

```python
def checkout_route():
    total = sum(item.price for item in cart.items)
    if user.is_vip:
        total *= 0.9
    order = Order(total=total)
    order.save()
    return jsonify({"total": total})
```

After:

```python
class CheckoutService:
    def checkout(self, user, cart):
        total = self.pricing.total_for(user, cart)
        return self.orders.create(total=total)
```

### 5. SQL in Route/Controller to Repository or Model Method

Move raw queries behind model/repository methods and parameterize inputs.

Before:

```python
@app.get("/users/<email>")
def get_user(email):
    row = db.execute(f"SELECT * FROM users WHERE email = '{email}'").fetchone()
    return jsonify(dict(row))
```

After:

```python
class UserRepository:
    def find_by_email(self, email):
        return db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
```

### 6. Boundary Validation to Validator or Schema

Centralize request/command validation at the boundary and pass validated data to controllers/services.

Before:

```python
def create_product():
    data = request.json
    product = Product(name=data["name"], price=data["price"])
    product.save()
```

After:

```python
def create_product_route():
    data = product_validator.validate_create(request.get_json())
    return product_controller.create_product(data)
```

### 7. Legacy Imports to New Package Imports

Update imports as files move so callers depend on the new package structure instead of stale flat modules.

Before:

```python
from models import User
from controllers import create_user
```

After:

```python
from models.user import User
from controllers.user_controller import create_user
```

### 8. Compatibility Shim or Full Import Migration

If external callers still import old flat files, keep only documented shims or migrate all callers to the new packages.

Before:

```python
# controllers.py
def create_user(payload):
    # primary implementation still lives here
    ...
```

After:

```python
# controllers.py
"""Compatibility shim; primary implementation lives in controllers/user_controller.py."""
from controllers.user_controller import create_user
```

### 9. Response Formatting Out of Model

Keep models focused on domain/data behavior and move HTTP/API formatting to serializers, views, or route boundaries.

Before:

```python
class User:
    def to_http_response(self):
        return {"id": self.id, "name": self.name}, 200
```

After:

```python
def serialize_user(user):
    return {"id": user.id, "name": user.name}
```

### 10. Global Mutable State to Injected Dependency

Replace shared mutable module state with explicit dependencies or framework-managed request/application context.

Before:

```python
current_cart = {}

def add_item(user_id, item):
    current_cart.setdefault(user_id, []).append(item)
```

After:

```python
class CartService:
    def __init__(self, cart_repository):
        self.cart_repository = cart_repository

    def add_item(self, user_id, item):
        self.cart_repository.add_item(user_id, item)
```

### 11. Hardcoded Config to Config Module

Move secrets, debug flags, database paths, ports, tokens, and provider settings into a config module/object loaded from environment.

Before:

```python
app.config["SECRET_KEY"] = "dev-secret"
app.run(debug=True)
```

After:

```python
app.config.from_object(Config.from_env())
app.run(debug=app.config["DEBUG"])
```

### 12. Scattered Error Handling to Boundary Error Adapter

Normalize expected errors in routes/controllers and avoid leaking internals in public responses.

Before:

```javascript
app.post("/checkout", async (req, res) => {
  try {
    res.json(await checkout(req.body));
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});
```

After:

```javascript
app.post("/checkout", checkoutController.create);
app.use(errorMiddleware);
```

## Validation Strategy

Use the project's own quality gates first.

- Python: `pytest`, `python -m pytest`, framework boot/import checks, Flask/FastAPI/Django test clients.
- JavaScript/TypeScript: `npm test`, `npm run test`, `npm run build`, `npm run typecheck`, framework dev/build checks.
- Java/Kotlin: `mvn test`, `gradle test`, Spring context checks.
- Ruby: `bundle exec rspec`, `rails test`, route checks.
- PHP: `composer test`, `phpunit`, Laravel/PHPStan checks.
- .NET: `dotnet test`, `dotnet build`.
- Go: `go test ./...`.
- Rust: `cargo test`, `cargo check`.

If no tests exist, create minimal smoke validation using the natural interface: boot the app, call representative endpoints, run CLI commands, or import the main module.

## Safety Rules

- Do not change public behavior unless the finding is a confirmed bug or security issue and the user accepted that correction.
- Do not introduce a new framework, ORM, router, or dependency injection container unless necessary.
- Avoid broad rewrites when targeted extraction solves the architectural issue.
- Keep commits or edits logically grouped when the environment supports it.
- Re-run a focused scan for the original findings before declaring them resolved.
