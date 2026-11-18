
import streamlit as st
import os
import io
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
from docx import Document

# Load API Key

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

# Initialize Gemini
client = genai.Client(api_key=api_key) if api_key else None

# Page Configuration
st.set_page_config(
    page_title="GenAI Resume Assistant",
    page_icon="📄",
    layout="wide"
)


# Custom CSS
st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.stApp {
    background-color: #f5f7fb;
}

h1 {
    color: #172554;
    font-weight: 700;
}

h2, h3 {
    color: #1e3a8a;
}

.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #eaf0ff;
}

div[data-testid="stFileUploader"] {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
}

div[data-testid="stTextArea"] textarea {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


st.title("📄 GenAI Resume Assistant")
st.write("Analyze and improve your resume using Generative AI.")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📄 Resume Analysis")

with col2:
    st.info("✨ AI Resume Improvement")

with col3:
    st.info("🎯 Job Matching")

st.markdown("---")

# Sidebar
st.sidebar.title("Navigation")

option = st.sidebar.selectbox(
    "Choose an Option",
    ["Resume Analyzer", "Resume Improver",
     "Job Matching", "Interview Questions"]
)

# Resume Extraction Function
def extract_resume_text(uploaded_file):

    if uploaded_file.name.endswith(".pdf"):

        pdf = PdfReader(uploaded_file)
        text = ""

        for page in pdf.pages:
            text += page.extract_text() or ""

        return text

    elif uploaded_file.name.endswith(".docx"):

        document = Document(
            io.BytesIO(uploaded_file.getvalue())
        )

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

        return text

# Resume Analyzer
if option == "Resume Analyzer":

    st.header("🔍 AI Resume Analysis")

    uploaded_file = st.file_uploader(
        "Upload Your Resume",
        type=["pdf", "docx"]
    )

    if uploaded_file is not None:

        resume_text = extract_resume_text(uploaded_file)

        if resume_text.strip():

            st.success("Resume uploaded successfully!")

            if st.button("Analyze My Resume"):

                if client is None:
                    st.error("Gemini API key not found. Check your .env file.")

                else:

                    prompt = f"""
                    You are an expert resume reviewer.

                    Analyze the following resume carefully.

                    Provide the following sections:

                    1. Overall Resume Summary
                    2. Technical Skills
                    3. Soft Skills
                    4. Key Strengths
                    5. Weaknesses and Missing Information
                    6. Suggestions for Improvement
                    7. Estimated ATS Compatibility Score out of 100

                    Give clear and practical suggestions.

                    Do not invent qualifications, skills,
                    experience or achievements that are not
                    supported by the resume.

                    Explain that the ATS score is an estimate,
                    not a score from an actual ATS platform.

                    Resume Content:
                    {resume_text}
                    """

                    with st.spinner("Gemini AI is analyzing your resume..."):

                        try:

                            response = client.models.generate_content(
                                model="gemini-3.5-flash-lite",
                                contents=prompt
                            )

                            st.subheader("📊 Resume Analysis Results")

                            st.markdown(response.text)

                            st.download_button(
                                label="📥 Download Resume Analysis Report",
                                data=response.text,
                                file_name="resume_analysis_report.txt",
                                mime="text/plain"
)


                        except Exception as e:
                            st.error(f"Error: {e}")

        else:
            st.warning("No readable text found in the resume.")

# Other Features

elif option == "Resume Improver":

    st.header("✨ AI Resume Improver")

    st.write(
        "Enter your existing resume content "
        "and let Gemini improve it."
    )

    resume_content = st.text_area(
        "Enter Your Resume Content",
        height=250,
        placeholder="Example: I know python, SQL and power bi. I worked on sales analysis project."
    )

    if st.button("Improve My Resume"):

        if not resume_content.strip():
            st.warning("Please enter your resume content.")

        elif client is None:
            st.error("Gemini API key not found. Check your .env file.")

        else:

            prompt = f"""
            You are a professional resume writer.

            Improve the following resume content.

            Requirements:
            1. Correct grammar and spelling.
            2. Use professional language.
            3. Improve sentence structure.
            4. Use ATS-friendly keywords naturally.
            5. Keep the original meaning.
            6. Do not invent skills, experience,
               qualifications or achievements.
            7. Make the content clear and concise.

            Original Resume Content:

            {resume_content}

            Provide only the improved resume content.
            """

            with st.spinner("Improving your resume..."):

                try:

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt
                    )

                    st.subheader("Improved Resume Content")

                    st.markdown(response.text)

                    st.download_button(
                        label="Download Improved Resume",
                        data=response.text,
                        file_name="improved_resume.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"Error: {e}")



elif option == "Job Matching":

    st.header("🎯 Job Description Matching")

    st.write(
        "Compare your resume with a job description "
        "using Gemini AI."
    )

    uploaded_file = st.file_uploader(
        "Upload Your Resume",
        type=["pdf", "docx"],
        key="job_resume"
    )

    job_description = st.text_area(
        "Paste Job Description",
        height=250,
        placeholder="Enter the complete job description here..."
    )

    if st.button("Analyze Job Match"):

        if uploaded_file is None:
            st.warning("Please upload your resume.")

        elif not job_description.strip():
            st.warning("Please enter a job description.")

        elif client is None:
            st.error("Gemini API key not found. Check your .env file.")

        else:

            resume_text = extract_resume_text(uploaded_file)

            if not resume_text.strip():
                st.warning("No readable text found in the resume.")

            else:

                prompt = f"""
                You are an expert career advisor.

                Compare the candidate's resume with
                the given job description.

                Provide the following:

                1. Estimated Job Match Score out of 100.
                2. Matching Skills.
                3. Missing or Underrepresented Skills.
                4. Relevant Experience.
                5. Areas for Improvement.
                6. Recommendations to improve job suitability.

                Evaluate skills, experience and qualifications
                based only on the provided information.

                Do not invent candidate qualifications
                or experience.

                Explain that the match score is an estimate,
                not an actual employer or ATS score.

                RESUME:
                {resume_text}

                JOB DESCRIPTION:
                {job_description}
                """

                with st.spinner("Analyzing job match..."):

                    try:

                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=prompt
                        )

                        st.subheader("📊 Job Match Results")

                        st.markdown(response.text)

                    except Exception as e:
                        st.error(f"Error: {e}")



