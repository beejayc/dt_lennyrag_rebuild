# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

**dt_dsc_crt1_ragsetup** is a research and setup documentation project for Retrieval-Augmented Generation (RAG) systems. It currently documents the LennyHub RAG architecture, a production-grade knowledge graph search engine over 297 Lenny's Podcast episodes.

**Scope**: Documentation, research analysis, and setup guides for RAG systems. The actual LennyHub RAG implementation lives in the `lennyhub-rag/` reference project (read-only).

**Purpose**: Provide architectural guidance, setup procedures, and technical decision documentation for building similar RAG systems.

## Project Structure

```
dt_dsc_crt1_ragsetup/
├── docs/
│   ├── lenny-prd.md                    # Product analysis (problem, users, journey, value prop)
│   └── TECH_BREAKDOWN_lennyhub_rag.md  # Technical architecture & decisions (8 key decisions documented)
├── CLAUDE.md                           # This file
└── README.md                           # (to be created: user-facing guide)
└── data/*.txt                          # (All Podcast Transcript files)
```

## LennyHub RAG System Overview

**What it does**: A local knowledge graph RAG system that answers questions about podcast transcripts with source attribution. Users query 297 Lenny's Podcast episodes via Streamlit web UI or CLI.

**Core flow**:
1. **Ingestion**: Transcripts (`.txt`) → RAG-Anything chunking → LightRAG entity/relationship extraction
2. **Embedding**: GPT-4.1-mini extracts entities; text-embedding-ada-002 generates vectors (1536-dim)
3. **Storage**: Three Qdrant collections (entities, relationships, chunks) + GraphML knowledge graph
4. **Query**: Four retrieval modes (hybrid, local, global, naive) route to relevant context
5. **Synthesis**: GPT-4o-mini generates answer with source attribution

**Key tech stack**:
- **RAG Framework**: RAG-Anything ≥1.2.9 (document orchestration)
- **Knowledge Graph**: LightRAG ≥1.4.9 (entity extraction, relationship mapping)
- **Vector Database**: Qdrant ≥1.16 (local, production-grade, no Docker)
- **LLM**: Azure OpenAI (GPT-4o-mini for synthesis, text-embedding-3-small for vectors)
- **UI**: Streamlit ≥1.28.0 (web interface) + HTTP server for graph visualization

## Critical Technical Decisions

If you're building or extending this system, understand these 8 key decisions documented in `docs/TECH_BREAKDOWN_lennyhub_rag.md`:

1. **Local Qdrant** (not cloud VectorDB or NanoVectorDB) — Production-grade performance locally; no scaling/remote access
2. **Parallel asyncio ingestion** (5–10× speedup) — Concurrent transcript processing with semaphore control
3. **Three separate Qdrant collections** — Enables specialized retrieval (entity-focused, relationship-focused, dense vector search)
4. **GraphML knowledge graph** (alongside Qdrant) — Dual representation: vectors for semantic search, graph for explicit traversal
5. **Subprocess isolation in Streamlit** — Avoids event loop conflicts by offloading queries to `query_worker.py`
6. **OpenAI response caching** (~80% cost savings) — Cached LLM responses via cache_control headers
7. **GPT-4o-mini + text-embedding-3-small** — Mid-tier models balance cost (~$7.20 for full index) and quality
8. **Mineru parser** (RAG-Anything default) — Intelligent chunking respects document structure

**Why this matters**: Replacing any core decision (e.g., switching to cloud VectorDB, dropping parallel ingestion, or using a different LLM) requires significant refactoring. See the dependency map in TECH_BREAKDOWN for replacement costs.

## Common Development Tasks

### Setup & Installation
```bash
# One-time Qdrant setup
./install_qdrant_local.sh
./start_qdrant.sh
curl http://localhost:6333/  # Verify running

# Install Python dependencies (first time)
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with Azure OpenAI API key
```

