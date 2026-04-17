"""
HTTP server for knowledge graph visualization.
Serves graph_viewer_simple.html at http://localhost:8000
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import subprocess

# Check if graph_data.json exists, if not try to export it
def ensure_graph_data_exists():
    """Generate graph_data.json if it doesn't exist."""
    if Path("graph_data.json").exists():
        return True

    print("graph_data.json not found. Generating from GraphML...")

    try:
        # Try to export from GraphML
        import export_graph
        success = export_graph.export_graphml_to_json(
            "rag_storage/graph_chunk_entity_relation.graphml",
            "graph_data.json"
        )
        return success
    except Exception as e:
        print(f"Error generating graph_data.json: {e}")
        return False


class GraphHTTPHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler with CORS headers."""

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_GET(self):
        # Serve graph_viewer_simple.html for root
        if self.path == "/":
            self.path = "/graph_viewer_simple.html"
        return super().do_GET()


def main():
    port = 8000

    # Ensure graph data exists
    if not ensure_graph_data_exists():
        print("Could not generate graph_data.json")
        print("Make sure to run: python setup_rag.py --quick")
        sys.exit(1)

    # Create HTTP server
    server_address = ("localhost", port)
    httpd = HTTPServer(server_address, GraphHTTPHandler)

    url = f"http://localhost:{port}/graph_viewer_simple.html"

    print("=" * 60)
    print("Knowledge Graph Viewer")
    print("=" * 60)
    print(f"Server running at {url}")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    # Open in browser
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser: {e}")
        print(f"Open manually: {url}")

    # Start server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped")
        httpd.server_close()
        sys.exit(0)


if __name__ == "__main__":
    main()
