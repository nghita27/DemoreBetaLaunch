import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import numpy as np
import mediapipe as mp
import io
import math
from scipy.spatial import ConvexHull
from beautyblend_theme import apply_beautyblend_theme, face_designer_nav
import sqlite3
import os
from Security.face_sketch_db import save_face_sketch, load_user_sketches, delete_sketch
# --- Theme & Navigation ---
apply_beautyblend_theme("")
from beautyblend_theme import face_designer_nav
face_designer_nav("Draw Face You Want")


##===========LOG IN
#from Security.auth_db import (
#    register_user,
#    verify_user_credentials,
#    send_password_reset_email,
#    update_remember_me
#)

# ========== UNIVERSAL LOGIN BLOCK ==========
#import streamlit as st
#import sqlite3
#import os
#from Security.auth_db import register_user, verify_user_credentials, send_password_reset_email
#from utils.profile import load_user_profile

# ==========================
# SESSION-LOCAL LOGIN (No Global DB Auto-Login)
# ==========================
#if "auth_status" not in st.session_state:
#    st.session_state["auth_status"] = False
#    st.session_state["user_id"] = None
#    st.session_state["username"] = None
#    st.session_state["remember_me"] = False
#    st.session_state["profile"] = {}

# === ACCOUNT SELECTOR (TOP-RIGHT) ===
#col1, col2 = st.columns([8, 1])
#with col2:
#    if st.session_state["auth_status"]:
#        account_action = st.selectbox(
#            "Account",
#            ["", "Logout"],
#            format_func=lambda x: "Account" if x == "" else x,
#            key="account_action_face_draw"
#        )
#    else:
#        account_action = st.selectbox(
#            "Account",
#            ["", "Log in", "Register", "Forgot Password"],
#            format_func=lambda x: "Account" if x == "" else x,
#            key="account_action_face_draw"
#        )

# === LOGIN LOGIC ===
#if account_action == "Log in":
#    with st.form("login_form_face_draw"):
#        st.subheader("Log In")
#        username = st.text_input("Username")
#        password = st.text_input("Password", type="password")
#        submit = st.form_submit_button("Log In")

#        if submit:
#            user_id = verify_user_credentials(username, password)
#            if user_id:
#                st.session_state["auth_status"] = True
#                st.session_state["user_id"] = user_id
#                st.session_state["username"] = username

#                # Load user profile for sketches
#                st.session_state["profile"] = load_user_profile(user_id)

#                st.success(f"Welcome back, {username}!")
#                st.rerun()
#            else:
#                st.error("Incorrect username or password.")

#elif account_action == "Register":
#    with st.form("register_form_face_draw"):
#        st.subheader("📝 Register")
#        st.info("Please memorize your Username.")
#        new_username = st.text_input("Username")
#        new_email = st.text_input("Email")
#        new_password = st.text_input("Password", type="password")
#        submit = st.form_submit_button("Register")

#        if submit:
#            conn = sqlite3.connect("portfolio.db")
#            c = conn.cursor()

#            # Check email
#            c.execute("SELECT 1 FROM users WHERE email = ?", (new_email,))
#            email_exists = c.fetchone() is not None

#            # Check username
#            c.execute("SELECT 1 FROM users WHERE username = ?", (new_username,))
#            username_exists = c.fetchone() is not None

#            if email_exists:
#                st.error("❌ This email is already registered.")
#                st.info("💡 You can use 'Forgot Password' to reset your password.")
#            elif username_exists:
#                st.error("❌ Username is already taken.")
#            else:
#                if register_user(new_username, new_email, new_password):
#                    st.success("✅ Registration successful! Please log in.")
#                else:
#                    st.error("❌ Registration failed. Please try again later.")
#            conn.close()

#elif account_action == "Forgot Password":
#    with st.form("forgot_form_face_draw"):
#        st.subheader("Forgot Password")
#        email = st.text_input("Enter your registered email")
#        submit = st.form_submit_button("Send Reset Link")

#        if submit:
#            if send_password_reset_email(email):
#                st.success("Reset link sent! Please check your inbox.")
#            else:
#                st.error("Email not found.")

