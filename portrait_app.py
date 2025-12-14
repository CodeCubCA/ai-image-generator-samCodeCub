import streamlit as st
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
import random
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configuration
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
GOOGLE_API_KEY = "AIzaSyAvdTt-t5KuGvAuzt7yZAyYBw9fklc-Wk8"

# Primary model
MODEL_NAME = "black-forest-labs/FLUX.1-schnell"
# Fallback models if quota exceeded
FALLBACK_MODELS = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "CompVis/stable-diffusion-v1-4"
]

# Initialize HuggingFace client for image generation
client = InferenceClient(token=HUGGINGFACE_TOKEN)

# Initialize Google AI for chat
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

# Consistent character description (based on the reference image)
BASE_CHARACTER = "a stylish man in his late 20s with a full brown beard, wearing trendy sunglasses, casual modern clothing"

# Random scenario components for the same person
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
    "walking along a boardwalk",
    "standing on a balcony overlooking the city",
    "at a rooftop bar with city lights",
    "relaxing in a hammock",
    "at a beach bonfire at dusk",
    "sitting at a marina with boats"
]

CLOTHING = [
    "wearing a casual hoodie and sunglasses",
    "in a stylish bomber jacket",
    "wearing a fitted t-shirt and chain necklace",
    "in a linen button-up shirt",
    "wearing a leather jacket",
    "in a designer sweater",
    "wearing a casual polo shirt",
    "in a denim jacket",
    "wearing an athletic jacket",
    "in a casual blazer"
]

SETTINGS = [
    "warm sunset lighting, golden hour",
    "soft natural lighting, afternoon",
    "vibrant beach atmosphere",
    "urban city background, evening",
    "tropical vacation vibes",
    "luxury lifestyle setting",
    "coastal Mediterranean style",
    "modern minimalist background",
    "warm bokeh lights in background",
    "ocean view in the distance"
]

DETAILS = [
    "photorealistic, high quality, professional photography",
    "cinematic portrait, 4k quality, sharp focus",
    "instagram aesthetic, modern photography",
    "lifestyle photography, natural pose",
    "professional headshot quality, well-lit",
    "travel photography style, authentic moment",
    "editorial photography, magazine quality",
    "candid portrait, relaxed atmosphere"
]

def generate_random_portrait():
    """Generate a random scenario for the same person"""
    activity = random.choice(ACTIVITIES)
    clothing = random.choice(CLOTHING)
    setting = random.choice(SETTINGS)
    detail = random.choice(DETAILS)

    prompt = f"{BASE_CHARACTER}, {clothing}, {activity}, {setting}, {detail}"
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

def generate_multiple_images(prompts_list):
    """Generate multiple images from a list of prompts"""
    images = []
    for i, prompt in enumerate(prompts_list):
        try:
            with st.spinner(f"Generating image {i+1} of {len(prompts_list)}... ⏳"):
                image = client.text_to_image(prompt, model=MODEL_NAME)
                images.append(image)
        except Exception as e:
            st.error(f"Error generating image {i+1}: {str(e)}")
            images.append(None)
    return images

def split_story_with_ai(full_story, num_pages):
    """Use AI to split a story into scenes for image generation with consistent character descriptions"""
    try:
        # Step 1: Extract character descriptions (short, concise)
        character_prompt = f"""Analyze this story and list ALL characters with BRIEF but SPECIFIC descriptions.

Story: {full_story}

For each character, write ONE LINE with:
- Name
- Type/species with color (e.g., "light brown bunny", "green dinosaur", "orange turtle")
- One key feature (e.g., "floppy ears", "long neck", "small shell")

Format: [Name] the [color] [type] with [key feature]
Example: Benny the light brown cottontail bunny with long floppy ears

List all characters, one per line."""

        char_response = gemini_model.generate_content(character_prompt)
        character_descriptions = char_response.text.strip()

        # Show character descriptions to user
        st.info("📝 Character Descriptions:")
        st.text(character_descriptions)

        # Step 2: Get scene actions only (what happens in each scene)
        action_prompt = f"""Split this story into {num_pages} scenes. For EACH scene, write ONLY what the characters are DOING and WHERE they are.

Story: {full_story}

Format (one per line):
Page 1: [brief action and setting]
Page 2: [brief action and setting]

Example:
Page 1: playing in a sunny forest clearing
Page 2: meeting a new friend by a pond
Page 3: searching for food together in the meadow

Provide exactly {num_pages} scenes."""

        action_response = gemini_model.generate_content(action_prompt)
        action_text = action_response.text

        # Parse actions
        actions = []
        for line in action_text.split('\n'):
            line = line.strip()
            if line and 'Page' in line and ':' in line:
                action = line.split(':', 1)[1].strip()
                if action and len(action) > 5:
                    actions.append(action)

        if len(actions) < num_pages:
            st.warning(f"Only got {len(actions)} actions, padding to {num_pages}")
            while len(actions) < num_pages:
                actions.append("continuing their adventure in a beautiful scene")

        actions = actions[:num_pages]

        # Step 3: Manually combine character descriptions with actions
        scenes = []
        for i, action in enumerate(actions):
            # Build complete scene with ALL characters + action
            scene = f"{character_descriptions}, {action}, children's book illustration, cute cartoon style, vibrant colors, consistent character design"
            scenes.append(scene)
            st.write(f"**Scene {i+1}:** {scene[:100]}...")

        return scenes

    except Exception as e:
        st.error(f"Error splitting story: {str(e)}")
        return None

