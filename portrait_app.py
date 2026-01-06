import streamlit as st
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import random

# Page configuration
st.set_page_config(
    page_title="AI Creative Assistant",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load environment variables
load_dotenv()

# Configuration
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "").strip().strip('"')
MODEL_NAME = "black-forest-labs/FLUX.1-schnell"

# Initialize HuggingFace client
client = InferenceClient(token=HUGGINGFACE_TOKEN)

# Custom CSS for ChatGPT-like styling
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container */
    .main {
        padding: 0;
        max-width: 100%;
    }

    .block-container {
        padding: 1rem 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Header */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        margin: -1rem -2rem 2rem -2rem;
        border-bottom: 1px solid #e5e7eb;
    }

    .app-header h1 {
        color: white;
        font-size: 1.75rem;
        font-weight: 600;
        margin: 0;
    }

    .app-header p {
        color: rgba(255,255,255,0.9);
        font-size: 0.95rem;
        margin: 0.25rem 0 0 0;
    }

    /* Chat messages */
    .chat-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        min-height: 500px;
        max-height: 600px;
        overflow-y: auto;
    }

    .message {
        margin-bottom: 1.5rem;
        display: flex;
        gap: 0.75rem;
    }

    .message-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.85rem;
        flex-shrink: 0;
    }

    .user-avatar {
        background: #667eea;
        color: white;
    }

    .assistant-avatar {
        background: #10b981;
        color: white;
    }

    .message-content {
        flex: 1;
        line-height: 1.6;
    }

    .message-role {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.25rem;
        color: #374151;
    }

    .message-text {
        color: #1f2937;
        font-size: 0.95rem;
    }

    /* Input area */
    .stTextInput input {
        border-radius: 24px;
        border: 2px solid #e5e7eb;
        padding: 0.75rem 1.25rem;
        font-size: 0.95rem;
    }

    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 24px;
        font-weight: 500;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s ease;
        border: none;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Image display */
    .generated-image-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }

    .stImage {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Quick actions */
    .quick-actions {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }

    /* Download button */
    .stDownloadButton > button {
        background: #10b981;
        color: white;
        border-radius: 8px;
        width: 100%;
        margin-top: 1rem;
    }

    .stDownloadButton > button:hover {
        background: #059669;
    }

    /* Placeholder text */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #9ca3af;
    }

    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Character and prompt configuration
BASE_CHARACTER = "a stylish man in his late 20s with a full brown beard, wearing trendy sunglasses, casual modern clothing"

ACTIVITIES = [
    "relaxing at a beach bar with a drink",
    "sitting at a rooftop cafe during sunset",
    "walking through a city street",
    "standing on a yacht deck",
    "enjoying coffee at an outdoor cafe",
    "lounging by a pool"
]

CLOTHING = [
    "wearing a casual hoodie and sunglasses",
    "in a stylish bomber jacket",
    "wearing a fitted t-shirt and chain necklace",
    "in a linen button-up shirt"
]

SETTINGS = [
    "warm sunset lighting, golden hour",
    "soft natural lighting, afternoon",
    "vibrant beach atmosphere",
    "urban city background, evening"
]

DETAILS = [
    "photorealistic, high quality, professional photography",
    "cinematic portrait, 4k quality, sharp focus"
]

def generate_random_portrait():
    """Generate a random scenario for the character"""
    activity = random.choice(ACTIVITIES)
    clothing = random.choice(CLOTHING)
    setting = random.choice(SETTINGS)
    detail = random.choice(DETAILS)
    return f"{BASE_CHARACTER}, {clothing}, {activity}, {setting}, {detail}"

def generate_image(prompt):
    """Generate image from text prompt"""
    try:
        image = client.text_to_image(prompt, model=MODEL_NAME)
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
            model="meta-llama/Llama-3.2-3B-Instruct",
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

# Header
st.markdown("""
<div class="app-header">
    <h1>AI Creative Assistant</h1>
    <p>Chat naturally or ask me to generate images</p>
</div>
""", unsafe_allow_html=True)

