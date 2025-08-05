import streamlit as st
import base64
import os

# --- Setup ---
#st.set_page_config(page_title="BeautyBlend Profile", layout="wide")

# --- Load and Apply Custom Theme ---
def apply_theme(bg_image_path="#utils/background/theme_background_3.png"):
    background = ""
    if bg_image_path and os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as f:
            bg_base64 = base64.b64encode(f.read()).decode()
            background = f"""
            background-image: url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
            """

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Poppins:wght@400&display=swap');

    [data-testid="stAppViewContainer"] {{
        {background}
    }}

    .stApp {{
        font-family: 'Poppins', sans-serif;
        font-size: 0.85rem;
        color: #2e2e2e;
    }}

    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        font-family: 'Cinzel Decorative', cursive;
        color: #3f3f3f;
        font-weight: 700;
        line-height: 1.3;
        text-shadow: 0.5px 0.5px 1px rgba(255, 255, 255, 0.4);
    }}
    h1 {{ font-size: 1.6rem; }}
    h2 {{ font-size: 1.3rem; }}
    h3 {{ font-size: 1.1rem; }}

    [data-testid="stAppViewContainer"] > .main {{
        background: none;
        padding: 2rem;
    }}

    .beautyblend-glasscard-wrapper {{
        background: rgba(255, 255, 255, 0.65);
        border: 1px solid rgba(200, 200, 200, 0.2);
        box-shadow: 0 6px 40px rgba(160, 180, 200, 0.18);
        backdrop-filter: blur(20px);
        padding: 1.5rem 2.5rem;
        margin: 1.5rem auto;
        max-width: 1200px;
        border-radius: 18px;
    }}

    .stButton > button, [data-testid="baseButton-secondary"] {{
        background: #8a7c6e;
        color: #fff;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        border: none;
        transition: background 0.2s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .stButton > button:hover, [data-testid="baseButton-secondary"]:hover {{
        background: linear-gradient(90deg, #8a7c6e 80%, #b4a896 100%);
    }}

    .stDownloadButton > button {{
        background-color: #ebe4d4;
        color: #222;
        border-radius: 8px;
        font-weight: 500;
    }}
    .stDownloadButton > button:hover {{
        background-color: #dcd0be;
        transition: 0.3s ease-in-out;
    }}

    input, select, textarea {{
        border-radius: 8px;
        border: 1.5px solid #b4a896;
        font-family: inherit;
        font-size: 0.85rem;
        background: rgba(255, 255, 255, 0.7);
    }}
    input:focus, select:focus, textarea:focus {{
        border-color: #b8a78f;
        box-shadow: 0 0 0 2px #b8a78f44;
    }}

    .element-container:has(.stSpinner) {{
        background: linear-gradient(to right, #eee6da 25%, #f9f4ef 50%, #eee6da 75%);
        background-size: 400% 100%;
        animation: shimmer 1.5s infinite;
    }}
    @keyframes shimmer {{
        0% {{ background-position: -400% 0; }}
        100% {{ background-position: 400% 0; }}
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()


