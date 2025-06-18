import streamlit as st
import requests
import base64
import json
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def encode_image(image_file):
    """Encode the image file to base64."""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def generate_transformed_image(api_key, prompt, image_data):
    """Generate a transformed image using GPT-4 Vision to analyze and DALL-E 3 to create."""
    
    # First: Use GPT-4 Vision to analyze the image
    vision_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    vision_payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Look at this image carefully. I want to transform it into: {prompt}. Describe the key elements, subjects, composition, and details of this image that should be preserved in the transformation. Give a detailed description that can be used as a prompt for DALL-E 3."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    vision_response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=vision_headers,
        json=vision_payload
    )
    
    if vision_response.status_code != 200:
        st.error(f"GPT-4 Vision Error: {vision_response.status_code}")
        st.error(vision_response.text)
        return None, None
    
    # Extract the image analysis from GPT-4 Vision
    image_analysis = vision_response.json()["choices"][0]["message"]["content"]
    
    # Now: Use DALL-E 3 to generate the transformed image
    dalle_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Combine the original prompt with the detailed analysis
    enhanced_prompt = f"{prompt} Based on this reference image with the following details: {image_analysis}"
    
    dalle_payload = {
        "model": "dall-e-3",
        "prompt": enhanced_prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard",
        "response_format": "url"
    }
    
    dalle_response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=dalle_headers,
        json=dalle_payload
    )
    
    if dalle_response.status_code == 200:
        return dalle_response.json()["data"][0]["url"], image_analysis
    else:
        st.error(f"DALL-E 3 Error: {dalle_response.status_code}")
        st.error(dalle_response.text)
        return None, image_analysis

def main():
    st.set_page_config(
        page_title="Image Style Transformer", 
        page_icon="🎨",
        layout="wide"
    )
    
    st.title("🎨 Image Style Transformer")
    st.markdown("""
    Upload your photo and transform it into various artistic styles using AI!
    This app uses GPT-4 Vision to analyze your image and DALL-E 3 to transform it.
    """)
    
    # API Key setup
    api_key_option = st.radio("How would you like to provide your OpenAI API Key?", 
                            ["Enter in the app", "Use from .env file"])
    
    api_key = None
    if api_key_option == "Enter in the app":
        api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.warning("No API key found in .env file. Please create a .env file with OPENAI_API_KEY=your_key")
    
    # Image upload
    uploaded_file = st.file_uploader("Upload your image to transform", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
        
        # Style selection
        st.subheader("Choose a transformation style")
        
        style_examples = {
            "Studio Ghibli": "Transform this image into Studio Ghibli animation style, with soft colors and dreamlike quality. Maintain the same scene, subjects, and composition.",
            "Anime": "Convert this image into anime style with bold lines and expressive features. Keep the same subjects and composition.",
            "Watercolor Painting": "Transform this image into a detailed watercolor painting with soft edges and flowing colors. Preserve the same scene and composition.",
            "Pixel Art": "Convert this image into detailed pixel art style with visible pixelation. Keep the same subjects and composition.",
            "Oil Painting": "Transform this image into a realistic oil painting with rich textures and depth. Maintain the same scene and subjects.",
            "Custom": "Custom prompt"
        }
        
        selected_style = st.selectbox("Select a style", list(style_examples.keys()))
        
        if selected_style == "Custom":
            prompt = st.text_area("Enter your custom prompt", 
                                height=100, 
                                placeholder="Example: Transform this photo into a cyberpunk style artwork with neon lights and futuristic elements. Keep the same subjects and composition.")
        else:
            prompt = style_examples[selected_style]
            st.text_area("Transformation prompt", prompt, height=100)
            
        # Optional prompt additions
        st.subheader("Fine-tune your transformation (optional)")
        additional_prompt = st.text_input("Add more details to your prompt")
        
        if additional_prompt:
            prompt = f"{prompt}. {additional_prompt}"
        
        # Process button
        if st.button("Transform Image") and api_key:
            with st.spinner("Analyzing your image and generating transformation..."):
                # Reset the file pointer to the beginning
                uploaded_file.seek(0)
                # Encode the image
                image_base64 = encode_image(uploaded_file)
                
                # Generate the image
                result_image_url, image_analysis = generate_transformed_image(api_key, prompt, image_base64)
                
                if result_image_url:
                    with col2:
                        st.subheader("Transformed Image")
                        st.image(result_image_url, use_container_width=True)
                        st.markdown(f"[Download Image]({result_image_url})")
                        
                        with st.expander("View Image Analysis"):
                            st.markdown(image_analysis)
        elif not api_key and st.button("Transform Image"):
            st.error("Please provide an OpenAI API Key to proceed.")
    
    st.markdown("---")
    st.markdown("""
    **How this works:**
    1. GPT-4 Vision analyzes your uploaded image in detail
    2. The analysis is combined with your style prompt
    3. DALL-E 3 generates a new image based on this enhanced prompt
    """)

if __name__ == "__main__":
    main()