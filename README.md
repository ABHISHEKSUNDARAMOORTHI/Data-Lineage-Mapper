
# 🔗 Intelligent Data Lineage Mapper 📊

This project delivers a powerful **Streamlit-based web application** designed to empower data professionals, engineers, and architects in understanding and managing complex data flows. By analyzing your ETL/ELT code and SQL scripts, it leverages **Google Gemini AI** to automatically generate **column-level data lineage**, provide a summary of transformations, and even offer **confidence scores** for its mappings. ✨

---

## ✨ Features

* **Smart Code Input**
  Paste your SQL queries, PySpark snippets, DBT models, or Airflow code. The application uses `streamlit_ace` for syntax highlighting (SQL and Python). 📝

* **AI-Powered Lineage Mapping**
  Utilizes Google Gemini AI to automatically analyze your code and produce:

  * **Detailed Column-Level Lineage**
    Clear descriptions of data flow from source to target, including transformations. ➡️
  * **Transformation Summary**
    A concise list of all distinct transformation types detected (e.g., `JOIN`, `SUM()`, `CASE WHEN`, `FILTER`). 🔍
  * **Column-Level Confidence Score**
    AI returns a confidence rating (1–5) for each transformation or mapping, helping users prioritize manual validation. ✅

* **Dual Output Views**

  * **Text Report**: A human-readable Markdown report of the lineage and transformations. 📄
  * **Graph View**: An interactive graph visualization of your data lineage for intuitive exploration. 🌐

* **Dark Mode / Light Mode Toggle**
  Seamlessly switch between dark and light themes for personalized viewing comfort. 🌙☀️

* **Downloadable Reports**
  Export your lineage analysis in Markdown or JSON format. ⬇️

* **User-Friendly & Responsive UI**
  Built with Streamlit and custom CSS for a modern, intuitive, and mobile-friendly user experience. 📱💻

---

## 🚀 Technologies Used

* **Python** 🐍 – Core programming language
* **Streamlit** 🌐 – Interactive UI framework
* **Google Gemini API** 🧠 – AI-powered lineage and transformation analysis
* **streamlit\_ace** ✍️ – Code editor with syntax highlighting
* **Custom CSS** 🎨 – For styling and responsive design

---

## ⚙️ Setup Instructions

### Prerequisites

* Python 3.8 or higher ✅
* pip (Python package installer) ✔️

### Clone the Project

If you're in a local environment, clone the repo:

```bash
git clone <your-repo-url>
cd <project-directory>
```

### Install Dependencies

Create a `requirements.txt` file if it doesn't exist, and include:

```
streamlit
streamlit-ace
python-dotenv
google-generativeai
```

Install dependencies with:

```bash
pip install -r requirements.txt
```

### Set up Google Gemini API Key

1. Obtain your API Key from Google AI Studio 🔑
2. Create a `.env` file in your root directory 📁
3. Add your key like this:

```env
GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"
```

---

## ▶️ Usage

To run the Streamlit application:

```bash
streamlit run main.py
```

Then visit [http://localhost:8501](http://localhost:8501) in your browser. 🔗

---

## 📂 Project Structure

* **`main.py`** 🏠
  Entry point of the app. Sets up layout, loads CSS, and coordinates all components.

* **`features.py`** 📝
  Handles user input area (code editor) and text-based output rendering.

* **`ai_logic.py`** 🤖
  Manages interactions with Gemini API including prompt logic and structured JSON responses.

* **`styling.py`** 🎨
  Injects custom CSS into Streamlit for styling and dark/light mode toggle.

* **`lineage_visualizer.py`** 🌐 *(optional)*
  Renders interactive data lineage graph from structured output using `pyvis` or similar.

* **`additional_features.py`** 📥 *(optional)*
  For future enhancements like clear/reset, download handling.

* **`.env`** 🔒
  Holds your Gemini API key.

---
