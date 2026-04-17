"""
Streamlit web UI for LennyHub RAG system.
Provides query interface, system health, and transcript browser.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from qdrant_config import check_qdrant_running, get_qdrant_client, get_collection_stats, QDRANT_URL

# Page config
st.set_page_config(
    page_title="LennyHub RAG",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment
load_dotenv()

# Styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .query-box {
        border-left: 4px solid #ff6b6b;
        padding: 1rem;
        margin: 1rem 0;
        background: #f8f9fa;
    }
    .stats-box {
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


def run_query_worker(query: str, mode: str = "hybrid") -> dict:
    """Run query in subprocess to avoid event loop conflicts."""
    try:
        result = subprocess.run(
            [sys.executable, "query_worker.py", query, mode],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {
                "success": False,
                "error": result.stderr or "Unknown error",
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Query timeout (60s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎙️ LennyHub RAG")
        st.caption("Search across 297 Lenny's Podcast episodes with AI")

    with col2:
        # Status indicator
        qdrant_running = check_qdrant_running(QDRANT_URL)
        if qdrant_running:
            st.success("✓ Online", icon="🟢")
        else:
            st.error("✗ Offline", icon="🔴")

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        retrieval_mode = st.selectbox(
            "Retrieval Mode",
            ["hybrid", "local", "global", "naive"],
            help="""
            - **Hybrid**: Combines multiple retrieval strategies (default)
            - **Local**: Entity-focused retrieval
            - **Global**: Relationship-aware traversal
            - **Naive**: Direct similarity search
            """,
        )

        st.divider()

        # Sample questions
        st.subheader("Sample Questions")
        samples = [
            "What is a curiosity loop?",
            "How do successful founders think about growth?",
            "What is product market fit?",
            "How do you build trust with customers?",
            "What makes a good product?",
        ]

        for sample in samples:
            if st.button(sample, key=sample):
                st.session_state.query_input = sample

    # Main tabs
    tab1, tab2, tab3 = st.tabs(["Query", "System Health", "Transcript Browser"])

    # TAB 1: QUERY
    with tab1:
        st.subheader("Ask a Question")

        # Initialize session state
        if "query_input" not in st.session_state:
            st.session_state.query_input = ""

        query = st.text_input(
            "Question",
            value=st.session_state.query_input,
            placeholder="Ask anything about the podcasts...",
            key="query_text",
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)

        if search_button and query:
            with st.spinner("Searching podcasts..."):
                start_time = time.time()

                result = run_query_worker(query, mode=retrieval_mode)

                elapsed = time.time() - start_time

            if result.get("success"):
                st.markdown("<div class='query-box'>", unsafe_allow_html=True)

                st.markdown("**Response:**")
                st.write(result.get("result", "No response"))

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Time", f"{elapsed:.2f}s")
                with col2:
                    st.metric("Mode", retrieval_mode.capitalize())
                with col3:
                    st.metric("Query", f"{len(query)} chars")

                st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")

    # TAB 2: SYSTEM HEALTH
    with tab2:
        st.subheader("System Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            if qdrant_running:
                st.success("Qdrant", icon="✓")
            else:
                st.error("Qdrant", icon="✗")

        with col2:
            data_dir = Path("data")
            if data_dir.exists():
                file_count = len(list(data_dir.glob("*.txt")))
                st.info(f"Transcripts: {file_count}")
            else:
                st.warning("No data directory")

        with col3:
            storage_dir = Path("rag_storage")
            if storage_dir.exists():
                st.success(f"Storage: Ready")
            else:
                st.warning("Storage: Empty")

        st.divider()

        # Collection stats
        if qdrant_running:
            st.subheader("Collections")

            try:
                client = get_qdrant_client(QDRANT_URL)
                stats = get_collection_stats(client)

                if stats:
                    for collection_name, info in stats.items():
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                f"{collection_name}",
                                info.get("points_count", "?"),
                                help=f"Status: {info.get('status', 'unknown')}"
                            )
                        with col2:
                            st.metric("Vectors", info.get("vectors_count", "?"))
                        with col3:
                            if "error" in info:
                                st.error("Error")
                else:
                    st.info("No collections created yet. Run setup_rag.py to index transcripts.")

            except Exception as e:
                st.error(f"Could not fetch stats: {e}")
        else:
            st.warning("Start Qdrant with: `./start_qdrant.sh`")

        st.divider()

        # Quick actions
        st.subheader("Quick Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🎬 Start Qdrant", use_container_width=True):
                with st.spinner("Starting Qdrant..."):
                    os.system("./start_qdrant.sh > /dev/null 2>&1 &")
                    time.sleep(2)
                    st.rerun()

        with col2:
            if st.button("📊 View Dashboard", use_container_width=True):
                st.info("Open: http://localhost:6333/dashboard")

        with col3:
            if st.button("🧠 View Graph", use_container_width=True):
                st.info("Run: `python serve_graph.py`")

    # TAB 3: TRANSCRIPT BROWSER
    with tab3:
        st.subheader("Podcast Transcripts")

        data_dir = Path("data")

        if not data_dir.exists():
            st.warning("Data directory not found")
        else:
            files = sorted(data_dir.glob("*.txt"))

            if not files:
                st.info("No transcripts found")
            else:
                st.caption(f"Total: {len(files)} episodes")

                # Searchable list
                search_term = st.text_input("Filter by guest name")

                filtered_files = [
                    f for f in files
                    if search_term.lower() in f.stem.lower()
                ]

                for file in filtered_files[:20]:  # Show first 20
                    with st.expander(f"🎙️ {file.stem}"):
                        try:
                            with open(file) as f:
                                content = f.read()
                                lines = content.split("\n")

                                # Show first 20 lines
                                preview = "\n".join(lines[:20])
                                st.text(preview)

                                if len(lines) > 20:
                                    st.caption(f"... ({len(lines) - 20} more lines)")

                        except Exception as e:
                            st.error(f"Could not read file: {e}")

                if len(filtered_files) > 20:
                    st.caption(f"... and {len(filtered_files) - 20} more")


if __name__ == "__main__":
    # Verify Qdrant is running
    if not check_qdrant_running(QDRANT_URL):
        st.warning(
            f"""
            ⚠️ Qdrant is not running at {QDRANT_URL}

            Start it with:
            ```bash
            ./start_qdrant.sh
            ```

            Or install it first:
            ```bash
            ./install_qdrant_local.sh
            ```
            """
        )

    main()
