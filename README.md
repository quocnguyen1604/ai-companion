# AI Companion

A small local-first foundation for a text conversation app. The React client talks to a FastAPI REST API; a conversation service persists messages through SQLAlchemy and asks an injected `AIProvider` for each assistant response. The default provider is deterministic and local, so no model account or API key is needed.

## Requirements

- Python 3.11 or newer and [uv](https://docs.astral.sh/uv/)
- Node.js 20 or newer and npm

## Python virtual environment

Create the virtual environment inside `backend/`. This keeps the Python environment alongside the backend and matches the `.gitignore` entry for `.venv/`:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate it with `source .venv/bin/activate` instead. After activation, run backend commands such as `uvicorn app.main:app --reload` and `pytest` from `backend/`.

Alternatively, use the included `pyproject.toml` and `uv.lock` with `uv sync`; uv creates the same `backend/.venv` environment for you.

## Configuration

Copy `.env.example` to `backend/.env` and `frontend/.env.local` (or use the defaults). `DATABASE_URL` defaults to a SQLite file at `backend/companion.db` when the backend is started from its directory. `CORS_ORIGINS` is a JSON array of allowed browser origins. The frontend uses `VITE_API_URL`, defaulting to `http://localhost:8000/api`.

## Run locally

In one terminal:

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

The API is at `http://localhost:8000`; interactive API docs are at `/docs` and health is at `/health`.

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://127.0.0.1:5173`). The frontend creates a conversation on first use, remembers its UUID in browser storage, and reloads its history on later visits. Each user/assistant turn is persisted to SQLite.

## Tests and build

```powershell
cd backend
uv run pytest
```

```powershell
cd frontend
npm test
npm run build
```

## API

- `POST /api/conversations` creates an empty conversation.
- `GET /api/conversations` lists conversations; `GET /api/conversations/{id}` loads one.
- `GET /api/conversations/{id}/messages` returns chronological history.
- `POST /api/conversations/{id}/messages` accepts `{"content":"..."}` and returns a `user_message` and `assistant_message` pair.

IDs are UUIDs. Roles are `user` and `assistant`. Conversation and message records have UTC timestamps. The frontend keeps one current conversation in browser storage; the list API is ready for a later conversation picker.

## Design notes

`AIProvider` in `backend/app/services/ai/base.py` accepts provider-neutral message values and is independent of HTTP and persistence. `ConversationService` coordinates history, persistence, and the provider; FastAPI injects the default mock provider through `get_ai_provider`. A later local or hosted provider can implement this interface without changing route or database code. No external model integration is included.

SQLite tables are initialized by the FastAPI lifespan on startup. Schema migrations are intentionally omitted for this small starting point; introduce a migration tool when the data model begins evolving beyond local development.
