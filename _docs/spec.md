# Mini Kanban Board — Specification

## 1. Project Overview

A small but fully functional full-stack Kanban board application.

The application allows authenticated users to create and manage multiple private Kanban boards, organize work into columns, and manage task cards.

The project should demonstrate solid full-stack engineering practices without introducing unnecessary features or complexity.

### Core principles

- Fully functional frontend + backend
- Clean and understandable architecture
- API-first development using an OpenAPI contract
- Secure authentication
- Persistent local database
- Automated backend tests
- Responsive frontend
- Small enough for an AI coding agent to implement and maintain efficiently
- Avoid unnecessary features that increase implementation complexity or token usage

---

# 2. Technology Stack

## Frontend

- React
- TypeScript
- Vite
- CSS
- REST API communication with the backend

Vite is used as the frontend build and development tool.

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest

## Authentication

- Password hashing
- Bearer token authentication
- Protected API endpoints where appropriate

---

# 3. Repository Structure

```text
/
├── backend/
│   ├── ...
│   └── tests/
│
├── frontend/
│   ├── ...
│   └── ...
│
├── docs/
│   └── ...
│
├── AGENTS.md
├── openapi.yaml
├── _docs/
│   ├── spec.md
│   └── tasks.md
└── Makefile
```

### Responsibilities

### `/backend`

Contains the FastAPI application, database layer, authentication, API routers, models, and backend tests.

### `/frontend`

Contains the React + TypeScript application.

### `/docs`

Contains supporting project documentation.

### `AGENTS.md`

Contains instructions and conventions for AI coding agents working on the repository.

### `openapi.yaml`

The API contract shared between the frontend and backend.

The backend must implement the API defined by this specification.

### `_docs/spec.md`

Product and functional specification for the project.

### `Makefile`

Provides convenient commands for installing, running, testing, and developing the project.

---

# 4. Authentication

Users must be able to:

- Register
- Log in
- Log out

Passwords must never be stored in plaintext.

Passwords must be securely hashed before being stored.

Authentication uses bearer tokens.

Protected resources must verify the authenticated user before allowing access.

A user must only be able to access their own boards and related resources.

---

# 5. Users

A user has at minimum:

- ID
- Username or email
- Hashed password
- Creation timestamp

The exact representation should follow the API contract.

---

# 6. Boards

Users can create and manage **multiple boards**.

Each board belongs to exactly one user.

Boards are **private**.

Users cannot access another user's boards.

Users can:

- Create a board
- View their boards
- View a specific board
- Rename a board
- Delete a board

A newly created board should contain sensible default columns.

Recommended default columns:

```text
To Do
In Progress
Done
```

---

# 7. Columns

Columns belong to a board.

Users can customize the columns of their boards.

Users can:

- Create a column
- Rename a column
- Delete a column
- Reorder columns

The application should prevent destructive operations from leaving cards in an invalid state.

When deleting a column containing cards, the API should require an explicit strategy, such as moving the cards to another existing column, rather than silently losing data.

---

# 8. Cards

Cards represent tasks.

Each card contains:

- ID
- Title
- Description
- Priority
- Due date
- Column
- Position/order
- Creation timestamp
- Updated timestamp

Recommended priority levels:

```text
low
medium
high
```

Users can:

- Create cards
- View cards
- Edit cards
- Delete cards
- Move cards between columns
- Reorder cards within a column

Cards should support drag-and-drop in the frontend.

The backend remains responsible for persisting the resulting column and ordering.

---

# 9. Card Movement

The primary interaction for moving cards is **drag and drop**.

Users should be able to:

- Move a card to another column
- Reorder cards within the same column
- Move a card while preserving its position

The frontend should send the resulting ordering to the backend.

A simple fallback control may also allow changing a card's column without drag-and-drop.

---

# 10. Search and Filtering

Keep this deliberately simple.

The application may provide basic:

- Card title search
- Priority filtering

Do not implement an advanced search engine.

Search/filtering should remain client-side where practical unless the dataset or API design makes backend filtering more appropriate.

---

# 11. Features Explicitly Out of Scope

The first version should **not** implement:

- Multi-user collaboration
- Board sharing
- Public boards
- Real-time synchronization
- WebSockets
- Comments
- Attachments
- File uploads
- Labels/tags
- Notifications
- Email notifications
- Activity feeds
- Chat
- Advanced permissions
- Team/workspace management
- Calendar views
- Recurring tasks
- Subtasks
- Time tracking
- Analytics dashboards
- Third-party integrations

These features may be considered in a future version but must not be added to the MVP.

---

# 12. Frontend Requirements

The React application should provide at minimum:

## Authentication

- Registration page
- Login page
- Logout functionality
- Authentication state handling
- Protected application routes

## Board management

- Board list
- Create board
- Rename board
- Delete board
- Open board

## Kanban interface

- Display columns horizontally
- Display cards inside columns
- Create cards
- Edit cards
- Delete cards
- Drag and drop cards
- Reorder cards
- Create/rename/delete/reorder columns

## Card UI

Display:

- Title
- Description where appropriate
- Priority
- Due date

## UX

The frontend should:

- Be responsive
- Show loading states
- Show useful error messages
- Handle empty states
- Confirm destructive operations where appropriate
- Avoid unnecessary animations or complex UI systems

