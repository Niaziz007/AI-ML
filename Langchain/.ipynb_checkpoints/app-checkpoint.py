import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

st.header("Research Tool")

user_input = st.text_input("Enter the prompt")

if st.button('Summarize'):
    result = model.invoke(user_input)
    st.write(result.content)
    

