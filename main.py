# main.py
import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv # To explicitly load .env
import json # Used for error display if AI logic fails on startup

# Import functions from our modular files
from styling import apply_base_styles
from ai_logic import ask_gemini_text, ask_gemini_structured # Import specific AI functions
from features import render_code_input_section, render_lineage_output, render_footer
from additional_features import render_download_section, render_clear_button
from lineage_visualizer import render_lineage_graph # Import graph rendering function


# --- Page Configuration ---
st.set_page_config(
    page_title="Data Lineage Mapper",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State for Dark Mode Toggle ---
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = True # Default to dark mode


# --- Apply Custom Styling ---
# Pass the dark_mode state to the styling function
apply_base_styles(dark_mode=st.session_state['dark_mode'])


# --- Load Environment Variables ---
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

# --- API Key Check and Model Initialization Status ---
api_key_set = os.getenv("GEMINI_API_KEY") is not None and os.getenv("GEMINI_API_KEY") != "YOUR_ACTUAL_GEMINI_API_KEY_HERE"

if not api_key_set:
    st.warning("🚨 **Google Gemini API Key** not found or is the placeholder! "
               "AI features will not work.")
    st.info("💡 Please set your `GEMINI_API_KEY` in a `.env` file in your project root "
            "(`GEMINI_API_KEY=\"YOUR_API_KEY\"`) or as an environment variable.")
    st.stop()


# --- Session State Initialization (for lineage data) ---
if 'lineage_text_output' not in st.session_state:
    st.session_state['lineage_text_output'] = ""
if 'structured_lineage_data' not in st.session_state:
    st.session_state['structured_lineage_data'] = {}


# --- Title and Introduction ---
st.title("🔗 Data Lineage Mapper")

# --- Dark Mode Toggle ---
# Place the toggle in a small column at the top right, or using sidebar for better placement
st.session_state['dark_mode'] = st.toggle(
    label="🌙 Dark Mode / ☀️ Light Mode",
    value=st.session_state['dark_mode'],
    key="dark_mode_toggle"
)
# Re-apply styles if toggle state changes
# This will cause a rerun of the script with the new theme
if st.session_state['dark_mode'] != st.session_state.get('_prev_dark_mode_state', st.session_state['dark_mode']):
    st.session_state['_prev_dark_mode_state'] = st.session_state['dark_mode']
    st.rerun()

st.markdown("---")
st.write(
    "Welcome to the **Intelligent Data Lineage Mapper**! "
    "This tool leverages **Google Gemini AI** to automatically map column-level data lineage "
    "from your ETL SQL scripts and pipeline code. "
    "Gain clarity on data flow, accelerate debugging, and enhance compliance without manual tracing. "
    "Just paste your code and let AI do the heavy lifting! ✨"
)
st.markdown("---")

# --- Render Input Section ---
current_etl_code_input = render_code_input_section()

# --- Process Button ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("✨ Map Data Lineage", type="primary", use_container_width=True, key="map_lineage_button"):
    if current_etl_code_input.strip():
        # Clear previous output before showing spinner to prevent overlap
        st.session_state['lineage_text_output'] = ""
        st.session_state['structured_lineage_data'] = {}
        
        # Moved st.subheader inside the spinner context
        with st.spinner("Generating Lineage Map... Please wait ⏳ AI is analyzing your code and mapping data flows and graph data..."):
            # Prompt for TEXT-BASED lineage report - UPDATED FOR DIFFERENT FORMAT AND TRANSFORMATION SUMMARY
            text_prompt = f"""
            As an expert Data Engineer, your task is to analyze the provided ETL code or SQL script.
            Identify and extract **column-level data lineage**, describing the flow of data from its sources through transformations to its final targets.

            For each target table and column, provide a concise narrative or flow description of how the data for that column is derived.
            Clearly mention the source columns and the transformations applied.

            Structure the report as follows in Markdown:

            ## Data Flow Summary
            [A brief, high-level summary of the overall data movement and purpose of the script.]

            ## Detailed Column-Level Lineage

            ### Target Table: `[Target Table Name]`
            * **`[Target Column Name 1]`**: Derived from `[Source Table.Column(s)]` using transformation `[Description of Transformation]`.
                * Example: **`fact_sales.total_amount`**: Derived from `staging.sales.units` and `raw_data.products.price` by multiplying `units` by `price` after an inner join, then aggregated by `SUM()`.
            * **`[Target Column Name 2]`**: Directly mapped from `[Source Table.Column]`.
                * Example: **`fact_sales.sale_id`**: Directly mapped from `staging.sales.id`.
            * ...

            ### Target Table: `[Another Target Table Name]`
            * ...

            ## Key Dependencies and Transformations
            [A brief narrative summarizing common joins, filtering, or complex transformations that are critical to the data flow.]

            ## Transformation Summary
            List all distinct types of transformations detected in the ETL code (e.g., `JOIN`, `SUM()`, `CAST`, `CASE WHEN`, `GROUP BY`, `LAG`, `COALESCE`, `FILTER`, `SELECT`, `MERGE`, `UNION`).

            ---

            If you cannot extract lineage, state "❌ Lineage extraction failed: [Reason]".
            
            **ETL Code/SQL Script:**
            ```
            {current_etl_code_input}
            ```
            """
            
            # Prompt for STRUCTURED JSON lineage for graph visualization - UPDATED FOR CONFIDENCE SCORE
            structured_prompt = f"""
            As an expert Data Engineer, your task is to analyze the provided ETL code or SQL script and extract **column-level data lineage** in a structured JSON format suitable for a graph database or visualization.

            Represent each table and column as a **node**.
            Represent lineage relationships (data flow) and transformations as **edges**.

            Node Types (groups):
            - `table`: Represents a database table.
            - `column`: Represents a column within a table.
            - `transformation`: Represents a data transformation operation.

            Edge Types (labels):
            - `FLOWS_TO`: From source column to target column.
            - `PRODUCES`: From transformation node to target column.
            - `CONSUMES`: From source column to transformation node.
            - `IS_PART_OF`: From column node to table node.

            For each edge representing a `FLOWS_TO`, `PRODUCES`, or `CONSUMES` relationship, also provide a `confidence_score` (integer, from 1 to 5) indicating your certainty that the lineage or transformation step is correctly identified.
            - 5: Highly confident, directly mapped or clearly defined transformation.
            - 4: Confident, clear transformation but might involve implicit logic.
            - 3: Moderately confident, inferred transformation, minor ambiguities possible.
            - 2: Low confidence, heavily inferred, significant ambiguities or complex logic.
            - 1: Very low confidence, highly ambiguous or speculative mapping.

            Provide the output as a JSON object with two main arrays: `nodes` and `edges`.

            **Node Object Structure:**
            `{{ "id": "unique_id_string", "label": "display_name", "group": "table" | "column" | "transformation", "title": "tooltip_text" }}`
            - `id`: A unique identifier (e.g., `schema.table.column`, `table_name`, `transform_hash`).
            - `label`: Display name (e.g., `column_name`, `table_name`, `SUM_transform`).
            - `group`: Categorization for styling (e.g., `table`, `column`, `transformation`).
            - `title`: Optional detailed tooltip for the node.

            **Edge Object Structure:**
            `{{ "source": "source_node_id", "target": "target_node_id", "label": "edge_type", "title": "tooltip_text_for_edge", "confidence_score": 1-5 (optional for IS_PART_OF) }}`
            - `source`: ID of the source node.
            - `target`: ID of the target node.
            - `label`: Type of relationship (e.g., `FLOWS_TO`, `PRODUCES`, `CONSUMES`, `IS_PART_OF`).
            - `title`: Optional detailed tooltip for the edge (e.g., `Transformation: SUM(amount)`).
            - `confidence_score`: (integer, 1-5) Confidence in this specific lineage connection. Only for `FLOWS_TO`, `PRODUCES`, `CONSUMES` edges.

            **Example Structure for JSON Output (with confidence_score):**
            ```json
            {{
                "nodes": [
                    {{"id": "raw.transactions", "label": "transactions", "group": "table"}},
                    {{"id": "raw.transactions.transaction_timestamp", "label": "transaction_timestamp", "group": "column", "title": "Source Column"}},
                    {{"id": "analytics.daily_product_sales", "label": "daily_product_sales", "group": "table"}},
                    {{"id": "analytics.daily_product_sales.sale_date", "label": "sale_date", "group": "column", "title": "Target Column"}},
                    {{"id": "transform_date_trunc", "label": "DATE_TRUNC", "group": "transformation", "title": "Transformation: Extract Month"}},
                    {{"id": "raw.transactions.quantity", "label": "quantity", "group": "column"}},
                    {{"id": "ref.products.unit_price", "label": "unit_price", "group": "column"}},
                    {{"id": "transform_gross_revenue", "label": "SUM(quantity * unit_price)", "group": "transformation"}},
                    {{"id": "analytics.daily_product_sales.gross_revenue", "label": "gross_revenue", "group": "column"}}
                ],
                "edges": [
                    {{"source": "raw.transactions.transaction_timestamp", "target": "transform_date_trunc", "label": "CONSUMES", "title": "Input for DATE_TRUNC", "confidence_score": 5}},
                    {{"source": "transform_date_trunc", "target": "analytics.daily_product_sales.sale_date", "label": "PRODUCES", "title": "Result of DATE_TRUNC", "confidence_score": 5}},
                    {{"source": "raw.transactions.quantity", "target": "transform_gross_revenue", "label": "CONSUMES", "confidence_score": 4}},
                    {{"source": "ref.products.unit_price", "target": "transform_gross_revenue", "label": "CONSUMES", "confidence_score": 4}},
                    {{"source": "transform_gross_revenue", "target": "analytics.daily_product_sales.gross_revenue", "label": "PRODUCES", "title": "Result of SUM(quantity * unit_price)", "confidence_score": 4}},
                    {{"source": "raw.transactions.transaction_timestamp", "target": "raw.transactions", "label": "IS_PART_OF"}},
                    {{"source": "analytics.daily_product_sales.sale_date", "target": "analytics.daily_product_sales", "label": "IS_PART_OF"}}
                ]
            }}
            ```

            **ETL Code/SQL Script to Analyze:**
            ```
            {current_etl_code_input}
            ```

            Please ensure your response is *only* the JSON object defined by the schema, with no additional text or markdown outside the JSON.
            If lineage cannot be extracted, return: `{{ "nodes": [], "edges": [], "error": "Could not extract lineage." }}`
            """
            
            # Define the JSON schema for structured output expected from AI - UPDATED: REMOVED minimum/maximum
            response_schema = {
                "type": "object",
                "properties": {
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "label": {"type": "string"},
                                "group": {"type": "string", "enum": ["table", "column", "transformation"]},
                                "title": {"type": "string"}
                            },
                            "required": ["id", "label", "group"]
                        }
                    },
                    "edges": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source": {"type": "string"},
                                "target": {"type": "string"},
                                "label": {"type": "string", "enum": ["FLOWS_TO", "PRODUCES", "CONSUMES", "IS_PART_OF"]},
                                "title": {"type": "string"},
                                "confidence_score": {"type": "integer"} # Removed minimum and maximum constraints
                            },
                            "required": ["source", "target", "label"]
                        }
                    },
                    "error": {"type": "string"}
                },
                "required": ["nodes", "edges"]
            }

            # Make both AI calls in parallel or sequential based on preference. Sequential for clarity here.
            st.session_state['lineage_text_output'] = ask_gemini_text(text_prompt)
            st.session_state['structured_lineage_data'] = ask_gemini_structured(structured_prompt, response_schema)
            
            # Check if structured data has an error from AI
            if st.session_state['structured_lineage_data'].get("error"):
                st.session_state['lineage_text_output'] += f"\n\n---\n\n❌ **Graph Generation Issue:** {st.session_state['structured_lineage_data']['error']}\n\n" \
                                                          "The AI struggled to provide data for the interactive graph. " \
                                                          "Please review the text report and consider simplifying the input for graph generation."

    else:
        st.warning("Please paste some ETL code or SQL script to analyze.")

# --- Display Output Section with Tabs (Conditional Rendering) ---
# Only display this section if there's actual lineage data generated
if st.session_state['lineage_text_output'] or st.session_state['structured_lineage_data']:
    st.markdown("---")
    st.header("Mapped Data Lineage")

    # Create tabs for different views
    tab_text_report, tab_graph_view = st.tabs(["📄 Text Report", "🌐 Graph View"])

    with tab_text_report:
        render_lineage_output(st.session_state['lineage_text_output'])

    with tab_graph_view:
        render_lineage_graph(st.session_state['structured_lineage_data'])

    # --- Additional Features (Download & Clear) ---
    st.markdown("---")
    render_download_section(st.session_state['structured_lineage_data'], st.session_state['lineage_text_output'])
    render_clear_button()

# --- Footer ---
render_footer()