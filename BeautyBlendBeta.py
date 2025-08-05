import streamlit as st
import base64
import os
from beautyblend_theme import apply_beautyblend_theme
from streamlit_extras.switch_page_button import switch_page
from streamlit.components.v1 import html

# --- Page Config ---
st.set_page_config(page_title="Demore", layout="wide")
#=============== PAGE AUTHENTICATION: LOG IN 

from Security.auth_db import (
    register_user,
    verify_user_credentials,
    send_password_reset_email,
    update_remember_me,
)

import streamlit as st
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "portfolio.db")


# --- Page Config ---
#st.set_page_config(page_title="Demore", layout="wide")


# --- Init session ---
# --- Init session ---
import streamlit as st
import sqlite3

import streamlit as st
import sqlite3
#from auth_db import register_user, verify_user_credentials, send_password_reset_email, update_remember_me

# --- Persistent Session Setup ---

# --- Persistent Session Setup ---
import streamlit as st
import os
import sqlite3
from Security.auth_db import (
    register_user,
    verify_user_credentials,
    send_password_reset_email,
    update_remember_me,
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "portfolio.db")



# --- Persistent Session Setup ---
if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["remember_me"] = False

    # Load from file if exists
    if os.path.exists(".login_session"):
        with open(".login_session", "r") as f:
            data = f.read().strip().split("::")
            if len(data) == 2:
                st.session_state["auth_status"] = True
                st.session_state["user_id"] = data[0]
                st.session_state["username"] = data[1]

# --- Top-right dropdown ---
col1, col2 = st.columns([8, 1])
with col2:
    if st.session_state["auth_status"]:
        account_action = st.selectbox(
            "Account",
            ["", "Logout"],
            format_func=lambda x: "Account" if x == "" else x,
            label_visibility="collapsed",
            key="account_action_app"
        )
    else:
        account_action = st.selectbox(
            "Account",
            ["", "Log in", "Register", "Forgot Password"],
            format_func=lambda x: "Account" if x == "" else x,
            label_visibility="collapsed",
            key="account_action_app"
        )

# --- Log in ---
if account_action == "Log in":
    with st.form("login_form"):
        st.subheader("🔐 Log In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember my account")
        submit = st.form_submit_button("Log In")

        if submit:
            user_id = verify_user_credentials(username, password)
            if user_id:
                st.session_state["auth_status"] = True
                st.session_state["user_id"] = user_id
                st.session_state["username"] = username
                st.session_state["remember_me"] = remember
                update_remember_me(user_id, remember)

                from utils.profile import load_user_profile
                st.session_state["profile"] = load_user_profile(user_id)

                # ✅ Save session to file for persistence
                with open(".login_session", "w") as f:
                    f.write(f"{user_id}::{username}")

                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Incorrect username or password.")


# --- Register ---
elif account_action == "Register":
    with st.form("register_form"):
        st.subheader("📝 Register")
        new_username = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")

        if submit:
            if register_user(new_username, new_email, new_password):
                st.success("Registration successful! Please log in.")
            else:
                st.error("Username or email already exists.")

# --- Forgot Password ---
elif account_action == "Forgot Password":
    with st.form("forgot_form"):
        st.subheader("❓ Forgot Password")
        email = st.text_input("Enter your registered email")
        submit = st.form_submit_button("Send Reset Link")

        if submit:
            if send_password_reset_email(email):
                st.success("Reset link sent! Please check your inbox.")
            else:
                st.error("Email not found.")

