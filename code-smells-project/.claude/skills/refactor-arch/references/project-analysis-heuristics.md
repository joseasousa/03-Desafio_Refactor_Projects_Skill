# Project Analysis Heuristics

Use these heuristics in Phase 1 to discover facts before making assumptions.

## Stack Detection

- Python: `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `.py` entrypoints.
- Node.js: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `.js/.ts` entrypoints.
- Java/Kotlin: `pom.xml`, `build.gradle`, `settings.gradle`, `src/main`.
- Go: `go.mod`, `main.go`, `cmd/`.
- Rust: `Cargo.toml`, `src/main.rs`, `src/lib.rs`.
- PHP: `composer.json`, `public/index.php`, framework bootstrap files.
- .NET: `.csproj`, `.sln`, `Program.cs`, `appsettings*.json`.

## Framework and Database Signals

- Flask/FastAPI/Django: imports, dependency files, app factories, blueprints/routers, ORM setup.
- Express/Nest/Koa: `express()`, route modules, controllers, middleware, package dependencies.
- Spring/Rails/Laravel/ASP.NET: conventional folders, annotations, route files, config files.
- Databases: SQLite files/imports, SQLAlchemy/ORM config, migrations, Prisma/Sequelize, JDBC, ActiveRecord, Eloquent, Mongo clients.

## Architecture Mapping

Map current responsibilities, not just folder names:

- routes/views: public interface binding and response formatting
- controllers/use cases: orchestration and boundary decisions
- models/repositories: domain data, persistence, invariants
- services: workflows spanning multiple models or external adapters
- config/composition: environment, dependency wiring, app startup
- validators/serializers: boundary validation and API representation

## Validation Discovery

Read manifests before guessing commands. Capture:

- test scripts and test folders
- build/typecheck/lint/syntax commands
- boot/start commands and ports
- sample requests, API docs, `.http` files, fixtures, seed scripts, or CLI examples
- fallback validation when no formal command exists
