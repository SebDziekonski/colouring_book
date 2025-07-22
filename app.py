import base64
import streamlit as st
import os
import requests
import openai
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

    # --------------- API KEY GATE (LOCK SCREEN) ---------------

# Ensure state tracking
if "api_valid" not in st.session_state:
    st.session_state.api_valid = False
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""

if not st.session_state.api_valid:
    st.title("🔐 Welcome to Draw-a-Book!")
    st.markdown("Please enter your OpenAI API key to access the app.")
    
    with st.form("api_key_form"):
        key_input = st.text_input("Enter your OpenAI API Key", type="password")
        submit = st.form_submit_button("🔓 Unlock")

        if submit:
            try:
                # Quick test to validate API key
                client = openai.OpenAI(api_key=key_input)
                client.models.list()
                st.session_state.user_api_key = key_input
                st.session_state.api_valid = True
                st.experimental_rerun()  # Refresh app without showing input again
            except Exception:
                st.error("❌ Invalid API key. Please try again.")

    st.stop()  # Prevent the rest of the app from loading

# # --------------- SIDEBAR - API KEY ---------------
# st.sidebar.title("🔐 API Settings")
# st.session_state.user_api_key = st.sidebar.text_input(
#     "Enter your OpenAI API Key",
#     type="password",
#     value=st.session_state.user_api_key
# )
# if not st.session_state.user_api_key:
#     st.sidebar.warning("Please enter your OpenAI API key to use the app.")

# ------- Logo Display --------
def get_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = get_image_base64("logo.png")  

st.markdown(
    f"""
    <div style='display: flex; align-items: center; gap: 16px; margin-top: 20px;'>
        <img src='data:image/png;base64,{logo_base64}' width='50'>
        <h1 style='color: #ff6f61; font-size: 2.25rem; margin: 0;'>Draw-a-Book</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------- TABS ---------------
tab1, tab2, tab3 = st.tabs(["🖍️ Generate", "📚 View Sessions", "🗑️ Delete Sessions"])

# ========== TAB 1: GENERATE ==========
with tab1:
    st.header("🎨 Welcome to Coloruring Book Generator!!")
    st.markdown("""
        Welcome to the **Coloring Book Creator**! 🖍️✨  
        Here’s what you can do on this page:

        - 🎯 Enter a fun topic like **Space Adventures**, **Dancing Dinosaurs**, or **Underwater Castles**  
        - 🤖 Let the AI dream up creative coloring ideas based on your topic  
        - 🖼️ Generate beautiful black-and-white images ready to print and color  
        - 💾 Save your session to build your very own custom coloring book!

        Whether you're making pages for yourself or a whole book to share with others, you're in the right place.  
        **Ready to get creative? Choose a topic and start generating your magical coloring pages below! 🚀🖌️**
    """)

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

            # Save display state
            st.session_state.last_topic = topic
            st.session_state.last_ideas = st.session_state.ideas
            st.session_state.generated_session = session_name

            st.success("✅ Images generated! Scroll down to preview and save your session.")

    # Always show current images
    if st.session_state.get("image_paths"):
        st.subheader(f"🖼️ Your Coloring Pages for: {st.session_state.get('last_topic', '')}")
        for i, path in enumerate(st.session_state.image_paths):
            st.image(path, caption=st.session_state.last_ideas[i])

        st.subheader("💾 Save This Session")
        custom_name = st.text_input("Session name (optional)", "")
        final_session_name = custom_name if custom_name else st.session_state.generated_session
        if st.button("✅ Save Session"):
            save_session(final_session_name, st.session_state.last_topic, st.session_state.last_ideas, st.session_state.image_paths)
            st.success(f"Session '{final_session_name}' saved successfully!")



# ========== TAB 2: VIEW ==========
with tab2:
    st.header("📚 Browse Saved Sessions")
    st.markdown("""
    Welcome to your **Coloring Book Library**! 📁✨  
    Here's where all your saved coloring sessions live.

    - 🔍 Select a saved session from the dropdown list  
    - 🖼️ View the AI-generated images and their creative prompts  
    - ⬇️ Download your favorite pictures to print or share with friends  

    This is your creative archive — perfect for revisiting magical ideas or printing pages whenever you want.  
    **Explore your saved sessions below and relive the fun! 🎨📖**
    """)

    sessions = list_sessions()
    if sessions:
        selected = st.selectbox("Choose a session", sessions)
        if st.button("📥 Load Session"):
            topic, ideas, image_paths = load_session(selected)
            if topic:
                st.session_state.image_paths = image_paths
                st.session_state.last_ideas = ideas
                st.session_state.last_topic = topic

                st.subheader(f"🖼️ Coloring Pages from '{selected}'")
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
    st.markdown("""
    Welcome to the **Cleanup Corner**! 🧹🗂️  
    Here you can manage your coloring book sessions.

    - 🧾 Select a session you'd like to remove from your library  
    - ❌ Click the delete button to tidy up your saved creations  
    - 🚨 Don’t worry — this won’t delete anything unless you choose to!

    Keeping your coloring book space organized makes room for even more fun and fresh ideas.  
    **Ready to clean up? Pick a session and give it a little goodbye wave! 👋🖍️**
    """)
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
