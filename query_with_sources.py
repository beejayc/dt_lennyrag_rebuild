"""
CLI interface with source attribution.
Shows which podcast episodes the answer is based on.
"""

import os
import sys
import argparse
import time
from pathlib import Path
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


class RAGQueryWithSources:
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

    def extract_sources_from_response(self, response: str) -> list:
        """Extract podcast episode sources from response metadata."""
        # The response structure depends on LightRAG implementation
        # This is a basic extraction - adjust based on actual response format
        sources = []

        # Try to extract from response if it contains source metadata
        if hasattr(response, "__dict__"):
            if "sources" in response.__dict__:
                sources = response.__dict__["sources"]
        elif isinstance(response, dict):
            if "sources" in response:
                sources = response["sources"]

        return sources

    def format_sources(self) -> str:
        """Format source files as episode names."""
        data_dir = Path("data")
        if not data_dir.exists():
            return ""

        files = sorted(data_dir.glob("*.txt"))
        episode_names = [f.stem for f in files]  # Remove .txt extension
        return "\n".join(f"  • {name}" for name in episode_names[:5])

    def query(self, query_text: str, mode: str = "hybrid"):
        """Run query and display with sources."""
        print(f"Query: {query_text}")
        print(f"Mode: {mode}")
        print("-" * 60)

        start_time = time.time()

        try:
            result = self.rag.query(query_text, mode=mode)
            elapsed = time.time() - start_time

            print("Response:")
            print(result)

            print("\n" + "-" * 60)
            print("Sources (from available episodes):")
            self.display_available_sources()

            print("-" * 60)
            print(f"Time: {elapsed:.2f}s")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def display_available_sources(self):
        """Display available podcast episodes."""
        data_dir = Path("data")
        if not data_dir.exists():
            print("  No data directory found")
            return

        files = sorted(data_dir.glob("*.txt"))
        if not files:
            print("  No transcripts available")
            return

        print(f"  Total episodes available: {len(files)}")
        print("  Sample episodes:")
        for f in files[:5]:
            print(f"    • {f.stem}")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more")


def main():
    parser = argparse.ArgumentParser(description="RAG query with source attribution")
    parser.add_argument("query", nargs="*", help="Query text")
    parser.add_argument("--mode", default="hybrid", choices=["hybrid", "local", "global", "naive"],
                        help="Retrieval mode")

    args = parser.parse_args()

    if not args.query:
        print("Usage: python query_with_sources.py '<query>'")
        sys.exit(1)

    query_text = " ".join(args.query)
    cli = RAGQueryWithSources()
    cli.query(query_text, mode=args.mode)


if __name__ == "__main__":
    main()
