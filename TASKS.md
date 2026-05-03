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

- [ ] Define the `rail_feature` schema.
- [ ] Create `data/features/features.geojson`.
- [ ] Add 10 starter features for the earliest smoke test.
- [ ] Expand to at least 20 MVP features.
- [ ] Include feature IDs, names, types, boroughs, statuses, geometry, and summaries.
- [ ] Add opened and closed years where known.
- [ ] Add nearby active routes and stations where known.
- [ ] Add `safety_classification` to every feature.
- [ ] Add source IDs to every feature.
- [ ] Validate GeoJSON syntax.

Done when:

- The backend can load the GeoJSON file.
- The dataset includes at least 20 useful, curated features.
- Every feature has a safety classification and source linkage.

## Phase 3: Source Corpus

Goal: build a small, clean local document corpus for source-grounded answers.

- [ ] Create `data/sources`.
- [ ] Collect 5-10 initial source documents for key features.
- [ ] Convert source material to markdown or plain text.
- [ ] Add metadata frontmatter to each source document.
- [ ] Track source title, document ID, source type, local path, access date, and license notes.
- [ ] Preserve dates, headings, and historical names.
- [ ] Remove navigation text and unrelated boilerplate.
- [ ] Create a source manifest.
- [ ] Mark which sources are personal-local-use only versus redistributable.

Done when:

- Each starter feature has at least one relevant local source.
- Source files are clean enough for chunking.
- Licensing and attribution notes are recorded.

## Phase 4: Ingestion and Vector Index

Goal: ingest local documents, chunk them, embed them locally, and persist vectors.

- [ ] Add ingestion module under `backend/app/rag`.
- [ ] Add script for building the index.
- [ ] Load markdown and text source documents.
- [ ] Parse source frontmatter.
- [ ] Chunk documents by headings first, then token length.
- [ ] Attach metadata to chunks, including document ID, source title, feature IDs, borough, and feature type.
- [ ] Generate embeddings through Ollama.
- [ ] Persist vectors to Chroma.
- [ ] Add a simple CLI query path for local testing.
- [ ] Add clear logging for indexed documents and chunks.

Done when:

- A local Chroma index can be rebuilt from `data/sources`.
- A CLI query retrieves relevant chunks for known feature questions.

## Phase 5: Feature and Search APIs

Goal: expose structured map data and basic search from the backend.

- [ ] Add `GET /api/features`.
- [ ] Support filtering by feature type.
- [ ] Support filtering by borough.
- [ ] Support filtering by status.
- [ ] Support optional bounding box filtering.
- [ ] Add `GET /api/features/{feature_id}`.
- [ ] Add `GET /api/search?q=...`.
- [ ] Implement exact and fuzzy name matching for features.
- [ ] Add `GET /api/features/nearby`.
- [ ] Calculate nearby features by lat/lon and radius.
- [ ] Add response schemas for feature and search results.
- [ ] Add tests for feature loading, filtering, detail lookup, and nearby search.

Done when:

- The frontend can fetch map features and details through stable API routes.
- Search can find known features such as City Hall Station and South 4th Street.

## Phase 6: Local RAG Chat API

Goal: answer questions using selected feature metadata and retrieved source snippets.

- [ ] Create RAG prompt templates.
- [ ] Create retrieval module.
- [ ] Implement vector search over Chroma.
- [ ] Add selected-feature retrieval filtering or boosting.
- [ ] Add fallback global retrieval when feature-specific results are sparse.
- [ ] Assemble prompt context from feature metadata, nearby context, and retrieved chunks.
- [ ] Call the local Ollama chat model.
- [ ] Add `POST /api/chat`.
- [ ] Return answer, sources, confidence, and retrieval debug data.
- [ ] Include source snippets or source titles in every answer.
- [ ] Make unsupported-answer behavior explicit in the prompt.
- [ ] Add tests with mocked retrieval and LLM responses.

Done when:

- A user can ask a question about a selected feature and get a grounded answer.
- Responses include source information.
- Unsupported questions produce a clear "not enough evidence" answer.

## Phase 7: Safety Layer

Goal: prevent the assistant from helping with restricted-access or trespass requests.

- [ ] Create safety policy module.
- [ ] Define unsafe request categories.
- [ ] Add simple classifier rules for access, trespass, bypass, and evasion requests.
- [ ] Block unsafe questions before RAG generation.
- [ ] Return a safe refusal with historical alternatives.
- [ ] Ensure feature `safety_classification` appears in prompt context.
- [ ] Add safety note handling for answers about visibility or access.
- [ ] Add tests for safety-sensitive questions.

