import streamlit as st
import sqlite3
import base64
import os
import json
import uuid
import datetime


st.set_page_config(page_title="Demore Gallery", layout="wide")

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


DB_PATH = "portfolio.db"

def ensure_likes_column(db_path="portfolio.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE projects ADD COLUMN likes INTEGER DEFAULT 0")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            print("Error adding likes column:", e)
    conn.commit()
    conn.close()

# ✅ Call this before anything uses likes
ensure_likes_column()

def ensure_likes_column_and_print_schema(db_path="portfolio.db"):
    import sqlite3
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Print schema before
    c.execute("PRAGMA table_info(projects)")
    columns_before = c.fetchall()
    print("projects table schema (before):")
    for col in columns_before:
        print(col)

    # Try to add 'likes' column
    try:
        c.execute("ALTER TABLE projects ADD COLUMN likes INTEGER DEFAULT 0")
        print("Added 'likes' column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'likes' column already exists.")
        else:
            print("Some other error:", e)

    # Print schema after
    c.execute("PRAGMA table_info(projects)")
    columns_after = c.fetchall()
    print("projects table schema (after):")
    for col in columns_after:
        print(col)

    conn.commit()
    conn.close()


def print_projects_table_schema(db_path="portfolio.db"):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(projects)")
    columns = cursor.fetchall()
    conn.close()
    print("projects table schema:")
    for col in columns:
        print(col)


def load_gallery_projects():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Needed to access column names as keys
    c = conn.cursor()
    c.execute("""
        SELECT 
            id, user_id, type, header, designer, categories, hashtag,
            designer_social, comment, image1_path, image2_path,
            video_path, created_at, is_public_profile, is_gallery_public, likes
        FROM projects
        WHERE is_gallery_public=1
        ORDER BY created_at DESC
    """)
    projects = c.fetchall()
    conn.close()
    return projects


def image_to_base64(path):
    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

def get_categories(p):
    try:
        cats = json.loads(p["categories"]) if isinstance(p["categories"], str) else p["categories"]
        return ", ".join([c.strip() for c in cats if c.strip()])
    except Exception:
        return str(p["categories"])



def get_artist_profile_link(p):
    try:
        user_id = p["user_id"]
        artist_name = p["designer"] if p["designer"] else "Unknown Artist"
    except KeyError:
        user_id = p[1]  # fallback if not using sqlite3.Row
        artist_name = "Unknown Artist"
    return f'<a href="?artist_id={user_id}" target="_self">{artist_name}</a>'


