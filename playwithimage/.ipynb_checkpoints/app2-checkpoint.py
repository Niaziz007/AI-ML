import streamlit as st
import random
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Load environment variables from .env file
load_dotenv()

# Access API keys securely
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure OpenAI client
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

# Set page config
st.set_page_config(
    page_title="Epic Humor Generator",
    page_icon="⚔️",
    layout="wide"
)

# Apply custom CSS for medieval/fantasy styling
st.markdown("""
<style>
    .main {
        background-color: #f5f1e8;
    }
    h1, h2, h3 {
        font-family: 'Cinzel', serif;
        color: #4a2b13;
    }
    p, div, span, .stText, .stMarkdown {
        color: #1a1a1a !important;
    }
    .stButton > button {
        background-color: #8b4513;
        color: #f5f1e8;
        border: 2px solid #4a2b13;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #4a2b13;
        color: #f5f1e8;
    }
    .humor-box {
        background-color: #fff9e6;
        border: 2px solid #8b4513;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        color: #1a1a1a !important;
    }
    .selected-box {
        background-color: #e6ffe6;
        border: 2px solid #006400;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        color: #1a1a1a !important;
    }
    .prompt-box {
        background-color: #e6f0ff;
        border: 2px solid #00008b;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        color: #1a1a1a !important;
    }
    .stTextInput > div > div > input {
        color: #1a1a1a !important;
    }
    .stTextArea > div > div > textarea {
        color: #1a1a1a !important;
    }
    .download-button {
        background-color: #2c5282 !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
        cursor: pointer !important;
        font-weight: bold !important;
        margin: 10px 0 !important;
    }
    .download-button:hover {
        background-color: #1a365d !important;
    }
</style>
""", unsafe_allow_html=True)

