# Epic Contrast Humor Generator

A Streamlit app that generates humorous content contrasting epic medieval fantasies with mundane modern life, perfect for creating unique Instagram content with matching DALL-E image prompts.

## Features

- Generate humor in three distinct styles:
  - Born/Cursed Contrast
  - Work Humor
  - The Urge
- Automatically create DALL-E 3 prompts for epic medieval-themed images
- Option to integrate directly with DALL-E API (requires API key)
- Medieval/fantasy-themed UI
- Easy copy functionality for content and prompts

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root (optional for DALL-E integration):
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

Run the app:
```
streamlit run app.py
```

### How to Use

1. Select a humor category from the sidebar
2. Generate new content using the button
3. Click "Select" next to any line you like
4. Use the generated DALL-E 3 prompt to create an epic medieval image
   - Copy the prompt and use it with DALL-E or other image generation tools
   - Or add your OpenAI API key to enable direct image generation (optional)
5. Share your creation on Instagram!

## Example Content

### Born/Cursed Contrast
- "Born to be a villain. Cursed to be a good employee."
- "Born to slay dragons. Cursed to answer emails."

### The Urge
- "The urge to raid villages is strong lately."
- "The masculine urge to defend the realm with my sword is strong lately."

### Work Humor
- "Feeling productive at work after doing the bare minimum and taking 87 coffee breaks."

## Example DALL-E Prompts

The app generates detailed prompts for DALL-E 3 that create medieval fantasy images matching your selected content, such as:

- "A heroic medieval warrior who was born to slay dragons, shown in a medieval fantasy setting. The warrior is wearing ornate armor with intricate designs, holding a legendary weapon. Dramatic lighting with golden hour sunlight, highly detailed oil painting style, epic and atmospheric. The scene depicts a moment of epic grandeur before the warrior's fall to mundane modern life."

- "A lone warrior about to raid villages in a medieval fantasy setting. The warrior is wearing weathered armor and carrying traditional weapons, surrounded by an atmosphere of tension and anticipation. Dramatic lighting with golden hour sunlight, highly detailed oil painting style, epic and atmospheric."