# --- Logout ---
elif account_action == "Logout":
    st.session_state["auth_status"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["remember_me"] = False
    update_remember_me(None, False)

    # ✅ Clear session file
    if os.path.exists(".login_session"):
        os.remove(".login_session")

    st.success("You have been logged out.")
    st.rerun()

# --- Greeting ---
if st.session_state["auth_status"]:
    st.markdown(
        f"<div style='position:fixed; top:10px; right:30px; z-index:999;'>"
        f"<b>Welcome, {st.session_state['username']}!</b> "
        f"</div>",
        unsafe_allow_html=True
    )
else:
    st.warning("🔒 Please log in to continue.")

####========================

from streamlit.components.v1 import html

def redirect_to_page(page_filename):
    html(f"""
        <script>
            window.location.href = "/?page={page_filename}";
        </script>
    """, height=0)



#=============== Initialize Session State ---
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "home"


# --- Hide Sidebar Nav ---
import streamlit as st

# --- Full CSS Injection for Optimized Front Page Look ---
import streamlit as st

# --- Full CSS Injection for Optimized Front Page Look ---
import streamlit as st

# --- Session state for active tab ---
# --- Full CSS Injection for Optimized Front Page Look ---
import streamlit as st

# --- Session state for active tab ---
if "main_tab" not in st.session_state:
    st.session_state.main_tab = "About"

# --- Background Base64 Helper ---
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Style ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400&display=swap');

html, body, .stApp {
    font-family: 'Cinzel Decorative', cursive, serif !important;
    color: white;
    background: linear-gradient(90deg, #91a8b8 20%, #f7cdd5 100%) !important;
    background-attachment: fixed;
    overflow-x: hidden;
}

h1, h2, h3, .title, .subtitle, .beautyblend-header, .beautyblend-subtitle, .beautyblend-section-header, .quote {
    font-family: 'Cinzel Decorative', cursive, serif !important;
    color: white !important;
    letter-spacing: 0.5px;
}

p, label, input, textarea, button, select {
    font-family: 'Poppins', sans-serif !important;
    letter-spacing: 0.3px;
}

div[data-testid="stButton"] button {
    background-color: #ffffff !important;
    color: #d8b3e6 !important;
    font-weight: 600 !important;
    font-family: 'Raleway', sans-serif !important;
    font-size: 16px !important;
    border: 2px solid #d8b3e6 !important;
    border-radius: 12px !important;
    padding: 8px 24px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
    transition: all 0.3s ease-in-out;
}

#div[data-testid="stButton"] button:hover {
#    background-color: #a91e47 !important;
#    color: white !important;
#    box-shadow: 0 6px 16px rgba(0,0,0,0.25) !important;
#}

.navbar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 24px;
    background: transparent;
    padding: 12px 0 8px 0;
    margin-bottom: 18px;
}

.nav-tab {
    font-family: 'Cinzel Decorative', cursive, serif !important;
    font-size: 16px;
    padding: 12px 30px;
    border-radius: 16px 16px 0 0;
    border: 1px solid #d8b3e6;
    border-bottom: none;
    background: rgba(255, 255, 255, 0.07);
    color: white;
    cursor: pointer;
    transition: all 0.4s ease;
    margin: 0 -2px;
}

.nav-tab:hover {
    background: rgba(255, 255, 255, 0.15);
    box-shadow: 0 0 12px rgba(216, 179, 230, 0.4);
}

.nav-tab.active {
    background: #d8b3e6;
    color: #0a2d2c;
    font-weight: bold;
    box-shadow: inset 0 6px 0 0 #d8b3e6, 0 -6px 12px rgba(216, 179, 230, 0.5);
    z-index: 2;
    position: relative;
}

.glass-box {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 30px;
    margin: 40px auto;
    max-width: 800px;
    animation: fadeInText 1.5s ease-in-out both;
    backdrop-filter: blur(8px);
}

.glass-box .title {
    font-size: 36px;
    margin-bottom: 16px;
    color: white;
    animation: fadeInText 2s ease forwards;
}

.glass-box .subtitle {
    font-size: 16px;
    line-height: 1.8;
    color: #f3e9f7;
    margin-bottom: 12px;
    animation: fadeInText 2.2s ease forwards;
}

.glass-box .quote {
    font-size: 16px;
    font-style: italic;
    color: #f3e9f7;
    margin-bottom: 12px;
    font-family: 'Cinzel Decorative', cursive, serif !important;
}

.role-section {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    gap: 36px;
    margin-top: 20px;
    flex-wrap: wrap;
    border-top: 2px solid #d8b3e6;
    padding-top: 30px;
}

.role-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 24px;
    padding: 20px;
    transition: transform 0.6s ease, box-shadow 0.6s ease;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
    text-align: center;
    width: 300px;
    animation: fadeInCard 1.2s ease-out forwards;
}

.role-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 30px rgba(216, 179, 230, 0.3);
}

.role-card img {
    border-radius: 20px;
    width: 100%;
    height: auto;
}

.role-title {
    font-family: 'Cinzel Decorative', serif;
    font-size: 16px;
    margin-top: 12px;
    color: white;
}

