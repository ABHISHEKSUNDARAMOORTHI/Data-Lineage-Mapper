# features.py
import streamlit as st
from streamlit_ace import st_ace # New import for syntax highlighting
import json # For handling JSON schema in features.py
# UPDATED: Import ask_gemini_text and ask_gemini_structured
from ai_logic import ask_gemini_text, ask_gemini_structured
# Import utility functions for schema operations, these would be in schema_utils.py
# Assuming schema_utils.py exists and contains these functions for "Auto Schema Recognition"
# from schema_utils import strip_sql_comments_and_normalize, parse_create_table_statement, compare_schemas


def render_code_input_section():
    """
    Renders the user input text area for ETL code/SQL scripts,
    now with syntax highlighting using st_ace.
    It returns the content entered by the user.
    """
    st.header("📝 Paste Your ETL Code/SQL Here")
    st.markdown("Easily map column-level lineage by pasting your SQL queries, PySpark snippets, DBT models, or Airflow code. Our AI will analyze the data flow.")

    # Use st_ace for syntax highlighting.
    # We'll make it intelligent by letting the user choose the language,
    # or default to SQL for the example.
    
    # Placeholder content - keep it rich for demonstration
    placeholder_code = """
-- SQL Example: Revenue Aggregation and Customer Segmentation
WITH MonthlyRevenue AS (
    SELECT
        DATE_TRUNC('month', o.order_date) AS sales_month,
        c.customer_id,
        SUM(o.amount) AS monthly_order_value,
        COUNT(DISTINCT o.order_id) AS distinct_orders
    FROM
        ecommerce_raw.orders o
    JOIN
        ecommerce_raw.customers c ON o.customer_id = c.id
    WHERE
        o.order_status = 'COMPLETED'
    GROUP BY
        1, 2
),
CustomerSegments AS (
    SELECT
        mr.sales_month,
        mr.customer_id,
        mr.monthly_order_value,
        CASE
            WHEN mr.monthly_order_value >= 1000 THEN 'High Value'
            WHEN mr.monthly_order_value BETWEEN 500 AND 999 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS customer_segment, -- Lineage: customer_segment derived from monthly_order_value
        LAG(mr.monthly_order_value, 1) OVER (PARTITION BY mr.customer_id ORDER BY mr.sales_month) AS previous_month_value -- Lineage: previous_month_value from monthly_order_value
    FROM
        MonthlyRevenue mr
)
INSERT INTO analytics_mart.customer_monthly_summary (
    reporting_month,
    customer_key,
    total_monthly_spend,
    segment,
    last_month_spend
)
SELECT
    cs.sales_month AS reporting_month,
    cs.customer_id AS customer_key,
    cs.monthly_order_value AS total_monthly_spend,
    cs.customer_segment AS segment,
    COALESCE(cs.previous_month_value, 0) AS last_month_spend
FROM
    CustomerSegments cs
WHERE
    cs.sales_month >= '2024-01-01';

---

# PySpark Example: Data Cleaning and Aggregation
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, when, lit, to_date

spark = SparkSession.builder.appName("ProductMetrics").getOrCreate()

# Load raw product and inventory data
df_raw_products = spark.read.json("s3://landing-zone/products_raw.json")
df_raw_inventory = spark.read.csv("s3://landing-zone/inventory_updates.csv", header=True, inferSchema=True)

# Clean and enrich product data
df_products_clean = df_raw_products.select(
    col("product_id").cast("string").alias("product_key"), # Lineage: product_key from product_id (raw)
    col("name").alias("product_name"),
    col("category_id").cast("int").alias("category_id_int"),
    when(col("is_active") == "true", True).otherwise(False).alias("is_active_flag") # Lineage: is_active_flag from is_active (raw)
).filter(col("product_key").isNotNull())

# Clean and enrich inventory data
df_inventory_clean = df_raw_inventory.select(
    col("product_ref").alias("product_key"),
    col("warehouse_location").alias("location"),
    col("stock_level").cast("int").alias("current_stock"),
    to_date(col("last_updated"), "yyyy-MM-dd").alias("update_date") # Lineage: update_date from last_updated (raw)
).filter(col("current_stock") > 0)

# Join and aggregate to get daily product insights
df_product_daily_metrics = df_products_clean.alias("p") \\
    .join(df_inventory_clean.alias("i"), col("p.product_key") == col("i.product_key"), "inner") \\
    .groupBy(col("p.product_key"), col("p.product_name"), col("i.update_date")) \\
    .agg(
        sum("i.current_stock").alias("total_stock_across_warehouses"), # Lineage: total_stock_across_warehouses from current_stock (inventory)
        count(col("i.location")).alias("num_warehouses_stocked") # Lineage: num_warehouses_stocked from location (inventory)
    )

# Write aggregated data to processed layer
df_product_daily_metrics.write.mode("overwrite").partitionBy("update_date").parquet("s3://processed-zone/daily_product_metrics/")

# End of script
"""

    # Allow user to select language for highlighting
    language_options = ["sql", "python"]
    selected_language = st.selectbox(
        "Select Code Language for Syntax Highlighting:",
        options=language_options,
        index=language_options.index("sql"), # Default to SQL
        key="code_language_select"
    )

    # Use st_ace for the code input
    etl_code_input = st_ace(
        value=placeholder_code, # Initial value is the placeholder example
        language=selected_language,
        theme="dracula", # A dark theme that fits the overall app style
        height=400, # Increased height for more code visibility
        font_size=14,
        tab_size=4,
        show_print_margin=False,
        wrap=True, # Enable word wrapping
        auto_update=True, # Update value in real-time
        key="etl_code_input" # Essential for session state management
    )
    return etl_code_input

