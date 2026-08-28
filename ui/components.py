"""Reusable Streamlit dashboard components — healthcare SaaS layout."""

from __future__ import annotations

import html
import json

import streamlit as st

import config
from extraction import CONFIDENCE_DISCLAIMER, extraction_to_dict
from generation import POC_DISCLAIMER
from pipeline import AnalysisResult, PatientAnalysisResult

SUPPORTED_TYPES = ["txt", "pdf", "png", "jpg", "jpeg"]

PIPELINE_STEPS = [
    "Ingest",
    "Extract",
    "Score",
    "Normalize",
    "Knowledge",
    "Assess",
    "Summarize",
]

MULTI_PIPELINE_STEPS = PIPELINE_STEPS[:4] + ["Merge"] + PIPELINE_STEPS[4:]


def esc(text: str) -> str:
    return html.escape(text or "")


def render_html(html_content: str) -> None:
    """
    Render HTML blocks that must inherit app CSS from inject_styles().

    Use compact single-line HTML only — indented multiline strings get escaped
    by Markdown as <pre> code blocks (raw tags visible on screen).
    """
    st.markdown(html_content, unsafe_allow_html=True)


def severity_pill(severity: str) -> str:
    css = {
        "critical": "pill-critical",
        "high": "pill-high",
        "medium": "pill-medium",
        "low": "pill-low",
    }.get(severity.lower(), "pill-medium")
    return f'<span class="pill {css}">{severity.upper()}</span>'


def get_documents(result: AnalysisResult | PatientAnalysisResult) -> list:
    if isinstance(result, PatientAnalysisResult):
        return result.documents
    return [result.document]


def build_export_payload(result: AnalysisResult | PatientAnalysisResult) -> dict:
    payload = {
        "extraction": json.loads(result.extraction.model_dump_json()),
        "assessments": [json.loads(a.model_dump_json()) for a in result.assessments],
        "knowledge": [json.loads(k.model_dump_json()) for k in result.knowledge],
        "summary": json.loads(result.summary.model_dump_json()),
    }
    if isinstance(result, PatientAnalysisResult):
        payload["patient_id"] = result.patient_id
        payload["source_filenames"] = result.source_filenames
    else:
        payload["document"] = {
            "filename": result.document.filename,
            "source_type": result.document.source_type,
        }
    return payload


