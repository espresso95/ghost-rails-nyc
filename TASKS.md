# Ghost Rails NYC Task Breakdown

This task plan turns the design document into implementation phases. The goal is to build a polished local-first MVP before expanding data coverage or adding advanced ML features.

## Phase 0: Project Foundation

Goal: create a clean repo structure and confirm the local development baseline.

- [x] Confirm target stack: FastAPI backend, React/Vite frontend, MapLibre map, Ollama, Chroma, GeoJSON/SQLite.
- [x] Create backend folder structure.
- [x] Create frontend folder structure.
- [x] Create data folders for raw inputs, processed outputs, source documents, features, Chroma, and evaluation files.
- [x] Add `.env.example` with local service settings.
- [x] Add basic developer setup instructions to `README.md`.
- [x] Decide initial chat model and embedding model.
- [ ] Install and verify Ollama locally.
- [ ] Pull local embedding model, starting with `nomic-embed-text`.
- [ ] Pull one local instruct model for development.

Done when:

- The repo has the expected project skeleton.
- Ollama is installed and can respond locally.
- The README explains how to start local development.

## Phase 1: Backend Skeleton

Goal: stand up a minimal FastAPI service with configuration and health checks.

- [x] Create backend Python environment.
- [x] Add FastAPI, Uvicorn, Pydantic, and core dependencies.
- [x] Create `backend/app/main.py`.
- [x] Create backend config module.
- [x] Add model role interfaces for chat and embeddings.
- [x] Add provider factory for swappable model configuration.
- [x] Add Ollama chat and embedding adapters.
- [x] Add Groq and Gemini chat adapters.
- [x] Add tests for model settings and provider selection.
- [x] Add `GET /api/health`.
- [x] Check Ollama availability from the health endpoint.
- [x] Add placeholder vector store availability check.
- [x] Add backend startup command to README.
- [x] Add minimal backend tests for health behavior.

Done when:

- `uvicorn app.main:app --reload --port 8000` starts successfully.
- `GET /api/health` returns local service status.

## Phase 2: Curated Feature Dataset

Goal: create the first map-ready dataset of historic rail features.

- [x] Define the `rail_feature` schema.
- [x] Create `data/features/features.geojson`.
- [x] Add 10 starter features for the earliest smoke test.
- [x] Expand to at least 20 MVP features.
- [x] Include feature IDs, names, types, boroughs, statuses, geometry, and summaries.
- [x] Add opened and closed years where known.
- [x] Add nearby active routes and stations where known.
- [x] Add `safety_classification` to every feature.
- [x] Add source IDs to every feature.
- [x] Validate GeoJSON syntax.

Done when:

- The backend can load the GeoJSON file.
- The dataset includes at least 20 useful, curated features.
- Every feature has a safety classification and source linkage.

## Phase 3: Source Corpus

Goal: build a small, clean local document corpus for source-grounded answers.

- [x] Create `data/sources`.
- [x] Collect 5-10 initial source documents for key features.
- [x] Convert source material to markdown or plain text.
- [x] Add metadata frontmatter to each source document.
- [x] Track source title, document ID, source type, local path, access date, and license notes.
- [x] Preserve dates, headings, and historical names.
- [x] Remove navigation text and unrelated boilerplate.
- [x] Create a source manifest.
- [x] Mark which sources are personal-local-use only versus redistributable.

Done when:

- Each starter feature has at least one relevant local source.
- Source files are clean enough for chunking.
- Licensing and attribution notes are recorded.

## Phase 4: Ingestion and Vector Index

Goal: ingest local documents, chunk them, embed them locally, and persist vectors.

- [x] Add ingestion module under `backend/app/rag`.
- [x] Add script for building the index.
- [x] Load markdown and text source documents.
- [x] Parse source frontmatter.
- [x] Chunk documents by headings first, then token length.
- [x] Attach metadata to chunks, including document ID, source title, feature IDs, borough, and feature type.
- [ ] Generate embeddings through Ollama.
- [x] Persist a low-RAM local retrieval index.
- [x] Add a simple CLI query path for local testing.
- [x] Add clear logging for indexed documents and chunks.

Done when:

- A local Chroma index can be rebuilt from `data/sources`.
- A CLI query retrieves relevant chunks for known feature questions.

## Phase 5: Feature and Search APIs

Goal: expose structured map data and basic search from the backend.

- [x] Add `GET /api/features`.
- [x] Support filtering by feature type.
- [x] Support filtering by borough.
- [x] Support filtering by status.
- [x] Support optional bounding box filtering.
- [x] Add `GET /api/features/{feature_id}`.
- [x] Add `GET /api/search?q=...`.
- [x] Implement exact and fuzzy name matching for features.
- [x] Add `GET /api/features/nearby`.
- [x] Calculate nearby features by lat/lon and radius.
- [x] Add response schemas for feature and search results.
- [x] Add tests for feature loading, filtering, detail lookup, and nearby search.

Done when:

- The frontend can fetch map features and details through stable API routes.
- Search can find known features such as City Hall Station and South 4th Street.

## Phase 6: Local RAG Chat API

Goal: answer questions using selected feature metadata and retrieved source snippets.

- [x] Create RAG prompt templates.
- [x] Create retrieval module.
- [x] Implement low-RAM local lexical retrieval.
- [x] Add selected-feature retrieval filtering or boosting.
- [x] Add fallback global retrieval when feature-specific results are sparse.
- [x] Assemble prompt context from feature metadata, nearby context, and retrieved chunks.
- [x] Support configured LLM generation when enabled.
- [x] Add `POST /api/chat`.
- [x] Return answer, sources, confidence, and retrieval debug data.
- [x] Include source snippets or source titles in every answer.
- [x] Make unsupported-answer behavior explicit in the prompt.
- [x] Add tests with deterministic local retrieval responses.