# Main chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">💬</div>
        <h3>How can I help you today?</h3>
        <p>Start a conversation or ask me to generate an image</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="message">
                <div class="message-avatar user-avatar">You</div>
                <div class="message-content">
                    <div class="message-text">{msg['content']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message">
                <div class="message-avatar assistant-avatar">AI</div>
                <div class="message-content">
                    <div class="message-text">{msg['content']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Display generated image if exists
if st.session_state.generated_image:
    st.markdown('<div class="generated-image-container">', unsafe_allow_html=True)
    st.markdown("**Generated Image**")
    st.image(st.session_state.generated_image)

    # Download button
    img_byte_arr = BytesIO()
    st.session_state.generated_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_portrait_{timestamp}.png"

    st.download_button(
        label="Download Image",
        data=img_byte_arr,
        file_name=filename,
        mime="image/png"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Quick action buttons
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    if st.button("Generate Random Portrait", use_container_width=True):
        prompt = generate_random_portrait()
        st.session_state.messages.append({"role": "user", "content": "Generate a random portrait"})
        st.session_state.messages.append({"role": "assistant", "content": "Generating a random portrait for you..."})

        with st.spinner("Creating image..."):
            image = generate_image(prompt)

        if isinstance(image, str):
            if "error_quota" in image:
                st.session_state.messages[-1]["content"] = "I've reached the API quota limit. Please try again later or upgrade your plan."
            else:
                st.session_state.messages[-1]["content"] = f"Sorry, I couldn't generate the image. {image}"
        else:
            st.session_state.generated_image = image
            st.session_state.messages[-1]["content"] = "I've generated a random portrait for you! Check it out above."
        st.rerun()

with col2:
    if st.button("Custom Image Prompt", use_container_width=True):
        st.session_state.show_prompt_input = True

with col3:
    if st.button("Clear", use_container_width=True):
        st.session_state.messages = []
        st.session_state.generated_image = None
        st.session_state.show_prompt_input = False
        st.rerun()

# Custom prompt input (if toggled)
if st.session_state.get("show_prompt_input", False):
    with st.form(key="custom_form", clear_on_submit=True):
        custom_input = st.text_input("Describe the image you want to create", placeholder="E.g., a person at sunset on a beach...")
        submit_custom = st.form_submit_button("Generate Image", type="primary", use_container_width=True)

        if submit_custom and custom_input:
            st.session_state.messages.append({"role": "user", "content": custom_input})
            st.session_state.messages.append({"role": "assistant", "content": "Creating your custom image..."})

            with st.spinner("Generating..."):
                image = generate_image(custom_input)

            if isinstance(image, str):
                if "error_quota" in image:
                    st.session_state.messages[-1]["content"] = "API quota exceeded. Please try again later."
                else:
                    st.session_state.messages[-1]["content"] = f"Couldn't generate the image: {image}"
            else:
                st.session_state.generated_image = image
                st.session_state.messages[-1]["content"] = "Your custom image is ready!"

            st.session_state.show_prompt_input = False
            st.rerun()

# Chat input
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Message",
        placeholder="Type your message here...",
        label_visibility="collapsed"
    )

    col_send, col_spacer = st.columns([1, 5])
    with col_send:
        send_button = st.form_submit_button("Send", type="primary", use_container_width=True)

if send_button and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Check if user wants to generate an image
    if any(keyword in user_input.lower() for keyword in ["generate", "create", "make", "draw", "image", "picture", "portrait", "photo"]):
        st.session_state.messages.append({"role": "assistant", "content": "Generating your image..."})

        with st.spinner("Creating image..."):
            # Extract description or use default
            if len(user_input.split()) > 3:
                prompt = user_input
            else:
                prompt = generate_random_portrait()

            image = generate_image(prompt)

        if isinstance(image, str):
            if "error_quota" in image:
                st.session_state.messages[-1]["content"] = "I've reached the API quota limit. Please try again later."
            else:
                st.session_state.messages[-1]["content"] = f"I couldn't generate the image: {image}"
        else:
            st.session_state.generated_image = image
            st.session_state.messages[-1]["content"] = "I've generated the image you requested! You can see it above."
    else:
        # Regular chat
        with st.spinner("Thinking..."):
            ai_response = chat_with_ai(user_input)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    st.rerun()

# Footer
st.markdown("---")
st.caption("Powered by HuggingFace FLUX.1 & Llama 3.2")
