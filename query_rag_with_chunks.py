"""
CLI interface with chunk-level debugging.
Shows which text chunks were retrieved for the query.
"""

import os
import sys
import argparse
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

from qdrant_config import WORKING_DIR

try:
    from raganything import RAGAnything, RAGAnythingConfig
    from lightrag.llm.openai import openai_complete_if_cache, openai_embed
except ImportError:
    print("Error: raganything and lightrag-hku are required")
    sys.exit(1)


class RAGQueryDebug:
    def __init__(self):
        """Initialize RAG system."""
        print("Initializing RAG system...")

        config = RAGAnythingConfig(parser="mineru", working_dir=WORKING_DIR)

        chat_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_CHAT", "gpt-4o-mini")
        embed_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBED", "text-embedding-3-small")

        self.rag = RAGAnything(
            config=config,
            llm_model_func=lambda *args, **kwargs: openai_complete_if_cache(
                chat_deployment, *args, **kwargs
            ),
            embedding_func=lambda *args, **kwargs: openai_embed(
                *args, model=embed_deployment, **kwargs
            ),
        )
        print("✓ RAG system ready\n")

    def query_with_debug(self, query_text: str, mode: str = "hybrid"):
        """Run query and show chunk-level detail."""
        print(f"Query: {query_text}")
        print(f"Mode: {mode}")
        print("-" * 80)

        start_time = time.time()

        try:
            # Run query with debug info
            result = self.rag.query(query_text, mode=mode)
            elapsed = time.time() - start_time

            print("ANSWER:")
            print("-" * 80)
            print(result)

            print("\n" + "-" * 80)
            print("RETRIEVAL DEBUG INFO:")
            print("-" * 80)

            # Attempt to get internal retrieval details if available
            # This structure depends on LightRAG implementation
            if hasattr(result, "retrieval_details"):
                self._print_retrieval_details(result.retrieval_details)
            else:
                print("(Chunk-level details depend on LightRAG implementation)")
                print("Note: Check rag_storage/ for knowledge graph and chunk files")

            print("-" * 80)
            print(f"Total time: {elapsed:.2f}s")

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _print_retrieval_details(self, details):
        """Pretty-print retrieval details."""
        if isinstance(details, dict):
            for key, value in details.items():
                print(f"\n{key}:")
                if isinstance(value, list):
                    for i, item in enumerate(value[:5], 1):  # Show first 5 items
                        print(f"  {i}. {item}")
                    if len(value) > 5:
                        print(f"  ... and {len(value) - 5} more")
                else:
                    print(f"  {value}")


def main():
    parser = argparse.ArgumentParser(description="RAG query with chunk-level debugging")
    parser.add_argument("query", nargs="*", help="Query text")
    parser.add_argument("--mode", default="hybrid", choices=["hybrid", "local", "global", "naive"],
                        help="Retrieval mode")

    args = parser.parse_args()

    if not args.query:
        print("Usage: python query_rag_with_chunks.py '<query>'")
        sys.exit(1)

    query_text = " ".join(args.query)
    debug = RAGQueryDebug()
    debug.query_with_debug(query_text, mode=args.mode)


if __name__ == "__main__":
    main()
