import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import io
import base64
import re
from dotenv import load_dotenv
import os
# 1. Page Configuration
st.set_page_config(page_title="ShobiAI Pro", page_icon="⚡", layout="centered")

## Premium Dark Theme UI and custom tweaks for File Uploader and Sidebar
st.html("""
    <style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0d0f14;
        color: #f3f4f6;
    }
    
    /* Elegant Chat Bubbles */
    div[data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 12px;
        border: 1px solid #1f2937;
    }
    
    /* Sidebar Professional Dashboard Custom Styling */
    section[data-testid="stSidebar"] {
        background-color: #111420 !important;
        border-right: 1px solid #1f2937;
    }
    
    .sidebar-card {
        background-color: #1b1e2e;
        border-radius: 12px;
        padding: 14px;
        border: 1px solid #2d3149;
        margin-bottom: 12px;
    }
    
    /* Clean CSS for File Uploader as an Input attachment */
    div[data-testid="stFileUploader"] {
        background-color: #161a29;
        border: 1px dashed #3b82f6;
        border-radius: 12px;
        padding: 8px;
    }
    
    /* Sidebar Metrics Cards */
    .metric-box {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        margin-top: 5px;
    }
    </style>
""")

st.title("⚡ ShobiAI: Pro Chatbot")

load_dotenv()

API_KEYS = [
    os.getenv("API_KEY_1"),
    os.getenv("API_KEY_2"),
    os.getenv("API_KEY_3"),
    os.getenv("API_KEY_4"),
]


if "key_index" not in st.session_state:
    st.session_state.key_index = 0

def get_current_client():
    current_key = API_KEYS[st.session_state.key_index]
    return genai.Client(api_key=current_key)

## --- 🔊 FUNCTION: Text to Speech Generator ---
def generate_voice_bytes(text, lang_code='en'):
    try:
        # Code blocks standard text ko discard karein taake code aloud na read ho (Avoid markdown syntax errors)
        clean_text = text.split("`" * 3)[0] 
        # Remove markdown stars, hashes, emojis for smooth voice experience
        clean_text = re.sub(r'[*#_`~🎵⚡🤖😂💻🎓]', '', clean_text)
        clean_text = clean_text.strip()
        
        if not clean_text:
            return None

        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        audio_bytes = fp.read()
        return base64.b64encode(audio_bytes).decode()
    except Exception:
        return None

## 3. Sidebar Pro Controls
st.sidebar.html("<h2 style='color:#3b82f6; text-align:center;'>💼 ShobiAI Dashboard</h2>")
st.sidebar.html("<p style='text-align:center; font-size:13px; color:#9ca3af;'>Enterprise Intelligent Console</p>")
st.sidebar.write("---")

# Feature 1: Language Selector inside sleek container
st.sidebar.markdown("**🌐 Core Dialect / ٻولي**")
selected_lang = st.sidebar.radio(
    "Select Language",
    ["English", "Urdu (اردو)", "Sindhi (سنڌي)"],
    label_visibility="collapsed"
)

# Feature 2: Persona Switcher
st.sidebar.html("<br><b>🎭 Assistant Personality Mode</b>")
selected_mode = st.sidebar.selectbox(
    "Select Persona",
    ["Standard AI Assistant 🤖", "Coding Expert Mode 💻", "Funny Mode 😂", "Teacher Mode 🎓"],
    label_visibility="collapsed"
)

## Dynamic Prompt Construction
base_instruction = "You are ShobiAI, a helpful, smart, and friendly AI chatbot created by Shoban Ali Khushk. Always identify yourself as ShobiAI."

# Set gTTS language code based on selection
if selected_lang == "Pure Sindhi (سنڌي)":
    gtts_lang = 'ur'  # Sindhi Arabic script matches Urdu voice engine phonetics perfectly
    base_instruction += " Strictly reply in beautifully written Sindhi script (سنڌي ٻولي اکرن ۾). Keep the Sindhi grammatically accurate and natural."
elif selected_lang == "Pure Urdu (اردو)":
    gtts_lang = 'ur'
    base_instruction += " Strictly reply in beautifully written Urdu script (اردو الفاظ)."
else:
    gtts_lang = 'en'
    base_instruction += " Reply in a mix of English and easy Roman Urdu/Hinglish, matching the user's tone."

if selected_mode == "Coding Expert Mode 💻":
    system_prompt = base_instruction + " You are now a world-class Coding Expert. Give precise code snippets and technical solutions."
elif selected_mode == "Funny Mode 😂":
    system_prompt = base_instruction + " You are now in a Funny Mode. Use light humor, crack safe jokes, use emojis, and reply in a witty or playful manner."
elif selected_mode == "Teacher Mode 🎓":
    system_prompt = base_instruction + " You are now an expert and patient Teacher. Explain complex topics using very simple everyday analogies."
else:
    system_prompt = base_instruction + " Respond nicely, smartly and professionally."

# Initialize conversation states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

