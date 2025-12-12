import streamlit as st
import json
import pandas as pd
from parser import *

st.title("📄 AI Resume Parser")

uploaded_file = st.file_uploader("Upload .docx", type=["docx"] , key="resume_file_uploader")
api_key = st.text_input("Enter your Gemini API key", type="password" , key = "api_key")

st.sidebar.header("🚀 Project Description")
st.sidebar.markdown(
    """
    This tool uses the **Gemini 2.5 Flash** model to automatically parse,
    extract, and reformat data from a Word (.docx) resume file.
    """
)

st.sidebar.header("📋 How to Use")
st.sidebar.markdown(
    """
    1. **Upload:** Upload your resume as a `.docx` file.
    2. **API Key:** Enter your Google Gemini API key (required).
    3. **Select Sections:** Choose the sections (Education, Experience, etc.) 
       you want to include in the output schema.
    4. **Summarize:** Click 'Summarize' to start the extraction process.
    5. **View:** View the output as structured JSON or a polished 
       Markdown resume.
    6. **Download:** Download it as JSON, DOCX or PDF file.
    """
)
st.sidebar.info("Note: The base response always includes Name, Email, and Phone.")

st.write("---")

col_check, col_content = st.columns([1, 2])

selected_extras = []
selectable_attributes = list(AVAILABLE_ATTRIBUTES.keys())

with col_check:
    st.subheader("Select Sections")
    
    for key in selectable_attributes:
        default_value = key in ["education", "experience", "skills"]
        if st.checkbox(key.title(), value=default_value):
            selected_extras.append(key)

effective_schema = merge_schemas(SCHEMA, selected_extras)

with col_content:

    st.text("") 
    st.text("")
    
    if uploaded_file and api_key:
        if st.button("Summarize"):
            with st.spinner("Reading resume..."):
                parsed = parse_resume(uploaded_file, api_key, effective_schema)
                st.session_state["parsed"] = parsed
                formatted = llm_strict_format(api_key, parsed)
                st.session_state["formatted"] = formatted
                st.success("Output Generated")

if "parsed" in st.session_state:
    
    if "view" not in st.session_state:
        st.session_state["view"] = None

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Show JSON"):
            st.session_state["view"] = "json"

    with col2:
        if st.button("Show Text"):
            st.session_state["view"] = "text"

    st.write("---")

    if st.session_state["view"] == "json":
        if "parsed" in st.session_state:
            st.subheader("Parsed JSON Output")
            st.json(st.session_state["parsed"])

            json_str = json.dumps(st.session_state["parsed"], indent=2, ensure_ascii=False)
            st.download_button(
                "Download JSON",
                data=json_str,
                file_name="resume.json",
                mime="application/json")

    if st.session_state["view"] == "text":
        if "formatted" in st.session_state:
            st.subheader("Formatted Resume")
            st.markdown(st.session_state["formatted"])

            st.subheader("Download Options")
            formatted_text = st.session_state["formatted"]
            docx_buffer = text_to_docx(formatted_text)
            st.download_button(
                "Download as DOCX",
                data=docx_buffer,
                file_name="formatted_resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            pdf_buffer = text_to_pdf(formatted_text)
            st.download_button(
                "Download as PDF",
                data=pdf_buffer,
                file_name="formatted_resume.pdf",
                mime="application/pdf"
            )