# Sidebar AI Chatbox (ChatGPT-style)
with st.sidebar:
    st.header("💬 AI Assistant")

    # Initialize conversations list
    if "conversations" not in st.session_state:
        st.session_state.conversations = [{"id": 1, "name": "Chat 1", "messages": []}]
        st.session_state.current_conversation_id = 1
        st.session_state.next_id = 2

    # New chat button
    if st.button("➕ New Chat", use_container_width=True):
        new_id = st.session_state.next_id
        st.session_state.conversations.append({
            "id": new_id,
            "name": f"Chat {new_id}",
            "messages": []
        })
        st.session_state.current_conversation_id = new_id
        st.session_state.next_id += 1
        st.rerun()

    st.divider()

    # Conversation list
    st.subheader("Conversations")
    for conv in st.session_state.conversations:
        # Determine if this is the active conversation
        is_active = conv["id"] == st.session_state.current_conversation_id

        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                f"{'📌 ' if is_active else ''}{conv['name']}",
                key=f"conv_{conv['id']}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_conversation_id = conv["id"]
                st.rerun()

        with col2:
            if st.button("🗑️", key=f"del_{conv['id']}", help="Delete"):
                if len(st.session_state.conversations) > 1:
                    st.session_state.conversations = [c for c in st.session_state.conversations if c["id"] != conv["id"]]
                    if st.session_state.current_conversation_id == conv["id"]:
                        st.session_state.current_conversation_id = st.session_state.conversations[0]["id"]
                    st.rerun()

    st.divider()

# Main chat interface (below sidebar)
st.sidebar.subheader("💭 Chat")

# Get current conversation
current_conv = next((c for c in st.session_state.conversations if c["id"] == st.session_state.current_conversation_id), None)

if current_conv:
    # Chat input with unique key per conversation
    user_message = st.sidebar.text_input(
        "Message:",
        key=f"chat_input_{st.session_state.current_conversation_id}",
        placeholder="Ask me anything..."
    )

    if st.sidebar.button("Send", use_container_width=True):
        if user_message:
            # Add user message
            current_conv["messages"].append({"role": "user", "content": user_message})

            # Update conversation name with first message
            if len(current_conv["messages"]) == 1:
                current_conv["name"] = user_message[:20] + ("..." if len(user_message) > 20 else "")

            try:
                # Generate AI response using Google Gemini
                response = gemini_model.generate_content(user_message)
                ai_response = response.text
                current_conv["messages"].append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")

            st.rerun()

    # Display messages
    st.sidebar.divider()
    if current_conv["messages"]:
        for msg in current_conv["messages"][-8:]:  # Show last 8 messages
            if msg["role"] == "user":
                st.sidebar.markdown(f"**You:** {msg['content']}")
            else:
                st.sidebar.markdown(f"**AI:** {msg['content']}")
    else:
        st.sidebar.caption("No messages yet. Start chatting!")

    # Clear current chat
    if st.sidebar.button("Clear This Chat", use_container_width=True):
        current_conv["messages"] = []
        current_conv["name"] = f"Chat {current_conv['id']}"
        st.rerun()

st.sidebar.divider()

# Streamlit UI
st.title("📸 AI Portrait Generator")
st.write("Generate portraits of a stylish bearded man in different scenarios!")

st.info("⚠️ Note: AI will generate similar-looking people based on the description, but exact face consistency is not guaranteed across generations.")

# Mode selection
mode = st.radio("Generation Mode:", ["Single Image", "Multiple Images (Story)"], horizontal=True)

# Initialize session state for prompt if not exists
if "prompt_value" not in st.session_state:
    st.session_state.prompt_value = ""

if mode == "Single Image":
    # Handle random prompt button first (before text area is created)
    if st.session_state.get("random_clicked", False):
        st.session_state.prompt_value = generate_random_portrait()
        st.session_state.random_clicked = False

    # Single image mode
    # Input
    prompt = st.text_area("Portrait description:",
                          value=st.session_state.prompt_value,
                          placeholder=f"Example: {BASE_CHARACTER}, relaxing at a beach...",
                          height=100)

    # Update session state when user types
    if prompt != st.session_state.prompt_value:
        st.session_state.prompt_value = prompt

    # Buttons in columns
    col1, col2 = st.columns([2, 1])

    with col1:
        generate_button = st.button("Generate Portrait", type="primary", use_container_width=True)

    with col2:
        if st.button("🎲 Random Scenario", use_container_width=True):
            st.session_state.random_clicked = True
            st.rerun()