def render_top_nav() -> None:
    st.markdown(
        """
        <div class="top-nav">
          <div class="nav-brand">
            <div class="nav-logo">⚕</div>
            <div>
              <div class="nav-title">Clinical Document Intelligence Hub</div>
              <div class="nav-sub">Parse · Extract · Assess · Summarize</div>
            </div>
          </div>
          <div class="nav-badge">POC · Early Access</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trust_strip() -> None:
    st.markdown(
        """
        <div class="trust-strip">
          <span class="trust-pill"><strong>Evidence-backed</strong> extraction</span>
          <span class="trust-pill"><strong>Rule-validated</strong> workflow flags</span>
          <span class="trust-pill"><strong>Human review</strong> required</span>
          <span class="trust-pill">TXT · PDF · Image OCR</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-grid">
          <div class="hero-main">
            <div class="hero-eyebrow">Clinical History Intelligence</div>
            <h1>Turn health documents into structured, review-ready data.</h1>
            <p>Upload clinical documents — physician notes, discharge summaries, lab reports —
            and get structured extraction, workflow flags, and a cited patient summary in minutes.</p>
          </div>
          <div class="live-panel">
            <div class="live-panel-header">Live structured output preview</div>
            <div class="code-block">
              <div class="code-label">patient.diagnosis</div>
              <div class="code-content">
                {<br>
                &nbsp;&nbsp;<span class="code-key">"name"</span>: <span class="code-str">"Type 2 diabetes mellitus"</span>,<br>
                &nbsp;&nbsp;<span class="code-key">"canonical"</span>: <span class="code-str">"type_2_diabetes_mellitus"</span>,<br>
                &nbsp;&nbsp;<span class="code-key">"conf"</span>: <span class="code-num">0.98</span><br>
                }
              </div>
            </div>
            <div class="code-block">
              <div class="code-label">lab.hba1c</div>
              <div class="code-content">
                {<br>
                &nbsp;&nbsp;<span class="code-key">"value"</span>: <span class="code-str">"9.2%"</span>,<br>
                &nbsp;&nbsp;<span class="code-key">"evidence"</span>: <span class="code-str">"HbA1c: 9.2%"</span><br>
                }
              </div>
            </div>
            <div class="code-block">
              <div class="code-label">assessment.flag</div>
              <div class="code-content">
                {<br>
                &nbsp;&nbsp;<span class="code-key">"severity"</span>: <span class="code-str">"high"</span>,<br>
                &nbsp;&nbsp;<span class="code-key">"action"</span>: <span class="code-str">"requires_additional_review"</span><br>
                }
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer() -> None:
    st.markdown(
        """
        <div class="disclaimer">
          <strong>Decision support only — not a clinical diagnostic system.</strong>
          All outputs require qualified human review and are not autonomous medical advice.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[str, object | None, list | None, str, bool, bool]:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand-block">
              <div class="sidebar-logo-text">CDI Hub</div>
              <div class="sidebar-tagline">Clinical document intelligence platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section">Analysis mode</div>', unsafe_allow_html=True)
        mode = st.radio(
            "Mode",
            options=["Single document", "Multi-document (same patient)"],
            label_visibility="visible",
        )

        patient_id = ""
        uploaded = None
        uploaded_many: list | None = None

        st.markdown('<div class="sidebar-section">Upload documents</div>', unsafe_allow_html=True)

        if mode == "Single document":
            uploaded = st.file_uploader(
                "Choose a clinical file",
                type=SUPPORTED_TYPES,
                help="Supported formats: TXT, PDF, PNG, JPG (max 200 MB)",
            )
            if uploaded:
                st.success(f"✓ {uploaded.name}")
                st.caption(f"{uploaded.size:,} bytes")
        else:
            patient_id = st.text_input(
                "Patient case ID",
                value="patient_001",
                help="Label shown on the dashboard for this case.",
            )
            uploaded_many = st.file_uploader(
                "Choose clinical files (same patient)",
                type=SUPPORTED_TYPES,
                accept_multiple_files=True,
                help="Select 2 or more files for one patient.",
            )
            if uploaded_many:
                st.success(f"✓ {len(uploaded_many)} files ready")

        with st.expander("How it works"):
            steps = MULTI_PIPELINE_STEPS if mode.startswith("Multi") else PIPELINE_STEPS
            flow = " → ".join(steps)
            st.caption(flow)

        with st.expander("Demo files"):
            path = config.PATIENT_DEMO_DIR if mode.startswith("Multi") else config.DEMO_DIR
            st.code(str(path), language=None)

        st.markdown("---")

        has_input = uploaded is not None if mode == "Single document" else bool(uploaded_many)
        analyze_clicked = st.button(
            "⚡ Analyze Document" if mode == "Single document" else "⚡ Analyze Patient Case",
            type="primary",
            use_container_width=True,
            disabled=not has_input,
        )
        clear_clicked = st.button(
            "Clear results",
            use_container_width=True,
            disabled=st.session_state.get("analysis_result") is None,
        )

    return mode, uploaded, uploaded_many, patient_id, analyze_clicked, clear_clicked


def render_empty_state(mode: str) -> None:
    st.markdown(
        """
        <div class="section-header">
          <div class="section-title">How it works</div>
        </div>
        <div class="pipeline-flow">
          <span class="pipe-step">📄 Upload</span><span class="pipe-arrow">→</span>
          <span class="pipe-step">🔍 Parse & OCR</span><span class="pipe-arrow">→</span>
          <span class="pipe-step">🧠 AI Extract</span><span class="pipe-arrow">→</span>
          <span class="pipe-step">📋 Validate</span><span class="pipe-arrow">→</span>
          <span class="pipe-step">⚠️ Assess</span><span class="pipe-arrow">→</span>
          <span class="pipe-step">📊 Summary</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    upload_desc = (
        "Add 2+ documents for the same patient."
        if mode.startswith("Multi")
        else "Add a TXT, PDF, or image in the sidebar."
    )
    st.markdown(
        f"""
        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">📤</div>
            <div class="feature-title">1 · Upload</div>
            <div class="feature-desc">{upload_desc}</div>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">2 · Analyze</div>
            <div class="feature-desc">Run the 7-stage pipeline with Groq LLM extraction and Python validation.</div>
          </div>
          <div class="feature-card">
            <div class="feature-icon">✅</div>
            <div class="feature-title">3 · Review</div>
            <div class="feature-desc">Review cited summary, workflow flags, entity cards, and structured JSON.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _count_fields(extraction) -> int:
    return (
        len(extraction.diagnoses)
        + len(extraction.medications)
        + len(extraction.laboratory_results)
        + len(extraction.vital_signs)
    )


def render_metric_strip(result: AnalysisResult | PatientAnalysisResult) -> None:
    patient = result.extraction.patient
    is_multi = isinstance(result, PatientAnalysisResult)
    docs = get_documents(result)

    flagged = sum(
        1 for a in result.assessments if a.severity.lower() in ("critical", "high", "medium")
    )
    fields = _count_fields(result.extraction)
    avg_conf = _avg_confidence(result.extraction)

    st.markdown(
        f"""
        <div class="stat-grid">
          <div class="stat-card highlight">
            <div class="stat-label">Patient</div>
            <div class="stat-value" style="font-size:1.1rem;">{esc((patient.name if patient and patient.name else "—")[:28])}</div>
            <div class="stat-sub">{f"Age {patient.age} · {patient.sex}" if patient and patient.age else "From extraction"}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Fields extracted</div>
            <div class="stat-value">{fields}</div>
            <div class="stat-sub">Diagnoses · meds · labs · vitals</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Workflow flags</div>
            <div class="stat-value">{flagged}</div>
            <div class="stat-sub">Rule-based assessment</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Avg confidence</div>
            <div class="stat-value">{avg_conf}</div>
            <div class="stat-sub">AI extraction estimate</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _avg_confidence(extraction) -> str:
    scores = []
    for group in (
        extraction.diagnoses,
        extraction.medications,
        extraction.laboratory_results,
        extraction.vital_signs,
    ):
        for item in group:
            if item.confidence is not None:
                scores.append(item.confidence)
    if not scores:
        return "—"
    return f"{sum(scores) / len(scores):.0%}"


def render_export_bar(result: AnalysisResult | PatientAnalysisResult) -> None:
    payload = build_export_payload(result)
    json_bytes = json.dumps(payload, indent=2).encode("utf-8")
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(
            """
            <div class="section-header">
              <div class="section-title">Clinical Summary — Live Output</div>
              <div class="live-dot">Analysis complete</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.download_button(
            "⬇ Export JSON",
            data=json_bytes,
            file_name="clinical_analysis.json",
            mime="application/json",
            use_container_width=True,
        )


def _entity_card(tag: str, name: str, value: str, meta: str) -> str:
    return (
        f'<div class="entity-card">'
        f'<div class="entity-tag">{esc(tag)}</div>'
        f'<div class="entity-name">{esc(name)}</div>'
        f'<div class="entity-value">{esc(value)}</div>'
        f'<div class="entity-meta">{esc(meta)}</div>'
        f"</div>"
    )


def render_entity_cards(result: AnalysisResult | PatientAnalysisResult) -> None:
    extraction = result.extraction
    cards: list[str] = []

    for lab in extraction.laboratory_results[:8]:
        unit = lab.unit or ""
        conf = f"{lab.confidence:.0%}" if lab.confidence else "—"
        source = lab.source_document or "source doc"
        cards.append(
            _entity_card(
                "Lab result",
                lab.display_name or lab.test_name,
                f"{lab.value} {unit}".strip(),
                f"conf {conf} · {source}",
            )
        )

    for vital in extraction.vital_signs[:6]:
        unit = vital.unit or ""
        conf = f"{vital.confidence:.0%}" if vital.confidence else "—"
        cards.append(
            _entity_card(
                "Vital sign",
                vital.display_name or vital.name,
                f"{vital.value} {unit}".strip(),
                f"conf {conf}",
            )
        )

    for med in extraction.medications[:6]:
        cards.append(
            _entity_card(
                "Prescription",
                med.display_name or med.name,
                med.dose or "—",
                med.frequency or "",
            )
        )

    if cards:
        render_html(f'<div class="entity-grid">{"".join(cards)}</div>')


def render_multi_document_banner(result: PatientAnalysisResult) -> None:
    chips = "".join(f'<span class="doc-chip">{esc(n)}</span>' for n in result.source_filenames)
    render_html(
        f'<div class="card-shell">'
        f'<div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.07em;color:#64748b;margin-bottom:0.5rem;">'
        f"Merged case · {esc(result.patient_id or '—')}</div>{chips}</div>"
    )


def render_overview_tab(result: AnalysisResult | PatientAnalysisResult) -> None:
    summary = result.summary

    render_html(
        f'<div class="summary-panel">'
        f'<div class="summary-eyebrow">Patient overview</div>'
        f'<div class="summary-body">{esc(summary.patient_summary)}</div>'
        f"</div>"
    )

    render_entity_cards(result)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("**Key findings**")
        if summary.key_findings:
            for item in summary.key_findings:
                render_html(
                    f'<div class="citation-card finding">'
                    f'<div class="citation-title">{esc(item)}</div></div>'
                )
        else:
            st.caption("No key findings.")

    with col2:
        st.markdown("**Risk flags**")
        if summary.risk_flags:
            for item in summary.risk_flags:
                render_html(
                    f'<div class="citation-card alert">'
                    f'<div class="citation-title">{esc(item)}</div></div>'
                )
        else:
            st.caption("No risk flags.")

    st.markdown("**Recommended next step**")
    render_html(f'<div class="next-step-box">{esc(summary.recommended_next_step)}</div>')

    if summary.evidence_highlights:
        st.markdown("**Cited evidence**")
        for item in summary.evidence_highlights:
            render_html(
                f'<div class="citation-card">'
                f'<div class="citation-body">{esc(item)}</div>'
                f'<div class="citation-source"><strong>Cited:</strong> source document evidence</div>'
                f"</div>"
            )


def render_assessment_tab(result: AnalysisResult | PatientAnalysisResult) -> None:
    st.caption("Deterministic workflow rules — transparent thresholds, no autonomous prescribing.")

    if not result.assessments:
        st.info("No workflow flags detected.")
        return

    for item in result.assessments:
        is_alert = item.severity.lower() in ("critical", "high")
        card_class = "citation-card alert" if is_alert else "citation-card"
        render_html(
            f'<div class="{card_class}">'
            f"{severity_pill(item.severity)}"
            f'<div class="citation-title" style="margin-top:0.5rem;">{esc(item.finding)}</div>'
            f'<div class="citation-body">Action: <code>{esc(item.recommended_action)}</code></div>'
            f'<div class="citation-source"><strong>Source:</strong> {esc(item.knowledge_source)}</div>'
            f'<div class="citation-source"><strong>Evidence:</strong> {esc(item.evidence)}</div>'
            f"</div>"
        )


def _evidence_rows(extraction) -> list[dict]:
    rows = []
    for dx in extraction.diagnoses:
        rows.append({
            "Category": "Diagnosis",
            "Field": dx.display_name or dx.name,
            "Value": "—",
            "Confidence": dx.confidence,
            "Source": dx.source_document or "—",
            "Evidence": dx.evidence,
        })
    for med in extraction.medications:
        val = f"{med.dose or ''} {med.frequency or ''}".strip() or "—"
        rows.append({
            "Category": "Medication",
            "Field": med.display_name or med.name,
            "Value": val,
            "Confidence": med.confidence,
            "Source": med.source_document or "—",
            "Evidence": med.evidence,
        })
    for lab in extraction.laboratory_results:
        rows.append({
            "Category": "Lab",
            "Field": lab.display_name or lab.test_name,
            "Value": f"{lab.value} {lab.unit or ''}".strip(),
            "Confidence": lab.confidence,
            "Source": lab.source_document or "—",
            "Evidence": lab.evidence,
        })
    for vital in extraction.vital_signs:
        rows.append({
            "Category": "Vital",
            "Field": vital.display_name or vital.name,
            "Value": f"{vital.value} {vital.unit or ''}".strip(),
            "Confidence": vital.confidence,
            "Source": vital.source_document or "—",
            "Evidence": vital.evidence,
        })
    return rows


def render_evidence_tab(result: AnalysisResult | PatientAnalysisResult) -> None:
    st.caption(CONFIDENCE_DISCLAIMER)
    rows = _evidence_rows(result.extraction)
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No evidence rows.")


def render_data_tab(result: AnalysisResult | PatientAnalysisResult) -> None:
    sub1, sub2, sub3 = st.tabs(["Document text", "Structured JSON", "Knowledge"])

    documents = get_documents(result)
    with sub1:
        if len(documents) == 1:
            st.text_area("Text", documents[0].text, height=380, label_visibility="collapsed")
        else:
            for doc in documents:
                with st.expander(f"{doc.filename} · {doc.source_type}"):
                    st.text_area("Text", doc.text, height=240, label_visibility="collapsed")

    with sub2:
        st.json(extraction_to_dict(result.extraction))

    with sub3:
        if not result.knowledge:
            st.info("No knowledge retrieved.")
        for item in result.knowledge:
            with st.container(border=True):
                st.markdown(f"**{item.topic}**")
                st.caption(f"{item.source} · v{item.version}")
                st.write(item.interpretation)
                if item.url:
                    st.link_button("Open reference", item.url)


def render_results(result: AnalysisResult | PatientAnalysisResult) -> None:
    render_metric_strip(result)
    render_export_bar(result)

    if isinstance(result, PatientAnalysisResult):
        render_multi_document_banner(result)

    tab_overview, tab_assessment, tab_evidence, tab_data = st.tabs(
        ["Summary", "Workflow flags", "Evidence table", "Raw data"]
    )
    with tab_overview:
        render_overview_tab(result)
    with tab_assessment:
        render_assessment_tab(result)
    with tab_evidence:
        render_evidence_tab(result)
    with tab_data:
        render_data_tab(result)


def render_footer() -> None:
    st.markdown(
        f'<div class="footer-note">{esc(POC_DISCLAIMER)}</div>',
        unsafe_allow_html=True,
    )
