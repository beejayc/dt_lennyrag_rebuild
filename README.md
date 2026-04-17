# LennyHub RAG: Knowledge Graph Search for Podcast Transcripts

**Search 297 Lenny's Podcast episodes with AI-powered retrieval and source attribution.**

A production-grade Retrieval-Augmented Generation (RAG) system that lets you ask natural language questions about podcast content and get answers backed by direct quotes and episode references.

## What This Does

Instead of manually searching transcripts or listening to episodes, ask a question and get:
- **Direct answers** synthesized from relevant content
- **Source attribution** showing which episodes contain the relevant information
- **Knowledge graph context** revealing connections between concepts across episodes

### Example Queries
- "What is a curiosity loop and how does it work?"
- "What frameworks did [guest] mention for product strategy?"
- "Which episodes discuss network effects?"

## Why This Matters

Podcast content is dense and hard to search. A single episode can contain multiple guests, frameworks, and case studies across 1–2 hours of audio. **LennyHub RAG** transforms 297 episodes (≈600 hours of content) into a queryable knowledge base.

**Use cases:**
- **Researchers** — Find references and frameworks across episodes
- **Product managers** — Discover relevant case studies and guest advice
- **Designers** — Search for usability, growth, and strategy insights
- **Founders** — Mine the archive for specific advice or examples

## How It Works (High Level)

```
Your Question
     ↓
[Semantic Search] → Find relevant transcript chunks
     ↓
[Knowledge Graph] → Extract connected concepts and entities
     ↓
[AI Synthesis]   → Generate answer with sources
     ↓
Answer + Episode References
```

**Behind the scenes:**
1. **Ingestion**: 297 podcast transcripts are chunked and analyzed to extract entities (people, concepts, frameworks) and relationships between them
2. **Storage**: A knowledge graph and vector database store both semantic meaning and explicit connections
3. **Query**: Your question is matched against the graph and vector index to find relevant context
4. **Synthesis**: An AI model generates a natural language answer and cites sources

## Getting Started

### Prerequisites
- **Python 3.11+** 
- **Azure OpenAI API key** (for GPT-4o-mini and embeddings)
- **Transcript data** (297 `.txt` files of Lenny's Podcast episodes)
- **~2 GB disk space** for the indexed knowledge base

### Quick Start (5 minutes)

1. **Clone and setup**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your Azure OpenAI API key
   ```

2. **Start the vector database**
   ```bash
   ./start_qdrant.sh
   curl http://localhost:6333/  # Verify it's running
   ```

3. **Index the transcripts** (first run takes 25–35 minutes)
   ```bash
   python setup_rag.py --parallel --workers 5
   ```

4. **Query via web UI**
   ```bash
   ./run_streamlit.sh
   # Opens http://localhost:8501
   ```

### Using the System

**Web UI (recommended for exploring):**
```bash
./run_streamlit.sh
```
- Query tab: Ask questions and see answers with sources
- Stats tab: View knowledge graph metrics
- Transcript browser: Explore raw transcript content

**Command line:**
```bash
# Single query
python query_rag.py "What is a curiosity loop?"

# Interactive mode
python query_rag.py --interactive

# With detailed source attribution
python query_with_sources.py "Your question here"
```

**Knowledge graph visualization:**
```bash
python serve_graph.py
# Opens http://localhost:8000 — explore 544 people/concepts and their connections
```

## Features

- **Semantic search** — Find relevant content even if exact words don't match
- **Knowledge graph** — See connections between concepts, people, and frameworks across episodes
- **Source attribution** — Know which episodes contributed to each answer
- **Multiple retrieval modes** — Hybrid (default), local (entity-focused), global (relationship-focused), or naive (vector similarity)
- **Cost-efficient** — Full indexing costs ~$7.20 with response caching
- **Offline-capable** — All components run locally; no external dependencies beyond Azure OpenAI API calls

## Architecture at a Glance

| Component | Purpose | Technology |
|-----------|---------|------------|
| **RAG Framework** | Document ingestion & chunking | RAG-Anything ≥1.2.9 |
| **Knowledge Graph** | Entity extraction & relationships | LightRAG ≥1.4.9 |
| **Vector Database** | Semantic search & retrieval | Qdrant ≥1.16 (local) |
| **Embeddings & Synthesis** | AI-powered answers | Azure OpenAI (GPT-4o-mini, text-embedding-3-small) |
| **Web UI** | Interactive query interface | Streamlit ≥1.28.0 |

**Key design decisions** (see [TECH_BREAKDOWN_lennyhub_rag.md](docs/TECH_BREAKDOWN_lennyhub_rag.md) for details):
- Local Qdrant for production-grade vector search without Docker
- Parallel async ingestion for 5–10× speedup
- Subprocess isolation in Streamlit to avoid event loop conflicts
- Dual representation (vector + graph) for flexible retrieval

## Documentation

- **[CLAUDE.md](CLAUDE.md)** — Developer guide: setup, commands, architecture, extending the system
- **[docs/lenny-prd.md](docs/lenny-prd.md)** — Product analysis: problem, users, value proposition
- **[docs/TECH_BREAKDOWN_lennyhub_rag.md](docs/TECH_BREAKDOWN_lennyhub_rag.md)** — Technical deep-dive: 8 key decisions, dependencies, performance considerations

## Troubleshooting

**Qdrant won't start:**
```bash
./start_qdrant.sh
curl http://localhost:6333/  # Should return HTTP 200
```

**Azure OpenAI auth fails:**
- Verify `.env` has correct API key, endpoint, and API version
- Check Azure account has quota available

**Indexing is slow or times out:**
- Reduce worker count: `python setup_rag.py --parallel --workers 2`
- Azure OpenAI has rate limits; smaller batches help

**Streamlit query hangs:**
- Check system logs for errors
- Qdrant or Azure OpenAI may be throttling; restart and retry

See [CLAUDE.md](CLAUDE.md) for more troubleshooting and performance tuning.

## Performance

- **Indexing**: 25–35 minutes (parallel, 5 workers) for 297 transcripts
- **Query latency**: 1–3 seconds (includes vector lookup + AI synthesis)
- **Cost**: ~$7.20 for full indexing (with response caching)
- **Storage**: ~1.5 GB for vector index + knowledge graph

## What's Included vs. Not Included

**Included:**
- ✅ RAG system code and setup scripts
- ✅ Architecture and design documentation
- ✅ Web UI and CLI tools
- ✅ Knowledge graph export utilities

**Not included:**
- ❌ Podcast transcripts (obtain from data owner)
- ❌ Azure OpenAI account (you provide your own)
- ❌ Pre-built vector index (generated during setup)

## For Developers

This is both a **working system** (production-ready RAG pipeline) and a **reference architecture** (documented for building similar systems).

- **To use it**: Follow "Getting Started" above
- **To extend it**: See [CLAUDE.md](CLAUDE.md) for development commands and architecture
- **To understand design choices**: See [docs/TECH_BREAKDOWN_lennyhub_rag.md](docs/TECH_BREAKDOWN_lennyhub_rag.md)

## Support

For issues, questions, or improvements:
1. Check [CLAUDE.md](CLAUDE.md) troubleshooting section
2. Review [docs/TECH_BREAKDOWN_lennyhub_rag.md](docs/TECH_BREAKDOWN_lennyhub_rag.md) for design context
3. Check application logs (Streamlit/CLI output includes detailed error messages)

---

**Built by**: Schaeffler Data Science Solutions Team  
**Status**: Production-ready (tested with 297 podcast episodes)  
**Last updated**: April 2026