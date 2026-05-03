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

The MVP path is implemented: backend APIs, curated GeoJSON features, local source notes, deterministic low-RAM retrieval, safety refusal behavior, responsive React/MapLibre frontend, station context, and evaluation scripts.

## Recommended Local Models

Start small while building the data and retrieval pipeline:

- Chat model: `llama3.2:3b`
- Embedding model: `nomic-embed-text`

These defaults are tuned for an M2 Pro with 16GB RAM. The balanced demo target can later move to a stronger local or cloud instruct model if latency and cost are acceptable.

## Local Setup

Fast path from a fresh clone:

```bash
git pull
./scripts/bootstrap.sh
./scripts/dev.sh
```

Then open `http://127.0.0.1:5173`.

Use the same flow on the Mac mini after pulling the latest branch. The checked-in source data and local lexical index builder mean the app can start without Ollama; Ollama or cloud chat can be enabled later through `.env`.

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

By default, `GHOST_RAILS_ENABLE_LLM_ANSWERS=false`. In that mode, answers are deterministic and assembled from retrieved local source snippets, which is useful on a 16GB Mac. To enable configured model generation, set:

```env
GHOST_RAILS_ENABLE_LLM_ANSWERS=true
```

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

Run the deterministic RAG evaluation:

```bash
cd backend
source .venv/bin/activate
python scripts/evaluate.py
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

## Developer Computer to Mac Mini Workflow

On the development computer:

```bash
git status
git push
```

On the Mac mini:

```bash
git pull
./scripts/bootstrap.sh
./scripts/dev.sh
```

If dependencies are already installed, `./scripts/dev.sh` is enough.

## Demo Flow

1. Start the backend and frontend with `./scripts/dev.sh`.
2. Open `http://127.0.0.1:5173`.
3. Search for `City Hall`.
4. Select City Hall Station on the map.
5. Ask `Why did this station close?`.
6. Confirm that the answer includes source snippets.
7. Ask `How do I get inside?`.
8. Confirm that the assistant refuses restricted-access guidance.

## Architecture

```text
Browser
  React + MapLibre
  Feature panel
  Chat panel
    |
FastAPI backend
  Feature/search/station APIs
  Safety policy
  RAG answer service
    |
Local data
  data/features/features.geojson
  data/processed/current_stations.json
  data/sources/*.md
  data/chroma/lexical_index.json
```

## Safety Policy

The assistant must refuse requests for entering tunnels, finding access points, bypassing locks or alarms, avoiding detection, or exploring non-public transit infrastructure. It can provide historical explanations, museum context, official-tour context, public map context, and legally viewable remnants when the local corpus supports those claims.

## Data and Attribution

The checked-in source corpus is made from original local project notes, not copied articles. Feature and station data are curated starter data for a portfolio MVP and should be verified before being presented as comprehensive. If OSM, MTA, archival, or third-party source imports are added later, keep their license and attribution records in the source manifest.

## Known Limitations

- The starter dataset is curated and incomplete.
- The default answer path is deterministic retrieval, not a full local LLM synthesis.
- The current station dataset is a small contextual subset, not full GTFS.
- Map tiles load from OpenStreetMap, so map rendering needs network access unless offline tiles are added.
- Historical claims should be expanded only with additional cited sources.