elif option == "Interview Questions":

    st.header("🎤 AI Interview Question Generator")

    st.write(
        "Generate personalized interview questions "
        "based on your resume."
    )

    uploaded_file = st.file_uploader(
        "Upload Your Resume",
        type=["pdf", "docx"],
        key="interview_resume"
    )

    job_role = st.text_input(
        "Enter Target Job Role",
        placeholder="Example: Data Analyst"
    )

    question_type = st.selectbox(
        "Choose Interview Type",
        [
            "Technical Questions",
            "HR Questions",
            "Project-Based Questions",
            "Mixed Questions"
        ]
    )

    if st.button("Generate Interview Questions"):

        if uploaded_file is None:
            st.warning("Please upload your resume.")

        elif not job_role.strip():
            st.warning("Please enter a job role.")

        elif client is None:
            st.error("Gemini API key not found. Check your .env file.")

        else:

            resume_text = extract_resume_text(uploaded_file)

            if not resume_text.strip():
                st.warning("No readable text found in the resume.")

            else:

                prompt = f"""
                You are an experienced technical interviewer.

                Generate 10 interview questions based on
                the candidate's resume.

                Target Job Role: {job_role}

                Interview Type: {question_type}

                Resume Content:
                {resume_text}

                Requirements:

                1. Generate relevant interview questions.
                2. Include questions about the candidate's skills.
                3. Include questions about projects if relevant.
                4. Make questions suitable for the target role.
                5. Provide a suggested answer for each question.
                6. Keep answers clear and beginner-friendly.
                7. Do not assume experience that is not
                   mentioned in the resume.

                Format the output with numbered questions
                and suggested answers.
                """

                with st.spinner(
                    "Generating interview questions..."
                ):

                    try:

                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=prompt
                        )

                        st.subheader("🎯 Interview Preparation")

                        st.markdown(response.text)

                    except Exception as e:
                        st.error(f"Error: {e}")

