# Mini Kanban Board — Development Backlog

## Goal

Build a complete but intentionally small full-stack Kanban application using:

* React + TypeScript + Vite
* FastAPI
* SQLAlchemy
* SQLite
* Bearer-token authentication
* OpenAPI
* Automated backend tests

Every task should be completable in one focused coding session by an AI coding agent.

The agent should not implement features outside `_docs/spec.md`.

---

# Phase 1 — Project Foundation

## TASK-001 — Initialize the repository

Create the project structure:

```text
backend/
frontend/
docs/
AGENTS.md
openapi.yaml
_docs/spec.md
_docs/tasks.md
Makefile
```

Initialize the React + TypeScript frontend and FastAPI backend.

### Done when

* Both applications exist.
* Both can start successfully.
* Dependencies are configured.
* The repository structure matches `_docs/spec.md`.

---

## TASK-002 — Configure AGENTS.md and Makefile

Create project-specific instructions for coding agents and useful Makefile commands.

The instructions should cover:

* Architecture
* API-first development
* Testing
* Database conventions
* Scope restrictions
* Development commands

The Makefile should provide convenient commands for:

```text
make install
make dev
make backend
make frontend
make test
make build
make seed
```

### Done when

A new agent can understand how to work on the repository and common development commands work from the project root.

---

# Phase 2 — API Contract

## TASK-003 — Define the complete OpenAPI contract

Create `openapi.yaml` describing the MVP API.

Include:

### Authentication

* Register
* Login
* Logout

### Boards

* List
* Create
* Get
* Update
* Delete

### Columns

* Create
* Update
* Delete
* Reorder

### Cards

* Create
* Get
* Update
* Delete
* Move
* Reorder

Define:

* Request schemas
* Response schemas
* Authentication requirements
* Validation errors
* Not-found errors
* Authorization errors

### Done when

The entire MVP API is defined in one valid OpenAPI document.

---

# Phase 3 — Backend Foundation

## TASK-004 — Build the FastAPI and database foundation

Configure:

* FastAPI application
* SQLAlchemy
* SQLite
* Database sessions
* Application configuration
* Basic health endpoint

Use a clean backend structure separating routers, models, schemas, authentication, and persistence.

### Done when

The backend starts successfully and can connect to a fresh SQLite database.

---

## TASK-005 — Implement the database models

Create the SQLAlchemy models for:

```text
User
 └── Board
      └── Column
           └── Card
```

Include:

* IDs
* Relationships
* Timestamps where useful
* Column ordering
* Card ordering
* Card priority
* Card due date

### Done when

The database schema supports everything required by the MVP.

---

# Phase 4 — Authentication

## TASK-006 — Implement authentication

Implement:

* Password hashing
* Password verification
* Bearer token creation
* Bearer token validation
* Current-user dependency

### Done when

The backend can securely authenticate a user and protect an endpoint.

---

## TASK-007 — Implement registration, login, and logout

Implement the authentication endpoints defined in `openapi.yaml`.

Handle:

* New account creation
* Duplicate accounts
* Invalid credentials
* Authentication responses

### Done when

A user can register and log in and receive a valid bearer token.

---

## TASK-008 — Test authentication

Add backend tests covering:

* Registration
* Duplicate registration
* Password hashing
* Login
* Invalid credentials
* Missing token
* Invalid token

Use an isolated test database.

### Done when

All authentication tests pass.

---

# Phase 5 — Backend Kanban API

## TASK-009 — Implement board and column APIs

Implement authenticated CRUD operations for:

### Boards

* Create
* List
* Get
* Rename
* Delete

### Columns

* Create
* Rename
* Delete
* Reorder

New boards must automatically receive:

```text
To Do
In Progress
Done
```

Enforce board ownership.

### Done when

A user can completely manage their own boards and columns through the API.

---

## TASK-010 — Implement card APIs

Implement:

* Create
* Get
* Update
* Delete
* Move
* Reorder

Cards must support:

* Title
* Description
* Priority
* Due date
* Column
* Position

Enforce ownership through the board hierarchy.

### Done when

The entire card lifecycle works through the API.

---

## TASK-011 — Test the Kanban API

Add tests for:

* Board CRUD
* Column CRUD
* Column ordering
* Card CRUD
* Card movement
* Card ordering
* Invalid relationships
* Ownership restrictions

### Done when

The important backend behavior is covered and all tests pass.

---

## TASK-012 — Add seed data

Create a simple deterministic development seed containing:

* A development user
* At least one board
* Default columns
* Several cards
* Different priorities
* Different due dates

### Done when

A fresh development database can be seeded and immediately displayed by the frontend.

