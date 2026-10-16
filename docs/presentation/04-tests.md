# Tests

Backend tests use SQLite in memory. Each test creates and drops tables in a fixture. They never talk to the Compose Postgres.

## Covered behavior

- Health and readiness, including readiness when the session cannot execute SQL
- Create, list, get, update, delete
- Stats on both routes
- Validation, 404, and list order
- Metric names on `/metrics`
- Alembic upgrade to `0001_create_tasks` and downgrade

Frontend tests cover status transitions, filtering, and time labels. `npm run build` produces the Nginx assets.

The pipeline runs pytest before it builds images. A failing test does not get a new tag in GHCR.
