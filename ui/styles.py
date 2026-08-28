"""Shared CSS — healthcare SaaS aesthetic (Fleming / ClinIQ inspired)."""


def inject_styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

          :root {
            --navy: #0a1628;
            --navy-mid: #132337;
            --navy-light: #1e3a5f;
            --teal: #0d9488;
            --teal-light: #14b8a6;
            --sky: #0ea5e9;
            --bg: #eef1f6;
            --surface: #ffffff;
            --border: #dde3ed;
            --text: #0f172a;
            --muted: #64748b;
            --critical: #dc2626;
            --warn: #d97706;
            --success: #059669;
          }

          html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
          }

          .stApp {
            background: var(--bg);
          }

          .main .block-container {
            padding-top: 0.5rem;
            padding-bottom: 3rem;
            max-width: 1320px;
          }

          #MainMenu, footer, header[data-testid="stHeader"] {
            visibility: hidden;
            height: 0;
          }

          /* ── Top navigation bar ── */
          .top-nav {
            background: var(--navy);
            border-radius: 0 0 16px 16px;
            padding: 0.85rem 1.75rem;
            margin: -1rem -1rem 1.5rem -1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 24px rgba(10, 22, 40, 0.25);
          }
          .nav-brand {
            display: flex;
            align-items: center;
            gap: 0.65rem;
          }
          .nav-logo {
            width: 34px;
            height: 34px;
            background: linear-gradient(135deg, var(--teal) 0%, var(--sky) 100%);
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
          }
          .nav-title {
            color: white;
            font-weight: 700;
            font-size: 1.05rem;
            letter-spacing: -0.02em;
          }
          .nav-sub {
            color: rgba(255,255,255,0.55);
            font-size: 0.72rem;
            font-weight: 500;
          }
          .nav-badge {
            background: rgba(20, 184, 166, 0.15);
            border: 1px solid rgba(20, 184, 166, 0.35);
            color: #5eead4;
            padding: 0.3rem 0.85rem;
            border-radius: 999px;
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
          }

          /* ── Trust strip ── */
          .trust-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-bottom: 1.25rem;
          }
          .trust-pill {
            background: white;
            border: 1px solid var(--border);
            padding: 0.4rem 0.85rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 500;
            color: var(--muted);
          }
          .trust-pill strong { color: var(--text); font-weight: 600; }

          /* ── Hero ── */
          .hero-grid {
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 1.25rem;
            margin-bottom: 1.25rem;
          }
          @media (max-width: 900px) {
            .hero-grid { grid-template-columns: 1fr; }
          }
          .hero-main {
            background: linear-gradient(145deg, var(--navy) 0%, var(--navy-light) 100%);
            border-radius: 20px;
            padding: 2rem 2.25rem;
            color: white;
            position: relative;
            overflow: hidden;
          }
          .hero-main::before {
            content: "";
            position: absolute;
            width: 320px; height: 320px;
            top: -120px; right: -80px;
            background: radial-gradient(circle, rgba(20,184,166,0.18) 0%, transparent 70%);
            border-radius: 50%;
          }
          .hero-eyebrow {
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #5eead4;
            margin-bottom: 0.65rem;
          }
          .hero-main h1 {
            color: white !important;
            font-size: 1.85rem !important;
            font-weight: 700 !important;
            line-height: 1.25 !important;
            margin: 0 0 0.75rem 0 !important;
            letter-spacing: -0.03em;
          }
          .hero-main p {
            color: rgba(255,255,255,0.78);
            font-size: 0.98rem;
            line-height: 1.65;
            margin: 0;
            max-width: 480px;
          }

          /* ── Live preview panel (Fleming-style) ── */
          .live-panel {
            background: var(--navy-mid);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 1.25rem;
            font-family: 'JetBrains Mono', monospace;
          }
          .live-panel-header {
            color: rgba(255,255,255,0.45);
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
          }
          .code-block {
            background: rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.65rem;
          }
          .code-label {
            color: #5eead4;
            font-size: 0.68rem;
            margin-bottom: 0.35rem;
          }
          .code-content {
            color: rgba(255,255,255,0.85);
            font-size: 0.75rem;
            line-height: 1.55;
          }
          .code-key { color: #7dd3fc; }
          .code-str { color: #86efac; }
          .code-num { color: #fcd34d; }

          /* ── Disclaimer ── */
          .disclaimer {
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-left: 4px solid #f59e0b;
            padding: 0.75rem 1.1rem;
            border-radius: 10px;
            color: #92400e;
            font-size: 0.85rem;
            margin-bottom: 1.25rem;
          }

          /* ── Metric cards (ClinIQ stats style) ── */
          .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.75rem;
            margin-bottom: 1.25rem;
          }
          @media (max-width: 900px) { .stat-grid { grid-template-columns: repeat(2, 1fr); } }
          .stat-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 1px 3px rgba(15,23,42,0.04);
          }
          .stat-card.highlight {
            background: linear-gradient(135deg, #f0fdfa 0%, #ffffff 100%);
            border-color: #99f6e4;
          }
          .stat-label {
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: var(--muted);
            margin-bottom: 0.4rem;
          }
          .stat-value {
            font-size: 1.65rem;
            font-weight: 700;
            color: var(--text);
            letter-spacing: -0.03em;
            line-height: 1.1;
          }
          .stat-sub {
            font-size: 0.75rem;
            color: var(--muted);
            margin-top: 0.25rem;
          }

          /* ── Live output header ── */
          .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
          }
          .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text);
            letter-spacing: -0.02em;
          }
          .live-dot {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--success);
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }
          .live-dot::before {
            content: "";
            width: 7px; height: 7px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
          }
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
          }

          /* ── Entity cards (Fleming biomarker style) ── */
          .entity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 0.65rem;
            margin: 1rem 0;
          }
          .entity-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.85rem 1rem;
            transition: box-shadow 0.15s;
          }
          .entity-card:hover {
            box-shadow: 0 4px 12px rgba(15,23,42,0.08);
          }
          .entity-tag {
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--teal);
            margin-bottom: 0.3rem;
          }
          .entity-name {
            font-size: 0.88rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 0.2rem;
          }
          .entity-value {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--navy-light);
            letter-spacing: -0.02em;
          }
          .entity-meta {
            font-size: 0.72rem;
            color: var(--muted);
            margin-top: 0.35rem;
          }

          /* ── Citation cards (ClinIQ style) ── */
          .citation-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.1rem 1.25rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid var(--sky);
          }
          .citation-card.alert {
            border-left-color: var(--critical);
            background: #fef2f2;
          }
          .citation-card.finding {
            border-left-color: var(--teal);
          }
          .citation-title {
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--text);
            margin-bottom: 0.4rem;
          }
          .citation-body {
            font-size: 0.88rem;
            color: #475569;
            line-height: 1.55;
          }
          .citation-source {
            margin-top: 0.55rem;
            font-size: 0.75rem;
            color: var(--muted);
            font-style: italic;
          }
          .citation-source strong { color: var(--teal); font-style: normal; }

          /* ── Summary panel ── */
          .summary-panel {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem 1.65rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(15,23,42,0.04);
          }
          .summary-eyebrow {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--teal);
            margin-bottom: 0.5rem;
          }
          .summary-body {
            font-size: 1.02rem;
            line-height: 1.75;
            color: var(--text);
          }

          .next-step-box {
            background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
            border: 1px solid #a7f3d0;
            border-radius: 14px;
            padding: 1.1rem 1.25rem;
            color: #065f46;
            font-size: 0.95rem;
            line-height: 1.6;
          }

          /* ── Pills ── */
          .pill {
            display: inline-block;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.04em;
          }
          .pill-critical { background: #fecaca; color: #991b1b; }
          .pill-high { background: #fee2e2; color: #b91c1c; }
          .pill-medium { background: #fef3c7; color: #b45309; }
          .pill-low { background: #dcfce7; color: #15803d; }

          .doc-chip {
            display: inline-block;
            background: #f1f5f9;
            border: 1px solid var(--border);
            padding: 0.3rem 0.7rem;
            border-radius: 8px;
            font-size: 0.78rem;
            margin: 0.2rem 0.3rem 0.2rem 0;
            color: #334155;
            font-family: 'JetBrains Mono', monospace;
          }

          /* ── Empty state pipeline ── */
          .pipeline-flow {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin: 1rem 0;
          }
          .pipe-step {
            background: white;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.55rem 0.85rem;
            font-size: 0.78rem;
            font-weight: 500;
            color: var(--text);
          }
          .pipe-arrow { color: var(--muted); font-size: 0.85rem; }

          .feature-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.85rem;
          }
          @media (max-width: 900px) { .feature-grid { grid-template-columns: 1fr; } }
          .feature-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.35rem;
          }
          .feature-icon {
            width: 40px; height: 40px;
            background: linear-gradient(135deg, #f0fdfa, #ecfeff);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
          }
          .feature-title {
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--text);
            margin-bottom: 0.35rem;
          }
          .feature-desc {
            font-size: 0.82rem;
            color: var(--muted);
            line-height: 1.5;
          }

          /* ── Sidebar (light — readable Streamlit widgets) ── */
          div[data-testid="stSidebar"] {
            background: #f8fafc !important;
            border-right: 1px solid var(--border) !important;
          }
          /* Brand header strip only */
          div[data-testid="stSidebar"] .sidebar-brand-block {
            background: linear-gradient(180deg, var(--navy) 0%, var(--navy-mid) 100%);
            padding: 1.1rem 1rem;
            border-radius: 12px;
            margin-bottom: 0.75rem;
          }
          div[data-testid="stSidebar"] .sidebar-brand-block .sidebar-logo-text {
            color: #ffffff !important;
          }
          div[data-testid="stSidebar"] .sidebar-brand-block .sidebar-tagline {
            color: rgba(255,255,255,0.78) !important;
          }
          /* All normal sidebar content — dark readable text */
          div[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
          div[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
          div[data-testid="stSidebar"] label,
          div[data-testid="stSidebar"] .stRadio label,
          div[data-testid="stSidebar"] .stRadio label span,
          div[data-testid="stSidebar"] .stRadio label p,
          div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label,
          div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span,
          div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p,
          div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div {
            color: #1e293b !important;
            font-weight: 500 !important;
          }
          div[data-testid="stSidebar"] .stFileUploader label {
            color: #475569 !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
          }
          div[data-testid="stSidebar"] .stCaption,
          div[data-testid="stSidebar"] small {
            color: #64748b !important;
          }
          div[data-testid="stSidebar"] hr {
            border-color: var(--border) !important;
            margin: 1rem 0 !important;
          }
          /* File uploader — force dark text on light dropzone */
          div[data-testid="stSidebar"] [data-testid="stFileUploader"],
          div[data-testid="stSidebar"] [data-testid="stFileUploader"] label,
          div[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
          div[data-testid="stSidebar"] [data-testid="stFileUploader"] p,
          div[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
          div[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"] {
            color: #334155 !important;
          }
          div[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"] {
            background: #ffffff !important;
            border: 2px dashed #cbd5e1 !important;
            border-radius: 12px !important;
          }
          div[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"]:hover {
            border-color: var(--teal) !important;
            background: #f0fdfa !important;
          }
          /* Text inputs */
          div[data-testid="stSidebar"] input {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #0f172a !important;
            border-radius: 8px !important;
          }
          div[data-testid="stSidebar"] input::placeholder {
            color: #94a3b8 !important;
          }
          /* Expanders */
          div[data-testid="stSidebar"] .stExpander {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
          }
          div[data-testid="stSidebar"] .stExpander summary,
          div[data-testid="stSidebar"] .stExpander summary span {
            color: #1e293b !important;
            font-weight: 600 !important;
          }
          div[data-testid="stSidebar"] .stExpander [data-testid="stMarkdownContainer"] p {
            color: #475569 !important;
          }
          /* Code block in expander */
          div[data-testid="stSidebar"] pre {
            background: #f1f5f9 !important;
            color: #0f172a !important;
          }
          /* Buttons */
          div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--teal) 0%, #0284c7 100%) !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
          }
          div[data-testid="stSidebar"] .stButton > button[kind="primary"]:disabled {
            background: #cbd5e1 !important;
            color: #64748b !important;
          }
          div[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #334155 !important;
            border-radius: 10px !important;
          }
          /* Success messages */
          div[data-testid="stSidebar"] [data-testid="stAlert"] {
            background: #ecfdf5 !important;
            color: #065f46 !important;
          }

          .sidebar-brand-block {
            margin-bottom: 0;
          }
          .sidebar-logo-text {
            font-size: 1.2rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.02em;
            margin-bottom: 0.15rem;
          }
          .sidebar-tagline {
            font-size: 0.78rem;
            color: rgba(255,255,255,0.75);
            margin-bottom: 0;
          }
          .sidebar-section {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            color: #64748b !important;
            margin: 0.85rem 0 0.45rem 0;
          }

          /* ── Tabs ── */
          .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.35rem;
          }
          .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            color: var(--muted);
          }
          .stTabs [aria-selected="true"] {
            background: var(--navy) !important;
            color: white !important;
          }

          .footer-note {
            color: var(--muted);
            font-size: 0.8rem;
            line-height: 1.55;
            padding-top: 1.25rem;
            border-top: 1px solid var(--border);
            margin-top: 2rem;
          }

          .card-shell {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.25rem;
            margin-bottom: 0.75rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