@keyframes fadeInText {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInCard {
    0% {opacity: 0; transform: translateY(30px);}
    100% {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# --- Header Title & Subtitle ---
st.markdown("""
<div class='center-intro'>
    <h1 class='title'>Demore</h1>
    <p class='subtitle'>Where the face is a canvas, makeup is poetry, and every creation is an unfiltered expression of the artist's soul</p>
</div>
""", unsafe_allow_html=True)

# --- About Tab Section ---
if st.session_state.get("main_tab") == "About":
    bg_image_base64 = get_base64_image("introduction_BeautyBlend.jpg")

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_image_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        animation: fadeInBg 1.2s ease-in-out forwards;
    }}
    .navbar {{
        display: flex;
        justify-content: center;
        padding: 10px 0;
        margin-top: 10px;
    }}
    .nav-tab {{
        padding: 10px 20px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        font-weight: bold;
        font-size: 18px;
        color: #333;
        cursor: pointer;
        margin: 0 8px;
    }}
    .nav-tab.active {{
        background: rgba(255, 255, 255, 0.4);
        border: 2px solid #fff;
        color: #000;
    }}
    .glass-box {{
        max-width: 750px;
        margin: 30px auto 40px;
        padding: 40px;
        background: rgba(255,255,255,0.25);
        border-radius: 20px;
        backdrop-filter: blur(14px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        text-align: center;
        color: #fff;
        animation: fadeIn 1.2s ease-in-out forwards;
    }}
    .title {{
        font-family: 'Cinzel Decorative', serif;
        font-size: 50px;
        margin-bottom: 20px;
    }}
    .subtitle {{
        font-size: 18px;
        line-height: 1.6;
        margin-bottom: 20px;
    }}
    .quote {{
        font-style: italic;
        font-size: 16px;
        margin: 30px 0;
        color: #ffe9f5;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes fadeInBg {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    </style>

    <div class='navbar'>
        <div class='nav-tab active'>About</div>
    </div>

    <div class='glass-box'>
        <div class="title">Demore Beta version</div>
        <div class="subtitle">
            Welcome to my very first app, inspired by my own pre-wedding photoshoot! 
            As a solo developer, I’ve built this space to help everyone express themselves through art and find joy in designing faces. 
            I’d love your feedback—just visit the feedback tab on the sidebar. Your ideas mean a lot to me!
            </div>
        <div class="quote">“Art is not what you see, but what you make others see.” — Edgar Degas</div>
        <div class="subtitle">Created with intention and love by Nikki.</div>
    </div>
    """, unsafe_allow_html=True)




col1, col2, col3, col4  = st.columns(4)

with col1:
    #st.markdown("<div class='role-card'>", unsafe_allow_html=True)
    if st.button("FaceCanvas", key="canvas_btn"):
        st.switch_page("pages/FaceChart.py")
    st.image("face_designer_card.png")
    st.markdown(
        "<div class='role-title'>your imaginative canvas to explore, design, and bring visionary face art to life.</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)



with col2:
    #st.markdown("<div class='role-card'>", unsafe_allow_html=True)
    if st.button("Dashboard", key="dashboard_btn"):
        st.switch_page("pages/5_Dashboard.py")
    st.image("makeup_artist_card.png")
    st.markdown(
        "<div class='role-title'>This is your personal hub to manage your face designs.</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    #st.markdown("<div class='role-card'>", unsafe_allow_html=True)
    if st.button("MyGallery", key="gallery_btn"):
        st.switch_page("pages/6_Gallery.py")
    st.image("gallery_card.png")
    st.markdown(
        "<div class='role-title'>Discover new talent, admire transformative artistry, and explore a growing archive of visual inspiration.</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    #st.markdown("<div class='role-card'>", unsafe_allow_html=True)
    if st.button("Feedback", key="feedback_btn"):
        st.switch_page("pages/Feedback.py")
    st.image("art_lover_card.png")
    st.markdown(
        "<div class='role-title'>Every piece of feedback helps us improve and evolve.</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("</div>", unsafe_allow_html=True)


# Parse the URL query parameter to update the active tab
import urllib.parse
query_params = st.query_params
if "tab" in query_params and query_params["tab"][0] in dict(tabs):
    if st.session_state["active_tab"] != query_params["tab"][0]:
        st.session_state["active_tab"] = query_params["tab"][0]
        st.rerun()




