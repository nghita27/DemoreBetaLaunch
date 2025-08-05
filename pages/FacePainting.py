import streamlit as st
from beautyblend_theme import face_designer_nav

# Use correct tab label
face_designer_nav("Makeup and Design")
# === Apply Poppins font to the entire sidebar ===
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
<style>
/* Sidebar container */
section[data-testid="stSidebar"] * {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap" rel="stylesheet">
<h1 style="font-family: 'Cinzel Decorative', serif; font-size: 2.5em; display: flex; align-items: center;">
    Makeup & Design
</h1>
""", unsafe_allow_html=True)

st.markdown("Please download a drawing app such as **Procreate** or **Adobe Fresco** to paint your face sketch, then upload it to our Gallery.")
st.markdown("We apologize for the inconvenience. We're currently developing our own drawing tools and gathering feedback to create a better experience.")