def fetch_profile_from_db(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM profile WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

# === LIKE UTILS ===

def get_user_fingerprint():
    if "user_fingerprint" not in st.session_state:
        st.session_state["user_fingerprint"] = str(uuid.uuid4())
    return st.session_state["user_fingerprint"]


def is_liked(project_id, fingerprint):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM project_likes WHERE project_id = ? AND fingerprint = ?", (project_id, fingerprint))
    liked = c.fetchone() is not None
    conn.close()
    return liked

def toggle_like(project_id, fingerprint):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if is_liked(project_id, fingerprint):
        c.execute("UPDATE projects SET likes = likes - 1 WHERE id = ?", (project_id,))
        c.execute("DELETE FROM project_likes WHERE project_id = ? AND fingerprint = ?", (project_id, fingerprint))
    else:
        c.execute("UPDATE projects SET likes = likes + 1 WHERE id = ?", (project_id,))
        c.execute("INSERT INTO project_likes (project_id, fingerprint, liked_at) VALUES (?, ?, ?)",
                  (project_id, fingerprint, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

# === USAGE INSIDE GALLERY CARD ===
def render_like_button(p):
    # --- Internal helper for formatting numbers ---
    def short_number(n):
        """Display numbers like 1, 999, 1k, 10k, 100k, 1M, etc."""
        try:
            n = int(n)
        except (ValueError, TypeError):
            n = 0
        if n < 1_000:
            return str(n)
        elif n < 10_000:
            return f"{n // 1_000}k"
        elif n < 100_000:
            return f"{(n // 1_000) * 1}k"
        elif n < 1_000_000:
            return f"{(n // 100_0) * 10}k"
        else:
            return f"{n // 1_000_000}M"

    fingerprint = get_user_fingerprint()
    project_id = p[0]
    # Ensure correct index for 'likes' and type
    current_likes = p["likes"] if p["likes"] is not None else 0
    shown_count = short_number(current_likes)
    liked = is_liked(project_id, fingerprint)
    heart = "❤️" if liked else "🤍"
    key_suffix = str(project_id)[:8]
    st.markdown("<div style='margin-top:4px; text-align:center;'>", unsafe_allow_html=True)
    if st.button(f"{heart} {shown_count}", key=f"like_{key_suffix}"):
        toggle_like(project_id, fingerprint)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)






# === CREATE TABLE IF NOT EXISTS ===
def create_likes_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS project_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        fingerprint TEXT,
        liked_at TEXT
    )
    """)
    conn.commit()
    conn.close()

# === FULL VIEW RENDERER ===
import html  # Ensure this is imported at the top of your file

import html  # Ensure this is at the top of your file

def build_info_html(p):
    # --- Safe header and category access ---
    header = html.escape(p["header"]) if "header" in p.keys() and p["header"] else "Untitled"
    categories = html.escape(get_categories(p)) if "categories" in p.keys() else ""

    # --- Escape and format multiline comments ---
    comment_raw = p["comment"] if "comment" in p.keys() and p["comment"] else ""
    comment = html.escape(comment_raw).replace("\n", "<br>")

    # --- Hashtags ---
    raw_hashtag = p["hashtag"] if "hashtag" in p.keys() and p["hashtag"] else ""
    try:
        hashtags = json.loads(raw_hashtag) if raw_hashtag.strip().startswith("[") else raw_hashtag.split()
    except:
        hashtags = raw_hashtag.split()
    hashtags = [html.escape(tag.strip()) for tag in hashtags if tag.strip()]
    hashtag_html = " ".join(hashtags)

    # --- Profile (about + social) ---
    profile = fetch_profile_from_db(p["user_id"])
    about_block = ""
    social_block = ""

    if profile:
        # About Artist
        if profile[2]:  # about_public
            about_text = html.escape(profile[1]) if profile[1] else "No bio available."
            about_block = f"<div><b>About Artist:</b> {about_text}</div>"

        # Social Media
        if profile[4]:  # social_public
            raw_links = profile[3] or ""
            links = [s.strip().strip("'\"") for s in raw_links.split(",") if s.strip()]

            def fmt_link(s):
                safe = html.escape(s)
                if "@" in s and not s.startswith("http"):
                    return f'<a href="mailto:{safe}" target="_blank" style="color:#1976d2;">{safe}</a>'
                if not s.startswith("http"):
                    return f'<a href="https://{safe}" target="_blank" style="color:#1976d2;">{safe}</a>'
                return f'<a href="{safe}" target="_blank" style="color:#1976d2;">{safe}</a>'

            if links:
                formatted_links = [fmt_link(link) for link in links]
                social_block = f"<div><b>Social Media:</b><br>{'<br>'.join(formatted_links)}</div>"

    # --- Final HTML block ---
    info_html = f"""
    <div style="margin-top:18px; font-size:1.05em; text-align:left;">
        <div><b>Categories:</b> {categories}</div>
        <div><b>Hashtag:</b> {hashtag_html}</div>
        <div><b>Comment:</b> {comment}</div>
        {about_block}
        {social_block}
    </div>
    """
    return info_html





def render_full_view(project):
    images_html = ""

    # --- Show sketch, regular, or video content ---
    if project["type"] == "sketch":
        if project["image1_path"] and os.path.exists(project["image1_path"]):
            images_html += f'<img src="data:image/png;base64,{image_to_base64(project["image1_path"])}" style="max-width:45%; margin:10px; border-radius:15px;" />'
        if project["image2_path"] and os.path.exists(project["image2_path"]):
            images_html += f'<img src="data:image/png;base64,{image_to_base64(project["image2_path"])}" style="max-width:45%; margin:10px; border-radius:15px;" />'
    elif project["type"] == "regular":
        if project["image1_path"] and os.path.exists(project["image1_path"]):
            images_html += f'<img src="data:image/png;base64,{image_to_base64(project["image1_path"])}" style="max-width:90%; margin:10px; border-radius:15px;" />'
    elif project["type"] == "video" and project["video_path"] and os.path.exists(project["video_path"]):
        st.video(project["video_path"])

    # --- Build the metadata section ---
    info_html = build_info_html(project)

    # --- Render the full layout ---
    st.markdown(f"""
    <div style="padding:20px 10px 30px 10px; background-color:#fafafa; border-radius:16px; border:1px solid #ddd;">
        <h3 style="text-align:center;">{html.escape(project["header"] or "Untitled")}</h3>
        <div style="display:flex; flex-wrap:wrap; justify-content:center;">
            {images_html}
        </div>
        {info_html}
    </div>
    """, unsafe_allow_html=True)




# === GALLERY CARD RENDER ===
st.markdown("""
<style>
/* Flat and downsized buttons */
button[data-baseweb="button"] {
    font-size: 10px !important;
    padding: 4px !important;
    height: 20px !important;
    width: 20px !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Center icon inside */
button[data-baseweb="button"] > div {
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)


def render_gallery_tab(projects, type, columns):
    filtered = sort_projects(projects)
    if not filtered:
        st.info(f"No {type} projects available.")
        return

    for i in range(0, len(filtered), columns):
        row = st.columns(columns)

        for j in range(columns):
            if i + j >= len(filtered):
                continue

            p = filtered[i + j]
            pid = f"like_{str(p['id'])[:6]}"
            st.session_state.setdefault("expanded_project_id", None)
            is_expanded = st.session_state["expanded_project_id"] == pid

            with row[j]:
                st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)

                # === Metadata ===
                short_header = (p["header"][:8] + "...") if len(p["header"]) > 8 else p["header"]
                category_full = get_categories(p)
                short_category = category_full.split(",")[0].strip() if "," in category_full else category_full
                short_category = (short_category[:8] + "...") if len(short_category) > 8 else short_category

                artist_link_html = get_artist_profile_link(p)
                if ">" in artist_link_html and "</a>" in artist_link_html:
                    start = artist_link_html.find(">") + 1
                    end = artist_link_html.find("</a>")
                    inner_text = artist_link_html[start:end]
                    short_inner = (inner_text[:6] + "...") if len(inner_text) > 6 else inner_text
                    short_artist = artist_link_html.replace(inner_text, short_inner)
                else:
                    short_artist = artist_link_html

                st.markdown(f"""
                    <div style="display:flex; justify-content:center; align-items:center; gap:10px; font-size:0.8em; margin-bottom:6px; flex-wrap:wrap;">
                        <div style="font-weight:600;">{short_header}</div>
                        <div style="color:gray;">📂 {short_category}</div>
                        <div style="color:#888;">👩‍🎨 {short_artist}</div>
                    </div>
                """, unsafe_allow_html=True)

                # === Image or Video Preview ===
                if type == "sketch":
                    sketch_b64 = image_to_base64(p["image1_path"])
                    final_b64 = image_to_base64(p["image2_path"])
                    st.markdown(f"""
                        <div style="display:flex; justify-content:center; gap:1px; margin-bottom:6px;">
                            <img src="data:image/png;base64,{sketch_b64}" style="width:100px; height:150px; border-radius:10px; object-fit:cover;" />
                            <img src="data:image/png;base64,{final_b64}" style="width:100px; height:150px; border-radius:10px; object-fit:cover;" />
                        </div>
                    """, unsafe_allow_html=True)

                elif type == "video" and p["video_path"] and os.path.exists(p["video_path"]):
                    st.video(p["video_path"])

                else:
                    img_b64 = image_to_base64(p["image1_path"])
                    st.markdown(f"""
                        <img src="data:image/png;base64,{img_b64}" style="width:100%; height:120px; border-radius:10px; object-fit:cover;" />
                    """, unsafe_allow_html=True)

                # === Action Buttons Row ===
                col_count = 4 if type == "sketch" else 3
                emoji_cols = st.columns(col_count)
                col_index = 0

                if type == "sketch":
                    if p["image1_path"] and os.path.exists(p["image1_path"]):
                        with emoji_cols[col_index]:
                            with open(p["image1_path"], "rb") as f:
                                st.download_button("⬇️", f, file_name="sketch_" + os.path.basename(p["image1_path"]), key=f"dl1_{pid}")
                        col_index += 1
                    if p["image2_path"] and os.path.exists(p["image2_path"]):
                        with emoji_cols[col_index]:
                            with open(p["image2_path"], "rb") as f:
                                st.download_button("⬇️", f, file_name="final_" + os.path.basename(p["image2_path"]), key=f"dl2_{pid}")
                        col_index += 1
                elif type == "video" and p["video_path"] and os.path.exists(p["video_path"]):
                    with emoji_cols[col_index]:
                        with open(p["video_path"], "rb") as f:
                            st.download_button("⬇️", f, file_name=os.path.basename(p["video_path"]), key=f"dlv_{pid}")
                    col_index += 1
                else:
                    if p["image1_path"] and os.path.exists(p["image1_path"]):
                        with emoji_cols[col_index]:
                            with open(p["image1_path"], "rb") as f:
                                st.download_button("⬇️", f, file_name=os.path.basename(p["image1_path"]), key=f"dli_{pid}")
                        col_index += 1

                # View Full Toggle
                with emoji_cols[col_index]:
                    if st.button("⛶" if not is_expanded else "x", key=f"view_{pid}"):
                        st.session_state["expanded_project_id"] = None if is_expanded else pid
                        st.rerun()
                col_index += 1

                # Like Button
                fingerprint = get_user_fingerprint()
                liked = is_liked(p["id"], fingerprint)
                heart = "❤️" if liked else "🤍"
                like_label = f"{heart} {p['likes'] if p['likes'] else 0}"
                with emoji_cols[col_index]:
                    if st.button(like_label, key=f"like_{pid}"):
                        toggle_like(p["id"], fingerprint)
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

                # === Expanded Full View Below ===
                if is_expanded:
                    st.markdown("---")
                    render_full_view(p)



# === FILTERS & TABS ===
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap" rel="stylesheet">
<style>
.beauty-title {
    font-family: 'Cinzel Decorative', cursive;
    font-size: 40px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

import streamlit as st
import base64
import os

# === Encode the image to base64 ===
def image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Local image path
image_path = "Gallery.png"  # Change path if needed
if os.path.exists(image_path):
    img_b64 = image_to_base64(image_path)
    st.markdown(f"""
        <div style='width:100%; text-align:center; margin-bottom: 20px;'>
            <div style='display:inline-flex; align-items:center; gap:12px;'>
                <img src='data:image/png;base64,{img_b64}' style='height: 38px; margin-top: 4px;' />
                <h1 style='font-family:"Cinzel Decorative", serif; margin: 0;'>Demore Gallery</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align:center;'>Demore Gallery</h1>", unsafe_allow_html=True)



#st.markdown("Browse artist creations across styles, sketches, and AI designs!")

projects = load_gallery_projects()
sketch_projects = [p for p in projects if p["type"] == "sketch"]
regular_projects = [p for p in projects if p["type"] == "regular"]
ai_projects = [p for p in projects if p["type"] == "ai"]
video_projects = [p for p in projects if p["type"] == "video"]

# --- Extract all unique categories ---
all_categories = sorted({cat.strip() for p in projects for cat in get_categories(p).split(",") if cat.strip()})

# --- Display 3 filters in one row ---
col1, col2, col3 = st.columns([1.5, 2.5, 1])

with col1:
    selected_cats = st.multiselect("Filter by category:", all_categories, default=[])

with col2:
    search_tag = st.text_input("Search by 👩‍🎨 artist name, #hashtag, or keyword", "")

with col3:
    sort_option = st.selectbox("Sort by:", ["Newest", "Likes"])


def matches_filter(p):
    search_lower = search_tag.lower()

    # --- Safely extract fields using dictionary-style access ---
    artist_name = (p["artist_name"] if "artist_name" in p.keys() and p["artist_name"] else p["designer"] if "designer" in p.keys() and p["designer"] else "").lower()
    title = (p["header"] if "header" in p.keys() and p["header"] else "").lower()
    comment = (p["comment"] if "comment" in p.keys() and p["comment"] else "").lower()

    # Categories
    project_cats = [c.strip().lower() for c in get_categories(p).split(",")]

    # Hashtags
    raw_hashtags = p["hashtag"] if "hashtag" in p.keys() and p["hashtag"] else ""
    try:
        hashtags = json.loads(raw_hashtags) if raw_hashtags.strip().startswith("[") else raw_hashtags.split(",")
    except:
        hashtags = raw_hashtags.split(",")
    hashtags = [h.strip().lower() for h in hashtags]

    # Tag match = search term appears in ANY field
    tag_match = any(
        search_lower in val
        for val in [artist_name, title, comment] + project_cats + hashtags
    )

    # Category filter match
    cat_match = not selected_cats or any(c in project_cats for c in map(str.lower, selected_cats))

    return tag_match and cat_match




def sort_projects(proj_list):
    filtered = [p for p in proj_list if matches_filter(p)]
    if sort_option == "Likes":
        filtered.sort(key=lambda x: x["likes"] if x["likes"] is not None else 0, reverse=True)
    else:
        filtered.sort(key=lambda x: x["created_at"], reverse=True)  # Newest
    return filtered

st.markdown("You can like an image multiple times after refereshing page")
tabs = st.tabs(["⋮ Face Sketch", "⋮ Single Face", "⋮ Video"])

with tabs[0]:
    render_gallery_tab(sketch_projects, "sketch", 4)

with tabs[1]:
    render_gallery_tab(regular_projects, "regular", 4)

#with tabs[2]:
#    render_gallery_tab(ai_projects, "ai", 5)

with tabs[2]:
    render_gallery_tab(video_projects, "video", 4)
