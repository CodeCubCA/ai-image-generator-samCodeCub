import streamlit as st
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import random

# Page configuration
st.set_page_config(
    page_title="AI Creative Studio",
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

# Custom CSS for professional styling
st.markdown("""
<style>
    .main {
        padding: 2rem 3rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    h1 {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .stTextArea textarea, .stTextInput input {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-size: 0.95rem;
    }

    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 3px solid #3b82f6;
        background-color: #f9fafb;
    }

    .stImage {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
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
    "lounging by a pool",
    "at a summer beach party",
    "sitting in a luxury car",
    "at a trendy restaurant",
    "walking along a boardwalk"
]

CLOTHING = [
    "wearing a casual hoodie and sunglasses",
    "in a stylish bomber jacket",
    "wearing a fitted t-shirt and chain necklace",
    "in a linen button-up shirt",
    "wearing a leather jacket",
    "in a designer sweater"
]

SETTINGS = [
    "warm sunset lighting, golden hour",
    "soft natural lighting, afternoon",
    "vibrant beach atmosphere",
    "urban city background, evening",
    "tropical vacation vibes",
    "luxury lifestyle setting"
]

DETAILS = [
    "photorealistic, high quality, professional photography",
    "cinematic portrait, 4k quality, sharp focus",
    "instagram aesthetic, modern photography",
    "lifestyle photography, natural pose"
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
            st.error("**API Quota Exceeded**")
            st.info("""
            Your free tier monthly usage limit has been reached.

            Visit [HuggingFace Billing](https://huggingface.co/settings/billing) to upgrade.
            """)
        else:
            st.error(f"**Error:** {error_msg}")
        return None

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
        return f"Error: {str(e)}"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

# Header
st.title("AI Creative Studio")
st.markdown('<p class="subtitle">Chat with AI and generate professional portrait images</p>', unsafe_allow_html=True)

# Main layout - Two columns
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### Conversation")

    # Display chat messages
    chat_container = st.container(height=400)
    with chat_container:
        if not st.session_state.messages:
            st.caption("Start a conversation or generate an image")
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown(f"**AI:** {msg['content']}")
                st.divider()

    # Chat input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message", placeholder="Ask anything or request an image...")
        col_send, col_clear = st.columns([3, 1])

        with col_send:
            send_button = st.form_submit_button("Send Message", use_container_width=True, type="primary")
        with col_clear:
            clear_button = st.form_submit_button("Clear Chat", use_container_width=True)

    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Check if user wants to generate an image
        if any(keyword in user_input.lower() for keyword in ["generate", "create", "make", "image", "picture", "portrait", "photo"]):
            st.session_state.messages.append({"role": "assistant", "content": "Generating your image..."})

            # Use user's description or generate random
            if len(user_input.split()) > 3:
                prompt = user_input
            else:
                prompt = generate_random_portrait()

            image = generate_image(prompt)
            if image:
                st.session_state.generated_image = image
                st.session_state.messages[-1]["content"] = f"Image generated successfully! Check the preview on the right."
            else:
                st.session_state.messages[-1]["content"] = "Failed to generate image. Please try again."
        else:
            # Regular chat
            ai_response = chat_with_ai(user_input)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

        st.rerun()

    if clear_button:
        st.session_state.messages = []
        st.session_state.generated_image = None
        st.rerun()

with col2:
    st.markdown("### Image Generation")

    # Quick actions
    st.caption("**Quick Actions**")
    col_gen1, col_gen2 = st.columns(2)

    with col_gen1:
        if st.button("Generate Random Portrait", use_container_width=True):
            prompt = generate_random_portrait()
            st.session_state.messages.append({"role": "user", "content": "Generate a random portrait"})
            st.session_state.messages.append({"role": "assistant", "content": "Generating random portrait..."})

            image = generate_image(prompt)
            if image:
                st.session_state.generated_image = image
                st.session_state.messages[-1]["content"] = f"Random portrait generated successfully!"
            else:
                st.session_state.messages[-1]["content"] = "Failed to generate image."
            st.rerun()

    with col_gen2:
        if st.button("Custom Prompt", use_container_width=True):
            st.session_state.show_custom_prompt = True

    # Custom prompt input
    if "show_custom_prompt" in st.session_state and st.session_state.show_custom_prompt:
        with st.form(key="custom_prompt_form"):
            custom_prompt = st.text_area(
                "Enter custom prompt",
                placeholder="Describe the image you want to generate...",
                height=100
            )
            submit_custom = st.form_submit_button("Generate", use_container_width=True, type="primary")

            if submit_custom and custom_prompt:
                st.session_state.messages.append({"role": "user", "content": f"Generate: {custom_prompt}"})
                st.session_state.messages.append({"role": "assistant", "content": "Generating custom image..."})

                image = generate_image(custom_prompt)
                if image:
                    st.session_state.generated_image = image
                    st.session_state.messages[-1]["content"] = "Custom image generated successfully!"
                else:
                    st.session_state.messages[-1]["content"] = "Failed to generate image."

                st.session_state.show_custom_prompt = False
                st.rerun()

    st.divider()

    # Display generated image
    if st.session_state.generated_image:
        st.markdown("**Generated Image**")
        st.image(st.session_state.generated_image)

        # Download button
        img_byte_arr = BytesIO()
        st.session_state.generated_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portrait_{timestamp}.png"

        st.download_button(
            label="Download Image",
            data=img_byte_arr,
            file_name=filename,
            mime="image/png",
            use_container_width=True
        )
    else:
        st.info("No image generated yet. Use quick actions or ask AI to generate an image.")

# Footer
st.divider()
st.caption("AI Creative Studio | Powered by HuggingFace FLUX.1 & Llama 3.2")
