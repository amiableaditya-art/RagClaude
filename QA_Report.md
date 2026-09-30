# QA Validation Report — HelixNova Pharma Quality & Regulatory RAG Assistant

**Date:** 2026-09-30
**Version tested:** `app.py` as committed in `33033cd`, plus a repeat of the security and deployment checks.
**Method:** Automated runs of `app.py` in Streamlit's test harness on Windows, Python 3.14. The sample data was generated TXT and PDF files, and the bundled `sample_policy.txt`. Most tests replaced the Claude client with a stand-in that records each request. A later round (see "Real-model test run") used a valid API key and the real model `claude-sonnet-5-5`, driving the app locally through the same test harness. Installed package versions match `requirements.txt`.

**Result: 14 PASS, 1 PASS with limits, 0 FAIL.**

**Deployment update:** the app was deployed to Streamlit Community Cloud and set to public, and the project owner reported it working. The QA engineer did not run questions against the deployed app, because its interface cannot be driven from the test environment. The real-model results below come from a local run of the same `app.py`.

| # | Test | Status | Evidence | Recommended fix |
|---|---|---|---|---|
| 1 | PDF upload | PASS | A generated PDF was accepted and its text was retrieved | None |
| 2 | TXT upload | PASS | TXT files, including `sample_policy.txt`, were accepted and indexed | None |
| 3 | Text extraction | PASS | 4,646 characters for a TXT plus PDF pair, and 2,900 for `sample_policy.txt`, shown in the UI | None |
| 4 | Chunking | PASS | 800-character chunks with a 100-character overlap, numbered from 1 per file (8 chunks for the pair, 4 for the sample) | None |
| 5 | Embedding generation | PASS | all-MiniLM-L6-v2 returned 384-dimension normalized vectors | None |
| 6 | FAISS storage | PASS | The index built and results mapped back to the correct filename and chunk | None |
| 7 | Retrieval accuracy | PASS with limits | The batch-release question ranked `batch.pdf` chunk 1 first (score 0.574, next best 0.169). The sample policy is only 4 chunks, so top-4 returns all of it and cannot test ranking | Test against a larger real document set |
| 8 | Claude grounding | PASS | Each request held exactly 4 labelled chunks plus the question, never the whole document (checked against the stand-in). With the real model, "How quickly must a critical deviation be reported to QA?" returned "A critical deviation must be reported to Quality Assurance within 24 hours of discovery.", matching the source text, with sources shown | None |
| 9 | Filename attribution | PASS | Sources show filenames in the list and the expander | None |
| 10 | Chunk number attribution | PASS | Sources show "chunk N" with the similarity score, for example `batch.pdf — chunk 1 — score 0.574` | None |
| 11 | Chat history | PASS | After 3 questions, all 6 messages stayed displayed, each answer with its sources | None |
| 12 | Session persistence | PASS | History, index, and dashboard figures live in `st.session_state` only, with no file or database | None |
| 13 | Fallback response | PASS | With the real model, "What is on the cafeteria menu today?" returned exactly "I could not find enough information in the uploaded document." with no sources | None |
| 14 | No hardcoded secrets | PASS | Scan of all project files found no keys, passwords, or tokens (only the placeholder `"your-key"` in docs). `.env` and `secrets.toml` are in `.gitignore` and absent from the repository | None |
| 15 | Streamlit Cloud readiness | PASS | `app.py` at the root, complete pinned `requirements.txt`, no local paths, and `st.secrets` tested locally (a key set only in secrets reached the Claude client). Deployed to Streamlit Community Cloud and reported working by the owner. The public URL answered HTTP 200 from a fresh session | None |

## Advanced features

| Feature | Status | Evidence |
|---|---|---|
| Multiple documents | PASS | Two files indexed together, with per-file counts |
| Document filter | PASS | Selecting `batch.pdf` returned sources only from that file |
| Similarity scores and metadata | PASS | Each source shows filename, chunk number, and score |
| Dashboard | PASS | After 3 questions with 1 fallback: questions 3, fallbacks 1, average retrieval score 0.544 (the mean of the two answered questions' top scores) |
| Evaluation framework | PASS | The bundled 11-question dataset ran with columns Question, Expected, Actual, Pass/Fail and logged each result. Against the stand-in it passed 11/11 (mechanics only). Against the real model it also passed 11/11 (100%); see "Real-model test run" |
| Evaluation pass rule | Limit | A keyword-overlap check (60% of key terms). A correct answer with very different wording can be marked Fail |

## Security and repository checks

- No secrets in any file, and no `.env` or `secrets.toml` present.
- Repository initialized, working tree clean, and both commits pushed. The remote `main` matched the local `main` (`33033cd`) when checked.

## Real-model test run

**Setup:** `app.py` run locally in the test harness with `sample_policy.txt` uploaded (2,900 characters, 4 chunks), a valid API key, and model `claude-sonnet-5-5`. An earlier attempt with a different key returned 401 `invalid x-api-key`. The app showed a readable error and kept running, as intended.

| Step | Result |
|---|---|
| Answerable question | Correct, grounded answer (24 hours). Sources listed: chunk 4 (0.543), chunk 1 (0.517), chunk 2 (0.500), chunk 3 (0.384) |
| Unrelated question | Exact fallback sentence, no sources |
| Dashboard after the two questions | Questions asked 2, fallback responses 1, average retrieval score 0.543 |
| Evaluation (11 cases) | 11 Pass, accuracy 100% |

The evaluation answers matched the expected content, for example CAPA approval within 10 business days with an effectiveness check at 90 days, Class I recall within 24 hours, training records kept 5 years, and critical suppliers audited every 2 years. The cafeteria case returned the exact fallback.

**Observations (not failures):**
- **Ranking:** for the deviation question, chunk 4 scored higher than chunk 1, which holds the answer. The sample is only 4 chunks, so all four are retrieved and the answer was still found. Ranking quality needs a larger document set.
- **Sources list:** "Sources Used" shows every retrieved chunk, not only the ones the answer drew on.
- **Not run on Cloud:** these results are from the local app, not the deployed one.

## Defects found and fixed during testing

- Non-ASCII characters in `app.py` were corrupted by a command-line edit. They were repaired before the first commit.
- The dashboard metrics lagged one interaction behind new questions and evaluation runs. The app now reruns after each.

## Risks to check

- **Model name:** `app.py` now uses `claude-sonnet-5-5` (changed from `claude-3-5-sonnet-latest`). A direct test call and the real-model run above both succeeded with this model name.
- **Slow first start:** importing `sentence-transformers` took about 90 seconds on the test machine, and the first Cloud start is slow as well.
- **Pins on Cloud:** the pinned versions were tested locally on Python 3.14. The Cloud build succeeded, but the Python version it used was not recorded.
- **Errors in chat history:** API error messages are stored as assistant messages in the history. This is cosmetic.
