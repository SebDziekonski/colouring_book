import streamlit as st
import os
import requests
from datetime import datetime
from utils.idea_generator import generate_coloring_ideas
from utils.image_generator import generate_images
from utils.session_manager import save_session, load_session, list_sessions, delete_session

# --------------- THEME & STYLING ---------------
st.set_page_config(page_title="Coloring Book Creator", page_icon="🖍️", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #fff8f0;
        }
        .main {
            background-color: #fff8f0;
        }
        h1, h2, h3 {
            color: #ff6f61;
        }
        .stButton>button {
            background-color: #ffcc70;
            color: black;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px 16px;
            margin-top: 10px;
        }
        .stButton>button:hover {
            background-color: #ffb347;
            color: white;
        }
        .stTextInput>div>div>input {
            font-size: 16px;
        }
        .stSlider>div>div>div {
            background-color: #ffd580;
        }
    </style>
""", unsafe_allow_html=True)

# --------------- SESSION STATE INIT ---------------
if "ideas" not in st.session_state:
    st.session_state.ideas = []
if "image_paths" not in st.session_state:
    st.session_state.image_paths = []
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""

# --------------- SIDEBAR - API KEY ---------------
st.sidebar.title("🔐 API Settings")
st.session_state.user_api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key",
    type="password",
    value=st.session_state.user_api_key
)
if not st.session_state.user_api_key:
    st.sidebar.warning("Please enter your OpenAI API key to use the app.")

st.header("Welcome to Coloruring Book Generator!!")

# --------------- TABS ---------------
tab1, tab2, tab3 = st.tabs(["🖍️ Generate", "📚 View Sessions", "🗑️ Delete Sessions"])

# ========== TAB 1: GENERATE ==========
with tab1:
    st.header("🖍️ Let's Make Some Coloring Pages!")
    st.markdown("Choose your theme and let the AI help draw the fun!")

    topic = st.text_input("🧠 Topic (e.g. Space Adventures)", "Jungle Animals")
    num_images = st.slider("🖼️ How many images to generate?", 1, 10, 3)

    if st.button("🚀 Generate Coloring Images"):
        if not st.session_state.user_api_key:
            st.warning("API key required to generate images.")
        else:
            with st.spinner("Thinking of fun ideas..."):
                st.session_state.ideas = generate_coloring_ideas(topic, num_images, st.session_state.user_api_key)

            with st.spinner("Drawing with AI magic..."):
                image_urls = generate_images(st.session_state.ideas, st.session_state.user_api_key)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"{topic.replace(' ', '_')}_{timestamp}"
            image_folder = os.path.join("sessions", "images", session_name)
            os.makedirs(image_folder, exist_ok=True)

            st.session_state.image_paths = []
            for i, url in enumerate(image_urls):
                image_data = requests.get(url).content
                img_path = os.path.join(image_folder, f"img_{i+1}.png")
                with open(img_path, "wb") as f:
                    f.write(image_data)
                st.session_state.image_paths.append(img_path)

            st.success("✅ Images generated! Scroll down to preview and save your session.")
            for i, path in enumerate(st.session_state.image_paths):
                st.image(path, caption=st.session_state.ideas[i])

            # Save form
            st.subheader("💾 Save This Session")
            custom_name = st.text_input("Session name (optional)", "")
            final_session_name = custom_name if custom_name else session_name
            if st.button("✅ Save Session"):
                save_session(final_session_name, topic, st.session_state.ideas, st.session_state.image_paths)
                st.success(f"Session '{final_session_name}' saved successfully!")



# ========== TAB 2: VIEW ==========
with tab2:
    st.header("📚 Browse Saved Sessions")
    sessions = list_sessions()
    if sessions:
        selected = st.selectbox("Choose a session", sessions)
        if st.button("📥 Load Session"):
            topic, ideas, image_paths = load_session(selected)
            if topic:
                st.subheader(f"Topic: {topic}")
                for i, img_path in enumerate(image_paths):
                    st.image(img_path, caption=ideas[i])
                    st.download_button("Download", open(img_path, "rb"), file_name=os.path.basename(img_path), key=f"dl_{i}")
            else:
                st.warning("Could not load session.")
    else:
        st.info("No saved sessions found. Go generate something cool!")

# ========== TAB 3: DELETE ==========
with tab3:
    st.header("🗑️ Manage and Delete Sessions")
    sessions = list_sessions()
    if sessions:
        selected = st.selectbox("Select a session to delete", sessions, key="delete_selector")
        if st.button("❌ Delete Selected Session"):
            success = delete_session(selected)
            if success:
                st.success(f"Session '{selected}' deleted.")
                st.rerun()
            else:
                st.error("Error deleting session.")
    else:
        st.info("Nothing to delete yet. Start creating fun pages!")