---

# Phase 6 — Frontend Foundation

## TASK-013 — Build the frontend API layer

Create:

* API client
* Authentication header handling
* API error handling
* TypeScript types for API resources

Types should cover:

```text
User
Board
Column
Card
Priority
```

### Done when

Frontend features can communicate with FastAPI through one consistent API layer.

---

## TASK-014 — Build authentication UI

Create:

* Registration page
* Login page
* Logout
* Authentication state
* Protected application routes

### Done when

A user can register, log in, access the application, and log out.

---

# Phase 7 — Board UI

## TASK-015 — Build the board dashboard

Create the authenticated user's board list.

Support:

* Loading state
* Empty state
* Create board
* Rename board
* Delete board

### Done when

Users can completely manage their boards from the frontend.

---

## TASK-016 — Build the Kanban board UI

Create the main board view displaying:

* Board name
* Columns
* Cards
* Column ordering

The layout should be responsive.

### Done when

A seeded board can be opened and visually represented as a Kanban board.

---

## TASK-017 — Implement column management UI

Allow users to:

* Create columns
* Rename columns
* Delete columns
* Reorder columns

Respect the backend's rules for deleting columns containing cards.

### Done when

Column customization works through the UI and persists through the API.

---

# Phase 8 — Card UI

## TASK-018 — Implement card creation and editing

Create a card form supporting:

* Title
* Description
* Priority
* Due date

Allow users to:

* Create cards
* Edit cards

### Done when

Cards can be created and edited from the Kanban interface.

---

## TASK-019 — Implement card deletion

Add card deletion with a confirmation step.

### Done when

Users can safely delete cards and the UI stays synchronized with the backend.

---

## TASK-020 — Implement card drag-and-drop

Add drag-and-drop functionality allowing cards to:

* Move between columns
* Reorder within a column

Persist changes through the backend.

### Done when

Dragging a card changes its position/column and the change survives a page refresh.

---

# Phase 9 — Search and UX

## TASK-021 — Implement card search and priority filtering

Add simple board-level controls for:

* Searching cards by title
* Filtering by priority

Keep this client-side.

### Done when

Users can quickly find and filter cards without modifying backend data.

---

## TASK-022 — Add application UX states

Improve the application with:

* Loading states
* Empty states
* API error messages
* Authentication error handling
* Destructive-action confirmations

Do not introduce a large UI framework solely for these features.

### Done when

Normal success, loading, empty, and failure scenarios provide understandable feedback.

---

# Phase 10 — Integration and Quality

## TASK-023 — Perform full-stack integration testing

Verify the complete flow:

```text
Register
→ Login
→ Create board
→ Customize columns
→ Create card
→ Edit card
→ Move card
→ Reorder card
→ Search/filter
→ Logout
→ Login again
→ Verify persistence
```

Also verify that one user cannot access another user's resources.

### Done when

The complete MVP works against the real FastAPI + SQLite backend.

---

## TASK-024 — Finalize documentation and release readiness

Verify and update:

* `README` or documentation
* `AGENTS.md`
* `_docs/spec.md`
* `_docs/tasks.md`
* `openapi.yaml`
* `Makefile`

Run:

* Backend tests
* Frontend type checking
* Frontend production build

Perform a final scope audit to remove unnecessary code or features.

### Done when

A new developer or AI coding agent can clone the repository, follow the documentation, run the application, run the tests, and understand the architecture.

---

# Definition of Done

The project is complete when:

* [ ] React + TypeScript frontend works
* [ ] FastAPI backend works
* [ ] SQLite persistence works
* [ ] SQLAlchemy models work
* [ ] Registration works
* [ ] Login works
* [ ] Logout works
* [ ] Passwords are hashed
* [ ] Bearer authentication protects private resources
* [ ] Users can create multiple boards
* [ ] Boards are private
* [ ] Boards have default columns
* [ ] Columns can be customized
* [ ] Columns can be reordered
* [ ] Cards support title, description, priority, and due date
* [ ] Cards can be created, edited, deleted, moved, and reordered
* [ ] Drag-and-drop works
* [ ] Search works
* [ ] Priority filtering works
* [ ] Data persists in SQLite
* [ ] Ownership is enforced
* [ ] Backend tests pass
* [ ] Frontend builds successfully
* [ ] OpenAPI matches the implemented API
* [ ] Seed data works
* [ ] Makefile works
* [ ] Documentation is complete

# Scope Rule

If a proposed feature is not required to satisfy the Definition of Done, **do not implement it unless the specification is explicitly changed first**.

The goal is a **small, complete full-stack Kanban application**, not a Trello clone.