---

# 13. Backend Requirements

The backend must be implemented with FastAPI.

It should be organized into clear modules rather than placing the entire application in one file.

Recommended structure:

```text
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── auth/
│   ├── store/
│   └── ...
└── tests/
```

The exact structure can be adjusted if a simpler architecture provides the same separation of concerns.

The backend should separate:

- API routing
- Request/response schemas
- Database models
- Database configuration
- Authentication
- Business logic
- Persistence

---

# 14. Database

Use:

- SQLite
- SQLAlchemy

The database must be persistent during normal application execution.

The main relationships should include:

```text
User
 └── Board
      └── Column
           └── Card
```

Foreign keys and ownership relationships must be enforced appropriately.

---

# 15. Seed Data

The project must include seed data for development.

The seed data should provide enough content for the frontend to immediately demonstrate:

- A user
- At least one board
- Multiple columns
- Multiple cards
- Different priorities
- Different card positions

Seed data should be deterministic and safe to recreate.

---

# 16. API

`openapi.yaml` is the source-of-truth API contract.

The backend must implement the endpoints defined in `openapi.yaml`.

The API should cover at minimum:

### Authentication

- Register
- Login
- Logout

### Boards

- List boards
- Create board
- Get board
- Update board
- Delete board

### Columns

- Create column
- Update column
- Delete column
- Reorder columns

### Cards

- Create card
- Get card
- Update card
- Delete card
- Move card
- Reorder cards

The exact endpoint names, request bodies, response schemas, status codes, and authentication requirements must be defined in `openapi.yaml`.

---

# 17. API Error Handling

The API should return consistent HTTP responses.

At minimum, handle:

- Invalid input
- Authentication failures
- Unauthorized access
- Missing resources
- Duplicate registration data
- Invalid board/column/card relationships
- Database errors where appropriate

Do not expose sensitive internal errors to API clients.

---

# 18. Backend Tests

Use Pytest.

Tests should cover the most important application behavior rather than attempting to test every implementation detail.

At minimum test:

### Authentication

- Registration
- Login
- Invalid credentials
- Password hashing
- Protected endpoint access

### Authorization

- User can access their own board
- User cannot access another user's board
- User cannot modify another user's resources

### Boards

- Create
- Read
- Update
- Delete

### Columns

- Create
- Update
- Delete
- Reordering

### Cards

- Create
- Update
- Delete
- Move
- Reorder

### Validation

- Invalid input
- Missing required fields
- Invalid relationships

Tests should use an isolated test database rather than modifying the development database.

---

# 19. OpenAPI Contract

`openapi.yaml` should be written before or alongside backend implementation.

It should describe:

- API endpoints
- HTTP methods
- Parameters
- Request bodies
- Response schemas
- Authentication requirements
- Error responses
- Data models

The frontend should consume the API according to this contract.

The backend must not silently diverge from the contract.

---

# 20. AGENTS.md

`AGENTS.md` should contain practical instructions for coding agents.

It should explain:

- Project architecture
- Directory responsibilities
- How to run the frontend
- How to run the backend
- How to run tests
- API-first development rules
- Database conventions
- Authentication rules
- Testing expectations
- Coding conventions
- Scope boundaries
- Rules against introducing unnecessary dependencies/features

Agents should prefer small, focused changes and avoid rewriting unrelated parts of the application.

---

# 21. Makefile

The Makefile should provide simple commands for common operations.

Recommended commands:

```text
make install
make dev
make backend
make frontend
make test
make test-backend
make build
make seed
make clean
```

The exact implementation can be adapted to the development environment.

The Makefile should make common development operations easy without hiding important behavior.

---

# 22. Development Workflow

Recommended implementation order:

```text
1. Define `_docs/spec.md`
2. Define openapi.yaml
3. Define repository structure
4. Configure backend
5. Configure database
6. Implement models
7. Implement authentication
8. Implement board/column/card API
9. Write backend tests
10. Seed database
11. Configure React + TypeScript frontend
12. Implement authentication UI
13. Implement board UI
14. Implement Kanban UI
15. Implement drag-and-drop
16. Connect frontend to API
17. Add error/loading/empty states
18. Test full application
19. Finalize documentation
```

---

# 23. MVP Definition

The MVP is complete when a new user can:

1. Register an account
2. Log in
3. Create multiple boards
4. Open a board
5. See default columns
6. Customize columns
7. Create cards
8. Edit cards
9. Delete cards
10. Drag cards between columns
11. Reorder cards
12. Set card priority
13. Set card due dates
14. Search/filter cards
15. Log out
16. Log back in and find their persisted boards and cards

The application must persist the data in SQLite.

The backend must have automated tests.

The frontend and backend must communicate through the documented OpenAPI-defined API.

---

# 24. Scope Constraint

When deciding whether to add a feature, prefer:

> **Simple + useful + demonstrable + easy to maintain**

over:

> **Feature-rich + complex + impressive**

The goal is a **complete mini Kanban application**, not a clone of Trello.

Any feature that significantly increases backend, frontend, database, authentication, real-time, or AI-agent complexity without being essential to the core Kanban experience should remain outside the MVP.
