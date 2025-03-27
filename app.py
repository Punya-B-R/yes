import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import tempfile
from PyPDF2 import PdfReader

load_dotenv()

# Initialize all session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = None

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ API key not found. Please set GOOGLE_API_KEY in .env file")
    st.stop()

genai.configure(api_key=api_key)

st.set_page_config(
    page_title="Medical AI Agent", 
    page_icon="🏥", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        .stDeployButton {display: none;}
        footer {visibility: hidden;}
        .stApp { 
            background-color: #f0f2f6;
            margin: 0;
            padding: 2rem 4rem;
        }
        .stTextInput>div>div>input {
            width: 100% !important;
        }
        .chat-container {
            height: 500px;
            overflow-y: auto;
            border-radius: 10px;
            padding: 15px;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: none;
        }
        .chat-container:has(> div) {
            display: block;
        }
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        .chat-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def set_custom_css():
    st.markdown(
        """
        <style>
            body, p, h1, h2, h3, h4, h5, h6, .stChatMessage, .stMarkdown, 
            .stAlert, .stToast, .disclaimer-box, .stButton>button {
                color: #000000 !important;
            }
            .main .block-container {
                max-width: 100% !important;
                padding-left: 5%;
                padding-right: 5%;
            }
            .stFileUploader>div {
                width: 100% !important;
            }
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
                margin: 5px 0;
                border-radius: 10px;
                padding: 10px;
            }
            [data-testid="assistant"] {
                background-color: #f0fff0;
                border-left: 4px solid #008080;
                margin: 5px 0;
                border-radius: 10px;
                padding: 10px;
            }
            .stChatMessage {
                max-width: 80% !important;
            }
            .chat-container {
                transition: all 0.3s ease;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
set_custom_css()

col1, col2 = st.columns([3, 1])
with col1:
    st.title("🩺 Dr. Sage: Your Virtual Health Companion")
    st.write("Ask medical questions or upload files for analysis.")

st.markdown(
    """
    <div class="disclaimer-box">
        ⚠️ <strong>Disclaimer:</strong> This AI provides informational support only and is not a substitute for professional medical advice. 
        Always consult a healthcare professional for accurate diagnosis and treatment.
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload a medical image or prescription", 
    type=["jpg", "jpeg", "png", "pdf"],
    help="Drag and drop or click to browse files"
)

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        try:
            reader = PdfReader(tmp_path)
            text = "\n".join([page.extract_text() for page in reader.pages])
            st.session_state.uploaded_text = text
            st.session_state.uploaded_image = None
            st.success("📄 PDF uploaded successfully!")
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
        finally:
            os.unlink(tmp_path)
    else:
        try:
            st.session_state.uploaded_image = Image.open(uploaded_file)
            st.session_state.uploaded_text = None
            st.image(st.session_state.uploaded_image, caption="📌 Uploaded File", use_container_width=True)
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

if st.session_state.messages:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
        Describe symptoms or ask a medical question:
    </div>
""", unsafe_allow_html=True)

user_input = st.chat_input(
    "Example: I've had a headache for 3 days with nausea...",
    key="user_input"
)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    with st.spinner("Analyzing... 🩺"):
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        medical_prompt = (
            "You are Dr. Sage, a highly specialized medical AI assistant and virtual health companion. "
            "Your primary role is to provide accurate medical information while maintaining a friendly, professional tone. "
            
            # Medical capabilities (your original requirements)
            "Specialize in medical topics including: "
            "- Patient symptoms analysis "
            "- Diagnosis information "
            "- Treatment options overview "
            "- Medication analysis "
            "- Medical image interpretation "
            
            # Response rules
            "Response guidelines: "
            "1. For MEDICAL queries: "
            "   - Provide helpful, evidence-based information "
            "   - Always emphasize the need for professional consultation "
            
            "2. ONLY when the user says exactly 'hi', 'hello', or 'hey' (and no other words), respond with: "
            "'Hello! I'm Dr. Sage, your virtual health assistant. How can I help with your medical questions today?' "
            "Otherwise, skip this greeting completely and proceed to answer the medical question directly. "
            
            "3. For THANKS (thanks/thank you): "
            "   'You're very welcome! Remember I'm here if you have any other health concerns.' "
            
            "4. For NON-MEDICAL queries: "
            "   'As Dr. Sage, I specialize in health-related topics. Would you like to discuss any medical concerns?' "
            
            # Update just the medical image portion of your prompt to:
            "5. For MEDICAL IMAGES: \n"
            "   - Analyze all visible features thoroughly \n"
            "   - Provide potential diagnostic possibilities based on visual evidence \n"
            "   - Clearly state these are not definitive diagnoses \n"
            "   - Explain your visual findings and reasoning \n"
            "   - Always recommend confirmation from a healthcare professional \n"
            "   - For serious conditions, advise immediate medical attention \n"
            
            "6. Wellness check ('how are you','how you doing','how do you do'): 'I'm functioning well as your AI health assistant! Do you have any medical questions?'\n"

            "7. For PRESCRIPTIONS: \n"
            "   - Analyze medication combinations to suggest possible conditions \n"
            "   - Explain likely purpose of each medication type \n"
            "   - Note any unusual dosing patterns \n"
            "   - Flag potential interactions to verify with doctor \n"
            "   - Example format: \n"
            "     1. Medication Analysis: [details] \n"
            "     2. Condition Insights: [likely purposes] \n"
            "     3. Professional Verification Needed For: [specific items] \n"

            "Safety protocols: "
            "- Never replace professional medical advice "
            "- Always suggest consulting a healthcare provider for serious symptoms "
            
            "Current query: "
        )
        
        if uploaded_file:
            if st.session_state.uploaded_text:
                response = model.generate_content([medical_prompt + user_input, st.session_state.uploaded_text])
            elif st.session_state.uploaded_image:
                response = model.generate_content([medical_prompt + user_input, st.session_state.uploaded_image])
            else:
                response = model.generate_content(medical_prompt + user_input)
        else:
            response = model.generate_content(medical_prompt + user_input)
        
        bot_reply = response.text if response.text else "I'm sorry, I couldn't generate a response. Please consult a doctor."
    
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.write(bot_reply)
    
    st.rerun()