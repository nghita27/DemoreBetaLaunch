import streamlit as st
import base64
import os


def apply_beautyblend_theme(bg_image_path=None):
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

    .stApp {{
        font-family: 'Poppins', sans-serif;
        {background}
        color: #222;
        animation: none !important;
    }}

    @keyframes rotateReveal {{
        0% {{ transform: rotateX(90deg); opacity: 0; }}
        100% {{ transform: rotateX(0); opacity: 1; }}
    }}

    h1, h2, h3, h4, h5, h6, .title, .subtitle, .beautyblend-header {{
        font-family: 'Cinzel Decorative', cursive !important;
        color: #333;
        font-weight: 700;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    main .block-container > div {{
        background: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-bottom: 0 !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: rgba(240, 240, 240, 0.95);
        backdrop-filter: blur(12px);
        border-top-right-radius: 16px;
        border-bottom-right-radius: 16px;
        box-shadow: 2px 0 12px rgba(0, 0, 0, 0.1);
    }}

    section[data-testid="stSidebar"] .css-1v0mbdj,
    section[data-testid="stSidebar"] .css-1aumxhk {{
        color: #7a1c3a;
        font-family: 'Poppins', sans-serif;
    }}

    .tab-folder {{
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }}

    .folder-tab {{
        background: #fff;
        padding: 12px 24px;
        border-radius: 18px;
        font-family: 'Cinzel Decorative', cursive;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        box-shadow: 0 3px 8px rgba(0,0,0,0.05);
        color: #444;
        text-align: center;
    }}

    .folder-tab:hover {{
        border-color: #333;
        color: #333;
    }}

    .folder-tab-active {{
    #    background-color: #fce4ec;
    #    border-color: #333;
        color: #333;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)


def face_designer_nav(current_page="Face Chart Sketch"):
    tabs = {
        "Face Chart Sketch": ("Face Chart Sketch", "pages/FaceChart.py"),
        "Draw Face You Want": ("Draw Face You Want", "pages/FaceDraw.py"),
        
        "Makeup and Design": ("Makeup & Design", "pages/FacePainting.py")
#"Face Mesh Editor": ("Face Mesh Editor", "pages/FaceMesh.py"),
    }

    st.markdown("<div class='tab-folder'>", unsafe_allow_html=True)
    cols = st.columns(len(tabs))

    for i, (key, (label, path)) in enumerate(tabs.items()):
        is_active = (key == current_page)
        tab_class = "folder-tab folder-tab-active" if is_active else "folder-tab"
        with cols[i]:
            if is_active:
                st.markdown(f"<div class='{tab_class}'>{label}</div>", unsafe_allow_html=True)
            else:
                if st.button(label, key=f"tab_{key}"):
                    st.switch_page(path)
    st.markdown("</div>", unsafe_allow_html=True)
