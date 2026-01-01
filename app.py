import streamlit as st
import google.generativeai as genai
import os
import io
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# -------- GEMINI RESPONSE FUNCTION --------
def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text


# -------- PDF TEXT EXTRACTION --------
def input_pdf_text(uploaded_file):
    text = ""

    # Read file as bytes (IMPORTANT for Streamlit Cloud)
    pdf_bytes = uploaded_file.read()
    pdf_stream = io.BytesIO(pdf_bytes)

    reader = PdfReader(pdf_stream)
    for page in reader.pages:
        text += page.extract_text() or ""

    return text


# -------- PROMPT TEMPLATE --------
input_prompt = """
You are a highly skilled ATS (Applicant Tracking System) with expertise in:
Software Engineering, AI/ML, Data Science, Data Analysis, and Big Data.

Evaluate the resume against the given job description.
The job market is very competitive, so provide accurate analysis.

Resume:
{text}

Job Description:
{jd}

Return the response strictly in the following JSON format:
{{
  "JD Match": "XX%",
  "Missing Keywords": [],
  "Profile Summary": ""
}}
"""


# -------- STREAMLIT UI --------
st.set_page_config(page_title="Smart ATS", page_icon="📄", layout="centered")

st.title("📄 Smart ATS Resume Analyzer")
st.write("Improve your resume using AI-powered ATS evaluation")

jd = st.text_area("📌 Paste Job Description Here")
uploaded_file = st.file_uploader(
    "📎 Upload Your Resume (PDF only)", type=["pdf"]
)

submit = st.button("🔍 Analyze Resume")


# -------- MAIN LOGIC --------
if submit:
    if uploaded_file is None:
        st.warning("⚠️ Please upload a resume PDF.")
    elif jd.strip() == "":
        st.warning("⚠️ Please paste the job description.")
    else:
        with st.spinner("Analyzing resume with AI..."):
            resume_text = input_pdf_text(uploaded_file)

            final_prompt = input_prompt.format(
                text=resume_text,
                jd=jd
            )

            response = get_gemini_response(final_prompt)

        st.subheader("📊 ATS Evaluation Result")

        # Try to format JSON output nicely
        try:
            response_json = json.loads(response)
            st.json(response_json)
        except:
            st.write(response)