else:
    # Multiple images mode (Story)
    st.subheader("📖 Story Mode - Generate Multiple Images")

    # Story mode selection
    story_mode = st.radio("Story Input Method:", ["Manual (one scene per line)", "Auto-Split (AI splits story)"], horizontal=True)

    if story_mode == "Manual (one scene per line)":
        st.write("Enter each scene/page description on a new line. Each line will generate a separate image.")

        story_prompts = st.text_area(
            "Story scenes (one per line):",
            placeholder="Example:\nPage 1: Benny the bunny in a sunny forest\nPage 2: Daisy the dinosaur visiting Benny\nPage 3: Terry the turtle helping them find grass",
            height=200
        )

        generate_button = st.button("Generate Story Images", type="primary", use_container_width=True)

    else:  # Auto-Split mode
        st.write("Paste your full story and let AI split it into scenes for you!")

        # Number of pages input
        num_pages = st.number_input("Number of pages:", min_value=2, max_value=10, value=5, step=1)

        # Full story input
        full_story = st.text_area(
            "Your full story:",
            placeholder="Example: Once upon a time, in a sunny forest, there lived a little bunny named Benny...",
            height=200
        )

        generate_button = st.button("Split Story & Generate Images", type="primary", use_container_width=True)

# Generate button
if generate_button:
    if mode == "Single Image":
        if prompt:
            with st.spinner("Generating portrait... ⏳"):
                image = generate_image(prompt)

                if image:
                    st.success("Portrait generated successfully! ✨")
                    st.image(image, use_container_width=True)

                    # Store image in session state for download
                    st.session_state.generated_image = image
                    st.session_state.generated_images = None  # Clear multi-image state
                else:
                    st.error("Failed to generate portrait. Please try again.")
        else:
            st.warning("Please enter a description first!")

    else:  # Multiple Images mode
        if story_mode == "Manual (one scene per line)":
            if story_prompts:
                # Split prompts by newline
                prompts_list = [p.strip() for p in story_prompts.split('\n') if p.strip()]

                if prompts_list:
                    st.info(f"Generating {len(prompts_list)} images...")
                    images = generate_multiple_images(prompts_list)

                    # Store images in session state
                    st.session_state.generated_images = images
                    st.session_state.story_prompts = prompts_list
                    st.session_state.generated_image = None  # Clear single image state

                    st.success(f"Generated {len([i for i in images if i is not None])} images successfully! ✨")
                else:
                    st.warning("Please enter at least one scene description!")
            else:
                st.warning("Please enter story scenes!")

        else:  # Auto-Split mode
            if full_story:
                # Step 1: Split story with AI
                with st.spinner("AI is splitting your story into scenes... 🤖"):
                    scenes = split_story_with_ai(full_story, num_pages)

                if scenes:
                    st.success(f"AI created {len(scenes)} scene descriptions!")

                    # Show the scenes to the user
                    with st.expander("📝 View AI-Generated Scenes"):
                        for i, scene in enumerate(scenes):
                            st.write(f"**Page {i+1}:** {scene}")

                    # Step 2: Generate images from scenes
                    st.info(f"Now generating {len(scenes)} images...")
                    images = generate_multiple_images(scenes)

                    # Store images in session state
                    st.session_state.generated_images = images
                    st.session_state.story_prompts = scenes
                    st.session_state.generated_image = None  # Clear single image state

                    st.success(f"Generated {len([i for i in images if i is not None])} images successfully! ✨")
                else:
                    st.error("Failed to split story. Please try again or use manual mode.")
            else:
                st.warning("Please enter your full story!")

# Display and download for single image
if "generated_image" in st.session_state and st.session_state.generated_image:
    # Convert PIL image to bytes
    img_byte_arr = BytesIO()
    st.session_state.generated_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"portrait_{timestamp}.png"

    st.download_button(
        label="📥 Download Portrait",
        data=img_byte_arr,
        file_name=filename,
        mime="image/png"
    )

# Display and download for multiple images
if "generated_images" in st.session_state and st.session_state.generated_images:
    st.divider()
    st.subheader("📚 Your Story Images")

    for i, (image, prompt) in enumerate(zip(st.session_state.generated_images, st.session_state.story_prompts)):
        st.markdown(f"### Page {i+1}")
        st.caption(prompt)

        if image:
            st.image(image, use_container_width=True)

            # Individual download button
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"story_page_{i+1}_{timestamp}.png"

            st.download_button(
                label=f"📥 Download Page {i+1}",
                data=img_byte_arr,
                file_name=filename,
                mime="image/png",
                key=f"download_{i}"
            )
        else:
            st.error(f"Failed to generate Page {i+1}")

        st.divider()
