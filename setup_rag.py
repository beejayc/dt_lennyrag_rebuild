"""
Main RAG setup orchestration script.
Indexes podcast transcripts into Qdrant and builds knowledge graph.
"""

import os
import sys
import asyncio
import json
import argparse
from pathlib import Path
from typing import Optional
import time
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

from qdrant_config import check_qdrant_running, get_qdrant_client, ensure_collections, QDRANT_URL, WORKING_DIR

# Import RAG libraries
try:
    from raganything import RAGAnything, RAGAnythingConfig
    from lightrag.llm.openai import openai_complete_if_cache, openai_embed
except ImportError:
    print("Error: raganything and lightrag-hku are required")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)


class RAGSetup:
    def __init__(self, working_dir: str = WORKING_DIR):
        self.working_dir = working_dir
        self.data_dir = Path("data")
        self.progress_file = Path(working_dir) / "kv_store_full_docs.json"

        # Initialize RAGAnything config
        self.rag_config = RAGAnythingConfig(
            parser="mineru",
            working_dir=working_dir,
        )

        self.rag = None

    def initialize_rag(self):
        """Initialize RAGAnything with Azure OpenAI."""
        print("Initializing RAGAnything with Azure OpenAI...")

        # Get Azure deployments
        chat_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_CHAT", "gpt-4o-mini")
        embed_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBED", "text-embedding-3-small")

        self.rag = RAGAnything(
            config=self.rag_config,
            llm_model_func=lambda *args, **kwargs: openai_complete_if_cache(
                chat_deployment,
                *args,
                **kwargs
            ),
            embedding_func=lambda *args, **kwargs: openai_embed(
                *args,
                model=embed_deployment,
                **kwargs
            ),
        )
        print("✓ RAGAnything initialized")

    def check_qdrant(self) -> bool:
        """Check and initialize Qdrant."""
        print(f"Checking Qdrant at {QDRANT_URL}...")

        if not check_qdrant_running(QDRANT_URL):
            print(f"✗ Qdrant not running at {QDRANT_URL}")
            print("Start it with: ./start_qdrant.sh")
            return False

        try:
            client = get_qdrant_client(QDRANT_URL)
            ensure_collections(client)
            print("✓ Qdrant ready")
            return True
        except Exception as e:
            print(f"✗ Qdrant error: {e}")
            return False

    def get_transcript_files(self) -> list:
        """Get all transcript files from data/ directory."""
        if not self.data_dir.exists():
            print(f"✗ Data directory not found: {self.data_dir}")
            return []

        files = sorted(self.data_dir.glob("*.txt"))
        print(f"Found {len(files)} transcript files")
        return files

    def get_already_indexed(self) -> set:
        """Get set of already-indexed documents."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                data = json.load(f)
                return set(data.keys())
        return set()

    async def process_single_transcript(self, file_path: Path, semaphore: asyncio.Semaphore):
        """Process a single transcript file."""
        async with semaphore:
            try:
                await self.rag.ainsert_file(str(file_path))
                return True
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
                return False

    async def index_parallel(self, files: list, workers: int = 5):
        """Index transcripts in parallel."""
        print(f"Indexing {len(files)} transcripts in parallel with {workers} workers...")

        already_indexed = self.get_already_indexed()
        files_to_process = [f for f in files if f.name not in already_indexed]

        if not files_to_process:
            print("All transcripts already indexed")
            return

        semaphore = asyncio.Semaphore(workers)
        tasks = [self.process_single_transcript(f, semaphore) for f in files_to_process]

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        successful = sum(1 for r in results if r)
        print(f"✓ Indexed {successful}/{len(files_to_process)} transcripts in {elapsed:.1f}s")

    def index_sequential(self, files: list):
        """Index transcripts sequentially."""
        print(f"Indexing {len(files)} transcripts sequentially...")

        already_indexed = self.get_already_indexed()
        files_to_process = [f for f in files if f.name not in already_indexed]

        if not files_to_process:
            print("All transcripts already indexed")
            return

        start_time = time.time()
        successful = 0

        for file_path in tqdm(files_to_process, desc="Indexing"):
            try:
                self.rag.insert_file(str(file_path))
                successful += 1
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

        elapsed = time.time() - start_time
        print(f"✓ Indexed {successful}/{len(files_to_process)} transcripts in {elapsed:.1f}s")

    def run_test_query(self):
        """Run verification query."""
        print("\nRunning verification query...")
        query = "What is a curiosity loop and how does it work?"

        try:
            response = self.rag.query(query, mode="hybrid")
            print(f"Query: {query}")
            print(f"Response: {response}")
            print("✓ System working correctly")
            return True
        except Exception as e:
            print(f"✗ Query failed: {e}")
            return False

    def run(self, quick: bool = False, parallel: bool = False, workers: int = 5):
        """Run the full setup."""
        print("=" * 60)
        print("LennyHub RAG Setup")
        print("=" * 60)

        # Check Qdrant
        if not self.check_qdrant():
            return False

        # Initialize RAG
        self.initialize_rag()

        # Get transcript files
        files = self.get_transcript_files()
        if not files:
            return False

        # Limit to quick test if requested
        if quick:
            files = files[:10]
            print(f"Quick mode: processing first {len(files)} files")

        # Index transcripts
        try:
            if parallel:
                asyncio.run(self.index_parallel(files, workers=workers))
            else:
                self.index_sequential(files)
        except KeyboardInterrupt:
            print("\n✗ Setup interrupted by user")
            return False
        except Exception as e:
            print(f"✗ Setup failed: {e}")
            return False

        # Run test query
        if not self.run_test_query():
            return False

        print("\n" + "=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("  Web UI:       ./run_streamlit.sh")
        print("  CLI Query:    python query_rag.py 'your question'")
        print("  Graph View:   python serve_graph.py")
        return True


def main():
    parser = argparse.ArgumentParser(description="RAG setup and indexing")
    parser.add_argument("--quick", action="store_true", help="Quick test (first 10 files)")
    parser.add_argument("--parallel", action="store_true", help="Use parallel indexing")
    parser.add_argument("--workers", type=int, default=5, help="Number of parallel workers")

    args = parser.parse_args()

    setup = RAGSetup()
    success = setup.run(quick=args.quick, parallel=args.parallel, workers=args.workers)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
