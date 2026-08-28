"""
app.py — Clinical Document Intelligence Hub (Streamlit UI).

Run:  streamlit run app.py
"""

import streamlit as st

from pipeline import analyze_uploaded_file, analyze_uploaded_files
from ui.components import (
    MULTI_PIPELINE_STEPS,
    PIPELINE_STEPS,
    render_disclaimer,
    render_empty_state,
    render_footer,
    render_hero,
    render_results,
    render_sidebar,
    render_top_nav,
    render_trust_strip,
)
from ui.styles import inject_styles


def run_analysis_single(uploaded_file):
    progress = st.progress(0, text="Parsing document...")
    for i, step in enumerate(PIPELINE_STEPS):
        progress.progress((i + 1) / len(PIPELINE_STEPS), text=step)
    result = analyze_uploaded_file(uploaded_file.getvalue(), uploaded_file.name)
    progress.empty()
    return result


def run_analysis_multi(uploaded_files, patient_id: str):
    progress = st.progress(0, text="Processing documents...")
    for i, step in enumerate(MULTI_PIPELINE_STEPS):
        progress.progress((i + 1) / len(MULTI_PIPELINE_STEPS), text=step)
    uploads = [(item.getvalue(), item.name) for item in uploaded_files]
    result = analyze_uploaded_files(uploads, patient_id=patient_id or None)
    progress.empty()
    return result


def main() -> None:
    st.set_page_config(
        page_title="CDI Hub · Clinical Document Intelligence",
        page_icon="⚕",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()
    render_top_nav()
    render_trust_strip()

    result = st.session_state.get("analysis_result")
    if result is None:
        render_hero()

    render_disclaimer()

    mode, uploaded, uploaded_many, patient_id, analyze_clicked, clear_clicked = render_sidebar()

    if clear_clicked:
        st.session_state.pop("analysis_result", None)
        st.rerun()

    if analyze_clicked:
        try:
            with st.spinner("Running clinical intelligence pipeline..."):
                if mode == "Single document" and uploaded is not None:
                    st.session_state["analysis_result"] = run_analysis_single(uploaded)
                elif uploaded_many:
                    st.session_state["analysis_result"] = run_analysis_multi(
                        uploaded_many, patient_id
                    )
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
            st.session_state.pop("analysis_result", None)

    result = st.session_state.get("analysis_result")

    if result is None:
        render_empty_state(mode)
    else:
        render_results(result)

    render_footer()


if __name__ == "__main__":
    main()
