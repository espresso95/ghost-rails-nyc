# Steering

This project should stay clean, simple, local-first, and easy to reason about.

## Code Style

- Prefer straightforward code over clever abstractions.
- Keep functions small and focused on one job.
- Use descriptive names for modules, functions, variables, schemas, and tests.
- Avoid hidden side effects. Pass dependencies explicitly where practical.
- Prefer typed interfaces and structured data over loose dictionaries when data crosses module boundaries.
- Keep business rules close to the domain they belong to.
- Make failure modes explicit with clear errors and predictable return shapes.
- Do not add broad framework wrappers until repeated real use proves they are needed.
- Do not add `//` comments. Use clear names and structure first; add short language-appropriate comments only when the code would otherwise be hard to understand.

## Architecture

- Preserve the local-first design: local LLM, local embeddings, local vector store, local feature data, and local source corpus.
- Keep frontend, backend, data processing, RAG, geospatial logic, and safety policy as separate concerns.
- Keep the MVP small: reliable selected-feature RAG over curated data is more important than broad coverage.
- Prefer explicit source metadata and citations over unsupported generated claims.
- Treat safety behavior as core application logic, not as UI decoration.

## Testing

- Add focused tests near the behavior being changed.
- Test contracts at API boundaries.
- Test safety-sensitive behavior directly.
- Add regression questions for RAG behavior as the corpus grows.
- Keep tests deterministic by mocking local model calls unless the test is explicitly marked as an integration check.

## Data

- Keep source attribution and license notes with every document.
- Keep raw, processed, source, feature, vector, and evaluation data separated.
- Curate feature data manually before adding imports or scraping workflows.
- Avoid redistributing copyrighted source text unless the license clearly permits it.

