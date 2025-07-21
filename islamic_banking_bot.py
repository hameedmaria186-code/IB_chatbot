import streamlit as st
import pymupdf
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-8b")

def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip().lower())

def extract_text_from_pdf(pdf_file):
    doc = pymupdf.open("islamic banking.pdf")
    full_text = ""

    for page in doc:
        full_text += page.get_text()
    return clean_text(full_text)

def generate_answers(content, query):
    prompt = f'''
    Based on the Following content:
    {content}

    Answer the following query:
    {query}

    Provide a concise, clear and relevant answer.
    '''
    try:
        response = model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text if response.candidates else "No answer generated"
    except Exception as e:
        return f"Error: {str(e)}"

st.set_page_config(page_title="Chat bot on Islamic Banking")
st.header("Ask Questions about Islamic Banking")


if 'pdf_content' not in st.session_state:
    st.session_state['pdf_content'] = extract_text_from_pdf("islamic banking.pdf")
    st.success("Pdf Content loaded successfully")
query = st.text_input("Enter your question:")

if st.button("Generate Answer") and st.session_state['pdf_content']:
    content = st.session_state['pdf_content']
    answer = generate_answers(content, query)

    st.subheader("Generated Answer:")
    st.text(answer)