#elif account_action == "Logout":
#    st.session_state["auth_status"] = False
#    st.session_state["user_id"] = None
#    st.session_state["username"] = None
#    st.session_state["profile"] = {}
#    st.success("Logged out successfully.")
#    st.rerun()

# === SHOW LOGIN STATUS ===
#if st.session_state["auth_status"]:
#    st.markdown(f"<div style='text-align:right;'>👋 Welcome, <b>{st.session_state['username']}</b></div>", unsafe_allow_html=True)
#else:
#    st.info("You're viewing as a guest. Log in to save your face sketches.")

####========================

st.title("Draw a Face")
st.info("Draw a face (with clear eyes, nose, mouth, and contour), then click '👁️ Detect Face Mesh & Generate Sketch'.")

# --- Face Shape Classification & Reference Templates ---
FACE_CONTOUR = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323,
    361, 288, 397, 365, 379, 378, 400, 377, 152, 148,
    176, 149, 150, 136, 172, 58, 132, 93, 234, 127,
    162, 21, 54, 103, 67, 109, 151, 10
]
LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
EYES = LEFT_EYE + RIGHT_EYE
NOSE = [1, 2, 98, 327, 168, 197, 5, 4, 94, 19]
LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

def loosen_points(points, loosen_factor=1.15):
    # Spread all points further from center to "loosen" the drawing
    xs = [x for x, y in points]
    ys = [y for x, y in points]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    return [(cx + (x - cx) * loosen_factor, cy + (y - cy) * loosen_factor) for x, y in points]


