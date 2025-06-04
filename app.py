import streamlit as st
import fitz  # PyMuPDF
import os
import tempfile
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini 2.5 Flash model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Streamlit page settings
st.set_page_config(
    page_title="📄 Gemini PDF Summarizer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for an amazing and vibrant UI
st.markdown("""
    <style>
    /* General styling */
    .stApp {
        max-width: 1300px;
        margin: 0 auto;
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #6B48FF 0%, #00DDEB 100%);
        padding: 20px;
        min-height: 100vh;
    }
    
    /* Title and subtitle */
    .title {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        animation: bounceIn 1s ease;
    }
    .subtitle {
        font-size: 1.3rem;
        color: #f1f1f1;
        text-align: center;
        margin-bottom: 2.5rem;
        animation: fadeIn 1.5s ease;
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.95);
        border: 3px dashed #FF6B6B;
        border-radius: 15px;
        padding: 25px;
        transition: all 0.4s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .stFileUploader > div > div:hover {
        border-color: #FFD700;
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #FFD700);
        color: #ffffff;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #FFD700, #FF6B6B);
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Summary and text box */
    .summary-box, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        color: #1a1a1a !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
        animation: slideIn 0.7s ease;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Expander */
    .stExpander {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    .stExpander summary {
        font-weight: 600;
        color: #1a3c87;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(45deg, #FF6B6B, #FFD700);
    }
    
    /* Animations */
    @keyframes bounceIn {
        0% { transform: scale(0.8); opacity: 0; }
        60% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(1); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideIn {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .title {
            font-size: 2.2rem;
        }
        .subtitle {
            font-size: 1.1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Confetti animation for success
def confetti():
    components.html("""
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
        <script>
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#FF6B6B', '#FFD700', '#6B48FF']
            });
        </script>
    """, height=0)

# Sidebar for settings
with st.sidebar:
    st.markdown("<h2 style='color: #1a3c87; font-weight: 700;'>⚡ Summarizer Settings</h2>", unsafe_allow_html=True)
    summary_length = st.slider("Summary Length (words)", 50, 500, 200, help="Control the length of the generated summary.")
    summary_style = st.selectbox("Summary Style", ["Bullet Points", "Paragraph"], help="Choose the format of the summary.")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>✨ Powered by Gemini 2.5 Flash</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'> Made with ❤️ by Roney Karki</p>", unsafe_allow_html=True)

# Main content
st.markdown("""
    <div class='title'>📄 AI PDF Summarizer</div>
    <div class='subtitle'>Transform your PDFs into concise insights with <span style='color: #FFD700;'>Gemini 2.5 Flash</span> ✨</div>
""", unsafe_allow_html=True)

# File uploader
st.markdown("<div style='text-align: center; margin-bottom: 1rem; color: #ffffff;'>📤 Drop your PDF or click to upload</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

if uploaded_file:
    # Progress bar
    progress_bar = st.progress(0)
    progress_bar.progress(10)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.success("✅ PDF uploaded successfully! Let's dive in...")

    # Extract text
    with st.spinner("📚 Extracting text from your PDF..."):
        doc = fitz.open(tmp_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        progress_bar.progress(50)

    # Show extracted text
    with st.expander("📖 View Extracted Text", expanded=False):
        st.text_area("Raw Text", text, height=250, disabled=True)

    if len(text) < 100:
        st.warning("⚠️ The PDF doesn't have enough readable text for summarization.")
    else:
        with st.spinner("🤖 Crafting your magical summary..."):
            try:
                # Dynamic prompt based on user selections
                prompt = f"Summarize the following PDF content in {'simple bullet points' if summary_style == 'Bullet Points' else 'a concise paragraph'} (aim for ~{summary_length} words):\n\n{text}"
                response = model.generate_content(prompt)
                summary = response.text
                progress_bar.progress(100)

                confetti()  # Trigger confetti animation
                st.subheader("📝 Your Sparkling Summary")
                st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)

                # Download button
                st.download_button(
                    label="📥 Download Summary",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ Error generating summary: {e}")
                progress_bar.progress(0)

    os.remove(tmp_path)
else:
    st.markdown("<div style='text-align: center; color: #f1f1f1;'>🎯 Upload a PDF to unlock the magic!</div>", unsafe_allow_html=True)