# API

| Method | Path | Role |
| --- | --- | --- |
| GET | `/` | Service name and links |
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness. `SELECT 1`, or 503 |
| GET | `/metrics` | Prometheus text |
| GET, POST | `/api/tasks` | List and create |
| GET, PUT, DELETE | `/api/tasks/{id}` | Read, update, delete |
| GET | `/api/tasks/stats` and `/api/stats` | Counts by status |

## Rules

- Title is required, trimmed, and at most 200 characters.
- Status is `TODO`, `IN_PROGRESS`, or `DONE`.
- Priority is `LOW`, `MEDIUM`, or `HIGH`.
- Unknown ids return 404. Blank titles and bad enums return 422.

Swagger is `/docs` on the API port.
