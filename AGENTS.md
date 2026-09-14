# Agent instructions — Mini Kanban

Small full-stack Kanban app. Follow `_docs/spec.md`. Do not implement features outside it. Prefer small, focused changes; do not rewrite unrelated code.

## Architecture

| Path             | Responsibility                                           |
| ---------------- | -------------------------------------------------------- |
| `backend/app/`   | FastAPI app: routers, schemas, models, auth, persistence |
| `backend/tests/` | Pytest suite (isolated test DB only)                     |
| `frontend/`      | React + TypeScript + Vite UI                             |
| `docs/`          | Supporting notes                                         |
| `openapi.yaml`   | Source-of-truth API contract                             |
| `_docs/spec.md`  | Product/functional spec                                  |
| `_docs/tasks.md` | Implementation backlog                                   |

Backend must stay modular (routing, schemas, models, DB, auth, business logic, persistence). SQLite + SQLAlchemy. Auth: hashed passwords, bearer tokens, users only access their own boards.

## API-first

1. Update `openapi.yaml` before or with backend changes.
2. Backend implements that contract; do not silently diverge.
3. Frontend consumes the API according to the contract.

## Database

- SQLite file, persistent in normal runs.
- Tests must use a separate isolated DB, never the development DB.
- Ownership: User → Board → Column → Card. Enforce FKs and ownership.
- Seed data must be deterministic and safe to recreate (`make seed`).

## Testing

- Pytest for important behavior: auth, authorization, boards, columns, cards, validation (see `_docs/spec.md` §18).
- Run with `make test` or `make test-backend`.

## Coding conventions

- Keep the MVP small. No extra libraries, UI kits, real-time, or AI features.
- Passwords never stored plaintext.
- Do not leak internal errors to API clients.
- CSS only on the frontend (no extra styling frameworks unless spec adds them).

## Scope

Out of scope unless `_docs/spec.md` says otherwise: sharing, real-time sync, comments, attachments, search, tags, analytics, notifications, dark mode, rich text, AI.

## Commands (repo root)

```text
make install        # backend venv + pip, frontend npm
make backend        # FastAPI on :8000
make frontend       # Vite dev server
make dev            # backend + frontend
make test           # pytest
make test-backend   # pytest
make build          # frontend production build
make seed           # load deterministic seed data
make clean          # caches and frontend dist
```

Windows (this machine has no GNU `make`): `.\make.ps1 install` (same target names). Unix/Git Bash: `make install`.
