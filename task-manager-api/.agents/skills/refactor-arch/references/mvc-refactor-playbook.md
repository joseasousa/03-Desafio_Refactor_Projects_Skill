# MVC Refactor Playbook

Use this playbook after the audit gate is approved.

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

## Common Transformations

- Fat route -> route/view delegates to controller; controller validates and orchestrates; model/repository handles persistence.
- God model -> split per domain entity or aggregate; move use-case orchestration into controller/service; keep data rules in model.
- SQL in controller/view -> repository/model method with parameterized queries.
- Response formatting in model -> serializer/view/DTO mapping.
- Global mutable state -> dependency injected state, request-scoped context, or framework-managed container.
- Duplicated validation -> shared boundary validator or model invariant, depending on where the rule belongs.
- Middleware with domain branching -> controller/use-case logic; keep middleware for auth, logging, CORS, parsing, error normalization.

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
