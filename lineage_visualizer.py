# lineage_visualizer.py
import streamlit as st
import networkx as nx
from pyvis.network import Network
import base64 # For embedding HTML directly
import json # For structured data handling
import tempfile # For creating temporary files
import os # For path operations and cleanup

def render_lineage_graph(structured_lineage_data: dict):
    """
    Renders an interactive data lineage graph using Pyvis based on structured data.
    The structured_lineage_data is expected to be a dictionary with 'nodes' and 'edges'.
    """
    st.subheader("🌐 Interactive Lineage Graph")

    if not structured_lineage_data or structured_lineage_data.get("nodes") is None:
        st.info("No structured lineage data available to generate the graph. Please generate the lineage report first.")
        return

    # Check for errors in structured data
    if structured_lineage_data.get("error"):
        st.error(f"Error generating graph data from AI: {structured_lineage_data['error']}")
        st.info("The AI might have struggled to produce valid structured lineage. Try simplifying your code or review the AI's plain text explanation.")
        return

    try:
        # Create a NetworkX graph
        G = nx.DiGraph()

        # Add nodes
        for node_data in structured_lineage_data.get("nodes", []):
            node_id = node_data.get("id")
            label = node_data.get("label", node_id)
            group = node_data.get("group", "unknown") # Use group for different colors/shapes
            # Ensure proper JSON string for tooltip: escape newlines, and escape quotes if title contains them
            title_text = node_data.get("title", f"ID: {node_id}\\nType: {group}")
            title = json.dumps(title_text) # Ensures correct JSON string for the title attribute
            G.add_node(node_id, label=label, group=group, title=title)

        # Add edges
        for edge_data in structured_lineage_data.get("edges", []):
            source = edge_data.get("source")
            target = edge_data.get("target")
            label = edge_data.get("label", "")
            title_text = edge_data.get("title", label)
            title = json.dumps(title_text) # Ensures correct JSON string for the title attribute
            G.add_edge(source, target, title=title, label=label)

        # Initialize Pyvis Network
        # Set cdn_resources='remote' to ensure Pyvis loads its JS/CSS from a CDN
        net = Network(notebook=True, height="750px", width="100%", directed=True, cdn_resources='remote')
        
        # Configure physics for better layout and readability
        net.toggle_physics(True)
        # Apply custom options as a valid JSON string (all keys must be double-quoted, no comments)
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "barnesHut": {
                    "gravitationalConstant": -10000,
                    "centralGravity": 0.3,
                    "springLength": 200,
                    "springConstant": 0.03,
                    "damping": 0.15,
                    "avoidOverlap": 0.9
                },
                "maxVelocity": 50,
                "minVelocity": 0.75,
                "solver": "barnesHut"
            },
            "nodes": {
                "font": { 
                    "color": "#E6EDF3",
                    "face": "Inter",
                    "size": 16,
                    "strokeWidth": 4,
                    "strokeColor": "#1a202c"
                },
                "color": {
                    "border": "#4a5568",
                    "background": "#2d3748",
                    "highlight": { "border": "#63b3ed", "background": "#4299e1" },
                    "hover": { "border": "#63b3ed", "background": "#4299e1" }
                },
                "borderWidth": 2,
                "shapeProperties": {
                  "useImageSize": true
                }
            },
            "edges": {
                "color": { "color": "#a0aec0", "highlight": "#63b3ed", "hover": "#63b3ed" },
                "arrows": { "to": { "enabled": true, "scaleFactor": 0.8 } },
                "font": { 
                    "color": "#E6EDF3",
                    "face": "Inter",
                    "size": 12,
                    "strokeWidth": 2,
                    "strokeColor": "#1a202c",
                    "align": "middle"
                },
                "dashes": false,
                "width": 1.5
            },
            "groups": {
                "table": { "shape": "box", "color": "#58A6FF", "font": {"multi": false} },
                "column": { "shape": "dot", "color": "#3FB950", "font": {"multi": false} },
                "transformation": { "shape": "diamond", "color": "#DD9F1B", "font": {"multi": false} },
                "unknown": { "shape": "triangle", "color": "#768390", "font": {"multi": false} }
            },
            "interaction": {
                "hover": true,
                "navigationButtons": true,
                "zoomView": true
            }
        }
        """)

        net.from_nx(G)

        # Use a temporary file to save and then read the HTML content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            net.save_graph(tmp_file.name)
            tmp_file_path = tmp_file.name

        with open(tmp_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Clean up the temporary file
        os.remove(tmp_file_path)

        # Embed the HTML using an iframe
        html_base64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
        iframe_src = f"data:text/html;base64,{html_base64}"
        st.components.v1.iframe(iframe_src, height=750, scrolling=True)

    except Exception as e:
        st.error(f"Error rendering interactive graph: {e}")
        st.info("This might happen if the structured lineage data is malformed or graph library issues. Check console for details.")
        st.exception(e)