def classify_face_shape(points):
    contour = [points[i] for i in FACE_CONTOUR if i < len(points)]
    if not contour:
        return "Unknown"
    xs = [x for x, y in contour]
    ys = [y for x, y in contour]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    if height == 0:
        return "Unknown"
    aspect_ratio = width / height
    jaw_width = np.linalg.norm(np.array(contour[0]) - np.array(contour[len(contour)//2]))
    cheekbone_width = np.linalg.norm(np.array(contour[8]) - np.array(contour[24]))
    chin_y = min(ys)
    forehead_y = max(ys)
    if aspect_ratio > 1.1 and cheekbone_width > jaw_width * 1.1 and (forehead_y - chin_y) > height * 0.6:
        return "Heart"
    if 0.9 < aspect_ratio < 1.1:
        return "Round"
    elif aspect_ratio < 0.9:
        return "Oblong"
    elif aspect_ratio > 1.1:
        return "Square"
    return "Unknown"

def get_template_offsets(face_type, contour_pts):
    n = len(contour_pts)
    offsets = [(0, 0)] * n
    if face_type == "Round":
        cx = sum(x for x, y in contour_pts) / n
        cy = sum(y for x, y in contour_pts) / n
        avg_radius = sum(math.hypot(x-cx, y-cy) for x, y in contour_pts) / n
        offsets = []
        for x, y in contour_pts:
            angle = math.atan2(y-cy, x-cx)
            new_x = cx + avg_radius * math.cos(angle)
            new_y = cy + avg_radius * math.sin(angle)
            offsets.append((new_x - x, new_y - y))
    elif face_type == "Square":
        xs = [x for x, y in contour_pts]
        ys = [y for x, y in contour_pts]
        cx = sum(xs) / n
        cy = sum(ys) / n
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        offsets = []
        for i, (x, y) in enumerate(contour_pts):
            fx = (x - cx) / width
            fy = (y - cy) / height
            if abs(fx) > 0.7 or abs(fy) > 0.7:
                new_x = x + (fx * 0.18 * width)
                new_y = y + (fy * 0.08 * height)
            else:
                new_x = x
                new_y = y
            offsets.append((new_x - x, new_y - y))
    elif face_type == "Oblong":
        cx = sum(x for x, y in contour_pts) / n
        cy = sum(y for x, y in contour_pts) / n
        offsets = []
        for x, y in contour_pts:
            new_y = cy + 1.18 * (y - cy)
            offsets.append((0, new_y - y))
    elif face_type == "Heart":
        xs = [x for x, y in contour_pts]
        ys = [y for x, y in contour_pts]
        cx = sum(xs) / n
        cy = sum(ys) / n
        top = max(ys)
        bottom = min(ys)
        offsets = []
        for i, (x, y) in enumerate(contour_pts):
            rel_y = (y - bottom) / (top - bottom + 1e-6)
            if rel_y > 0.66:
                new_x = x + (x - cx) * 0.13
                new_y = y
            elif 0.33 < rel_y <= 0.66:
                new_x = x + (x - cx) * 0.10
                new_y = y
            else:
                new_x = x - (x - cx) * 0.18
                new_y = y + (rel_y - 0.33) * 10
            offsets.append((new_x - x, new_y - y))
    elif face_type == "Triangle":
        xs = [x for x, y in contour_pts]
        ys = [y for x, y in contour_pts]
        cx = sum(xs) / n
        cy = sum(ys) / n
        top = max(ys)
        bottom = min(ys)
        offsets = []
        chin_factor = 0.07  # slightly bigger chin area
        for i, (x, y) in enumerate(contour_pts):
            rel_y = (y - bottom) / (top - bottom + 1e-6)
            if rel_y < chin_factor:
                # Make chin very pointed and pulled down
                new_x = cx + (x - cx) * 0.01  # almost centered x (super sharp)
                new_y = y + (chin_factor - rel_y) * 100  # much sharper downward for long, pointy chin
            elif rel_y < 0.33:
                # Jaw: fairly narrow and tall to accentuate triangle
                jaw_ratio = (rel_y - chin_factor) / (0.33 - chin_factor + 1e-6)
                new_x = cx + (x - cx) * (0.25 + 0.4 * jaw_ratio)
                new_y = y + (0.33 - rel_y) * 8
            elif rel_y < 0.66:
                # Cheek: normal width, rising toward forehead
                new_x = x
                new_y = y
            else:
                # Forehead: slightly narrower, but not too narrow
                new_x = cx + (x - cx) * 0.90
                new_y = y
            offsets.append((new_x - x, new_y - y))
    elif face_type == "Rectangle":
        xs = [x for x, y in contour_pts]
        ys = [y for x, y in contour_pts]
        cx = sum(xs) / n
        cy = sum(ys) / n
        top = max(ys)
        bottom = min(ys)
        width = max(xs) - min(xs)
        offsets = []
        for (x, y) in contour_pts:
            rel_y = (y - bottom) / (top - bottom + 1e-6)
            if rel_y < 0.10 or rel_y > 0.90:
                new_x = x
                new_y = y
            else:
                new_x = cx + (x - cx) * 1.10
                new_y = y
            # Add vertical elongation for rectangle
            new_y = cy + (new_y - cy) * 1.12
            offsets.append((new_x - x, new_y - y))
    elif face_type == "A-Triangle":
        xs = [x for x, y in contour_pts]
        ys = [y for x, y in contour_pts]
        cx = sum(xs) / n
        cy = sum(ys) / n
        top = max(ys)
        bottom = min(ys)
        offsets = []
        for (x, y) in contour_pts:
            rel_y = (y - bottom) / (top - bottom + 1e-6)
            if rel_y < 0.17:
                new_x = cx + (x - cx) * 1.16
                new_y = y
            elif rel_y < 0.4:
                new_x = cx + (x - cx) * (1.10 + 0.05 * (rel_y - 0.17) / 0.23)
                new_y = y
            elif rel_y > 0.73:
                new_x = cx + (x - cx) * 0.90
                new_y = y
            else:
                new_x = x
                new_y = y
            offsets.append((new_x - x, new_y - y))
    elif face_type == "Diamond":
        xs = [x for x, y in contour_pts]
        ys = [y for x, y in contour_pts]
        cx = sum(xs) / n
        cy = sum(ys) / n
        top = max(ys)
        bottom = min(ys)
        offsets = []
        for (x, y) in contour_pts:
            rel_y = (y - bottom) / (top - bottom + 1e-6)
            if 0.30 < rel_y < 0.70:
                new_x = cx + (x - cx) * 1.18
                new_y = y
            elif rel_y < 0.16 or rel_y > 0.84:
                new_x = cx + (x - cx) * 0.90
                new_y = y
            else:
                new_x = x
                new_y = y
            offsets.append((new_x - x, new_y - y))
    elif face_type == "Oval":
        cx = sum(x for x, y in contour_pts) / n
        cy = sum(y for x, y in contour_pts) / n
        avg_radius_x = sum(abs(x - cx) for x, y in contour_pts) / n
        avg_radius_y = sum(abs(y - cy) for x, y in contour_pts) / n
        offsets = []
        for (x, y) in contour_pts:
            angle = math.atan2(y - cy, x - cx)
            ellipse_x = cx + avg_radius_x * 1.04 * math.cos(angle)
            ellipse_y = cy + avg_radius_y * 1.17 * math.sin(angle)
            offsets.append((ellipse_x - x, ellipse_y - y))
    else:
        offsets = [(0, 0)] * n
    return offsets




def morph_face_shape(points, face_type):
    contour_indices = FACE_CONTOUR
    contour_pts = [points[i] for i in contour_indices if i < len(points)]
    if not contour_pts:
        return points
    offsets = get_template_offsets(face_type, contour_pts)
    new_points = points.copy()
    for idx, i in enumerate(contour_indices):
        if i < len(points):
            ox, oy = offsets[idx]
            new_points[i] = (int(points[i][0] + ox), int(points[i][1] + oy))
    return new_points

def apply_scales_and_translations(
    points,
    face_x_scale, face_y_scale, face_x_trans, face_y_trans,
    eyes_x_scale, eyes_y_scale, eyes_x_trans, eyes_y_trans,
    nose_x_scale, nose_y_scale, nose_x_trans, nose_y_trans,
    nostrils_x_scale, nostrils_y_scale, nostrils_x_trans, nostrils_y_trans,
    lips_x_scale, lips_y_scale, lips_x_trans, lips_y_trans
):
    LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    RIGHT_EYE = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
    EYES = LEFT_EYE + RIGHT_EYE
    NOSE = [1, 2, 98, 327, 168, 197, 5, 4, 94, 19]
    LEFT_NOSTRIL = [49, 59, 60, 48]
    RIGHT_NOSTRIL = [279, 289, 290, 278]
    NOSTRILS = LEFT_NOSTRIL + RIGHT_NOSTRIL
    LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

    xs = [x for x, y in points]
    ys = [y for x, y in points]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)

    # Face scale/translate
    scaled = []
    for (x, y) in points:
        new_x = cx + (x - cx) * face_x_scale + face_x_trans
        new_y = cy + (y - cy) * face_y_scale + face_y_trans
        scaled.append((new_x, new_y))

    # Eyes
    eyes_pts = [scaled[i] for i in EYES if i < len(scaled)]
    if eyes_pts:
        ex = sum(x for x, y in eyes_pts) / len(eyes_pts)
        ey = sum(y for x, y in eyes_pts) / len(eyes_pts)
        for idx in EYES:
            if idx < len(scaled):
                x, y = scaled[idx]
                scaled[idx] = (
                    ex + (x - ex) * eyes_x_scale + eyes_x_trans,
                    ey + (y - ey) * eyes_y_scale + eyes_y_trans
                )
    # Nose
    nose_pts = [scaled[i] for i in NOSE if i < len(scaled)]
    if nose_pts:
        nx = sum(x for x, y in nose_pts) / len(nose_pts)
        ny = sum(y for x, y in nose_pts) / len(nose_pts)
        for idx in NOSE:
            if idx < len(scaled):
                x, y = scaled[idx]
                scaled[idx] = (
                    nx + (x - nx) * nose_x_scale + nose_x_trans,
                    ny + (y - ny) * nose_y_scale + nose_y_trans
                )
    # Nostrils
    nostrils_pts = [scaled[i] for i in NOSTRILS if i < len(scaled)]
    if nostrils_pts:
        nx = sum(x for x, y in nostrils_pts) / len(nostrils_pts)
        ny = sum(y for x, y in nostrils_pts) / len(nostrils_pts)
        for idx in NOSTRILS:
            if idx < len(scaled):
                x, y = scaled[idx]
                scaled[idx] = (
                    nx + (x - nx) * nostrils_x_scale + nostrils_x_trans,
                    ny + (y - ny) * nostrils_y_scale + nostrils_y_trans
                )
    # Lips
    lips_pts = [scaled[i] for i in LIPS if i < len(scaled)]
    if lips_pts:
        lx = sum(x for x, y in lips_pts) / len(lips_pts)
        ly = sum(y for x, y in lips_pts) / len(lips_pts)
        for idx in LIPS:
            if idx < len(scaled):
                x, y = scaled[idx]
                scaled[idx] = (
                    lx + (x - lx) * lips_x_scale + lips_x_trans,
                    ly + (y - ly) * lips_y_scale + lips_y_trans
                )
    return scaled


def draw_face_sketch(img, points):
    draw = ImageDraw.Draw(img)
    FACE_CONTOUR = [
        10, 338, 297, 332, 284, 251, 389, 356, 454, 323,
        361, 288, 397, 365, 379, 378, 400, 377, 152, 148,
        176, 149, 150, 136, 172, 58, 132, 93, 234, 127,
        162, 21, 54, 103, 67, 109, 151, 10
    ]
    LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    RIGHT_EYE = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
    LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
    NOSE_BRIDGE = [168, 197, 5, 4, 1, 19, 94, 2]
    LEFT_NOSTRIL = [49, 59, 60, 48]
    RIGHT_NOSTRIL = [279, 289, 290, 278]
    LEFT_EYEBROW = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
    RIGHT_EYEBROW = [336, 296, 334, 293, 300, 276, 283, 282, 295, 285]
    def draw_feature(indices, color=(0,0,0), width=2, close=True):
        pts = [points[i] for i in indices if i < len(points)]
        if len(pts) > 1:
            if close:
                draw.line(pts + [pts[0]], fill=color, width=width)
            else:
                draw.line(pts, fill=color, width=width)
    draw_feature(FACE_CONTOUR, color=(0,0,0), width=3, close=True)
    draw_feature(LEFT_EYE, color=(0,0,0), width=2, close=True)
    draw_feature(RIGHT_EYE, color=(0,0,0), width=2, close=True)
    draw_feature(LIPS, color=(80,0,0), width=2, close=True)
    draw_feature(NOSE_BRIDGE, color=(0,0,0), width=2, close=False)
    draw_feature(LEFT_NOSTRIL, color=(0,0,0), width=1, close=True)
    draw_feature(RIGHT_NOSTRIL, color=(0,0,0), width=1, close=True)
    draw_feature(LEFT_EYEBROW, color=(30,30,30), width=2, close=False)
    draw_feature(RIGHT_EYEBROW, color=(30,30,30), width=2, close=False)
    return img

def draw_outermost_face(img, points):
    draw = ImageDraw.Draw(img)
    pts = np.array(points)
    # Draw convex hull (outermost face line)
    if len(pts) >= 3:
        hull = ConvexHull(pts)
        hull_points = [tuple(pts[v]) for v in hull.vertices]
        draw.line(hull_points + [hull_points[0]], fill=(200,0,0), width=3)
    # Draw eyes, nose, lips (same style as sketch)
    LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    RIGHT_EYE = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
    LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
    NOSE_BRIDGE = [168, 197, 5, 4, 1, 19, 94, 2]
    LEFT_NOSTRIL = [49, 59, 60, 48]
    RIGHT_NOSTRIL = [279, 289, 290, 278]
    LEFT_EYEBROW = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
    RIGHT_EYEBROW = [336, 296, 334, 293, 300, 276, 283, 282, 295, 285]
    def draw_feature(indices, color=(0,0,0), width=2, close=True):
        pts_ = [points[i] for i in indices if i < len(points)]
        if len(pts_) > 1:
            if close:
                draw.line(pts_ + [pts_[0]], fill=color, width=width)
            else:
                draw.line(pts_, fill=color, width=width)
    draw_feature(LEFT_EYE, color=(0,0,0), width=2, close=True)
    draw_feature(RIGHT_EYE, color=(0,0,0), width=2, close=True)
    draw_feature(LIPS, color=(80,0,0), width=2, close=True)
    draw_feature(NOSE_BRIDGE, color=(0,0,0), width=2, close=False)
    draw_feature(LEFT_NOSTRIL, color=(0,0,0), width=1, close=True)
    draw_feature(RIGHT_NOSTRIL, color=(0,0,0), width=1, close=True)
    draw_feature(LEFT_EYEBROW, color=(30,30,30), width=2, close=False)
    draw_feature(RIGHT_EYEBROW, color=(30,30,30), width=2, close=False)
    return img



canvas_result = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=4,
    stroke_color="#222222",
    background_color="#FFFFFF",
    background_image=None,
    update_streamlit=True,
    height=512,
    width=512,
    drawing_mode="freedraw",
    key="canvas"
)



if "landmarks" not in st.session_state:
    st.session_state.landmarks = None
if "drawn_img" not in st.session_state:
    st.session_state.drawn_img = None

if st.button(" 👁️ Detect Face Mesh & Generate Sketch"):
    if canvas_result.image_data is not None:
        drawn_img = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA").convert("RGB")
        img_np = np.array(drawn_img)
        mp_face_mesh = mp.solutions.face_mesh
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
            results = face_mesh.process(img_np)
            if results.multi_face_landmarks:
                w, h = drawn_img.size
                points = []
                for lm in results.multi_face_landmarks[0].landmark:
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    points.append((x, y))
                st.session_state.landmarks = points
                st.session_state.drawn_img = drawn_img
            else:
                st.session_state.landmarks = None
                st.session_state.drawn_img = None
                st.error("No face detected in your drawing. Please try drawing a clearer face (frontal, with eyes, nose, mouth, and jawline).")
    else:
        st.warning("Please draw on the canvas first.")

if st.session_state.landmarks is not None and st.session_state.drawn_img is not None:
    points = st.session_state.landmarks
    drawn_img = st.session_state.drawn_img

    face_shape = classify_face_shape(points)
    st.info(f"**Detected Face Shape:** {face_shape}")

    face_shape_option = st.selectbox(
    "Choose face shape for sketch:",
    ["Round", "Square", "Oblong", "Heart", "Triangle","Rectangle","A-Triangle","Diamond", "Unknown"],
    index=["Round", "Square", "Oblong", "Heart", "Triangle","Rectangle","A-Triangle","Diamond", "Unknown"].index(face_shape) if face_shape in ["Round", "Square", "Oblong", "Heart", "Triangle","Rectangle","A-Triangle","Diamond", "Unknown"] else 5
)

    morphed_points = morph_face_shape(points, face_shape_option)

    col1, col2, col3, col4 = st.columns(4)

    # --- Controls in the sidebar ---
    st.sidebar.markdown("### Translation (move features)")
    face_x_trans = st.sidebar.slider("Face X Translation", -100, 100, 0, 1)
    face_y_trans = st.sidebar.slider("Face Y Translation", -100, 100, 0, 1)
    eyes_x_trans = st.sidebar.slider("Eyes X Translation", -50, 50, 0, 1)
    eyes_y_trans = st.sidebar.slider("Eyes Y Translation", -50, 50, 0, 1)
    nose_x_trans = st.sidebar.slider("Nose X Translation", -50, 50, 0, 1)
    nose_y_trans = st.sidebar.slider("Nose Y Translation", -50, 50, 0, 1)
    nostrils_x_trans = st.sidebar.slider("Nostrils X Translation", -50, 50, 0, 1)
    nostrils_y_trans = st.sidebar.slider("Nostrils Y Translation", -50, 50, 0, 1)
    lips_x_trans = st.sidebar.slider("Lips X Translation", -50, 50, 0, 1)
    lips_y_trans = st.sidebar.slider("Lips Y Translation", -50, 50, 0, 1)

    st.sidebar.markdown("### Scale (resize features)")
    face_x_scale = st.sidebar.slider("Face X Scale (Width)", 0.7, 1.3, 1.0, 0.01)
    face_y_scale = st.sidebar.slider("Face Y Scale (Height)", 0.7, 1.3, 1.0, 0.01)
    eyes_x_scale = st.sidebar.slider("Eyes X Scale (Width)", 0.7, 1.3, 1.0, 0.01)
    eyes_y_scale = st.sidebar.slider("Eyes Y Scale (Height)", 0.7, 1.3, 1.0, 0.01)
    nose_x_scale = st.sidebar.slider("Nose X Scale (Width)", 0.7, 1.3, 1.0, 0.01)
    nose_y_scale = st.sidebar.slider("Nose Y Scale (Height)", 0.7, 1.3, 1.0, 0.01)
    nostrils_x_scale = st.sidebar.slider("Nostrils X Scale (Width)", 0.7, 1.3, 1.0, 0.01)
    nostrils_y_scale = st.sidebar.slider("Nostrils Y Scale (Height)", 0.7, 1.3, 1.0, 0.01)
    lips_x_scale = st.sidebar.slider("Lips X Scale (Width)", 0.7, 1.3, 1.0, 0.01)
    lips_y_scale = st.sidebar.slider("Lips Y Scale (Height)", 0.7, 1.3, 1.0, 0.01)

    # --- Apply all scales and translations ---
    trans_points = apply_scales_and_translations(
    morphed_points,
    face_x_scale, face_y_scale, face_x_trans, face_y_trans,
    eyes_x_scale, eyes_y_scale, eyes_x_trans, eyes_y_trans,
    nose_x_scale, nose_y_scale, nose_x_trans, nose_y_trans,
    nostrils_x_scale, nostrils_y_scale, nostrils_x_trans, nostrils_y_trans,
    lips_x_scale, lips_y_scale, lips_x_trans, lips_y_trans
)
        # Loosen face sketch by spreading all points outward
    trans_points_loose = loosen_points(trans_points, loosen_factor=1.15)


    # --- Display all four images with the transformed points ---
    with col1:
        st.subheader("Drawing Overlay")
        mesh_img = drawn_img.copy()
        mp_face_mesh = mp.solutions.face_mesh
        draw = ImageDraw.Draw(mesh_img)
        for conn in mp_face_mesh.FACEMESH_TESSELATION:
            i, j = conn
            if i < len(trans_points) and j < len(trans_points):
                draw.line([trans_points_loose[i], trans_points_loose[j]], fill=(80, 80, 80), width=1)
        st.image(mesh_img, use_container_width=True)
        buf_mesh_overlay = io.BytesIO()
        mesh_img.save(buf_mesh_overlay, format="PNG")
        st.download_button("Download Mesh Overlay", buf_mesh_overlay.getvalue(), file_name="mesh_overlay.png", mime="image/png")

    with col2:
        st.subheader("Mesh Only")
        mesh_only_img = Image.new("RGB", drawn_img.size, (255, 255, 255))
        draw_only = ImageDraw.Draw(mesh_only_img)
        for conn in mp_face_mesh.FACEMESH_TESSELATION:
            i, j = conn
            if i < len(trans_points) and j < len(trans_points):
                draw_only.line([trans_points[i], trans_points[j]], fill=(80, 80, 80), width=1)
        st.image(mesh_only_img, use_container_width=True)
        buf_mesh = io.BytesIO()
        mesh_only_img.save(buf_mesh, format="PNG")
        st.download_button("Download Mesh Only", buf_mesh.getvalue(), file_name="mesh_only.png", mime="image/png")

    with col3:
        st.subheader("Contour Line Art ")
        sketch_img = draw_face_sketch(Image.new("RGB", drawn_img.size, (255,255,255)), trans_points)
        st.image(sketch_img, use_container_width=True)
        buf_sketch = io.BytesIO()
        sketch_img.save(buf_sketch, format="PNG")
        st.download_button("Download Face Sketch", buf_sketch.getvalue(), file_name="face_sketch.png", mime="image/png")

    with col4:
        st.subheader("Face Outline")
        outer_img = Image.new("RGB", drawn_img.size, (255,255,255))
        outer_img = draw_outermost_face(outer_img, trans_points)
        st.image(outer_img, use_container_width=True)
        buf_outer = io.BytesIO()
        outer_img.save(buf_outer, format="PNG")
        st.download_button("Download Outer Face Mesh", buf_outer.getvalue(), file_name="outer_face_mesh.png", mime="image/png")



