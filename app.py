import streamlit as st
import os
import requests
from dotenv import load_dotenv
from utils.idea_generator import generate_coloring_ideas
from utils.image_generator import generate_images
from utils.session_manager import save_session, load_session
import uuid
import shutil

# Load API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Directories
SESSION_DIR = "sessions"
IMAGE_DIR = os.path.join(SESSION_DIR, "images")
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# 🎨 Custom Styling
st.set_page_config(page_title="Coloring Book Generator", layout="wide")

st.markdown("""
    <style>
        .main {
            background-color: #fff5e6;
        }
        .title-text {
            font-size: 40px;
            color: #ff7f50;
            font-weight: bold;
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }
        .subheader {
            font-size: 22px;
            font-weight: bold;
            color: #ff6600;
        }
        .stButton>button {
            background-color: #ffcc70;
            color: black;
            font-weight: bold;
            border-radius: 10px;
        }
        .stTextInput>div>input {
            background-color: #fff8dc;
        }
        .stSelectbox>div>div {
            background-color: #fff8dc;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title-text">🖍️ Coloring Book Generator for Kids</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🎨 Generate", "📁 My Sessions", "🗑️ Delete Sessions"])

# --- TAB 1: Generate ---
with tab1:
    st.markdown('<div class="subheader">🎯 Enter Your Theme</div>', unsafe_allow_html=True)
    topic = st.text_input("e.g., Jungle Adventure or Space Explorers")

    st.markdown('<div class="subheader">🖼️ Number of Images</div>', unsafe_allow_html=True)
    num_images = st.slider("How many images to generate?", 1, 5, 1)

    if "generated_ideas" not in st.session_state:
        st.session_state.generated_ideas = []
    if "generated_image_paths" not in st.session_state:
        st.session_state.generated_image_paths = []

    if st.button("✨ Generate Coloring Images"):
        with st.spinner("🌟 Generating creative ideas..."):
            ideas = generate_coloring_ideas(topic, num_images, openai_api_key)

        with st.spinner("🎨 Creating beautiful coloring images..."):
            image_urls = generate_images(ideas, openai_api_key)

        image_paths = []
        session_id = str(uuid.uuid4())[:8]
        session_image_dir = os.path.join(IMAGE_DIR, f"{topic.replace(' ', '_')}_{session_id}")
        os.makedirs(session_image_dir, exist_ok=True)

        for i, url in enumerate(image_urls):
            image_data = requests.get(url).content
            image_path = os.path.join(session_image_dir, f"coloring_image_{i+1}.png")
            with open(image_path, "wb") as f:
                f.write(image_data)
            image_paths.append(image_path)

        st.session_state.generated_ideas = ideas
        st.session_state.generated_image_paths = image_paths
        st.session_state.session_image_dir = session_image_dir
        st.session_state.topic = topic

    # Display generated images
    if st.session_state.generated_image_paths:
        st.markdown('<div class="subheader">🖼️ Your Generated Images</div>', unsafe_allow_html=True)
        for i, path in enumerate(st.session_state.generated_image_paths):
            st.image(path, caption=st.session_state.generated_ideas[i])
            with open(path, "rb") as img_file:
                st.download_button("⬇️ Download", data=img_file, file_name=os.path.basename(path), key=f"download_{i}")

        st.markdown('<div class="subheader">💾 Save Your Session</div>', unsafe_allow_html=True)
        session_name = st.text_input("Give this session a fun name!")
        if st.button("💾 Save Session"):
            if session_name:
                session_name_with_id = f"{session_name}_{str(uuid.uuid4())[:8]}"
                save_session(session_name_with_id, st.session_state.topic, st.session_state.generated_ideas, st.session_state.generated_image_paths)
                st.success(f"✅ Session '{session_name_with_id}' saved!")
            else:
                st.warning("⚠️ Please enter a name for the session.")

# --- TAB 2: View Sessions ---
with tab2:
    st.markdown('<div class="subheader">📁 Load Saved Sessions</div>', unsafe_allow_html=True)
    saved_sessions = [f.replace(".json", "") for f in os.listdir(SESSION_DIR) if f.endswith(".json")]

    if saved_sessions:
        selected_session = st.selectbox("Choose a session to view:", saved_sessions, key="load_selector")
        if st.button("📂 Load Session"):
            topic, ideas, image_paths = load_session(selected_session)
            st.info(f"📚 Topic: {topic}")
            for i, path in enumerate(image_paths):
                st.image(path, caption=ideas[i])
                with open(path, "rb") as img_file:
                    st.download_button("⬇️ Download", data=img_file, file_name=os.path.basename(path), key=f"load_dl_{i}")
    else:
        st.warning("🕵️ No sessions found yet.")

# --- TAB 3: Delete Sessions ---
with tab3:
    st.markdown('<div class="subheader">🗑️ Manage Your Sessions</div>', unsafe_allow_html=True)
    saved_sessions = [f.replace(".json", "") for f in os.listdir(SESSION_DIR) if f.endswith(".json")]

    if saved_sessions:
        session_to_delete = st.selectbox("Select session to delete:", saved_sessions, key="delete_selector")
        if st.button("🗑️ Delete This Session"):
            try:
                os.remove(os.path.join(SESSION_DIR, session_to_delete + ".json"))
                session_image_folder = os.path.join(IMAGE_DIR, session_to_delete)
                if os.path.exists(session_image_folder):
                    shutil.rmtree(session_image_folder)
                st.success(f"🧹 Session '{session_to_delete}' deleted!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Error deleting session: {e}")
    else:
        st.info("🎒 No sessions to delete yet.")
