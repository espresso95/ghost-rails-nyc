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

- Chat model: `llama3.1:8b`
- Embedding model: `nomic-embed-text`

The balanced demo target can later move to a stronger local instruct model if latency is acceptable.

## Local Setup

Install Ollama:

```bash
brew install ollama
ollama serve
```

In another terminal, pull the starting models:

```bash
ollama pull nomic-embed-text
ollama pull llama3.1:8b
```

Create a local environment file:

```bash
cp .env.example .env
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

See [STEERING.md](STEERING.md) for coding and architecture guidance. In short: keep the code clean and simple, preserve the local-first design, keep safety behavior explicit, and avoid unsupported generated claims.
