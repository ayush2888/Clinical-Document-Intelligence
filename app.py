"""
app.py — Clinical Document Intelligence Hub (Streamlit UI).

Professional dashboard: upload → analyze → patient summary card.
"""

import html
import json

import streamlit as st

from extraction import extraction_to_dict
from generation import POC_DISCLAIMER
from pipeline import AnalysisResult, analyze_uploaded_file

SUPPORTED_TYPES = ["txt", "pdf", "png", "jpg", "jpeg"]

PIPELINE_STEPS = [
    "Document ingestion",
    "AI structured extraction",
    "Confidence scoring",
    "Terminology normalization",
    "Knowledge retrieval",
    "Rule-based assessment",
    "Patient summary generation",
]

st.set_page_config(
    page_title="Clinical Document Intelligence Hub",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

          html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
          }

          .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1200px;
          }

          .hero {
            background: linear-gradient(135deg, #0f2744 0%, #1a4d7c 55%, #0d9488 100%);
            color: white;
            padding: 1.75rem 2rem;
            border-radius: 16px;
            margin-bottom: 1.25rem;
            box-shadow: 0 10px 30px rgba(15, 39, 68, 0.18);
          }
          .hero h1 {
            color: white !important;
            font-size: 1.85rem !important;
            font-weight: 700 !important;
            margin: 0 0 0.35rem 0 !important;
          }
          .hero p {
            color: rgba(255,255,255,0.92);
            margin: 0;
            font-size: 1rem;
          }

          .disclaimer {
            background: #fff7ed;
            border: 1px solid #fdba74;
            border-left: 5px solid #f97316;
            padding: 0.85rem 1rem;
            border-radius: 10px;
            color: #9a3412;
            font-size: 0.92rem;
            margin-bottom: 1rem;
          }

          .card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
            height: 100%;
          }
          .card-title {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 0.65rem;
          }
          .card-body {
            color: #0f172a;
            font-size: 0.98rem;
            line-height: 1.55;
          }

          .summary-card {
            background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1rem;
          }
          .summary-label {
            color: #1d4ed8;
            font-weight: 700;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
          }
          .summary-text {
            color: #0f172a;
            font-size: 1.05rem;
            line-height: 1.65;
          }

          .pill {
            display: inline-block;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 0.35rem;
          }
          .pill-high { background: #fee2e2; color: #b91c1c; }
          .pill-medium { background: #fef3c7; color: #b45309; }
          .pill-low { background: #dcfce7; color: #15803d; }
          .pill-critical { background: #fecaca; color: #991b1b; }

          .finding-item, .risk-item {
            padding: 0.55rem 0.75rem;
            border-radius: 10px;
            margin-bottom: 0.45rem;
            font-size: 0.93rem;
          }
          .finding-item {
            background: #f8fafc;
            border-left: 3px solid #3b82f6;
          }
          .risk-item {
            background: #fff7ed;
            border-left: 3px solid #f97316;
          }

          .next-step {
            background: #ecfdf5;
            border: 1px solid #6ee7b7;
            border-radius: 14px;
            padding: 1rem 1.15rem;
            color: #065f46;
            font-size: 1rem;
            line-height: 1.55;
          }

          div[data-testid="stSidebar"] {
            background: #f8fafc;
            border-right: 1px solid #e2e8f0;
          }

          .sidebar-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
          }

          .footer-note {
            color: #64748b;
            font-size: 0.82rem;
            line-height: 1.5;
            padding-top: 0.5rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def esc(text: str) -> str:
    """Escape text before inserting into HTML blocks."""
    return html.escape(text or "")


def severity_pill(severity: str) -> str:
    css = {
        "critical": "pill-critical",
        "high": "pill-high",
        "medium": "pill-medium",
        "low": "pill-low",
    }.get(severity.lower(), "pill-medium")
    return f'<span class="pill {css}">{severity.upper()}</span>'


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <h1>Clinical Document Intelligence Hub</h1>
          <p>Transform unstructured clinical documents into structured, review-ready intelligence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer() -> None:
    st.markdown(
        """
        <div class="disclaimer">
          <strong>Proof of concept — decision support only.</strong>
          Outputs require human review and are not autonomous medical advice or a clinical diagnosis.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[object | None, bool]:
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Document input</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload clinical file",
            type=SUPPORTED_TYPES,
            label_visibility="collapsed",
            help="Supported: TXT, PDF, PNG, JPG",
        )

        if uploaded:
            st.success(f"**{uploaded.name}**")
            st.caption(f"{uploaded.size:,} bytes")

        st.markdown("---")
        st.markdown('<div class="sidebar-title">Processing pipeline</div>', unsafe_allow_html=True)
        for idx, step in enumerate(PIPELINE_STEPS, start=1):
            st.markdown(f"{idx}. {step}")

        st.markdown("---")
        st.markdown('<div class="sidebar-title">Demo files</div>', unsafe_allow_html=True)
        st.caption("Try: physician_note.txt, discharge_summary.pdf, lab_report.png")

        analyze_clicked = st.button(
            "Analyze Document",
            type="primary",
            use_container_width=True,
            disabled=uploaded is None,
        )

    return uploaded, analyze_clicked


def run_analysis(uploaded_file) -> AnalysisResult:
    progress = st.progress(0, text="Starting analysis...")
    for i in range(len(PIPELINE_STEPS)):
        progress.progress((i + 1) / len(PIPELINE_STEPS), text=PIPELINE_STEPS[i])

    result = analyze_uploaded_file(uploaded_file.getvalue(), uploaded_file.name)
    progress.progress(1.0, text="Analysis complete")
    return result


def patient_metrics(result: AnalysisResult) -> None:
    patient = result.extraction.patient
    cols = st.columns(4)
    cols[0].metric("Patient", patient.name if patient and patient.name else "—")
    cols[1].metric("Age", patient.age if patient and patient.age else "—")
    cols[2].metric("Risk flags", len(result.summary.risk_flags))
    cols[3].metric("Lab results", len(result.extraction.laboratory_results))


def render_summary_section(result: AnalysisResult) -> None:
    summary = result.summary

    st.markdown("## Clinical summary")
    st.markdown(
        f"""
        <div class="summary-card">
          <div class="summary-label">Patient overview</div>
          <div class="summary-text">{esc(summary.patient_summary)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            '<div class="card"><div class="card-title">Key findings</div><div class="card-body">',
            unsafe_allow_html=True,
        )
        if summary.key_findings:
            for item in summary.key_findings:
                st.markdown(
                    f'<div class="finding-item">{esc(item)}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No key findings returned.")
        st.markdown("</div></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            '<div class="card"><div class="card-title">Risk flags</div><div class="card-body">',
            unsafe_allow_html=True,
        )
        if summary.risk_flags:
            for item in summary.risk_flags:
                st.markdown(
                    f'<div class="risk-item">{esc(item)}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No risk flags returned.")
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("### Recommended next step")
    st.markdown(
        f'<div class="next-step">{esc(summary.recommended_next_step)}</div>',
        unsafe_allow_html=True,
    )


def render_assessment_section(result: AnalysisResult) -> None:
    st.markdown("## Workflow assessment")
    st.caption("Deterministic rules applied to validated extraction + knowledge context.")

    for item in result.assessments:
        st.markdown(severity_pill(item.severity), unsafe_allow_html=True)
        st.markdown(f"**{item.finding}**")
        st.markdown(
            f"Action: `{item.recommended_action}` · Source: _{item.knowledge_source}_"
        )
        st.caption(f"Evidence: {item.evidence}")
        st.markdown("---")


def render_details_tabs(result: AnalysisResult) -> None:
    st.markdown("## Evidence & technical details")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Extracted text", "Structured data", "Evidence", "Knowledge", "Summary JSON"]
    )

    with tab1:
        st.text_area("Original document text", result.document.text, height=320)

    with tab2:
        st.json(extraction_to_dict(result.extraction))

    with tab3:
        extraction = result.extraction
        rows = []
        for dx in extraction.diagnoses:
            rows.append({"Type": "Diagnosis", "Name": dx.name, "Confidence": dx.confidence, "Evidence": dx.evidence})
        for med in extraction.medications:
            rows.append({"Type": "Medication", "Name": med.name, "Confidence": med.confidence, "Evidence": med.evidence})
        for lab in extraction.laboratory_results:
            rows.append({"Type": "Lab", "Name": lab.test_name, "Confidence": lab.confidence, "Evidence": lab.evidence})
        for vital in extraction.vital_signs:
            rows.append({"Type": "Vital", "Name": vital.name, "Confidence": vital.confidence, "Evidence": vital.evidence})
        st.dataframe(rows, use_container_width=True, hide_index=True)

    with tab4:
        if not result.knowledge:
            st.info("No knowledge passages retrieved.")
        for item in result.knowledge:
            with st.container(border=True):
                st.markdown(f"**{item.topic}**")
                st.caption(f"{item.source} · {item.version}")
                st.write(item.interpretation)
                if item.url:
                    st.markdown(f"[Open reference]({item.url})")

    with tab5:
        st.json(json.loads(result.summary.model_dump_json()))


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="card" style="text-align:center; padding: 2.5rem 1rem;">
          <div class="card-title">Ready to analyze</div>
          <div class="card-body">
            Upload a clinical document in the sidebar, then click <strong>Analyze Document</strong>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    render_hero()
    render_disclaimer()

    uploaded, analyze_clicked = render_sidebar()

    if analyze_clicked and uploaded is not None:
        try:
            with st.spinner("Running clinical intelligence pipeline..."):
                st.session_state["analysis_result"] = run_analysis(uploaded)
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
            st.session_state.pop("analysis_result", None)

    result: AnalysisResult | None = st.session_state.get("analysis_result")

    if result is None:
        render_empty_state()
        st.markdown(
            f'<div class="footer-note">{POC_DISCLAIMER}</div>',
            unsafe_allow_html=True,
        )
        return

    patient_metrics(result)
    st.markdown("")
    render_summary_section(result)
    render_assessment_section(result)
    render_details_tabs(result)

    st.markdown(
        f'<div class="footer-note">{POC_DISCLAIMER}</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
