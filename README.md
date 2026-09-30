# HelixNova Pharma Quality & Regulatory RAG Assistant

A Streamlit app for asking natural-language questions about pharmaceutical policy documents (deviations, CAPA, batch release, cold-chain, change control, recalls, and more). Answers come only from your uploaded PDF or TXT files, and every answer shows its sources.

## Features

- **Multiple documents:** upload several PDF and TXT files at once. The app shows the number of files, total characters, and total chunks, with per-file figures.
- **Grounded answers:** only the top 4 retrieved chunks and your question are sent to Claude, never whole documents.
- **Sources with scores:** each answer lists filename, chunk number, and similarity score. An expander shows the retrieved chunk text.
- **Fallback:** if the documents don't contain the answer, the app replies exactly: *I could not find enough information in the uploaded document.*
- **File filter:** limit retrieval to selected files from the sidebar.
- **Dashboard:** documents uploaded, chunks created, average retrieval score, questions asked, fallback count, and last evaluation accuracy.
- **Evaluation testing:** run test questions and see Question, Expected, Actual, and Pass/Fail.
- **Session only:** chat history, the index, and dashboard figures last for the current browser session and are not stored permanently.

## How it works

Upload → extract text → clean → chunk (800 characters, 100 overlap) → embed (`all-MiniLM-L6-v2`) → FAISS index → question → similarity search → document filter → top 4 chunks → Claude answers from those chunks only → sources shown.

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

The first run downloads the embedding model and imports are slow, so the first start takes a while.

## Try it

1. Upload `sample_policy.txt`. It is a fictional policy summary written for testing.
2. Ask, for example: *How quickly must a critical deviation be reported to QA?*
3. Open **Evaluation testing** and click **Run evaluation** to run the 11 questions in `evaluation_dataset.json`.

### Evaluation dataset

`evaluation_dataset.json` is a list of objects with `question` and `expected_answer`. A test passes when the answer contains at least 60% of the key terms (words longer than 3 letters, and all numbers) in the expected answer. A test that expects the fallback sentence passes only when the exact fallback is returned. You can upload your own JSON file in the same format. Results are also logged to the console.

## Configuration

Settings are constants at the top of `app.py`: `CLAUDE_MODEL`, `EMBEDDING_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`, and `PASS_THRESHOLD`.

## Deploy to Streamlit Community Cloud

See `DEPLOYMENT.md` for the full steps and `Streamlit_Cloud_Ready_Checklist.md` for status. In short:

1. Push this repository to GitHub. Make sure no keys are committed.
2. On Streamlit Community Cloud, create a new app that points to `app.py`.
3. Under **Advanced settings → Secrets**, add: `ANTHROPIC_API_KEY = "your-key"`.
4. If the build fails to install the pinned packages, set the app's Python version to 3.12 or 3.13.

## Files

| File | Purpose |
|---|---|
| `app.py` | The application |
| `requirements.txt` | Pinned dependencies |
| `evaluation_dataset.json` | Evaluation questions and expected answers |
| `sample_policy.txt` | Fictional sample policy for testing |
| `requirements.md` | Business requirements |
| `specification.md` | Architecture and workflow |
| `CLAUDE.md` | Development rules |
| `QA_Report.md` | QA results |
| `GitHub_Ready_Checklist.md` | Repository readiness checklist |
| `Streamlit_Cloud_Ready_Checklist.md` | Cloud deployment readiness checklist |
| `DEPLOYMENT.md` | Push and deploy steps |
| `.streamlit/secrets.toml.example` | Template for local secrets (no real key) |

## Limitations

- Text-based documents only. Scanned PDFs are not supported, because there is no OCR.
- Each question is answered on its own. Earlier chat turns are not sent to Claude.
- The evaluation's pass rule is a simple keyword check, so a correct answer worded very differently can be marked Fail.
- The assistant supports policy lookup and does not replace formal QA or regulatory judgment.
