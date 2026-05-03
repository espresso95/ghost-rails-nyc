from __future__ import annotations

import argparse
from pathlib import Path

from app.config import load_settings
from app.rag.index import build_lexical_index, save_index
from app.rag.retriever import retrieve_chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the local Ghost Rails retrieval index.")
    parser.add_argument("--query", help="Run a test query after building the index.")
    parser.add_argument("--sources-path", type=Path, help="Override the source document directory.")
    parser.add_argument("--index-path", type=Path, help="Override the local index directory.")
    args = parser.parse_args()

    settings = load_settings()
    sources_path = args.sources_path or settings.sources_path
    index_path = args.index_path or settings.chroma_path

    index = build_lexical_index(sources_path)
    output_path = save_index(index, index_path)
    print(f"Indexed {index.document_count} documents into {index.chunk_count} chunks")
    print(f"Wrote {output_path}")

    if args.query:
        results = retrieve_chunks(index, args.query, top_k=settings.retrieval.similarity_top_k)
        for result in results:
            print(f"{result.score:.2f} {result.chunk.document_id} {result.chunk.chunk_id}")
            print(result.chunk.text[:240])


if __name__ == "__main__":
    main()