### Indexing Transcripts
```bash
# Quick test (first 10 transcripts, ~5 min)
python setup_rag.py --quick

# Full sequential indexing (all 297, ~2–3 hrs)
python setup_rag.py

# Full parallel indexing (all 297, ~25–35 min, 5–10x faster)
python setup_rag.py --parallel --workers 5

# Resume failed run
python setup_rag.py  # Automatically skips already-indexed transcripts via kv_store_full_docs.json
```

### Querying the System
```bash
# CLI single query
python query_rag.py "What is a curiosity loop?"

# CLI interactive mode
python query_rag.py --interactive

# CLI with source attribution
python query_with_sources.py "Question here"

# CLI with chunk-level detail (debugging)
python query_rag_with_chunks.py "Question here"
```

### Running User Interfaces
```bash
# Web UI (recommended for exploration)
./run_streamlit.sh
# Opens http://localhost:8501

# Graph visualization (network of 544 people/concepts)
python serve_graph.py
# opens http://localhost:8000/graph_viewer_simple.html

# Qdrant dashboard (vector store health)
open http://localhost:6333/dashboard
```

### System Health Checks
```bash
# Check Qdrant status
./status_qdrant.sh
curl http://localhost:6333/

# Verify vector collections exist
# (via Qdrant dashboard or by querying in Python)
```

### Managing Qdrant
```bash
# Start background service
./start_qdrant.sh

# Stop service
./stop_qdrant.sh

# Check status
./status_qdrant.sh
```

## Code Organization (Current & Future)

### Entry Points
- **`setup_rag.py`** — Main orchestration; checks Qdrant, indexes transcripts (seq or parallel), runs test query
- **`streamlit_app.py`** — Web UI (query tab, stats tab, transcript browser)
- **`query_rag.py`** — CLI query interface (single or interactive mode)
- **`serve_graph.py`** — HTTP server for interactive knowledge graph visualization

### Core Components
- **`qdrant_config.py`** — Centralized Qdrant configuration; detects server, handles fallback to NanoVectorDB
- **`query_worker.py`** — Subprocess handler for Streamlit (avoids event loop conflicts)

### Utilities & Legacy
- **`query_with_sources.py`** — CLI with source attribution
- **`query_rag_with_chunks.py`** — CLI with chunk-level debugging
- **`export_graph.py`** — Export knowledge graph for analysis
- **`build_transcript_rag.py`, `build_transcript_rag_parallel.py`, `build_rag_quick.py`** — Legacy; use `setup_rag.py` instead

### Configuration & Data
- **`.env.example`** — Environment template; copy to `.env` and add API keys
- **`requirements.txt`** — Pinned Python dependencies
- **`qdrant_config.yaml`** — Qdrant server configuration (port, logging, storage)
- **`data/`** — 297 podcast transcripts (`.txt` files)
- **`rag_storage/`** — LightRAG index output (GraphML, JSON metadata, chunk store)
- **`qdrant_storage/`** — Qdrant database files (generated)

## Architecture Highlights

### Data Ingestion Pipeline
1. **Chunking** (RAG-Anything + Mineru): Transcripts split into semantic segments respecting document boundaries
2. **Extraction** (LightRAG): GPT-4o-mini identifies entities (people, concepts, frameworks) and relationships
3. **Embedding** (OpenAI): text-embedding-3-small generates 1536-dim vectors for entities, relationships, and chunks
4. **Storage** (Qdrant + GraphML): Three collections store vectors; GraphML persists explicit graph structure

### Query Resolution
1. **Retrieval routing** (LightRAG): Four modes available:
   - **Hybrid** (default): Combines local (entity-focused) + global (relationship-focused) + naive (vector similarity)
   - **Local**: Extract entities from query → fetch related entities from Qdrant
   - **Global**: Traverse relationships → fetch concept chains
   - **Naive**: Direct cosine similarity on query embedding
2. **Ranking**: Top-k chunks/entities scored and ordered
3. **Synthesis**: GPT-4o-mini generates answer with optional source attribution
4. **Caching**: OpenAI cache headers (~80% cost savings on repeated queries)

