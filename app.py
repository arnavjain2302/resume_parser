import streamlit as st
import json
import pandas as pd
from parser import parse_resume, merge_schemas, SCHEMA, llm_strict_format, text_to_docx, text_to_pdf  # ← IMPORT from parser.py

st.title("📄 AI Resume Parser")

uploaded_file = st.file_uploader("Upload .docx", type=["docx"])
api_key = st.text_input("Enter your Gemini API key", type="password")

st.sidebar.header("Optional fields")
add_patents = st.sidebar.checkbox("Include patents")
add_awards = st.sidebar.checkbox("Include awards")
add_scholarships = st.sidebar.checkbox("Include scholarships")

selected_extras = []
if add_patents:
    selected_extras.append("patents")
if add_awards:
    selected_extras.append("awards")
if add_scholarships:
    selected_extras.append("scholarships")


effective_schema = merge_schemas(SCHEMA, selected_extras)

cola, colb, colc = st.columns([1,1,1])

if uploaded_file and api_key:
    with colb:
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
                file_name="resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            pdf_buffer = text_to_pdf(formatted_text)
            st.download_button(
                "Download as PDF",
                data=pdf_buffer,
                file_name="resume.pdf",
                mime="application/pdf"
            )
