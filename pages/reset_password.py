import streamlit as st
from Security.auth_db import verify_temp_password, save_new_password
import streamlit as st

query_params = st.query_params
prefilled_email = query_params.get("email", [""])[0]

st.title("🔐 Set a New Password")

st.info("Please go to Home page, choose \"Forgot Password\", enter your registered email to get temporary code first. Thank you!")


with st.form("reset_password_form"):
    email = st.text_input("Email", value=prefilled_email)
    temp_password = st.text_input("Temporary Password (from email)", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    submit_reset = st.form_submit_button("Update Password")

    if submit_reset:
        if not email or not temp_password or not new_password or not confirm_password:
            st.error("❌ All fields are required.")
        elif new_password != confirm_password:
            st.error("❌ New passwords do not match.")
        else:
            if verify_temp_password(email, temp_password):
                save_new_password(email, new_password)
                st.success("✅ Password updated successfully. You can now log in.")
            else:
                st.error("❌ Invalid email or temporary password.")