#st.sidebar.write("---")
st.sidebar.markdown("**🛠️ Action Center**")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("📝 Summarize", use_container_width=True):
        if st.session_state.messages:
            with st.spinner("Analyzing..."):
                try:
                    client = get_current_client()
                    full_text = " ".join([m["content"] for m in st.session_state.messages])
                    summary_res = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"Summarize this conversation briefly in points: {full_text}"
                    )
                    st.sidebar.success(summary_res.text)
                except Exception:
                    st.sidebar.error("Error generating summary.")
        else:
            st.sidebar.warning("No chat yet!")

with col2:
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tts_audio = None
        st.rerun()

# Analytics Indicator
st.sidebar.html("<br><b>📈 Live Conversation Stats</b>")
st.sidebar.html(f"""
    <div class="metric-box">
        <span style="font-size: 11px; color: #9ca3af; text-transform: uppercase;">Total Active Turns</span><br>
        <span style="font-size: 20px; font-weight: bold; color: #10b981;">{len(st.session_state.messages)}</span>
    </div>
""")

st.info(f"🚀 Active Engine Mode: **{selected_mode}** | Language: **{selected_lang}**")

## 4. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def process_ai_input(user_prompt):
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        attempts = 0
        success = False
        
        while attempts < len(API_KEYS) and not success:
            try:
                client = get_current_client()
                gemini_history = []
                
                # Dynamic Context Memory structure creation
                for msg in st.session_state.messages[:-1]:
                    api_role = "model" if msg["role"] == "assistant" else "user"
                    parts_list = []
                    
                    # If this message contained a saved file payload, append it to the chat memory
                    if "file_data" in msg:
                        file_part = types.Part.from_bytes(
                            data=msg["file_data"],
                            mime_type=msg["file_mime"]
                        )
                        parts_list.append(file_part)
                        
                    parts_list.append(types.Part.from_text(text=msg["content"]))
                    
                    gemini_history.append(
                        types.Content(role=api_role, parts=parts_list)
                    )
                
                chat = client.chats.create(
                    model='gemini-2.5-flash',
                    history=gemini_history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt
                    )
                )
                
                # Check if the latest message has an active file payload
                current_msg_obj = st.session_state.messages[-1]
                if "file_data" in current_msg_obj:
                    current_file_part = types.Part.from_bytes(
                        data=current_msg_obj["file_data"],
                        mime_type=current_msg_obj["file_mime"]
                    )
                    response = chat.send_message([current_file_part, user_prompt])
                else:
                    response = chat.send_message(user_prompt)
                
                ai_response = response.text
                response_placeholder.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                success = True
                
                # Dynamic TTS payload generation - saved to session state to bypass st.rerun destruction
                tts_b64 = generate_voice_bytes(ai_response, lang_code=gtts_lang)
                if tts_b64:
                    st.session_state.tts_audio = tts_b64
                
                st.rerun()
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str or "UNAVAILABLE" in error_str:
                    attempts += 1
                    st.session_state.key_index = (st.session_state.key_index + 1) % len(API_KEYS)
                    response_placeholder.warning(f"Connecting to backup server proxy... (Attempt {attempts})")
                else:
                    response_placeholder.error(f"API Error: {e}")
                    break
        
        if not success and attempts >= len(API_KEYS):
            response_placeholder.error("All systems busy! 🛑 Please retry in 10-20 seconds.")

#st.write("---")
uploaded_file = st.file_uploader(
    "📎 Attach files, screenshots, or assignments right here to analyze:", 
    type=["png", "jpg", "jpeg", "txt", "py", "java", "pdf"],
    label_visibility="visible",
    key=f"uploader_{st.session_state.file_uploader_key}"
)

if user_input := st.chat_input("Type or ask anything about your files..."):
    new_message_dict = {"role": "user", "content": user_input}
    
    # Process attachment securely if present in current context
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        new_message_dict["file_data"] = file_bytes
        new_message_dict["file_mime"] = uploaded_file.type
        new_message_dict["content"] = f"📎 **File Attached:** `{uploaded_file.name}`\n\n{user_input}"
        # Increment key to clear/reset the file uploader widget instantly on next rerun
        st.session_state.file_uploader_key += 1
        
    st.session_state.messages.append(new_message_dict)
    st.rerun()

# Execute model call cleanly
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]
    process_ai_input(last_prompt)

# # --- 🔊 STATE-BASED VOICE OUTPUT AUTOPLAY (SAFE FROM REFRESH ERASURE) ---
# if "tts_audio" in st.session_state and st.session_state.tts_audio:
#     audio_html = f"""
#         <audio autoplay="true" style="display:none;">
#         <source src="data:audio/mp3;base64,{st.session_state.tts_audio}" type="audio/mp3">
#         </audio>
#         """
#     st.html(audio_html)
#     # Clear state so it doesn't replay when user interacts with other sidebar elements
#     st.session_state.tts_audio = None

if "tts_audio" in st.session_state and st.session_state.tts_audio:

    st.markdown("### 🔊 Voice")

    audio_bytes = base64.b64decode(st.session_state.tts_audio)

    st.audio(audio_bytes, format="audio/mp3")

    if st.button("🗑 Remove Voice"):
        st.session_state.tts_audio = None
        st.rerun()