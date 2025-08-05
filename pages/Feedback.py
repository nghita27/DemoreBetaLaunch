import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
import datetime

# 🔐 Load secrets from .streamlit/secrets.toml
EMAIL_ADDRESS = st.secrets["email"]["address"]
EMAIL_APP_PASSWORD = st.secrets["email"]["app_password"]
EMAIL_RECEIVE = st.secrets["email"]["receive"]
ADMIN_PASSWORD = st.secrets["admin"]["password"]

FEEDBACK_FILE = "feedback.csv"
FEEDBACK_COLUMNS = [
    "Feature Name",
    "Rating (out of 5)",
    "What do you like about this feature?",
    "How can we improve?",
    "What features would you like to see in the future?",
    "Submitted At"
]

def send_feedback_email(columns, data, receiver=EMAIL_RECEIVE):
    msg = EmailMessage()
    submitted_at = data[5] if len(data) > 5 else ""
    msg['Subject'] = f'New Demore Feedback: {data[0]} on {submitted_at}'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = receiver
    body = "\n".join([f"{col}: {val}" for col, val in zip(columns, data)])
    msg.set_content(body)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)

if 'feedback_rows' not in st.session_state:
    st.session_state.feedback_rows = [
        {"feature": "", "rating": 3, "like": "", "improve": "", "future": ""}
    ]

def add_row():
    st.session_state.feedback_rows.append(
        {"feature": "", "rating": 3, "like": "", "improve": "", "future": ""}
    )

# --- App Title and Header ---
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
""", unsafe_allow_html=True)

st.markdown("""
<div style='padding: 32px 0; text-align: center; background: linear-gradient(90deg, #91a8b8 20%, #f7cdd5 100%);'>
    <h1 style='font-family: "Cinzel Decorative", serif; font-size: 2.5em;'>Demore User Feedback</h1>
    <p style='font-size: 1.2em; color: #fff;'>Share your experience to help us improve!</p>
</div>
<div style="margin-top: 30px;"></div>
""", unsafe_allow_html=True)

st.write("You can submit feedback for multiple features at once.")
st.write('Or contact us directly through email: "admin@beautyblend.company"')


# --- Feedback Form ---
with st.form("multi_feedback_form"):
    updated_rows = []
    for i, row in enumerate(st.session_state.feedback_rows):
        cols = st.columns([2,1,3,3,3,0.3])
        with cols[0]:
            feature = st.text_input("Feature Name", value=row["feature"], key=f"feature_{i}")
        with cols[1]:
            rating = st.slider("Rating (1-5)", 1, 5, value=row["rating"], key=f"rating_{i}")
        with cols[2]:
            like = st.text_area("What do you like/dislike?", value=row["like"], key=f"like_{i}", height=70)
        with cols[3]:
            improve = st.text_area("How to improve?", value=row["improve"], key=f"improve_{i}", height=70)
        with cols[4]:
            future = st.text_area("Future wishes", value=row["future"], key=f"future_{i}", height=70)
        with cols[5]:
            if len(st.session_state.feedback_rows) > 1:
                remove = st.form_submit_button(f"➖ {i}")
                if remove:
                    st.session_state.feedback_rows.pop(i)
                    st.rerun()
        updated_rows.append({
            "feature": feature,
            "rating": rating,
            "like": like,
            "improve": improve,
            "future": future
        })
    st.session_state.feedback_rows = updated_rows

    add = st.form_submit_button("+ Add Feature")
    submitted = st.form_submit_button("Submit All Feedback")

    if add:
        add_row()
        st.rerun()

    if submitted:
        submission_date = datetime.datetime.now().strftime("%Y-%m-%d")
        rows_to_save = []
        for row in st.session_state.feedback_rows:
            if row['feature'].strip() or row['like'].strip():
                new_row = [
                    row['feature'],
                    row['rating'],
                    row['like'],
                    row['improve'],
                    row['future'],
                    submission_date
                ]
                rows_to_save.append(new_row)

        if not rows_to_save:
            st.warning("Please provide feedback for at least one feature.")
        else:
            df = pd.DataFrame(rows_to_save, columns=FEEDBACK_COLUMNS)
            if os.path.exists(FEEDBACK_FILE):
                df.to_csv(FEEDBACK_FILE, mode='a', header=False, index=False)
            else:
                df.to_csv(FEEDBACK_FILE, mode='w', header=True, index=False)
            for row in rows_to_save:
                try:
                    send_feedback_email(FEEDBACK_COLUMNS, row)
                except Exception as e:
                    st.warning(f"Saved, but failed to send email for one row: {e}")
            st.success(f"Thank you for your feedback on {len(rows_to_save)} feature(s)!")
            st.session_state.feedback_rows = [
                {"feature": "", "rating": 3, "like": "", "improve": "", "future": ""}
            ]

# --- Admin-only Feedback Table (login required) ---
st.markdown("---")
with st.expander("🔒 Admin Panel (login required)", expanded=False):
    admin_password = st.text_input("Admin Password", type="password")
    if admin_password == ADMIN_PASSWORD:
        st.success("Admin login successful.")
        if os.path.exists(FEEDBACK_FILE):
            feedback_df = pd.read_csv(FEEDBACK_FILE)
            st.dataframe(feedback_df)
            st.write("Total feedback entries:", len(feedback_df))
            st.download_button(
                label="Download CSV",
                data=feedback_df.to_csv(index=False),
                file_name=FEEDBACK_FILE,
                mime="text/csv",
            )
        else:
            st.info("No feedback available yet.")
    elif admin_password:
        st.error("Incorrect password.")
