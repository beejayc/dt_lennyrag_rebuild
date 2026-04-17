"""
CLI interface for querying the RAG system.
Supports single query or interactive mode.
"""

import os
import sys
import argparse
import time
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


class RAGQueryCLI:
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

    def query(self, query_text: str, mode: str = "hybrid"):
        """Run a single query."""
        print(f"Query: {query_text}")
        print(f"Mode: {mode}")
        print("-" * 60)

        start_time = time.time()

        try:
            result = self.rag.query(query_text, mode=mode)
            elapsed = time.time() - start_time

            print("Response:")
            print(result)
            print("-" * 60)
            print(f"Time: {elapsed:.2f}s")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def interactive(self):
        """Run interactive query loop."""
        print("Interactive mode (Ctrl+C to exit)")
        print("Available modes: hybrid, local, global, naive")
        print("-" * 60)

        while True:
            try:
                query_text = input("\nQuery: ").strip()
                if not query_text:
                    continue

                # Check if mode specified
                parts = query_text.rsplit(" --mode=", 1)
                if len(parts) == 2:
                    query_text, mode = parts
                else:
                    mode = "hybrid"

                self.query(query_text, mode=mode)
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="RAG query CLI")
    parser.add_argument("query", nargs="?", help="Query text")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--mode", default="hybrid", choices=["hybrid", "local", "global", "naive"],
                        help="Retrieval mode")

    args = parser.parse_args()

    cli = RAGQueryCLI()

    if args.interactive or not args.query:
        cli.interactive()
    else:
        cli.query(args.query, mode=args.mode)


if __name__ == "__main__":
    main()
