import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

st.title("Image Text Overlay")

# 1) Upload image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# 2) Text customization options
col1, col2 = st.columns(2)
with col1:
    # Change text_input to text_area for multi-line support
    overlay_text = st.text_area("Enter text to overlay", value="Your text here", height=100)
    font_size = st.slider("Font Size", min_value=20, max_value=200, value=100)
with col2:
    text_color = st.color_picker("Text Color", "#FFFFFF")
    add_outline = st.checkbox("Add Text Outline", value=True)
    line_spacing = st.slider("Line Spacing", min_value=0.5, max_value=2.0, value=1.2, step=0.1)
    # Add text alignment options
    text_align = st.selectbox("Text Alignment", ["Center", "Left", "Right"])

if uploaded_file and overlay_text:
    # Open the image with Pillow
    img = Image.open(uploaded_file)
    
    # Convert image to RGBA if it isn't already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Create a new transparent layer for the text
    txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    # Try loading a TrueType bold font; fallback to default
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except OSError:
        try:
            system_fonts = [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "C:\\Windows\\Fonts\\arialbd.ttf"
            ]
            for font_path in system_fonts:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

    # Split text into lines, preserving empty lines
    lines = overlay_text.split('\n')
    
    # Calculate total text height including line spacing
    total_height = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        total_height += line_height
    
    # Add line spacing
    total_height += (len(lines) - 1) * (font_size * (line_spacing - 1))
    
    # Calculate starting y position to center all lines
    y = (img.height - total_height) / 2
    
    # Draw each line
    for i, line in enumerate(lines):
        # Get text size for this line
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        
        # Calculate x position based on alignment
        if text_align == "Center":
            x = (img.width - text_width) / 2
        elif text_align == "Right":
            x = img.width - text_width - 20  # 20px padding from right
        else:  # Left alignment
            x = 20  # 20px padding from left
        
        # Draw outline if enabled
        if add_outline:
            outline_color = "black"
            outline_width = 3
            for offset_x in range(-outline_width, outline_width + 1):
                for offset_y in range(-outline_width, outline_width + 1):
                    draw.text((x + offset_x, y + offset_y), line, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), line, font=font, fill=text_color)
        
        # Move y position for next line, including line spacing
        if i < len(lines) - 1:  # Don't add spacing after the last line
            y += line_heights[i] + (font_size * (line_spacing - 1))

    # Combine the original image with the text layer
    result = Image.alpha_composite(img, txt_layer)
    
    # Convert back to RGB for display
    result = result.convert('RGB')

    # Display result
    st.image(result, use_column_width=True)
    
    # Add download button
    if st.button("Download Image"):
        # Save the image to a bytes buffer
        from io import BytesIO
        buf = BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)
        
        # Create download button
        st.download_button(
            label="Click to Download",
            data=buf,
            file_name="text_overlay.png",
            mime="image/png"
        )
