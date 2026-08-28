# Superinsight Medical Chronology Benchmark

Files in this folder are sourced from the public benchmark:

- **Dataset:** [Superinsight/medical-chronology-benchmark](https://huggingface.co/datasets/Superinsight/medical-chronology-benchmark)
- **License:** Apache 2.0
- **Content:** Synthetic clinical documents — not real PHI

## Files

| File | Source | Style |
|------|--------|-------|
| `golden_a_dde.txt` | `golden/golden_a/synthetic_source.txt` | Disability Determination (DDE) |
| `golden_a_golden.json` | `golden/golden_a/golden.json` | Reference annotations |
| `golden_b_clinical_note.txt` | `golden/golden_b/synthetic_source.txt` | Clinical psychotherapy notes |
| `golden_b_golden.json` | `golden/golden_b/golden.json` | Reference annotations |
| `golden_a_eval.txt` | Excerpt of golden_a | Used by `evaluate_extraction.py` (Groq token limit) |
| `golden_b_eval.txt` | Excerpt of golden_b | Used by `evaluate_extraction.py` (Groq token limit) |

Re-download with:

```powershell
python scripts/download_superinsight.py
```

Ground-truth mappings for our extractor live in `../ground_truth.json` (cases prefixed `superinsight_`).
