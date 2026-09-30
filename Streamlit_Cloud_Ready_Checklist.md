# Streamlit Community Cloud Ready Checklist — HelixNova Pharma Quality & Regulatory RAG Assistant

## Code and dependencies

- [x] `app.py` at the repository root is the entry point
- [x] `requirements.txt` lists every third-party import, with pinned versions: streamlit, anthropic, sentence-transformers, faiss-cpu, pypdf
- [x] FAISS (`faiss-cpu`) and sentence-transformers included
- [x] No local file paths. The bundled evaluation dataset is found relative to `app.py`
- [x] No database or local storage. All state lives in the session

## Secrets

- [x] API key read from the `ANTHROPIC_API_KEY` environment variable, then `st.secrets`
- [x] Tested locally with the key set only in secrets
- [x] No key in the repository
- [x] Key added in the Cloud app's **Secrets** setting

## Deployment

- [x] Repository pushed to GitHub
- [x] App created on share.streamlit.io with the `main` branch and `app.py`
- [x] App set to public, and the URL answered HTTP 200 from a fresh session
- [x] Owner reported the deployed app working
- [x] Claude model set to `claude-sonnet-5-5`

## Results still to capture

- [x] Answerable question, with its answer and sources, recorded in `QA_Report.md` (real model, local run)
- [x] Unrelated question, with its exact fallback reply, recorded in `QA_Report.md` (real model, local run)
- [x] Evaluation run recorded in `QA_Report.md`: 11 of 11 passed (real model, local run)
- [ ] The same three checks repeated on the deployed Cloud app. The results above are from a local run
- [ ] PDF upload confirmed on Cloud. Only tested locally
- [ ] Python version used by the Cloud build recorded

## If something fails

| Symptom | Likely fix |
|---|---|
| Build fails installing packages | In **Advanced settings**, set Python to 3.12 or 3.13 |
| "ANTHROPIC_API_KEY is not set" in the app | Add the key under **Settings → Secrets**, then reboot the app |
| Model error when asking a question | Check `CLAUDE_MODEL` in `app.py` against Anthropic's current model list |
| Very slow first load | Normal. The embedding model downloads and loads on first start |
| App shows a sign-in page | Set **Settings → Sharing** to public |

See `DEPLOYMENT.md` for the full steps.