Done when:

- Questions like "How do I get inside?" are refused.
- The assistant redirects to public, legal, historical, or museum context.

## Phase 8: Frontend Map MVP

Goal: build the first usable browser experience around the map.

- [ ] Create Vite React frontend.
- [ ] Add MapLibre GL JS.
- [ ] Add API client module.
- [ ] Build main app layout with map and side panel.
- [ ] Render current base map.
- [ ] Load historic rail features from the backend.
- [ ] Render point features as markers.
- [ ] Render line features as overlays.
- [ ] Add click selection for map features.
- [ ] Build feature detail panel.
- [ ] Show name, type, borough, years, status, routes, summary, safety note, and sources.
- [ ] Add empty, loading, and error states.
- [ ] Keep layout usable on desktop and mobile widths.

Done when:

- Users can open the app, see NYC rail-history features, click a feature, and inspect its details.

## Phase 9: Frontend Chat Experience

Goal: connect selected map features to the local AI guide.

- [ ] Build chat panel.
- [ ] Add text input and submit behavior.
- [ ] Add preset prompts for selected features.
- [ ] Send selected feature ID with chat requests.
- [ ] Display assistant answers.
- [ ] Display source snippets or source cards.
- [ ] Display confidence and safety notes where relevant.
- [ ] Add loading and error states.
- [ ] Keep chat history scoped to the current session.
- [ ] Add a clear way to ask global questions when no feature is selected.

Done when:

- Users can click a feature and ask questions like "Why did this close?"
- The answer includes source support in the UI.

## Phase 10: Better Retrieval and Evaluation

Goal: improve answer quality and make regressions visible.

- [ ] Add evaluation dataset under `data/eval/questions.jsonl`.
- [ ] Include direct fact questions.
- [ ] Include synthesis questions.
- [ ] Include geospatial questions.
- [ ] Include unsupported questions.
- [ ] Include safety-sensitive questions.
- [ ] Add evaluation script.
- [ ] Track retrieved chunk IDs for each question.
- [ ] Track groundedness, citation usefulness, refusal correctness, and latency.
- [ ] Add keyword search for exact historical names.
- [ ] Add hybrid keyword plus vector retrieval.
- [ ] Add metadata filters for borough, feature type, route, station, and year where available.
- [ ] Add retrieval debug output for development.

Done when:

- Evaluation can be run locally.
- Known questions retrieve useful chunks and produce safer, more grounded answers.

## Phase 11: Geospatial Intelligence

Goal: support location-aware exploration beyond clicking markers.

- [ ] Add current subway station dataset.
- [ ] Add current subway route context.
- [ ] Link rail features to nearby active stations and routes.
- [ ] Improve nearby feature search.
- [ ] Support questions about features near a station or neighborhood.
- [ ] Support route-oriented questions such as "near the 6 train."
- [ ] Add map filters for borough and feature type.
- [ ] Add layer controls for abandoned stations, former elevated lines, disused corridors, provisions, and public-view-only features.

Done when:

- Questions like "What abandoned features are near Brooklyn Bridge-City Hall?" work through structured geospatial context and RAG.

## Phase 12: Portfolio Polish

Goal: make the app demo-ready and understandable to reviewers.

- [ ] Improve visual design and spacing.
- [ ] Add polished source cards.
- [ ] Add screenshots or GIFs.
- [ ] Add architecture diagram.
- [ ] Add complete local setup docs.
- [ ] Add demo script to README.
- [ ] Add safety policy section to README.
- [ ] Add data licensing and attribution section.
- [ ] Add sample questions.
- [ ] Add known limitations.
- [ ] Ensure no cloud AI dependency is required for the core demo.
- [ ] Test startup from a fresh clone.

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

- [ ] Runs locally on the Mac mini.
- [ ] Uses local LLM and local embeddings.
- [ ] Shows at least 20 curated historic rail features on a map.
- [ ] Supports clicking a feature and viewing structured details.
- [ ] Supports selected-feature chat.
- [ ] Answers include source snippets or source titles.
- [ ] Unsafe access questions are refused.
- [ ] Nearby feature search works for at least one demo location.
- [ ] README includes setup, architecture, safety, and demo instructions.
- [ ] Licensing and attribution notes are present for included data.
