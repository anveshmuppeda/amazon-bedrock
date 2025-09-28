"""
AI Agent Hub - Unified Streamlit Web Interface

This creates a comprehensive web interface with multiple AI features:
1. Image Generator - Create images from text prompts
2. Background Remover - Remove backgrounds from uploaded images
"""

import streamlit as st
import sys
import os
import io
from PIL import Image

# Add subdirectories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'image_generator'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'bg_remover'))

# Import backend modules
try:
    import image_generate_backend as image_gen
    import bg_remover_backend as bg_remover
except ImportError as e:
    st.error(f"Import error: {e}")

# Configure the web page
st.set_page_config(
    page_title="AI Agent Hub",
    page_icon="🤖",
    layout="wide"
)

# Main title
st.markdown('<h1 style="text-align: center; color: #2E86AB;">🤖 AI Agent Hub</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 18px;">Your one-stop solution for AI-powered tasks</p>', unsafe_allow_html=True)

# Create tabs for different features
tab1, tab2 = st.tabs(["🎨 Image Generator", "✂️ Background Remover"])

# Image Generator Tab
with tab1:
    st.header("🎨 AI Image Generator")
    st.markdown("**Create unique images from text descriptions**")
    
    # Initialize session state
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    
    # Prompt input
    image_prompt = st.text_area(
        "Describe the image you want to generate:",
        placeholder="Example: A serene mountain landscape at sunset",
        height=100
    )
    
    if st.button("🎨 Generate Image", type="primary", key="generate_button"):
        if image_prompt.strip():
            with st.spinner("🎨 Generating image..."):
                try:
                    image_bytes = image_gen.generate_image_from_prompt(image_prompt)
                    st.session_state.generated_image = image_bytes
                    st.success("✅ Image generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a description first!")
    
    # Display generated image
    if st.session_state.generated_image:
        st.subheader("🖼️ Generated Image:")
        image = Image.open(io.BytesIO(st.session_state.generated_image))
        st.image(image, use_container_width=True)
        
        st.download_button(
            label="💾 Download Image",
            data=st.session_state.generated_image,
            file_name="ai_generated_image.png",
            mime="image/png"
        )

# Background Remover Tab
with tab2:
    st.header("✂️ AI Background Remover")
    st.markdown("**Remove backgrounds from your images using AI**")
    
    # Initialize session state
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload an image:",
        type=['png', 'jpg', 'jpeg'],
        help="Supported formats: PNG, JPG, JPEG"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_image = uploaded_file.getvalue()
        
        # Display uploaded image
        st.subheader("📷 Original Image:")
        uploaded_image = Image.open(io.BytesIO(st.session_state.uploaded_image))
        st.image(uploaded_image, use_container_width=True)
        
        # Remove background button
        if st.button("✂️ Remove Background", type="primary", key="remove_bg_button"):
            with st.spinner("✂️ Processing image..."):
                try:
                    processed_image_bytes = bg_remover.remove_background_from_image(st.session_state.uploaded_image)
                    st.session_state.processed_image = processed_image_bytes
                    st.success("✅ Background removed successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display processed image
    if st.session_state.processed_image:
        st.subheader("✨ Processed Image:")
        processed_image = Image.open(io.BytesIO(st.session_state.processed_image))
        st.image(processed_image, use_container_width=True)
        
        st.download_button(
            label="💾 Download Processed Image",
            data=st.session_state.processed_image,
            file_name="background_removed_image.png",
            mime="image/png"
        )
        
        # Before/after comparison
        if st.session_state.uploaded_image:
            st.subheader("🔄 Before & After:")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Before**")
                original_image = Image.open(io.BytesIO(st.session_state.uploaded_image))
                st.image(original_image, use_container_width=True)
            with col2:
                st.write("**After**")
                st.image(processed_image, use_container_width=True)

# Sidebar with system information
with st.sidebar:
    st.header("📋 System Status")
    st.info("""
    **Available Features:**
    - 🎨 Image Generator: Text-to-image
    - ✂️ Background Remover: Image processing
    
    **Models Used:**
    - Amazon Titan (Images)
    """)
    
    st.header("💡 Quick Tips")
    st.markdown("""
    - **Image Gen**: Be descriptive in your prompts
    - **BG Remover**: Use high-quality images for best results
    """)