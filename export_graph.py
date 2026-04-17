"""
Export GraphML knowledge graph to JSON for D3.js visualization.
"""

import json
import sys
from pathlib import Path
from typing import Optional

try:
    import networkx as nx
except ImportError:
    print("Error: networkx is required")
    sys.exit(1)


def export_graphml_to_json(graphml_path: str, output_path: str = "graph_data.json") -> bool:
    """
    Convert GraphML to JSON suitable for D3.js visualization.

    Args:
        graphml_path: Path to GraphML file
        output_path: Output JSON file path

    Returns:
        True if successful, False otherwise
    """
    graphml_file = Path(graphml_path)

    if not graphml_file.exists():
        print(f"GraphML file not found: {graphml_path}")
        return False

    print(f"Loading GraphML from {graphml_path}...")

    try:
        # Load GraphML
        G = nx.read_graphml(graphml_path)
        print(f"Loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

        # Convert to D3.js format
        nodes = []
        node_index = {}

        for i, (node_id, data) in enumerate(G.nodes(data=True)):
            node_index[node_id] = i
            node = {
                "id": node_id,
                "name": data.get("label", node_id),
                "type": data.get("type", "unknown"),
                "size": 10 + min(len(str(data.get("description", ""))), 100) / 10,
            }
            nodes.append(node)

        edges = []
        for source, target, data in G.edges(data=True):
            if source in node_index and target in node_index:
                edge = {
                    "source": node_index[source],
                    "target": node_index[target],
                    "type": data.get("type", "unknown"),
                    "weight": data.get("weight", 1),
                }
                edges.append(edge)

        # Create D3.js compatible structure
        d3_data = {
            "nodes": nodes,
            "links": edges,
        }

        # Write JSON
        output_file = Path(output_path)
        with open(output_file, "w") as f:
            json.dump(d3_data, f, indent=2)

        print(f"✓ Exported to {output_path}")
        print(f"  {len(nodes)} nodes, {len(edges)} links")
        return True

    except Exception as e:
        print(f"Error exporting graph: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    # Try standard locations
    possible_paths = [
        "rag_storage/graph_chunk_entity_relation.graphml",
        "./rag_storage/graph_chunk_entity_relation.graphml",
    ]

    graphml_path = None
    for path in possible_paths:
        if Path(path).exists():
            graphml_path = path
            break

    if not graphml_path:
        print("GraphML file not found in standard locations:")
        for path in possible_paths:
            print(f"  - {path}")
        sys.exit(1)

    success = export_graphml_to_json(graphml_path, "graph_data.json")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