# Pre-defined humor templates
humor_categories = {
    "Born/Cursed Contrast": {
        "template": [
            "Born to {epic}. Cursed to {mundane}.",
            "Born for {epic}. Cursed to {mundane}.",
            "Born with {epic}. Cursed with {mundane}."
        ],
        "epic_examples": [
            "be a villain", "seduce kings and princes", "protect my homeland", 
            "bleed out on a battlefield", "slay dragons", "glory",
            "command armies", "write epic poetry", "discover new worlds",
            "wield ancient magic", "rule an empire", "craft legendary weapons",
            "be worshipped as a deity", "lead rebellions", "conquer distant lands"
        ],
        "mundane_examples": [
            "be a good employee", "get creeps in my DMs", "move for a job opportunity",
            "perish young from work-related stress", "answer emails", "9 to 5",
            "manage group chats", "draft passive-aggressive emails", 
            "discover new ways my manager says 'we need to talk'",
            "wield Excel spreadsheets", "rule the break room microwave line",
            "craft PowerPoint presentations", "be rejected on dating apps",
            "sit through endless meetings", "commute during rush hour"
        ],
        "examples": [
            "Born to be a villain. Cursed to be a good employee.",
            "Born to seduce kings and princes. Cursed to get creeps in my DMs.",
            "Born to protect my homeland. Cursed to move for a job opportunity.",
            "Born to bleed out on a battlefield. Cursed to perish young from work-related stress.",
            "Born to slay dragons. Cursed to answer emails.",
            "Born for glory. Cursed to 9 to 5.",
            "Born to command armies. Cursed to manage group chats.",
            "Born to write epic poetry. Cursed to draft passive-aggressive emails.",
            "Born to discover new worlds. Cursed to discover new ways my manager says 'we need to talk'.",
            "Born to wield ancient magic. Cursed to wield Excel spreadsheets.",
            "Born to rule an empire. Cursed to rule the break room microwave line.",
            "Born to craft legendary weapons. Cursed to craft PowerPoint presentations.",
            "Born with the soul of a wanderer. Cursed with the schedule of a corporate drone.",
            "Born to be worshipped as a deity. Cursed to be rejected on dating apps."
        ]
    },
    "Work Humor": {
        "template": [
            "{amusing_observation}",
            "{relatable_workplace_scenario}: a memoir.",
            "My {exaggerated_claim}."
        ],
        "examples": [
            "Feeling productive at work after doing the bare minimum and taking 87 coffee breaks.",
            "Putting 'urgent' in an email subject line and still waiting three weeks for a response: a memoir.",
            "My productivity is directly proportional to how close I am to my deadline and how many energy drinks I've had.",
            "Switching my personality from 'professional' to 'unhinged' the second I clock out.",
            "Nothing says 'I respect your time' like scheduling a meeting that could've been an email.",
            "Setting my alarm for 7:00, 7:05, 7:10, 7:15, and 7:20 because I respect myself but not enough to actually get up the first time.",
            "My greatest skill is making it look like I'm typing something important when my boss walks by.",
            "Saying 'let me think about it' when what I really mean is 'absolutely not but I need time to craft a polite rejection.'"
        ]
    },
    "The Urge": {
        "template": [
            "The urge to {epic_action} is strong lately.",
            "The {gendered} urge to {epic_action} is powerful today.",
            "The urge to {epic_action} is getting harder to resist."
        ],
        "gendered_examples": [
            "masculine", "feminine", "primal", "ancient", "overwhelming", "noble"
        ],
        "epic_action_examples": [
            "raid villages", "close my laptop and hold the line", 
            "defend the realm with my sword", "cast fireball", "own a direwolf",
            "abandon my desk job and become a medieval blacksmith",
            "respond to meeting invites with 'I shall consider your request, mortal'",
            "trade my business casual for battle armor",
            "resolve workplace conflicts with a formal duel at dawn",
            "replace my LinkedIn profile with 'available for quests and monster slaying'",
            "answer emails with ancient runes and cryptic prophecies",
            "build a moat around my cubicle",
            "tame a falcon instead of downloading another productivity app",
            "respond 'thou shalt not' to every request from management",
            "trade my morning commute for a noble steed",
            "declare myself sovereign of the break room and demand tribute in snacks",
            "respond to criticism with 'you dare question the chosen one?'",
            "leave a meeting and go on an epic quest"
        ],
        "examples": [
            "The urge to raid villages is strong lately.",
            "The urge to close my laptop and hold the line is powerful lately.",
            "The masculine urge to defend the realm with my sword is strong lately.",
            "The urge to cast fireball is strong.",
            "The urge to own a direwolf is strong lately.",
            "The urge to abandon my desk job and become a medieval blacksmith is overwhelming lately.",
            "The urge to respond to meeting invites with 'I shall consider your request, mortal' is getting harder to resist.",
            "The feminine urge to trade my business casual for battle armor is strong today.",
            "The urge to resolve workplace conflicts with a formal duel at dawn rather than another HR meeting is powerful lately.",
            "The urge to replace my LinkedIn profile with 'available for quests and monster slaying' grows stronger each day.",
            "The urge to answer emails with ancient runes and cryptic prophecies is almost irresistible.",
            "The masculine urge to build a moat around my cubicle is difficult to ignore this morning.",
            "The urge to tame a falcon instead of downloading another productivity app is mighty.",
            "The urge to respond 'thou shalt not' to every request from management is intensifying.",
            "The urge to trade my morning commute for a noble steed is particularly strong on Mondays.",
            "The urge to declare myself sovereign of the break room and demand tribute in snacks is overwhelming lately.",
            "The urge to respond to criticism with 'you dare question the chosen one?' is getting harder to suppress.",
            "The urge to leave a meeting and go on an epic quest is strong today."
        ]
    }
}

