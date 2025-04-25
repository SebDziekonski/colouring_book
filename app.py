import streamlit as st
import os
import requests
from datetime import datetime
from utils.idea_generator import generate_coloring_ideas
from utils.image_generator import generate_images
from utils.session_manager import save_session, load_session, delete_session, list_sessions
import uuid

# App styling
st.set_page_config(page_title="Kids Coloring Book Generator", layout="wide")

# Initialize session state
if "generated_ideas" not in st.session_state:
    st.session_state.generated_ideas = []
if "generated_image_paths" not in st.session_state:
    st.session_state.generated_image_paths = []
if "generated_image_urls" not in st.session_state:
    st.session_state.generated_image_urls = []
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""

# Ask for OpenAI API key
st.sidebar.title("🔐 API Key Required")
st.session_state.user_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.user_api_key)
if not st.session_state.user_api_key:
    st.sidebar.warning("API key required to use the app.")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["🎨 Generate Coloring Book", "📁 Saved Sessions", "🗑️ Manage Sessions"])

# --- 🎨 Generate Coloring Book ---
with tab1:
    st.header("🎨 Create New Coloring Book Page")

    topic = st.text_input("📝 Enter a topic for the coloring book", "Underwater Adventure")
    num_images = st.slider("📷 How many images?", 1, 10, 1)

    if st.button("Generate Coloring Page"):
        with st.spinner("Generating ideas..."):
            ideas = generate_coloring_ideas(topic, num_images, st.session_state.user_api_key)

        with st.spinner("Generating images..."):
            image_urls = generate_images(ideas, st.session_state.user_api_key)

        image_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{topic.replace(' ', '_')}_{timestamp}_{str(uuid.uuid4())[:8]}"
        session_folder = os.path.join("sessions", "images", session_id)
        os.makedirs(session_folder, exist_ok=True)

        for i, url in enumerate(image_urls):
            image_data = requests.get(url).content
            image_path = os.path.join(session_folder, f"{session_id}_{i + 1}.png")
            with open(image_path, "wb") as f:
                f.write(image_data)
            image_paths.append(image_path)

        st.session_state.generated_ideas = ideas
        st.session_state.generated_image_paths = image_paths
        st.session_state.generated_image_urls = image_urls
        st.session_state.current_session_id = session_id
        st.session_state.current_topic = topic

    # Display generated content
    if st.session_state.generated_ideas and st.session_state.generated_image_paths:
        st.subheader("🖼️ Preview")
        for i, path in enumerate(st.session_state.generated_image_paths):
            st.image(path, caption=st.session_state.generated_ideas[i])
            st.download_button("⬇️ Download Image", data=open(path, "rb"), file_name=os.path.basename(path), key=f"download_{i}")

        # Save session
        session_name = st.text_input("💾 Name your session:", "")
        if st.button("💾 Save Session"):
            if session_name:
                save_session(session_name, st.session_state.current_topic, st.session_state.generated_ideas, st.session_state.generated_image_paths)
                st.success(f"✅ Session '{session_name}' saved!")
            else:
                st.warning("⚠️ Please enter a session name before saving.")

# --- 📁 Saved Sessions ---
with tab2:
    st.header("📁 Saved Sessions")
    sessions = list_sessions()
    if not sessions:
        st.info("No saved sessions yet. Generate and save your first one in the first tab!")
    else:
        selected = st.selectbox("Choose a session to load", sessions)
        if st.button("📂 Load Session"):
            topic, ideas, image_paths = load_session(selected)
            st.success(f"✅ Loaded session: {selected} (Topic: {topic})")
            for i, path in enumerate(image_paths):
                st.image(path, caption=ideas[i])
                st.download_button("⬇️ Download", data=open(path, "rb"), file_name=os.path.basename(path), key=f"load_dl_{i}")

# --- 🗑️ Manage Sessions ---
with tab3:
    st.header("🗑️ Delete Saved Sessions")
    sessions = list_sessions()
    if not sessions:
        st.info("No sessions to delete.")
    else:
        session_to_delete = st.selectbox("Select a session to delete", sessions, key="delete_box")
        if st.button("❌ Delete Session"):
            delete_session(session_to_delete)
            st.success(f"🗑️ Session '{session_to_delete}' deleted!")
            st.rerun()
