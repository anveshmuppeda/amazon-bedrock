"""
AI Image Generator Frontend - Streamlit Web Interface

This creates a simple web interface where users can:
1. Enter text prompts to generate images
2. View generated images instantly
3. Download images to their device
"""

import streamlit as st 
import image_generate_backend as image_gen
import io
from PIL import Image

# Configure the web page
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

# Create attractive title
page_title = '<p style="font-family:sans-serif; color:Purple; font-size: 42px;">🎨 AI Image Generator 🖼️</p>'
st.markdown(page_title, unsafe_allow_html=True)

# Add explanation for users
st.markdown("""
**How it works:**
- ✍️ Enter a descriptive text prompt
- 🎨 AI generates a unique image based on your description
- 👀 View the generated image instantly
- 💾 Download the image to your device
""")

# Initialize session state for generated image
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

# User input section
st.subheader("✍️ Describe the image you want to generate:")

# Text input for image prompt
user_prompt = st.text_area(
    "Type your image description here...",
    placeholder="Example: A serene mountain landscape at sunset with a lake reflecting the orange sky",
    height=100,
    label_visibility="collapsed"
)

# Generate button
generate_button = st.button("🎨 Generate Image", type="primary")

# Process prompt when button is clicked
if generate_button and user_prompt.strip():
    with st.spinner("🎨 Generating your image... This may take a few moments..."):
        try:
            # Generate image using backend
            image_bytes = image_gen.generate_image_from_prompt(user_prompt)
            
            # Store in session state
            st.session_state.generated_image = image_bytes
            
            st.success("✅ Image generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Error generating image: {str(e)}")
            
elif generate_button and not user_prompt.strip():
    st.warning("⚠️ Please enter a description first!")

# Display generated image if available
if st.session_state.generated_image:
    st.subheader("🖼️ Generated Image:")
    
    # Convert bytes to PIL Image for display
    image = Image.open(io.BytesIO(st.session_state.generated_image))
    
    # Display image
    st.image(image, caption="Your AI-generated image", use_container_width=True)
    
    # Download button
    st.download_button(
        label="💾 Download Image",
        data=st.session_state.generated_image,
        file_name="ai_generated_image.png",
        mime="image/png",
        type="secondary"
    )

# Add helpful information in sidebar
with st.sidebar:
    st.header("📋 System Info")
    st.info("""
    **AI Image Generator Status:**
    - ✅ Amazon Titan Image Generator ready
    - ✅ Image processing enabled
    - ✅ Download functionality active
    
    **Model Used:**
    - 🎨 Amazon Titan Image Generator G1
    - 📐 Resolution: 1024x1024
    - 🎯 High-quality image generation
    """)
    
    st.header("💡 Tips for Better Images")
    st.markdown("""
    - Be specific and descriptive in your prompts
    - Include details about style, colors, and mood
    - Mention lighting conditions (sunset, bright, dim)
    - Specify the type of scene (landscape, portrait, abstract)
    - Add artistic styles if desired (realistic, cartoon, painting)
    """)