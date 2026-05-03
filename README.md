# Ghost Rails NYC

Ghost Rails NYC is a local-first AI map and RAG assistant for exploring New York City subway history, abandoned stations, unused tunnels, former elevated lines, disused rail corridors, and historical track provisions.

The project is designed to run on local services:

- FastAPI backend on `http://localhost:8000`
- React/Vite frontend on `http://localhost:5173`
- Ollama on `http://localhost:11434`
- Chroma vector store in `data/chroma`
- Local source documents in `data/sources`
- Local map feature data in `data/features`

## Current Status

Phase 0 is underway. The repository now has the initial folder structure, environment template, and project steering guidance. Backend, frontend, ingestion, map, and RAG implementation will be added in later phases.

## Recommended Local Models

Start small while building the data and retrieval pipeline:

- Chat model: `llama3.2:3b`
- Embedding model: `nomic-embed-text`

These defaults are tuned for an M2 Pro with 16GB RAM. The balanced demo target can later move to a stronger local or cloud instruct model if latency and cost are acceptable.

## Local Setup

Install Ollama:

```bash
brew install ollama
ollama serve
```

In another terminal, pull the starting models:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2:3b
```

Create a local environment file:

```bash
cp .env.example .env
```

Install backend dependencies:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Start the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Check health:

```bash
curl http://127.0.0.1:8000/api/health
```

## Repository Layout

```text
backend/
  app/
    api/
    geo/
    models/
    rag/
    safety/
  scripts/
  tests/
frontend/
  src/
    api/
    components/
    styles/
data/
  raw/
    historical_sources/
    mta/
    osm/
  processed/
  sources/
  features/
  chroma/
  eval/
```

## Development Principles

See [AGENTS.md](AGENTS.md) for coding and architecture guidance. In short: keep the code clean and simple, preserve the local-first design, keep safety behavior explicit, and avoid unsupported generated claims.

## Model Configuration

Models are configured by role so they can be swapped independently:

- `chat`: generates answers.
- `embedding`: embeds source chunks and search queries.

The default profile keeps both roles local through Ollama:

```env
GHOST_RAILS_MODEL_PROFILE=local_m2_16gb
GHOST_RAILS_CHAT_PROVIDER=ollama
GHOST_RAILS_CHAT_MODEL=llama3.2:3b
GHOST_RAILS_EMBEDDING_PROVIDER=ollama
GHOST_RAILS_EMBEDDING_MODEL=nomic-embed-text
```

For a cheap cloud-answering profile, keep retrieval and embeddings local while sending only the assembled RAG prompt to a cloud chat model:

```env
GHOST_RAILS_CHAT_PROVIDER=groq
GHOST_RAILS_CHAT_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=your-api-key
GHOST_RAILS_EMBEDDING_PROVIDER=ollama
GHOST_RAILS_EMBEDDING_MODEL=nomic-embed-text
```

Changing the chat model does not require rebuilding the vector index. Changing the embedding model does require rebuilding the index, because embedding dimensions and similarity behavior can change.

## Test Commands

Backend tests:

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

Build the local retrieval index:

```bash
cd backend
source .venv/bin/activate
python scripts/build_index.py --query "Why did City Hall Station close?"
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

Start the frontend:

```bash
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`.