# Function to generate new humor content (fallback method)
def generate_humor(category, num_items=5):
    humor_type = humor_categories[category]
    
    if category == "Born/Cursed Contrast":
        results = []
        for _ in range(num_items):
            template = random.choice(humor_type["template"])
            epic = random.choice(humor_type["epic_examples"])
            mundane = random.choice(humor_type["mundane_examples"])
            line = template.format(epic=epic, mundane=mundane)
            results.append(line)
        return results
    
    elif category == "The Urge":
        results = []
        for _ in range(num_items):
            template = random.choice(humor_type["template"])
            
            if "{gendered}" in template:
                gendered = random.choice(humor_type["gendered_examples"])
                epic_action = random.choice(humor_type["epic_action_examples"])
                line = template.format(gendered=gendered, epic_action=epic_action)
            else:
                epic_action = random.choice(humor_type["epic_action_examples"])
                line = template.format(epic_action=epic_action)
            
            results.append(line)
        return results
    
    elif category == "Work Humor":
        # For Work Humor, just return examples since they're more custom
        return random.sample(humor_type["examples"], min(num_items, len(humor_type["examples"])))

# Function to generate content using OpenAI's API
def generate_with_openai(category, num_items=5):
    if not client:
        st.warning("OpenAI API key not found. Using built-in generator instead.")
        return generate_humor(category, num_items)
    
    # Get examples for the selected category
    examples = humor_categories[category]["examples"]
    examples_str = "\n".join(examples[:5])  # Use first 5 examples
    
    try:
        # Craft the prompt based on category
        if category == "Born/Cursed Contrast":
            prompt = f"""Create {num_items} unique humorous lines in the 'Born/Cursed Contrast' format. 
            Each line should contrast an epic medieval/fantasy destiny with a mundane modern reality.
            
            Examples:
            {examples_str}
            
            Generate {num_items} new, original lines in this style:"""
        
        elif category == "The Urge":
            prompt = f"""Create {num_items} unique humorous lines in 'The Urge' format.
            Each line should describe a medieval/fantasy urge that contrasts with modern life.
            
            Examples:
            {examples_str}
            
            Generate {num_items} new, original lines in this style:"""
        
        elif category == "Work Humor":
            prompt = f"""Create {num_items} unique humorous lines about modern work life with an ironic or amusing twist.
            
            Examples:
            {examples_str}
            
            Generate {num_items} new, original lines in this style:"""
            
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4
            messages=[
                {"role": "system", "content": "You are a creative writer specializing in humorous content that contrasts epic medieval fantasy with mundane modern life."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        # Extract and clean the generated content
        content = response.choices[0].message.content
        # Split by newlines and filter out empty lines or numbering
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        # Remove numbering if present (e.g., "1. ")
        lines = [re.sub(r'^\d+\.\s*', '', line) for line in lines]
        
        return lines[:num_items]  # Return requested number of items
    
    except Exception as e:
        st.error(f"Error generating content with OpenAI: {e}")
        return generate_humor(category, num_items)  # Fallback to built-in generation

# Function to generate DALL-E prompt
def generate_dalle_prompt(selected_text):
    # Extract key themes from the selected text
    text = selected_text.lower()
    
    # Default medieval setting components
    setting = "medieval fantasy setting"
    lighting = "dramatic lighting with golden hour sunlight"
    style = "highly detailed oil painting style"
    atmosphere = "epic and atmospheric"
    
    # Identify the type of content and extract keywords
    if "born to" in text and "cursed to" in text:
        # Extract the epic part (after "born to" and before "cursed to")
        match = re.search(r"born to (.*?)[.] cursed to", text, re.IGNORECASE)
        if match:
            epic_part = match.group(1)
            prompt = f"A heroic medieval warrior who was born to {epic_part}, shown in a {setting}. The warrior is wearing ornate armor with intricate designs, holding a legendary weapon. {lighting}, {style}, {atmosphere}. The scene depicts a moment of epic grandeur before the warrior's fall to mundane modern life."
        else:
            prompt = f"A heroic medieval warrior standing at a crossroads between an epic fantasy world and the modern world, wearing ornate armor in a {setting}. {lighting}, {style}, {atmosphere}."
    
    elif "the urge to" in text:
        # Extract the action part (after "the urge to")
        match = re.search(r"the (?:.*? )?urge to (.*?) is", text, re.IGNORECASE)
        if match:
            action_part = match.group(1)
            prompt = f"A lone warrior about to {action_part} in a {setting}. The warrior is wearing weathered armor and carrying traditional weapons, surrounded by an atmosphere of tension and anticipation. {lighting}, {style}, {atmosphere}."
        else:
            prompt = f"A lone warrior looking longingly at a medieval castle from afar, standing on a hilltop in full battle armor with sword drawn, in a {setting}. {lighting}, {style}, {atmosphere}."
    
    else:
        # For work humor, create a contrast between medieval and modern
        prompt = f"A medieval warrior sitting at a modern office desk, still wearing full armor and with weapons nearby, looking frustrated or bored with modern work life. The contrast between the medieval warrior aesthetic and modern office setting is stark and humorous. {lighting}, {style}, {atmosphere}."
    
    return prompt

# DALL-E integration function
def generate_dalle_image(prompt):
    if not client:
        st.error("OpenAI API key is required for image generation.")
        return None
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        return response.data[0].url
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None

# Function to enhance prompt using GPT-4
def enhance_prompt_with_gpt(prompt):
    if not client:
        return prompt
    
    try:
        enhancement_prompt = f"""Enhance this DALL-E 3 image generation prompt to be more detailed, realistic, and visually striking. 
        Add specific details about lighting, composition, style, and atmosphere. 
        Make it more cinematic and professional.
        
        Original prompt: {prompt}
        
        Return only the enhanced prompt, no explanations."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at creating detailed and realistic image generation prompts. Focus on adding specific details about lighting, composition, style, and atmosphere."},
                {"role": "user", "content": enhancement_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        enhanced_prompt = response.choices[0].message.content.strip()
        return enhanced_prompt
    except Exception as e:
        st.warning(f"Could not enhance prompt with GPT-4: {e}")
        return prompt

# Function to download image directly
def download_image(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Failed to download image: HTTP {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error downloading image: {e}")
        return None

# App title and description
st.title("⚔️ Epic Contrast Humor Generator ⚔️")
st.markdown("### Transform mundane modern life into epic medieval fantasy")

# API status indicator
if OPENAI_API_KEY:
    st.sidebar.success("OpenAI API connected ✓")
else:
    st.sidebar.warning("OpenAI API key not found. Add it to your .env file for AI-powered content and image generation.")

# Sidebar for category selection
st.sidebar.header("Generate Content")
selected_category = st.sidebar.selectbox(
    "Choose humor category",
    list(humor_categories.keys())
)

num_items = st.sidebar.slider("Number of items to generate", 3, 10, 5)

if st.sidebar.button("Generate New Content"):
    with st.spinner("Generating creative content..."):
        st.session_state.generated_content = generate_with_openai(selected_category, num_items)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Generated Content")
    
    # Display examples first
    st.subheader("Examples")
    for example in humor_categories[selected_category]["examples"][:3]:
        st.markdown(f"""<div class="humor-box">{example}</div>""", unsafe_allow_html=True)
    
    # Display generated content
    if "generated_content" in st.session_state:
        st.subheader("New Content")
        for i, content in enumerate(st.session_state.generated_content):
            if st.button(f"Select #{i+1}", key=f"select_{i}"):
                st.session_state.selected_content = content
            st.markdown(f"""<div class="humor-box">{content}</div>""", unsafe_allow_html=True)

with col2:
    st.header("Selected Content")
    if "selected_content" in st.session_state:
        st.markdown(f"""<div class="selected-box">{st.session_state.selected_content}</div>""", unsafe_allow_html=True)
        
        # Generate DALL-E prompt
        dalle_prompt = generate_dalle_prompt(st.session_state.selected_content)
        st.subheader("DALL-E 3 Prompt")
        st.markdown(f"""<div class="prompt-box">{dalle_prompt}</div>""", unsafe_allow_html=True)
        
        # Copy buttons
        col_copy1, col_copy2 = st.columns(2)
        with col_copy1:
            if st.button("Copy Content"):
                st.toast("Content copied to clipboard!")
        
        with col_copy2:
            if st.button("Copy DALL-E Prompt"):
                st.toast("DALL-E prompt copied to clipboard!")
        
        # Image generation section
        if OPENAI_API_KEY:
            st.success("DALL-E API is configured and ready to use. You can generate images directly using the 'Create Image with DALL-E' button.")
            
            if "selected_content" in st.session_state and st.button("Create Image with DALL-E"):
                with st.spinner("Creating epic medieval image..."):
                    # Generate initial prompt
                    initial_prompt = generate_dalle_prompt(st.session_state.selected_content)
                    
                    # Show the initial prompt
                    st.subheader("Initial Prompt")
                    st.markdown(f"""<div class="prompt-box">{initial_prompt}</div>""", unsafe_allow_html=True)
                    
                    # Enhance the prompt with GPT-4
                    with st.spinner("Enhancing prompt with GPT-4..."):
                        enhanced_prompt = enhance_prompt_with_gpt(initial_prompt)
                        
                        # Show the enhanced prompt
                        st.subheader("Enhanced Prompt")
                        st.markdown(f"""<div class="prompt-box">{enhanced_prompt}</div>""", unsafe_allow_html=True)
                        
                        # Generate image with enhanced prompt
                        image_url = generate_dalle_image(enhanced_prompt)
                        if image_url:
                            st.session_state.image_url = image_url
                            st.session_state.enhanced_prompt = enhanced_prompt
                            
                            # Display the generated image
                            st.image(image_url, caption="Generated with DALL-E 3", use_column_width=True)
                            
                            # Create two columns for download buttons
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Direct image download button
                                image_data = download_image(image_url)
                                if image_data:
                                    st.download_button(
                                        label="⬇️ Download Image",
                                        data=image_data,
                                        file_name="generated_image.png",
                                        mime="image/png",
                                        key="download_image_button"
                                    )
                            
                            with col2:
                                # Download enhanced prompt
                                st.download_button(
                                    label="📝 Download Enhanced Prompt",
                                    data=enhanced_prompt,
                                    file_name="enhanced_prompt.txt",
                                    mime="text/plain",
                                    key="download_prompt_button"
                                )
                            
                            # Add a success message
                            st.success("Image generated successfully! Use the buttons above to download the image and prompt.")
        else:
            st.warning("DALL-E integration requires an OpenAI API key. Add your key to the .env file as OPENAI_API_KEY to enable direct image generation.")

# Add download button for the generated text
if "selected_content" in st.session_state:
    st.download_button(
        label="Download Generated Text",
        data=st.session_state.selected_content,
        file_name="generated_text.txt",
        mime="text/plain"
    )

# Optional DALL-E integration section
st.markdown("---")
st.header("DALL-E Integration")

# Only show this section if API key is available
if OPENAI_API_KEY:
    st.success("DALL-E API is configured and ready to use. You can generate images directly using the 'Create Image with DALL-E' button.")
else:
    st.warning("DALL-E integration requires an OpenAI API key. Add your key to the .env file as OPENAI_API_KEY to enable direct image generation.")
    st.code("# Example .env file\nOPENAI_API_KEY=your-api-key-here")

# Instructions section
st.markdown("---")
st.header("How to Use")
st.markdown("""
1. Select a humor category from the sidebar
2. Generate new content using the button
3. Click "Select" next to any line you like
4. Use the generated DALL-E 3 prompt to create an epic medieval image
   - Copy the prompt and use it with DALL-E or other image generation tools
   - Or use the built-in image generation if your API key is configured
5. Share your creation on Instagram!
""")

# Initialize session state if it doesn't exist
if "generated_content" not in st.session_state:
    # Generate initial content when app starts
    st.session_state.generated_content = generate_with_openai(selected_category, num_items)

if "selected_content" not in st.session_state:
    st.session_state.selected_content = humor_categories[selected_category]["examples"][0]

# Main function to run the app
def main():
    # The app layout and functionality is already defined above
    pass

if __name__ == "__main__":
    main()