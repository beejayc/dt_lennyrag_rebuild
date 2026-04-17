# LennyHub RAG — Product Analysis

## What This Product Does

LennyHub RAG lets you ask questions about 297 episodes of Lenny's Podcast and get AI-synthesized answers with source attribution. Instead of listening through hours of audio or searching transcripts, you query a knowledge graph of extracted concepts, people, and relationships, then get an answer grounded in specific episodes.

## The Problem It Solves

Lenny's Podcast contains valuable advice on product strategy, growth, leadership, and career development from top founders and executives—but that knowledge is scattered across 297 episodes. Finding specific frameworks, advice, or connections between guests requires manually rewinding through audio or grep-searching transcripts. This product makes the value immediately accessible and searchable.

## Target Audience

**Primary Users:**
- **Product managers** researching decision-making frameworks, product strategy, and lessons from successful companies
- **Growth professionals** studying onboarding, retention, and growth loops from industry leaders
- **Founders and early-stage leaders** seeking tactical advice on startup challenges, team building, and hiring
- **Career developers** exploring decision-making frameworks, values exercises, and leadership principles
- **Researchers and content creators** building on ideas from the podcast or cross-referencing expert opinions

These users want structured knowledge from the podcast but don't have time to listen end-to-end. They value **quick retrieval, source attribution, and connection discovery** (seeing who mentioned what and how concepts relate).

## Core User Journey

1. **Arrive**: Open Streamlit web app or run CLI command
2. **Ask**: Type a question ("What is the growth competency model?" or "How should I think about career transitions?")
3. **Discover**: Choose search mode (hybrid recommended for balance, naive for speed, local for specific entities, global for context)
4. **Read**: Get synthesized answer with quoted sources and episode references
5. **Explore**: Optionally view the interactive network graph to see how people and concepts connect (544 people from transcripts)
6. **Iterate**: Ask follow-up questions (each query is independent; no conversation history)

## Value Proposition

Instant access to expert advice from 297 hours of high-quality interviews without manual searching. The knowledge graph makes implicit connections explicit—you don't just find an answer, you see who mentioned it and how it relates to other concepts.

## Tech Stack (Brief)

- **LightRAG** → Extracts entities and relationships from raw transcripts; creates the underlying knowledge graph
- **Qdrant** (local, no Docker) → Stores embeddings for semantic search across entities, relationships, and text chunks in a production-grade vector database
- **AzureOpenAI (GPT-4.1-mini + text-embedding-ada-002)** → Powers entity extraction (small model for cost) and LLM synthesis; embeddings create the semantic space for search
- **Streamlit** → Chosen for ease of deployment and interactive UX (eliminates friction of CLI-only access)
- **RAG-Anything** → High-level framework that orchestrates the above; handles chunking, parallel processing, and search routing

## Product Gaps & Open Questions

1. **No conversation context** — Each query is independent; multi-turn follow-ups don't maintain context (e.g., "Tell me more" requires re-querying with full context)
2. **Search modes are preset** — Users can't customize relevance weights, chunk size, or graph traversal depth; limited control over retrieval strategy
3. **Knowledge base is static** — Podcast-specific; no mechanism for users to add their own transcripts or sources (though `ADDING_TRANSCRIPTS.md` suggests this is possible for power users)
4. **No curation or export** — No way to save findings, annotate, or export research summaries as documents
5. **Graph visualization is limited to people** — You see the network of who knows whom, but not entity-to-entity relationships in the interactive view (those are only in answers)
6. **Sparse documentation on quality trade-offs** — Unclear when to choose which search mode beyond "hybrid is best"; no guidance on accuracy vs. latency
7. **Likely assumes high API familiarity for on-premise deployment** — Setup instructions are clear, but extending the system (custom embeddings, different LLMs, private deployments) may be complex

## One-Line Summary

A local knowledge graph search engine over 297 Lenny's Podcast episodes that answers questions with episode sources and visualizes the network of guests and their connections.
