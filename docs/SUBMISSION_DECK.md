# 5-Slide Submission Deck
Copy each slide into PowerPoint. One slide per section below. Export as PDF.

---

## SLIDE 1 — Problem Understanding and Objective

**Title:** Problem Understanding and Objective

**Bullets:**
- Mid-size healthcare providers manually review intake forms, discharge summaries, lab reports, and physician notes
- Process is **slow, inconsistent, and error-prone**
- Staff need structured data and actionable summaries — not raw document reading

**Objective:**
Build an AI proof-of-concept that:
1. Accepts clinical documents (TXT, PDF, image)
2. Extracts structured clinical entities with evidence
3. Generates patient summaries, risk flags, and recommended next steps
4. Supports multi-document merge for the same patient

**Footer:** Clinical Document Intelligence Hub · Synthetic demo data only

---

## SLIDE 2 — Solution Architecture and Design Flow

**Title:** Solution Architecture and Design Flow

**Diagram (paste as SmartArt or boxes):**

```
┌─────────────┐    ┌──────────┐    ┌─────────────┐    ┌────────────┐
│  Upload     │───▶│ Ingest   │───▶│ LLM Extract │───▶│ Confidence │
│ TXT/PDF/IMG │    │ PyMuPDF  │    │ Groq API    │    │ + Normalize│
└─────────────┘    │ Tesseract│    └─────────────┘    └─────┬──────┘
                   └──────────┘                              │
                                                             ▼
┌─────────────┐    ┌──────────┐    ┌─────────────┐    ┌────────────┐
│  Dashboard  │◀───│ Summary  │◀───│ Assessment  │◀───│ Knowledge  │
│  Streamlit  │    │ Generator│    │ Rule flags  │    │ Retrieval  │
└─────────────┘    └──────────┘    └─────────────┘    └────────────┘
                          ▲
                   ┌──────┴──────┐
                   │ Multi-doc   │
                   │ Merge       │
                   └─────────────┘
```

**Stack:** Python · Groq LLM · Pydantic · Streamlit · PyMuPDF · Tesseract

---

## SLIDE 3 — Implementation Highlights

**Title:** Implementation Highlights

**Key features:**
- **7-step pipeline** — ingest → extract → score → normalize → knowledge → assess → summarize
- **Schema-validated extraction** — Pydantic models with evidence quotes per field
- **Workflow flags** — transparent rules (e.g. HbA1c > 9%, BP > 140/90) in `assessment/`
- **Multi-document merge** — dedupe by canonical name, provenance tags, patient conflict guard
- **Evaluation** — live metrics vs `ground_truth.json` + Superinsight benchmark
- **JSON export** — full audit trail for downstream systems

**Screenshots to insert here:**
1. Dashboard overview (summary + metrics)
2. Workflow flags tab
3. Multi-document merge view

---

## SLIDE 4 — Challenges and Learnings

**Title:** Challenges and Learnings

| Challenge | Learning / Mitigation |
|-----------|----------------------|
| OCR noise on lab images | Documented limitation; plain-text demo is most reliable |
| Groq token limits on long docs | Evaluation uses curated excerpts; full docs for UI demo |
| LLM JSON validation failures | Retry logic in evaluation script |
| Medical terminology variance | `terminology_map.json` maps aliases → canonical names |
| POC vs production | Clear disclaimer — decision support, not diagnosis |

**Takeaway:** Hybrid approach works best — **LLM for extraction**, **deterministic rules for clinical flags**, **human review required**.

---

## SLIDE 5 — Demo Summary and Next Steps

**Title:** Demo Summary and Next Steps

**What we delivered:**
- Working Streamlit prototype with single + multi-document modes
- Synthetic demo dataset (Jane Doe diabetes case)
- Public benchmark validation (Superinsight, Apache 2.0)
- GitHub repo + README + evaluation scripts

**Links:**
- **GitHub:** https://github.com/ayush2888/Clinical-Document-Intelligence
- **Demo:** [INSERT YOUR STREAMLIT CLOUD LINK OR "See attached video"]
- **Video:** [INSERT IF USING SCREEN RECORDING]

**Future enhancements (if given more time):**
- FHIR / HL7 export
- Clinician review queue for low-confidence fields
- Production OCR (Azure Document Intelligence / AWS Textract)
- Role-based access and audit logging

**Thank you.**
