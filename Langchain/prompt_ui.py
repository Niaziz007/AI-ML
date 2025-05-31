from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import streamlit as st
import json
from langchain_core.prompts import PromptTemplate


load_dotenv()

st.header("Research Paper Summarizer")
paper_input = st.selectbox(
    "Select a Research Paper Name",["Slect....", "Attention is All You Need", "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", 
                                    "GPT-3: Language Models are Few-Shot Learners","Diffusion Models Beat GANs on Image Synthesis", "DALL·E 2: A Second Generation Image Generation Model",
                                    "CLIP: Connecting Text and Images", "Image GPT: Generative Pre-Training from Pixels", "T5: Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer",
                                    "XLNet: Generalized Autoregressive Pretraining for Language Understanding", "RoBERTa: A Robustly Optimized BERT Pretraining Approach", "ALBERT: A Lite BERT for Self-supervised Learning of Language Representations",
                                    "ERNIE: Enhanced Representation through kNowledge Integration", "ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators", "Turing-NLG: A 17-billion-parameter language model by Microsoft",]
)
style_input = st.selectbox(
    "Select a Style", ["Slect....","Beginner-Friendly","Technical", "Code_Oriented","Mathematical","Formal", "Informal", "Technical", "Conversational"
                       , "Persuasive", "Descriptive", "Narrative", "Expository", "Analytical", "Critical", "Comparative", "Reflective"]
)
audience_input = st.selectbox(
    "Select an Audience", ["Slect....","General Public", "Students", "Researchers", "Developers", "Data Scientists", "Business Professionals", "Academics", "Journalists", "Policymakers"]
)

lenght_input = st.selectbox(
    "Select a Length", ["Slect....","Short(1-2 paragraphs)", "Medium(3-4 paragraphs)", "Long(5-6 paragraphs)", "Very Long(7+ paragraphs)"]
)

#template
template = PromptTemplate(
    input_variables=["paper", "style", "audience", "length"],
    template="Summarize the research paper '{paper}' in a {style} style for a {audience} audience. The summary should be {length}.",
)

#fill the placeholders
prompt = template.format(
    paper=paper_input,
    style=style_input,
    audience=audience_input,
    length=lenght_input
)

user_input = st.text_input("Enter your prompt here:")
if st.button("Summarize"):
    model = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o",
        temperature=0,
        max_tokens=1000,
    )
    result = model.invoke(prompt)
    st.write(result.content)