### Key Performance Considerations
- **Indexing**: Parallel asyncio with semaphore (default 5 workers) achieves 5–10× speedup (25–35 min vs 2–3 hrs)
- **Query latency**: Qdrant sub-50ms vector lookups; GPT-4o-mini synthesis adds 1–3 sec
- **Cost**: ~$7.20 total for full 297-transcript indexing (with caching, GPT-4o-mini + text-embedding-3-small)
- **Concurrency**: Streamlit is single-threaded; subprocess isolation avoids event loop conflicts

## Testing & Validation

**Current state**: No automated test suite; manual testing via CLI and Streamlit app.

**Manual test embedded in setup**:
- `setup_rag.py` runs "What is a curiosity loop and how does it work?" at the end to verify system works

**What's untested**:
- Parallel ingestion failure modes (network timeout, rate limit exceeded)
- Qdrant crash/recovery
- Streamlit subprocess query timeouts
- Non-ASCII characters in transcripts
- Concurrent users (Streamlit is single-threaded)

**If adding tests**: Consider pytest with fixtures for Qdrant health checks, query validation, and parallel ingestion rollback.

## Environment Setup

**Required**:
- Python 3.11+ (RAG-Anything requires 3.11+)
- Azure OpenAI API key (for GPT-4o-mini and embeddings)
- Qdrant installed locally (automated via `install_qdrant_local.sh`)

**Optional**:
- `QDRANT_URL`: Qdrant server (default: `http://localhost:6333`)
- `USE_QDRANT`: Enable/disable (default: `true`; falls back to NanoVectorDB if false)
- `WORKING_DIR`: RAG storage directory (default: `./rag_storage`)

## Documentation References

Read these files to understand the system:

1. **`docs/lenny-prd.md`** — Product overview: problem, users, journey, value proposition, gaps
2. **`docs/TECH_BREAKDOWN_lennyhub_rag.md`** — Technical deep-dive: stack, data flow, 8 key decisions, dependencies, testing assessment

These docs are **not meant for end-users**; they're architectural guides for developers and architects working on RAG systems.

## Extending or Modifying the System

### Adding New Transcripts
See `ADDING_TRANSCRIPTS.md` (mentioned in PRD but may not exist yet; check `data/` structure and `setup_rag.py` for the pattern).

### Replacing Components
Consult the **Dependency Map** in `TECH_BREAKDOWN_lennyhub_rag.md` before replacing:
- RAG-Anything (orchestration) — High cost to replace
- LightRAG (knowledge graph extraction) — High cost; core to system
- Qdrant (vector DB) — Medium cost; use NanoVectorDB for local alternative, cloud VectorDB for scaling
- OpenAI API (LLM + embeddings) — Medium cost; requires recomputing all embeddings and fine-tuning

### Custom Retrieval Strategies
Currently supports four modes (hybrid, local, global, naive). To add custom routing:
1. Extend LightRAG query interface (in `setup_rag.py` or via wrapper)
2. Update Streamlit UI if adding to web interface

### Monitoring & Debugging
- **Qdrant health**: `./status_qdrant.sh` or `curl http://localhost:6333/`
- **Vector store dashboard**: `http://localhost:6333/dashboard`
- **Knowledge graph**: Inspect `rag_storage/graph_chunk_entity_relation.graphml` (NetworkX-compatible)
- **Query logs**: Check Streamlit/CLI stdout for timing, source attribution, and retrieval mode used

## Conventions

- **Async patterns**: Use asyncio.Semaphore for concurrency control (see `setup_rag.py` parallel ingestion)
- **Error handling**: Log failures but don't stop batch (tracked in `kv_store_full_docs.json` for resume)
- **Config**: Use `.env` for secrets; `qdrant_config.py` for defaults
- **CLI interfaces**: Prefer `query_rag.py` (or variants) over direct Python imports when possible for simplicity

## What I Use Claude Code For

- Updating and refining documentation (`lenny-prd.md`, `TECH_BREAKDOWN_lennyhub_rag.md`)
- Writing setup guides and troubleshooting docs
- Analyzing and extending RAG system components
- Improving Streamlit UI and CLI tools
- Optimizing ingestion performance and error handling