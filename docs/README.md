# Mini Kanban

Mini Kanban is a private Kanban application with a React/Vite frontend and a FastAPI/SQLite backend.

## Quick Start

Windows PowerShell:

```powershell
.\make.ps1 install
.\make.ps1 seed
.\make.ps1 dev
```

Unix or Git Bash:

```text
make install
make seed
make dev
```

The API runs at `http://127.0.0.1:8000`; its health check is `/health`.

## Commands

| Command             | Purpose                                   |
| ------------------- | ----------------------------------------- |
| `make install`      | Install backend and frontend dependencies |
| `make dev`          | Start both development servers            |
| `make test-backend` | Run the Pytest suite                      |
| `make build`        | Type-check and build the frontend         |
| `make seed`         | Recreate deterministic development data   |
| `make clean`        | Remove build and test caches              |

On Windows, use the equivalent `./make.ps1 <command>` command in PowerShell.

## Architecture

- `backend/app/database.py`: SQLAlchemy engine and session dependency
- `backend/app/models/`: User, Board, Column, and Card entities
- `backend/app/auth/`: password hashing, bearer tokens, and auth schemas
- `backend/app/routers/`: health, auth, board/column, and card endpoints
- `backend/app/schemas/`: Kanban request and response schemas
- `frontend/src/api.ts`: typed API client and token/error handling
- `frontend/src/App.tsx`: application UI and state
- `openapi.yaml`: source-of-truth API contract

Ownership is enforced through `User -> Board -> Column -> Card`.

## Seed Account

The repeatable seed creates `dev@example.com` with password `dev-password-123`, one board, default columns, and four cards.

## Scope

The MVP excludes collaboration, sharing, real-time updates, comments, attachments, tags, analytics, notifications, and dark mode. See [`spec.md`](../_docs/spec.md) and [`AGENTS.md`](../AGENTS.md) for product and engineering rules.
