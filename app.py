import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()  # Load environment variables

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ API key not found. Please set GOOGLE_API_KEY in .env file")
    st.stop()  # This will stop the app if no key is found

genai.configure(api_key=api_key)  # Configure before any Gemini calls

# --- MUST BE FIRST STREAMLIT COMMAND ---
st.set_page_config(
    page_title="Medical AI Agent", 
    page_icon="🏥", 
    layout="wide",  # CHANGED from "centered" to "wide"
    initial_sidebar_state="collapsed"
)

# --- Hide Default UI Elements ---
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        .stDeployButton {display: none;}
        footer {visibility: hidden;}
        /* Remove max-width constraint */
        .stApp { 
            background-color: #f0f2f6;
            margin: 0;
            padding: 2rem 4rem;
        }
        /* Make form elements wider */
        .stTextInput>div>div>input {
            width: 100% !important;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Updated Custom CSS ---
def set_custom_css():
    st.markdown(
        """
        <style>
            /* Black text everywhere except input labels */
            body, p, h1, h2, h3, h4, h5, h6, .stChatMessage, .stMarkdown, 
            .stAlert, .stToast, .disclaimer-box, .stButton>button {
                color: #000000 !important;
            }
            
            /* Full-width containers */
            .main .block-container {
                max-width: 100% !important;
                padding-left: 5%;
                padding-right: 5%;
            }
            
            /* Wider file uploader */
            .stFileUploader>div {
                width: 100% !important;
            }
            
            /* Preserve other styling */
            .stButton>button {
                background-color: #0066cc;
                border-radius: 10px;
                width: 150px !important;
            }
            .disclaimer-box {
                background-color: #fff3cd;
                padding: 12px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #ffc107;
                width: 100%;
            }
            [data-testid="user"] {
                background-color: #e6f2ff;
            }
            [data-testid="assistant"] {
                background-color: #f0fff0;
                border-left: 4px solid #008080;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
set_custom_css()

# --- Main Content ---
col1, col2 = st.columns([3, 1])  # For potential logo placement
with col1:
    st.title("🏥 AI-Powered Medical Assistant")
    st.write("Ask medical questions or upload files for analysis.")

# --- Disclaimer (Full-width) ---
st.markdown(
    """
    <div class="disclaimer-box">
        ⚠️ <strong>Disclaimer:</strong> This AI provides informational support only. 
        Always consult a healthcare professional for medical advice.
    </div>
    """,
    unsafe_allow_html=True
)

# --- Rest of Your Code (Now Full-Width) ---
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# File uploader (full-width)
uploaded_file = st.file_uploader(
    "Upload a medical image or prescription", 
    type=["jpg", "jpeg", "png", "pdf"],
    help="Drag and drop or click to browse files"
)
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="📌 Uploaded File", use_container_width=True)
    st.session_state.uploaded_image = image

# User input (full-width)
user_input = st.text_input(
    "Describe symptoms or ask a medical question:", 
    "", 
    key="user_input",
    placeholder="Example: I've had a headache for 3 days with nausea...",
    label_visibility="collapsed"  # This hides the "Press Enter to apply" text
)

if st.button("🔍 Analyze", type="primary"):
    if not user_input:
        st.warning("Please enter a medical question")
    else:
        with st.chat_message("user"):
            st.write(user_input)
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Analyzing... 🩺"):
            model = genai.GenerativeModel("gemini-1.5-flash")
            medical_prompt = (
                "You are a highly specialized medical AI assistant. "
                "You only provide responses related to medical topics, patient symptoms, diagnoses, treatments, and medication analysis. "
                "Ignore any non-medical queries and focus solely on medical image analysis and symptom interpretation. "
                "If a question is unrelated to medicine, respond with 'I only provide medical-related information.'"
            )
            
            if uploaded_file:
                response = model.generate_content([medical_prompt + user_input, st.session_state.uploaded_image])
            else:
                response = model.generate_content(medical_prompt + user_input)
            
            bot_reply = response.text if response.text else "I'm sorry, I couldn't generate a response. Please consult a doctor."
        
        with st.chat_message("assistant"):
            st.write(bot_reply)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})