def render_lineage_output(lineage_text_output: str):
    """
    Renders the AI-generated lineage map.
    """
    st.subheader("📊 Mapped Data Lineage")
    if lineage_text_output and not lineage_text_output.startswith("❌"): # Check for error prefix from AI logic
        # Apply the custom CSS class for better presentation
        st.markdown(f"<div class='lineage-display-box'>{lineage_text_output}</div>", unsafe_allow_html=True)
        st.success("Lineage mapping complete! 🎉 Your data flow insights are ready.")
    elif lineage_text_output.startswith("❌"):
        st.error(f"Failed to generate lineage map: {lineage_text_output}")
        st.info("Please ensure your API key is correctly configured and the input code is valid. If the issue persists, try simplifying the code snippet.")
    else:
        st.info("No lineage map generated yet. Paste your ETL code/SQL and click 'Map Data Lineage' to see results.")

def render_footer():
    """Renders a consistent footer for the application."""
    st.markdown("---")
    st.caption("🔗 Intelligent Data Lineage Mapper | Powered by Streamlit & Google Gemini API")

# This function will infer a structured schema from raw text input.
# This was part of the 'Auto Schema Recognition' feature
def ask_gemini_infer_structured_schema(raw_input_text: str) -> dict:
    """
    Asks Gemini to infer a structured schema (JSON) from raw text input.
    """
    prompt = f"""
    You are an expert Data Modeler and Database Engineer.
    Analyze the following raw text, which describes a database schema. This text can be SQL CREATE TABLE statements,
    JSON schema definitions, or even natural language descriptions of tables and columns.

    Your task is to infer a structured JSON schema from this text.
    The output JSON should be an array of table objects. Each table object should have:
    - `table_name`: (string) The name of the table.
    - `columns`: (array of objects) Each object representing a column.
        - `name`: (string) The column name.
        - `type`: (string) The inferred data type (e.g., "INT", "VARCHAR(255)", "DATE", "BOOLEAN", "TEXT", "DECIMAL(10,2)", "UUID").
        - `is_pk`: (boolean, optional) True if it's a primary key.
        - `not_null`: (boolean, optional) True if the column is NOT NULL.
        - `unique`: (boolean, optional) True if the column has a UNIQUE constraint.
        - `default_value`: (string, optional) The default value if specified.
        - `references`: (string, optional) If it's a foreign key, in format `referenced_table.referenced_column`.

    If the input contains multiple tables, include all of them in the array.
    If the input is just descriptive text, infer the most reasonable table and column structure.
    Ensure the JSON is perfectly valid and can be directly parsed. Do not include any extra text or markdown outside the JSON.
    If unable to infer, return `{{ "error": "Could not infer schema from the provided text." }}`.

    Raw Schema Text:
    ```
    {raw_input_text}
    ```
    """

    response_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string"},
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "is_pk": {"type": "boolean"},
                            "not_null": {"type": "boolean"},
                            "unique": {"type": "boolean"},
                            "default_value": {"type": "string"},
                            "references": {"type": "string"}
                        },
                        "required": ["name", "type"]
                    }
                }
            },
            "required": ["table_name", "columns"]
        }
    }

    try:
        ai_response = ask_gemini_structured(prompt, response_schema)
        if ai_response and not ai_response.get("error"):
            if isinstance(ai_response, dict) and "table_name" in ai_response:
                return [ai_response]
            return ai_response
        return ai_response
    except Exception as e:
        return {"error": f"AI inference failed: {e}. Ensure your input is clear."}

