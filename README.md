# AI Companion

A local-first, text-based AI companion built with a React and TypeScript frontend and a FastAPI backend. The backend talks to a model served by LM Studio through its OpenAI-compatible Responses API, streams replies to the browser over Server-Sent Events (SSE), and stores conversation data in SQLite.

## Current features

- Chat with a locally served language model through LM Studio's OpenAI-compatible API.
- Persist conversations and messages in a local SQLite database.
- Stream assistant text deltas to the frontend over SSE.
- Compact older conversation context into summaries when the configured token threshold is reached; keep summaries in SQLite and use them in later model requests.
- Let the model retrieve relevant saved memories through a tool call. The current memory store is a local JSON file; retrieval ranks embedded memories by vector similarity and returns the top matches.

Automatic memory saving is **not implemented yet**. The next planned feature is for the model to decide when a useful memory should be saved, while the backend validates and persists it and generates its embedding.

## Architecture

```text
React + TypeScript + Vite
        │ REST request / SSE response
        ▼
FastAPI routes
        ▼
Conversation service ───── SQLite (SQLAlchemy)
        │
        ├── LM Studio provider (OpenAI-compatible Responses API)
        ├── Context summaries stored in SQLite
        └── Memory retrieval tool ── local JSON + embeddings
```

The provider is isolated behind the `AIProvider` interface in `backend/app/services/ai/base.py`. The current runtime provider is selected in `backend/app/services/providers.py`.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Node.js 20 or newer and npm
- LM Studio, with its local server enabled and the model expected by `backend/app/services/ai/lmstudio.py` loaded
- Access to the Hugging Face embedding model used by `backend/app/services/embeddings.py` on first use

The tokenizer used for context counting is loaded from `backend/app/tokenizers/models/gemma-4-26b-a4b-qat`. Keep the tokenizer files in place.

## Configuration

Copy the root `.env.example` to `backend/.env`, then add the settings needed by the current LM Studio and memory features:

```dotenv
LMSTUDIO_API_URL=http://localhost:1234/v1
SUMMARY_TOKEN_THRESHOLD=5000
MEMORY_FILE_PATH=./memory.json
# Set this if Hugging Face requires authentication for model access.
HUGGING_FACE_TOKEN=
```

The example file also contains `DATABASE_URL`, `CORS_ORIGINS`, and `VITE_API_URL`. The default SQLite URL creates `backend/companion.db` when the backend runs from `backend/`. `VITE_API_URL` defaults to `http://localhost:8000/api`.

Create `backend/memory.json` if it does not exist. It is local application data and is intentionally ignored by Git. The memory retrieval code expects a JSON array of memory records; records need `content` and an `embedding` for retrieval. The embedding generation utility can add embeddings to records that do not have them.

Start LM Studio's local server before sending chat requests. Set `LMSTUDIO_API_URL` to its OpenAI-compatible `/v1` base URL, and load the model identifier configured in the LM Studio provider. The application does not require a paid cloud AI account.

## Install and run

### Backend

Create the virtual environment inside `backend/`:

```powershell
cd backend
uv sync
```

The new LM Studio and embedding features import packages that are not yet listed in the project's dependency manifests. Install those into the backend environment as well:

```powershell
uv pip install openai python-dotenv sentence-transformers
```

Then, from `backend/`, run:

```powershell
uv run uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`, and the health endpoint is `http://localhost:8000/health`.

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, normally `http://127.0.0.1:5173`. The frontend creates a conversation on first use, stores its ID in browser local storage, and loads its message history on later visits. While chatting, it reads SSE events and updates the in-progress assistant message as text deltas arrive.

## Context management and memories

Conversation messages, token counts, and generated summaries are stored in SQLite. When the tracked prompt token count reaches `SUMMARY_TOKEN_THRESHOLD`, the conversation service asks the provider to summarize eligible history and uses that summary in later requests.

Memory retrieval is separate from the SQLite conversation history. The model can call the `retrieve_memory` tool; the backend embeds the search query, compares it with saved memory embeddings, and returns the highest-ranked matches. At present, memory records live in the ignored local `memory.json` file. The model cannot automatically save new memories yet.

## Tests and frontend build

Backend tests:

```powershell
cd backend
uv run pytest
```

Frontend tests and production build:

```powershell
cd frontend
npm test
npm run build
```

## API overview

- `POST /api/conversations` creates a conversation.
- `GET /api/conversations` lists conversations.
- `GET /api/conversations/{conversation_id}` loads a conversation.
- `GET /api/conversations/{conversation_id}/messages` loads its message history.
- `POST /api/conversations/{conversation_id}/messages` accepts `{"content":"..."}` and streams SSE events. Text deltas use `response.output_text.delta`; the final `response.completed` event contains the persisted user and assistant messages.

Message and conversation identifiers are UUIDs. Message roles are `user` and `assistant`.

## Data and schema notes

The SQLite database and `memory.json` are local data and are ignored by Git. Back up any local conversations or memories you want to keep. Tables are created at application startup, but `create_all` does not migrate existing tables when columns change. For local development, back up and recreate the database after incompatible schema changes; use a migration tool such as Alembic when the schema needs to evolve while retaining data.

## Next milestone

Implement automatic persistent memory saving: let the model propose a memory through a tool call, validate the proposed content in the backend, persist it, generate and store its embedding, and make it available to later retrieval calls.
