import streamlit as st
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import random

# Page configuration
st.set_page_config(
    page_title="Zeno - AI Creative Assistant",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load environment variables
load_dotenv()

# Configuration
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "").strip().strip('"')
MODEL_NAME = "black-forest-labs/FLUX.1-schnell"

# Initialize HuggingFace client
client = InferenceClient(token=HUGGINGFACE_TOKEN)

# Professional CSS styling
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* App background */
    .stApp {
        background: linear-gradient(to bottom, #f8f9fa 0%, #e9ecef 100%);
    }

    .main {
        padding: 0 !important;
    }

    .block-container {
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 900px !important;
    }

    /* Header */
    .header-container {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        padding: 2rem 2rem 1.75rem 2rem;
        margin: -1.5rem -2rem 1.5rem -2rem;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.25);
    }

    .header-container h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
    }

    .header-container p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1rem;
        margin: 0;
        font-weight: 400;
    }

    /* Chat messages */
    .message-container {
        margin-bottom: 1.25rem;
        display: flex;
        align-items: flex-start;
        gap: 0.875rem;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.875rem;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .user-avatar {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
    }

    .ai-avatar {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }

    .message-bubble {
        flex: 1;
        padding: 1rem 1.25rem;
        border-radius: 16px;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    .user-bubble {
        background: white;
        color: #1f2937;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    .ai-bubble {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        color: #1f2937;
        border: 1px solid #bbf7d0;
    }

    /* Input area */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 0.875rem 1.25rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        background: white;
    }

    .stTextInput > div > div > input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
        border: none;
        font-size: 0.9rem;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
    }

    .stButton > button[kind="secondary"] {
        background: white;
        color: #6366f1;
        border: 2px solid #e5e7eb;
    }

    .stButton > button[kind="secondary"]:hover {
        border-color: #8b5cf6;
        background: #faf5ff;
    }

    /* Image container */
    .image-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }

    .image-card h4 {
        margin: 0 0 1rem 0;
        color: #1f2937;
        font-weight: 600;
        font-size: 1.1rem;
    }

    .stImage {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 12px;
        width: 100%;
        margin-top: 1rem;
        font-weight: 600;
        padding: 0.875rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        background: white;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    }

    .empty-state-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        filter: grayscale(20%);
    }

    .empty-state h3 {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
    }

    .empty-state p {
        color: #6b7280;
        font-size: 1rem;
    }

    /* Quick actions */
    .action-buttons {
        display: flex;
        gap: 0.75rem;
        margin: 1.5rem 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #9ca3af;
        font-size: 0.875rem;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: #8b5cf6 !important;
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
<div class="header-container">
    <h1>Zeno</h1>
    <p>Chat naturally or ask me to generate professional images</p>
</div>
""", unsafe_allow_html=True)

# Chat messages
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
            <div class="message-container">
                <div class="avatar user-avatar">You</div>
                <div class="message-bubble user-bubble">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-container">
                <div class="avatar ai-avatar">AI</div>
                <div class="message-bubble ai-bubble">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)

# Display generated image
if st.session_state.generated_image:
    st.markdown('<div class="image-card">', unsafe_allow_html=True)
    st.markdown("<h4>Generated Image</h4>", unsafe_allow_html=True)
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
col1, col2, col3 = st.columns([2.5, 2.5, 1.5])

with col1:
    if st.button("Generate Random Portrait", use_container_width=True, type="primary"):
        prompt = generate_random_portrait()
        st.session_state.messages.append({"role": "user", "content": "Generate a random portrait"})
        st.session_state.messages.append({"role": "assistant", "content": "Creating a random portrait for you..."})

        with st.spinner("Generating image..."):
            image = generate_image(prompt)

        if isinstance(image, str):
            if "error_quota" in image:
                st.session_state.messages[-1]["content"] = "API quota limit reached. Please try again later or upgrade your plan."
            else:
                st.session_state.messages[-1]["content"] = f"Unable to generate image. {image}"
        else:
            st.session_state.generated_image = image
            st.session_state.messages[-1]["content"] = "Your random portrait is ready! Check it out above."
        st.rerun()

with col2:
    if st.button("Custom Image Prompt", use_container_width=True, type="secondary"):
        st.session_state.show_prompt_input = True

with col3:
    if st.button("Clear", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.generated_image = None
        st.session_state.show_prompt_input = False
        st.rerun()

# Custom prompt input
if st.session_state.get("show_prompt_input", False):
    with st.form(key="custom_form", clear_on_submit=True):
        custom_input = st.text_input("Describe the image you want to create", placeholder="e.g., a person at sunset on a beach with golden lighting...")
        submit_custom = st.form_submit_button("Generate Image", type="primary", use_container_width=True)

        if submit_custom and custom_input:
            st.session_state.messages.append({"role": "user", "content": custom_input})
            st.session_state.messages.append({"role": "assistant", "content": "Creating your custom image..."})

            with st.spinner("Generating your image..."):
                image = generate_image(custom_input)

            if isinstance(image, str):
                if "error_quota" in image:
                    st.session_state.messages[-1]["content"] = "API quota exceeded. Please try again later."
                else:
                    st.session_state.messages[-1]["content"] = f"Unable to generate image: {image}"
            else:
                st.session_state.generated_image = image
                st.session_state.messages[-1]["content"] = "Your custom image is ready!"

            st.session_state.show_prompt_input = False
            st.rerun()

# Chat input
st.markdown("<br>", unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Message",
        placeholder="Type your message here...",
        label_visibility="collapsed"
    )

    col_send, col_spacer = st.columns([1.5, 4.5])
    with col_send:
        send_button = st.form_submit_button("Send", type="primary", use_container_width=True)

if send_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Check if user wants to generate an image
    if any(keyword in user_input.lower() for keyword in ["generate", "create", "make", "draw", "image", "picture", "portrait", "photo"]):
        st.session_state.messages.append({"role": "assistant", "content": "Generating your image..."})

        with st.spinner("Creating image..."):
            if len(user_input.split()) > 3:
                prompt = user_input
            else:
                prompt = generate_random_portrait()

            image = generate_image(prompt)

        if isinstance(image, str):
            if "error_quota" in image:
                st.session_state.messages[-1]["content"] = "API quota limit reached. Please try again later."
            else:
                st.session_state.messages[-1]["content"] = f"Unable to generate image: {image}"
        else:
            st.session_state.generated_image = image
            st.session_state.messages[-1]["content"] = "Image generated successfully! You can see it above."
    else:
        # Regular chat
        with st.spinner("Thinking..."):
            ai_response = chat_with_ai(user_input)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    st.rerun()

# Footer
st.markdown("""
<div class="footer">
    Powered by HuggingFace FLUX.1 & Llama 3.2
</div>
""", unsafe_allow_html=True)
