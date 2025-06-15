# additional_features.py
import streamlit as st
import json
from io import StringIO, BytesIO # For in-memory file operations for downloads

def render_download_section(lineage_data_structured, lineage_text_report):
    """
    Renders the download section for the generated lineage data.
    Allows downloading structured JSON and a full Markdown report.
    """
    st.subheader("💾 Download Lineage Report")

    if lineage_data_structured and lineage_text_report:
        col1, col2 = st.columns(2)

        with col1:
            # Download as Markdown
            st.download_button(
                label="⬇️ Download Markdown Report",
                data=lineage_text_report.encode('utf-8'),
                file_name="data_lineage_report.md",
                mime="text/markdown",
                use_container_width=True,
                key="download_md_report"
            )

        with col2:
            # Download as JSON (structured lineage data)
            json_data = json.dumps(lineage_data_structured, indent=2).encode('utf-8')
            st.download_button(
                label="⬇️ Download Structured JSON",
                data=json_data,
                file_name="data_lineage_structured.json",
                mime="application/json",
                use_container_width=True,
                key="download_json_report"
            )
    else:
        st.info("Generate lineage data first to enable download options.")

def render_clear_button():
    """
    Renders a button to clear all application state and rerun.
    """
    st.markdown("---")
    if st.button("🔄 Clear All Inputs & Results", type="secondary", use_container_width=True, key="clear_all_button"):
        # Clear session state variables
        if 'etl_code_input' in st.session_state:
            del st.session_state.etl_code_input
        if 'lineage_result' in st.session_state:
            del st.session_state.lineage_result
        if 'structured_lineage_data' in st.session_state:
            del st.session_state.structured_lineage_data
        
        # Rerun the app to reflect the cleared state
        st.rerun()

