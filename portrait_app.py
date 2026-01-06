import streamlit as st
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import random

# Page configuration
st.set_page_config(
    page_title="Zeno",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load environment variables
load_dotenv()

# Configuration
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "").strip().strip('"')
IMAGE_MODEL = "black-forest-labs/FLUX.1-dev"  # Better quality model
CHAT_MODEL = "meta-llama/Llama-3.2-11B-Vision-Instruct"  # Smarter chat model

# Initialize HuggingFace client
client = InferenceClient(token=HUGGINGFACE_TOKEN)

# Professional CSS styling - ChatGPT style
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* App background */
    .stApp {
        background: #ffffff;
    }

    .main {
        padding: 0 !important;
    }

    .block-container {
        padding: 0 !important;
        max-width: 800px !important;
    }

    /* Header */
    .header-container {
        background: #ffffff;
        padding: 1.25rem 2rem;
        border-bottom: 1px solid #e5e7eb;
        position: sticky;
        top: 0;
        z-index: 100;
    }

    .header-container h1 {
        color: #000000;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
    }

    /* Chat container */
    .chat-area {
        padding: 0rem 2rem 6rem 2rem;
        min-height: calc(100vh - 200px);
    }

    /* Chat messages */
    .message-container {
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }

    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.875rem;
        flex-shrink: 0;
    }

    .user-avatar {
        background: #10a37f;
        color: white;
    }

    .ai-avatar {
        background: #5436da;
        color: white;
    }

    .message-content {
        flex: 1;
        line-height: 1.7;
        font-size: 1rem;
        color: #000000;
    }

    /* Input area */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #ffffff;
        padding: 1.5rem 2rem 2rem 2rem;
        border-top: 1px solid #e5e7eb;
    }

    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #d1d5db;
        padding: 0.875rem 1rem;
        font-size: 1rem;
        background: #ffffff;
        color: #000000;
    }

    .stTextInput > div > div > input:focus {
        border-color: #10a37f;
        box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        padding: 0.625rem 1.25rem;
        transition: all 0.2s ease;
        border: none;
        font-size: 0.95rem;
    }

    .stButton > button[kind="primary"] {
        background: #10a37f;
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: #0d8a6a;
    }

    .stButton > button[kind="secondary"] {
        background: #f7f7f8;
        color: #000000;
        border: 1px solid #d1d5db;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #ececf1;
    }

    /* Image display */
    .image-container {
        margin: 1.5rem 0;
        border-radius: 8px;
        overflow: hidden;
    }

    .stImage {
        border-radius: 8px;
    }

    /* Download button */
    .stDownloadButton > button {
        background: #10a37f;
        color: white;
        border-radius: 8px;
        width: 100%;
        margin-top: 0.75rem;
        font-weight: 500;
        padding: 0.625rem;
    }

    .stDownloadButton > button:hover {
        background: #0d8a6a;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 0.5rem 2rem;
    }

    .empty-state h2 {
        color: #000000;
        font-weight: 400;
        margin: 0;
        font-size: 1.25rem;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: #10a37f !important;
    }

    /* Form */
    .stForm {
        padding-bottom: 6rem;
    }
</style>
<script>
    // Auto-scroll to bottom of chat
    window.addEventListener('load', function() {
        window.scrollTo(0, document.body.scrollHeight);
    });
</script>
""", unsafe_allow_html=True)

def enhance_image_prompt(user_prompt):
    """Enhance user prompt for better image generation"""
    # Add professional photography terms for realistic results
    enhancements = [
        "ultra realistic",
        "8k uhd",
        "high quality",
        "professional photography",
        "detailed",
        "sharp focus",
        "natural lighting",
        "depth of field"
    ]

    # Check if prompt already has quality terms
    if not any(term in user_prompt.lower() for term in ["realistic", "quality", "4k", "8k", "professional"]):
        return f"{user_prompt}, {', '.join(enhancements)}"
    return user_prompt

def generate_image(prompt):
    """Generate image from text prompt with enhanced quality"""
    try:
        # Enhance the prompt for better results
        enhanced_prompt = enhance_image_prompt(prompt)
        image = client.text_to_image(
            enhanced_prompt,
            model=IMAGE_MODEL,
            height=1024,
            width=1024
        )
        return image
    except Exception as e:
        error_msg = str(e)
        if "402" in error_msg or "Payment Required" in error_msg:
            return "error_quota"
        else:
            return f"error_{error_msg}"

def chat_with_ai(message):
    """Send message to AI and get response"""
    try:
        response = client.chat_completion(
            messages=[{"role": "user", "content": message}],
            model=CHAT_MODEL,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

def is_image_request(user_input):
    """Check if user wants to generate an image"""
    image_keywords = [
        "generate", "create", "make", "draw", "design",
        "image", "picture", "photo", "portrait", "art",
        "show me", "illustrate", "render", "visualize"
    ]

    # Check for keywords
    user_lower = user_input.lower()
    for keyword in image_keywords:
        if keyword in user_lower:
            return True
    return False

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("""
<div class="header-container">
    <h1>Zeno</h1>
</div>
""", unsafe_allow_html=True)

# Chat area
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <h2>How can I help you today?</h2>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="message-container">
                <div class="avatar user-avatar">U</div>
                <div class="message-content">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-container">
                <div class="avatar ai-avatar">Z</div>
                <div class="message-content">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)

            if msg.get("type") == "image" and msg.get("image"):
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(msg["image"])

                # Download button
                img_byte_arr = BytesIO()
                msg["image"].save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                st.download_button(
                    label="Download Image",
                    data=img_byte_arr,
                    file_name=f"zeno_{timestamp}.png",
                    mime="image/png"
                )
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input (fixed at bottom)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Message",
        placeholder="Message Zeno...",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([5, 1])
    with col2:
        send_button = st.form_submit_button("Send", type="primary", use_container_width=True)

if send_button and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input, "type": "text"})

    # Check if user wants to generate an image
    if is_image_request(user_input):
        st.session_state.messages.append({"role": "assistant", "content": "Creating your image...", "type": "text"})

        with st.spinner("Generating high-quality image..."):
            image = generate_image(user_input)

        if isinstance(image, str):
            st.session_state.messages[-1]["content"] = "I've reached my API quota. Please try again later."
        else:
            st.session_state.messages[-1] = {
                "role": "assistant",
                "content": "Here's your image!",
                "type": "image",
                "image": image
            }
    else:
        # Regular chat
        with st.spinner("Thinking..."):
            ai_response = chat_with_ai(user_input)
        st.session_state.messages.append({"role": "assistant", "content": ai_response, "type": "text"})

    st.rerun()
