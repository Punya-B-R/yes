# 🩺 Dr. Sage - AI-Powered Medical Assistant  

**Dr. Sage** is an intelligent virtual health companion that provides *preliminary* medical insights through natural conversation. Powered by Google's Gemini AI, it helps users:  

- 🔍 Analyze symptoms and suggest possible conditions  
- 💊 Interpret prescriptions and medication instructions  
- 🖼️ Examine medical images (X-rays, skin photos, etc.)  
- 📄 Upload and discuss PDFs/images for instant analysis  

**Important Note**: This tool provides *informational support only* and should never replace professional medical advice. Always consult a healthcare provider for diagnoses and treatment.  

## 🌟 Live Demo Preview  
![Dr. Sage Interface](https://github.com/Punya-B-R/clinical-ai-agent/blob/master/Screenshot%202025-03-27%20170435.png?raw=true)  
*Caption explaining key features shown*  

## 🛠️ Local Setup Guide
### 1. **Install Python 3.9+**  
   Download from [python.org](https://www.python.org/downloads/) then verify:
   ```bash
   python --version
   ```

### 2. Clone the Repository
   ```bash
   git clone <repository-url>
   cd <repository-folder-name>
   ```

### 3. Set Up Virtual Environment
   ```bash
   python -m venv venv
   venv\Scripts\activate # Windows
   source venv/bin/activate # macOS/Linux
   ```

### 4. Install Dependencies
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
### 5. Configure API Key 
   - Get key from [Google AI Studio](https://aistudio.google.com/app/apikey)  
   - Add to `.env`:
     ```text
     GEMINI_API_KEY="YOUR_API_KEY"  # Paste your key here
     ```
     
### 6. Run the Application
   ```bash
   streamlit run app.py
   ```
   The application will start running at http://localhost:8501.
