# HelixNova Pharma Quality & Regulatory RAG Assistant

A Streamlit app for asking natural-language questions about pharmaceutical policy documents (deviations, CAPA, batch release, cold-chain, change control, recalls, and more). Answers come only from your uploaded PDF or TXT files, and every answer shows its sources.

## How it works

Upload → extract text → clean → chunk (800 chars, 100 overlap) → embed (`all-MiniLM-L6-v2`) → FAISS index → question → retrieve top 4 chunks → Claude answers from those chunks only → sources shown (filename and chunk number).

- Only the 4 retrieved chunks and your question are sent to Claude, never the whole document.
- If the documents don't contain the answer, the app replies exactly: *I could not find enough information in the uploaded document.*
- Chat history lasts only for the current browser session. Nothing is stored permanently.

## Run locally

```
pip install -r requirements.txt
```

Set your API key, then start the app.

PowerShell:
```
$env:ANTHROPIC_API_KEY = "your-key"
streamlit run app.py
```

macOS/Linux:
```
export ANTHROPIC_API_KEY="your-key"
streamlit run app.py
```

Alternatively, create `.streamlit/secrets.toml` (git-ignored) containing `ANTHROPIC_API_KEY = "your-key"`.

The first run downloads the embedding model, so it starts slowly.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub. Make sure no keys are committed.
2. On Streamlit Community Cloud, create a new app and point it to `app.py`.
3. Under **Settings → Secrets**, add: `ANTHROPIC_API_KEY = "your-key"`.

## Files

| File | Purpose |
|---|---|
| `app.py` | The application |
| `requirements.txt` | Pinned dependencies |
| `requirements.md` | Business requirements |
| `specification.md` | Architecture and workflow |
| `CLAUDE.md` | Development rules |

## Limitations

- Text-based documents only. Scanned PDFs are not supported, because there is no OCR.
- The assistant supports policy lookup and does not replace formal QA or regulatory judgment.
