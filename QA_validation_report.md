# QA Validation Report — HelixNova Pharma Quality & Regulatory RAG Assistant

**Date:** 2026-09-30
**Method:** Automated run of `app.py` in Streamlit's test harness (`streamlit.testing`) on Windows, Python 3.14. The sample data was a generated TXT policy (4,588 characters) and a generated one-page PDF. The Claude client was replaced by a stand-in that records each request. Installed package versions were newer than the pins in `requirements.txt`.
**Result: 13 PASS, 2 BLOCKED (need a valid API key), 0 FAIL.** No defects were found, so no code was changed.

| # | Test | Status | Evidence | Recommended fix |
|---|---|---|---|---|
| 1 | PDF upload | PASS | `batch.pdf` accepted and indexed; its text was retrieved as `batch.pdf` chunk 1 | None |
| 2 | TXT upload | PASS | `dev.txt` accepted and indexed | None |
| 3 | Text extraction | PASS | UI showed 4,646 extracted characters for both files; no "no text" warnings | None |
| 4 | Chunking | PASS | 8 chunks (800 chars, 100 overlap), numbered from 1 per file | None |
| 5 | Embedding generation | PASS | all-MiniLM-L6-v2 loaded and returned 384-dimension normalized vectors | None |
| 6 | FAISS storage | PASS | Index built with 8 vectors; search results mapped back to the correct chunk metadata | None |
| 7 | Retrieval accuracy | PASS | Deviation question returned `dev.txt` chunks. "Who signs batch release?" returned `batch.pdf` chunk 1 in the top 4 | None |
| 8 | Claude grounding | BLOCKED | Request structure verified: the system prompt carries the grounding rules and the user message holds only 4 labelled chunks plus the question (about 2.6–3.4 KB against about 4.6 KB indexed; the full document is never sent). Whether the real model obeys the rules is untested. The live run failed with 401 `invalid x-api-key` | Re-run with a valid key |
| 9 | Filename attribution | PASS | "Sources Used" list and chunk-text expander both show filenames | None |
| 10 | Chunk number attribution | PASS | Every source line shows "chunk N" | None |
| 11 | Chat history | PASS | After 3 questions, all 6 messages were kept in session state and displayed | None |
| 12 | Session persistence | PASS | History is held in `st.session_state` only, with no file or database. It stays visible across reruns and each new browser session starts empty (by design of session state) | None |
| 13 | Fallback response | BLOCKED | Display logic verified: the exact sentence is shown with no sources. The stand-in supplied that sentence, so whether Claude produces it for an unrelated question is untested | Re-run with a valid key |
| 14 | No hardcoded secrets | PASS | Searches for `sk-ant` and literal `api_key = "…"` found nothing. The key is read from `os.getenv`, then `st.secrets`. `.env` and `secrets.toml` are in `.gitignore` | None |
| 15 | Streamlit Cloud readiness | PASS (static checks only) | Entry point is `app.py`, with no local paths and all five packages in `requirements.txt`. Each pinned version exists on PyPI. The app was not deployed | Deploy once and confirm |

## Live API attempt

A live run with the machine's `ANTHROPIC_API_KEY` returned 401 `invalid x-api-key` for every question. The app showed a readable error and kept running, which is the intended behavior. Tests 8 and 13 stay BLOCKED until the key is replaced.

## Risks to check

- **Model name:** `claude-3-5-sonnet-latest` may be retired. If the first real call fails with a model error, change the `CLAUDE_MODEL` constant at the top of `app.py`.
- **Slow first start:** importing `sentence-transformers` took about 90 seconds on this machine, and the first Cloud start will be slow as well.
- **Pins not exercised:** tests ran on newer package versions than the ones pinned.
- **Errors in chat history:** API error messages are stored as assistant messages in the history. This is cosmetic and was not treated as a defect.
