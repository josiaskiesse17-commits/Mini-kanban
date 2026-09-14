# Mini Kanban Frontend

React + TypeScript + Vite frontend for the Mini Kanban application.

## Commands

```text
npm install
npm run dev
npm run build
```

The frontend expects the API at `http://127.0.0.1:8000` by default. Set `VITE_API_URL` to use another API URL.

## Structure

- `src/api.ts`: typed REST client, bearer-token storage, and API errors
- `src/App.tsx`: authentication, board dashboard, Kanban board, and card workflows
- `src/App.css`: application styling

The frontend follows the API contract in the repository root at `openapi.yaml`.
