# Mini Kanban — run from repository root.
# GNU Make. On Windows, Git Bash `make` is expected.

.PHONY: install backend frontend dev test test-backend build seed clean

ifeq ($(OS),Windows_NT)
VENV_PY := .venv/Scripts/python.exe
ROOT_PY := backend/.venv/Scripts/python.exe
else
VENV_PY := .venv/bin/python
ROOT_PY := backend/.venv/bin/python
endif

install:
	python -m venv backend/.venv
	$(ROOT_PY) -m pip install -r backend/requirements.txt
	cd frontend && npm install

backend:
	cd backend && $(VENV_PY) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev

dev:
	$(MAKE) -j2 backend frontend

test test-backend:
	cd backend && $(VENV_PY) -m pytest

build:
	cd frontend && npm run build

seed:
	cd backend && $(ROOT_PY) -m app.seed

clean:
	rm -rf frontend/dist backend/.pytest_cache
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
