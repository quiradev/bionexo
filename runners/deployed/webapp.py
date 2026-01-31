from pathlib import Path
import sys
import os

if __name__ == '__main__':
    sys.path.append(str(Path(__file__).parents[2] / "src"))
    os.chdir(Path(__file__).parents[2])

    import streamlit as st
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["OPENAI_BASE_URL"] = st.secrets["OPENAI_BASE_URL"]
    os.environ["GOOGLE_CHAT_MODEL"] = st.secrets["GOOGLE_CHAT_MODEL"]
    os.environ["MONGODB_URI"] = st.secrets["MONGODB_URI"]
    os.environ["MONGODB_NAME"] = st.secrets["MONGODB_NAME"]
    os.environ["MONGODB_COLLECTION"] = st.secrets["MONGODB_COLLECTION"]
    os.environ["USE_ATLAS_VECTOR_SEARCH"] = st.secrets["USE_ATLAS_VECTOR_SEARCH"]
    os.environ["OPENFOODFACTS_EMAIL"] = st.secrets["OPENFOODFACTS_EMAIL"]
    os.environ["OPENFOODFACTS_APP"] = st.secrets["OPENFOODFACTS_APP"]
    os.environ["VERSION"] = st.secrets["VERSION"]

    from bionexo.application.webapp.main import create_n_run_app
    create_n_run_app()