Done when:

- A user can ask a question about a selected feature and get a grounded answer.
- Responses include source information.
- Unsupported questions produce a clear "not enough evidence" answer.

## Phase 7: Safety Layer

Goal: prevent the assistant from helping with restricted-access or trespass requests.

- [x] Create safety policy module.
- [x] Define unsafe request categories.
- [x] Add simple classifier rules for access, trespass, bypass, and evasion requests.
- [x] Block unsafe questions before RAG generation.
- [x] Return a safe refusal with historical alternatives.
- [x] Ensure feature `safety_classification` appears in prompt context.
- [x] Add safety note handling for answers about visibility or access.
- [x] Add tests for safety-sensitive questions.

Done when:

- Questions like "How do I get inside?" are refused.
- The assistant redirects to public, legal, historical, or museum context.

## Phase 8: Frontend Map MVP

Goal: build the first usable browser experience around the map.

- [x] Create Vite React frontend.
- [x] Add MapLibre GL JS.
- [x] Add API client module.
- [x] Build main app layout with map and side panel.
- [x] Render current base map.
- [x] Load historic rail features from the backend.
- [x] Render point features as markers.
- [x] Render line features as overlays.
- [x] Add click selection for map features.
- [x] Build feature detail panel.
- [x] Show name, type, borough, years, status, routes, summary, safety note, and sources.
- [x] Add empty, loading, and error states.
- [x] Keep layout usable on desktop and mobile widths.

Done when:

- Users can open the app, see NYC rail-history features, click a feature, and inspect its details.

## Phase 9: Frontend Chat Experience

Goal: connect selected map features to the local AI guide.

- [x] Build chat panel.
- [x] Add text input and submit behavior.
- [x] Add preset prompts for selected features.
- [x] Send selected feature ID with chat requests.
- [x] Display assistant answers.
- [x] Display source snippets or source cards.
- [x] Display confidence and safety notes where relevant.
- [x] Add loading and error states.
- [x] Keep chat history scoped to the current session.
- [x] Add a clear way to ask global questions when no feature is selected.

Done when:

- Users can click a feature and ask questions like "Why did this close?"
- The answer includes source support in the UI.

## Phase 10: Better Retrieval and Evaluation

Goal: improve answer quality and make regressions visible.

- [x] Add evaluation dataset under `data/eval/questions.jsonl`.
- [x] Include direct fact questions.
- [x] Include synthesis questions.
- [x] Include geospatial questions.
- [x] Include unsupported questions.
- [x] Include safety-sensitive questions.
- [x] Add evaluation script.
- [x] Track retrieved chunk IDs for each question.
- [x] Track groundedness, citation usefulness, refusal correctness, and latency.
- [x] Add keyword search for exact historical names.
- [ ] Add hybrid keyword plus vector retrieval.
- [ ] Add metadata filters for borough, feature type, route, station, and year where available.
- [x] Add retrieval debug output for development.

Done when:

- Evaluation can be run locally.
- Known questions retrieve useful chunks and produce safer, more grounded answers.

## Phase 11: Geospatial Intelligence

Goal: support location-aware exploration beyond clicking markers.

- [x] Add current subway station dataset.
- [x] Add current subway route context.
- [x] Link rail features to nearby active stations and routes.
- [x] Improve nearby feature search.
- [x] Support questions about features near a station or neighborhood.
- [x] Support route-oriented questions such as "near the 6 train."
- [x] Add map filters for borough and feature type.
- [x] Add layer controls for abandoned stations, former elevated lines, disused corridors, provisions, and public-view-only features.

Done when:

- Questions like "What abandoned features are near Brooklyn Bridge-City Hall?" work through structured geospatial context and RAG.

## Phase 12: Portfolio Polish

Goal: make the app demo-ready and understandable to reviewers.

- [x] Improve visual design and spacing.
- [x] Add polished source cards.
- [ ] Add screenshots or GIFs.
- [x] Add architecture diagram.
- [x] Add complete local setup docs.
- [x] Add demo script to README.
- [x] Add safety policy section to README.
- [x] Add data licensing and attribution section.
- [x] Add sample questions.
- [x] Add known limitations.
- [x] Ensure no cloud AI dependency is required for the core demo.
- [x] Test startup from a fresh clone.

Done when:

- A reviewer can run the project locally and understand the architecture, safety model, and demo path.

## Phase 13: Post-MVP Extensions

Goal: add advanced functionality only after the MVP is stable.

- [ ] Expand curated dataset to 50+ features.
- [ ] Add optional reranker.
- [ ] Add local LLM-assisted historical entity extraction.
- [ ] Add human review workflow for extracted facts.
- [ ] Add reuse discussion score as an educational feature.
- [ ] Add "then vs now" route comparison.
- [ ] Explore offline map tiles.
- [ ] Explore OSM import workflow.
- [ ] Explore PostGIS and pgvector migration.
- [ ] Explore historical map overlays where licensing permits.

Done when:

- The MVP remains stable while advanced features are added incrementally.

## MVP Acceptance Checklist

- [x] Runs locally on the Mac mini.
- [x] Uses local retrieval by default with optional local/cloud LLM configuration.
- [x] Shows at least 20 curated historic rail features on a map.
- [x] Supports clicking a feature and viewing structured details.
- [x] Supports selected-feature chat.
- [x] Answers include source snippets or source titles.
- [x] Unsafe access questions are refused.
- [x] Nearby feature search works for at least one demo location.
- [x] README includes setup, architecture, safety, and demo instructions.
- [x] Licensing and attribution notes are present for included data.
