import streamlit as st
import fitz  # pymupdf
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
from googletrans import Translator
from gtts import gTTS
import tempfile

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-8b")

def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip().lower())

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return clean_text(full_text)



def generate_answers(content, query):
    prompt = f'''
    You are a perfect islamic banking bot so based on the Following content:
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

def text_to_speech(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    return tmp_file.name

st.set_page_config(page_title="🕌 Shari’ah Guide", page_icon="🕌")
st.title("🕌 Shari’ah Guide")
st.subheader("💼 Islamic Banking, The Halal Way")
st.markdown('<span style="background-color: #d4edda;">*Ask your question – get a Shari’ah-compliant answer.*</span>', unsafe_allow_html=True)

@st.cache_data
def load_pdf_content():
    return extract_text_from_pdf("islamic banking.pdf")

if 'pdf_content' not in st.session_state:
    st.session_state['pdf_content'] = load_pdf_content()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
query = st.text_input("❓ Enter your question below:")


def is_islamic_banking_query(query):
    islamic_keywords = [
        "islamic", "halal", "haram", "shariah", "shari’ah", "riba",
        "interest", "mudarabah", "musharakah", "ijarah", "murabaha",
        "takaful", "profit", "loan", "finance", "bank", "investment",
        "islamic banking", "karz", "sood", "bay", "sukuk"
    ]
    query = query.lower()
    return any(keyword in query for keyword in islamic_keywords)

if st.button("🧾 Generate Answer") and query:
    if is_islamic_banking_query(query):
        with st.spinner("🔍 Searching for a Shari’ah-compliant answer..."):
            content = st.session_state['pdf_content']
            answer = generate_answers(content, query)
            
            st.success("✅ Answer generated:")
            st.markdown(f"**{answer}**")
            with st.spinner("Loading audio...."):
            # Audio generation and playback
                audio_file = text_to_speech(answer)
                audio_bytes = open(audio_file, "rb").read()
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.chat_history.append({"question": query, "answer": answer})

# Display chat history
        if st.session_state.chat_history:
            st.subheader("🧾 Chat History")
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**🧑 You:** {chat['question']}")
            st.markdown(f"**🤖 Bot:** {chat['answer']}")
            st.markdown("---")

            
    else:
        st.warning("⚠️ This bot is designed to answer questions related only to **Islamic Banking**. Please ask a relevant question.")