# Streamlit Cloud deploy (2 minutes)

## 1. Push latest code

```powershell
git push origin main
```

## 2. Create app

1. Open https://share.streamlit.io
2. Sign in with GitHub
3. **New app** → Repository: `ayush2888/Clinical-Document-Intelligence`
4. Branch: `main` · Main file: `app.py`
5. **Deploy**

## 3. Secrets (Settings → Secrets)

Paste **TOML** (not `.env` format):

```toml
GROQ_API_KEY = "your_groq_key_here"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-20b"
```

Save → **Reboot app**.

## 4. Demo file

Upload `data/demo/physician_note.txt` in the app sidebar.

## Notes

- Secrets are read via `config.py` (`st.secrets` on cloud, `.env` locally).
- Image OCR needs `packages.txt` (tesseract) on Cloud — TXT/PDF demos work without it.
- Never commit `.env` or paste keys in GitHub.
