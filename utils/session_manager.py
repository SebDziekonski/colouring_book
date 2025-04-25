import json
import os
import shutil

SESSION_DIR = "sessions"  # Folder where session files will be saved
IMAGE_DIR = os.path.join(SESSION_DIR, "images")

# Create the session directory if it doesn't exist
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

def save_session(session_name, topic, ideas, image_paths):
    try:
        session_data = {
            "topic": topic,
            "ideas": list(ideas),
            "image_paths": list(image_paths)
        }

        session_file = os.path.join(SESSION_DIR, f"{session_name}.json")

        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)

        print(f"✅ Session saved at: {session_file}")
    except Exception as e:
        print("❌ Error saving session:", e)

def load_session(session_name):
    session_file = os.path.join(SESSION_DIR, f"{session_name}.json")

    if not os.path.exists(session_file):
        return None, [], []

    try:
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("topic", ""), data.get("ideas", []), data.get("image_paths", [])
    except Exception as e:
        print("❌ Error loading session:", e)
        return None, [], []

def list_sessions():
    return [f.replace(".json", "") for f in os.listdir(SESSION_DIR) if f.endswith(".json")]

def delete_session(session_name):
    try:
        # Delete session file
        session_file = os.path.join(SESSION_DIR, f"{session_name}.json")
        if os.path.exists(session_file):
            os.remove(session_file)

        # Delete images folder associated with the session
        session_image_dir = os.path.join(IMAGE_DIR, session_name)
        if os.path.exists(session_image_dir):
            shutil.rmtree(session_image_dir)
        return True
    except Exception as e:
        print("❌ Error deleting session:", e)
        return False
