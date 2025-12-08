import streamlit as st
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import random

# Load environment variables
load_dotenv()

# Configuration
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MODEL_NAME = "black-forest-labs/FLUX.1-schnell"

# Initialize HuggingFace client
client = InferenceClient(token=HUGGINGFACE_TOKEN)

# Random prompt generator components (mix and match for infinite prompts)
SUBJECTS = [
    "a majestic dragon", "a cute robot", "an astronaut", "a wizard cat", "a phoenix",
    "a steampunk airship", "a cyberpunk hacker", "a magical unicorn", "a samurai warrior",
    "a space explorer", "a mechanical owl", "a fantasy castle", "a neon cityscape",
    "a vintage car", "a pirate ship", "a floating island", "a crystal palace",
    "a ancient temple", "a futuristic train", "a mythical griffin", "a cosmic whale",
    "a enchanted forest", "a robot companion", "a steam locomotive", "a glass garden"
]

ACTIONS = [
    "flying over", "resting in", "emerging from", "standing in", "floating above",
    "racing through", "exploring", "guarding", "sleeping in", "rising from",
    "hovering near", "traveling through", "hiding in", "discovering", "watching over"
]

LOCATIONS = [
    "a neon-lit city", "ancient ruins", "a magical forest", "outer space",
    "a desert at sunset", "an underwater kingdom", "a mountain peak", "a crystal cave",
    "a futuristic metropolis", "a peaceful meadow", "a stormy ocean", "a starry night",
    "a cherry blossom garden", "a volcanic landscape", "a frozen tundra", "a bamboo forest",
    "a medieval village", "a coral reef", "a cloudy sky", "a misty swamp"
]

STYLES = [
    "digital art", "oil painting", "watercolor", "photorealistic", "anime style",
    "cyberpunk aesthetic", "fantasy art", "steampunk design", "minimalist", "pixel art",
    "impressionist style", "surrealism", "concept art", "comic book style", "retro futurism",
    "art nouveau", "vaporwave", "gothic art", "cel shaded", "sketch style"
]

LIGHTING = [
    "warm lighting", "dramatic shadows", "neon glow", "golden hour", "moonlight",
    "bioluminescent", "soft ambient light", "volumetric lighting", "sunset colors",
    "northern lights", "candlelight", "RGB lighting", "ethereal glow", "harsh sunlight",
    "twilight", "starlight", "fire glow", "underwater lighting", "studio lighting"
]

DETAILS = [
    "highly detailed", "4k quality", "intricate details", "atmospheric",
    "cinematic composition", "vibrant colors", "moody atmosphere", "epic scale",
    "fine details", "rich textures", "dynamic pose", "dramatic composition",
    "painterly", "ultra realistic", "dreamy atmosphere", "sharp focus"
]

def generate_random_prompt():
    """Generate a random prompt by combining different elements"""
    subject = random.choice(SUBJECTS)
    action = random.choice(ACTIONS)
    location = random.choice(LOCATIONS)
    style = random.choice(STYLES)
    lighting = random.choice(LIGHTING)
    detail = random.choice(DETAILS)

    prompt = f"{subject} {action} {location}, {lighting}, {style}, {detail}"
    return prompt

def generate_image(prompt):
    """Generate image from text prompt using InferenceClient"""
    try:
        # Generate image using text_to_image
        image = client.text_to_image(prompt, model=MODEL_NAME)
        return image
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Streamlit UI
st.title("🎨 AI Image Generator")
st.write("Create amazing images from text descriptions!")

# Handle random prompt button first (before text area is created)
if st.session_state.get("random_clicked", False):
    st.session_state.prompt_value = generate_random_prompt()
    st.session_state.random_clicked = False

# Initialize session state for prompt if not exists
if "prompt_value" not in st.session_state:
    st.session_state.prompt_value = ""

# Input
prompt = st.text_area("Enter your image prompt:",
                      value=st.session_state.prompt_value,
                      placeholder="Example: A sunset over mountains, digital art",
                      height=100)

# Update session state when user types
if prompt != st.session_state.prompt_value:
    st.session_state.prompt_value = prompt

# Buttons in columns
col1, col2 = st.columns([2, 1])

with col1:
    generate_button = st.button("Generate Image", type="primary", use_container_width=True)

with col2:
    if st.button("🎲 Random Prompt", use_container_width=True):
        st.session_state.random_clicked = True
        st.rerun()

# Generate button
if generate_button:
    if prompt:
        with st.spinner("Generating your image... ⏳"):
            image = generate_image(prompt)

            if image:
                st.success("Image generated successfully! ✨")
                st.image(image, use_container_width=True)

                # Store image in session state for download
                st.session_state.generated_image = image
            else:
                st.error("Failed to generate image. Please try again.")
    else:
        st.warning("Please enter a prompt first!")

# Download button (only shows if image exists)
if "generated_image" in st.session_state and st.session_state.generated_image:
    # Convert PIL image to bytes
    img_byte_arr = BytesIO()
    st.session_state.generated_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_generated_{timestamp}.png"

    st.download_button(
        label="📥 Download Image",
        data=img_byte_arr,
        file_name=filename,
        mime="image/png"
    )
