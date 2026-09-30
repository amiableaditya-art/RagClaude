# QA Validation Report — HelixNova Pharma Quality & Regulatory RAG Assistant

**Date:** 2026-09-30
**Version tested:** `app.py` as committed in `33033cd`, plus a repeat of the security and deployment checks.
**Method:** Automated runs of `app.py` in Streamlit's test harness on Windows, Python 3.14. The sample data was generated TXT and PDF files, and the bundled `sample_policy.txt`. **The Claude client was replaced by a stand-in that records each request. No real Claude call has succeeded**, because the API key on the test machine is rejected (401). Installed package versions match `requirements.txt`.

**Result: 12 PASS, 1 PASS with limits, 2 BLOCKED (need a valid API key), 0 FAIL.**

| # | Test | Status | Evidence | Recommended fix |
|---|---|---|---|---|
| 1 | PDF upload | PASS | A generated PDF was accepted and its text was retrieved | None |
| 2 | TXT upload | PASS | TXT files, including `sample_policy.txt`, were accepted and indexed | None |
| 3 | Text extraction | PASS | 4,646 characters for a TXT plus PDF pair, and 2,900 for `sample_policy.txt`, shown in the UI | None |
| 4 | Chunking | PASS | 800-character chunks with a 100-character overlap, numbered from 1 per file (8 chunks for the pair, 4 for the sample) | None |
| 5 | Embedding generation | PASS | all-MiniLM-L6-v2 returned 384-dimension normalized vectors | None |
| 6 | FAISS storage | PASS | The index built and results mapped back to the correct filename and chunk | None |
| 7 | Retrieval accuracy | PASS with limits | The batch-release question ranked `batch.pdf` chunk 1 first (score 0.574, next best 0.169). The sample policy is only 4 chunks, so top-4 returns all of it and cannot test ranking | Test against a larger real document set |
| 8 | Claude grounding | BLOCKED | Each request held exactly 4 labelled chunks plus the question, never the whole document. Whether the real model obeys the rules is untested | Re-run with a valid key |
| 9 | Filename attribution | PASS | Sources show filenames in the list and the expander | None |
| 10 | Chunk number attribution | PASS | Sources show "chunk N" with the similarity score, for example `batch.pdf — chunk 1 — score 0.574` | None |
| 11 | Chat history | PASS | After 3 questions, all 6 messages stayed displayed, each answer with its sources | None |
| 12 | Session persistence | PASS | History, index, and dashboard figures live in `st.session_state` only, with no file or database | None |
| 13 | Fallback response | BLOCKED | The exact sentence shows with no sources when returned. The stand-in supplied it, so whether Claude returns it for an unrelated question is untested | Re-run with a valid key |
| 14 | No hardcoded secrets | PASS | Scan of all project files found no keys, passwords, or tokens (only the placeholder `"your-key"` in docs). `.env` and `secrets.toml` are in `.gitignore` and absent from the repository | None |
| 15 | Streamlit Cloud readiness | PASS (static checks) | `app.py` at the root, complete pinned `requirements.txt`, no local paths, and `st.secrets` tested (a key set only in secrets reached the Claude client). Not deployed | Deploy once and confirm |

## Advanced features

| Feature | Status | Evidence |
|---|---|---|
| Multiple documents | PASS | Two files indexed together, with per-file counts |
| Document filter | PASS | Selecting `batch.pdf` returned sources only from that file |
| Similarity scores and metadata | PASS | Each source shows filename, chunk number, and score |
| Dashboard | PASS | After 3 questions with 1 fallback: questions 3, fallbacks 1, average retrieval score 0.544 (the mean of the two answered questions' top scores) |
| Evaluation framework | PASS (mechanics only) | The bundled 11-question dataset ran with columns Question, Expected, Actual, Pass/Fail and logged each result. All 11 passed, but with the stand-in echoing its context and all 4 sample chunks retrieved each time, this checks the plumbing and scoring, not answer quality |
| Evaluation pass rule | Limit | A keyword-overlap check (60% of key terms). A correct answer with very different wording can be marked Fail |

## Security and repository checks

- No secrets in any file, and no `.env` or `secrets.toml` present.
- Repository initialized, working tree clean, and both commits pushed. The remote `main` matched the local `main` (`33033cd`) when checked.

## Live API attempt

A live run with the machine's `ANTHROPIC_API_KEY` returned 401 `invalid x-api-key` for every question. The app showed a readable error and kept running, as intended. Tests 8 and 13 stay BLOCKED, and the evaluation has not been run against the real model.

## Defects found and fixed during testing

- Non-ASCII characters in `app.py` were corrupted by a command-line edit. They were repaired before the first commit.
- The dashboard metrics lagged one interaction behind new questions and evaluation runs. The app now reruns after each.

## Risks to check

- **Model name:** `claude-3-5-sonnet-latest` may be retired. If the first real call fails with a model error, change the `CLAUDE_MODEL` constant at the top of `app.py`.
- **Slow first start:** importing `sentence-transformers` took about 90 seconds on the test machine, and the first Cloud start will be slow as well.
- **Pins on Cloud:** the pinned versions were tested on Python 3.14. If the Cloud build fails, set the app's Python version to 3.12 or 3.13.
- **Errors in chat history:** API error messages are stored as assistant messages in the history. This is cosmetic.
