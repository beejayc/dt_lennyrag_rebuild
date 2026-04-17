"""
Centralized Qdrant configuration and client factory.
"""

import os
from typing import Optional
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()

# Qdrant collection names
COLLECTION_ENTITIES = "lightrag_vdb_entities"
COLLECTION_RELATIONSHIPS = "lightrag_vdb_relationships"
COLLECTION_CHUNKS = "lightrag_vdb_chunks"

# Vector dimension (from text-embedding-3-small)
VECTOR_DIM = 1536

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
USE_QDRANT = os.getenv("USE_QDRANT", "true").lower() == "true"
WORKING_DIR = os.getenv("WORKING_DIR", "./rag_storage")


def check_qdrant_running(url: str = QDRANT_URL) -> bool:
    """Check if Qdrant server is running."""
    try:
        response = requests.get(f"{url}/", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def get_qdrant_client(url: str = QDRANT_URL) -> QdrantClient:
    """
    Get Qdrant client. Falls back to in-memory if server not available
    and USE_QDRANT is False.
    """
    if not check_qdrant_running(url):
        if not USE_QDRANT:
            print(f"Warning: Qdrant not running at {url}. Using in-memory NanoVectorDB fallback.")
            return None
        raise ConnectionError(f"Qdrant server not running at {url}")

    return QdrantClient(url=url)


def ensure_collections(client: QdrantClient, vector_dim: int = VECTOR_DIM) -> None:
    """Create Qdrant collections if they don't exist."""
    collections = [COLLECTION_ENTITIES, COLLECTION_RELATIONSHIPS, COLLECTION_CHUNKS]

    for collection_name in collections:
        try:
            client.get_collection(collection_name)
            print(f"Collection {collection_name} exists")
        except Exception:
            print(f"Creating collection {collection_name}...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
            )


def get_collection_stats(client: Optional[QdrantClient]) -> dict:
    """Get stats for all collections."""
    if not client:
        return {}

    stats = {}
    for collection_name in [COLLECTION_ENTITIES, COLLECTION_RELATIONSHIPS, COLLECTION_CHUNKS]:
        try:
            collection_info = client.get_collection(collection_name)
            stats[collection_name] = {
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "status": collection_info.status,
            }
        except Exception as e:
            stats[collection_name] = {"error": str(e)}

    return stats
