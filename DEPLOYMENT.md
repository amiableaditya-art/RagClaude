# DEPLOYMENT.md — HelixNova Pharma Quality & Regulatory RAG Assistant

Checklists for the two deployment deliverables: a GitHub-ready repository and a Streamlit Community Cloud-ready solution. Status reflects the checks run on 2026-09-30.

## 1. GitHub-Ready Repository

| Check | Status |
|---|---|
| Git repository initialized (`main` branch) | Done |
| First commit made | Done (`1bb96c7`) |
| Remote `origin` set to `https://github.com/amiableaditya-art/RagClaude.git` | Done |
| `.gitignore` excludes `.env`, `.streamlit/secrets.toml`, virtual environments, and caches | Done |
| No API keys, passwords, or tokens in any file | Done (scanned) |
| No `.env` or `secrets.toml` in the repository | Done |
| README with run and deploy instructions | Done, but it predates the filter, dashboard, and evaluation features |
| Working tree clean | Done at the time of the first commit |
| Code pushed to GitHub | **Pending.** GitHub sign-in is required on this machine |

### Push to GitHub

1. Create a GitHub personal access token with `repo` scope (classic), or Contents read/write for the repository (fine-grained).
2. Run `git push -u origin main`. Enter your GitHub username when asked, and paste the token as the password.
3. If the remote already holds commits (for example a README created by GitHub), the push is rejected. Pull and merge first. Do not force-push.

## 2. Streamlit Community Cloud-Ready Solution

| Check | Status |
|---|---|
| `app.py` at the repository root (entry point) | Done |
| `requirements.txt` lists every third-party import, with pinned versions | Done: streamlit, anthropic, sentence-transformers, faiss-cpu, pypdf |
| FAISS and sentence-transformers included | Done |
| API key read from `ANTHROPIC_API_KEY`, then `st.secrets` | Done; tested with the key set only in secrets |
| No local file paths | Done; the bundled evaluation dataset is located relative to `app.py` |
| No database or local storage | Done; all state lives in the session |
| PDF and TXT upload | Done in local tests; not yet run on Cloud |
| Claude model name confirmed working | **Not confirmed.** See below |
| Deployed and tested on Cloud | **Pending** |

### Deploy to Streamlit Community Cloud

1. Push the repository to GitHub (section 1).
2. On [share.streamlit.io](https://share.streamlit.io), choose **Create app** and select the repository, the `main` branch, and `app.py`.
3. In **Advanced settings**, open **Secrets** and add:
   ```
   ANTHROPIC_API_KEY = "your-key"
   ```
4. Deploy. The first start is slow, because the embedding model downloads and loads.
5. Upload `sample_policy.txt`, ask a question, and check that the answer shows sources.
6. Open **Evaluation testing** and run the bundled `evaluation_dataset.json` against `sample_policy.txt`.

## 3. Open Issues Before Release

1. **Claude model name.** `CLAUDE_MODEL` in `app.py` is `claude-3-5-sonnet-latest`. That model may be retired, and it could not be tested because the key on the development machine was rejected. If questions fail with a model error, change the constant to a current model such as `claude-sonnet-5-5`.
2. **Real-model behavior untested.** Grounding and the exact fallback sentence have only been checked against a stand-in for Claude. Ask one answerable and one unrelated question with a valid key.
3. **Pinned versions.** They are the versions tested on Python 3.14. If the Cloud build fails to install them, set the app's Python version to 3.12 or 3.13 under **Advanced settings**.
4. **Documentation drift.** `README.md` and `QA_validation_report.md` describe the earlier version of the app and need updating.

## 4. Security Reminders

- Never commit `.env` or `.streamlit/secrets.toml`.
- Keep the API key only in the Cloud **Secrets** setting or in an environment variable.
- Use a dedicated key for this project so it can be rotated without affecting other work.
