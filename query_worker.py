"""
Query worker process - runs RAG queries in isolation to avoid Streamlit event loop conflicts.
Called as subprocess by streamlit_app.py
"""

import os
import sys
import json
import asyncio
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


async def run_query(query: str, mode: str = "hybrid") -> dict:
    """Run a single query."""
    try:
        # Initialize RAGAnything
        config = RAGAnythingConfig(parser="mineru", working_dir=WORKING_DIR)

        chat_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_CHAT", "gpt-4o-mini")
        embed_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBED", "text-embedding-3-small")

        rag = RAGAnything(
            config=config,
            llm_model_func=lambda *args, **kwargs: openai_complete_if_cache(
                chat_deployment, *args, **kwargs
            ),
            embedding_func=lambda *args, **kwargs: openai_embed(
                *args, model=embed_deployment, **kwargs
            ),
        )

        # Run query
        result = await rag.aquery(query, mode=mode)

        return {
            "success": True,
            "query": query,
            "mode": mode,
            "result": result,
        }
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "mode": mode,
            "error": str(e),
        }


def main():
    """Entry point - expects query and mode as CLI args."""
    if len(sys.argv) < 2:
        print("Usage: python query_worker.py '<query>' [mode]")
        sys.exit(1)

    query = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "hybrid"

    # Run async query
    result = asyncio.run(run_query(query, mode))

    # Print JSON result to stdout
    print(json.dumps(result))


if __name__ == "__main__":
    main()
