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
| README with run and deploy instructions | Done, and updated for the filter, dashboard, and evaluation features |
| Working tree clean | Done |
| Code pushed to GitHub | Done; the `main` branch is on the remote |

### Push to GitHub (reference)

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
| PDF and TXT upload | Done in local tests. Not separately recorded on Cloud |
| Claude model name (`claude-sonnet-5-5`) | The owner reported the deployed app working; no model-error check was recorded |
| Deployed to Cloud | Done; the app is public and the owner reported it working |
| Cloud test results captured | **Pending.** Specific questions and answers were not recorded |

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

1. **Cloud results not captured.** Grounding and the exact fallback sentence are reported working on the deployed app, but the answers were not recorded. Record one answerable question with its sources, one unrelated question with its exact reply, and the evaluation table, then update `QA_validation_report.md`.
2. **Claude model name.** `CLAUDE_MODEL` in `app.py` is `claude-sonnet-5-5`. If questions ever fail with a model error, check the name against Anthropic's current model list.
3. **Pinned versions.** They were tested locally on Python 3.14. The Cloud build succeeded, but the Python version it used was not recorded.

## 4. Security Reminders

- Never commit `.env` or `.streamlit/secrets.toml`.
- Keep the API key only in the Cloud **Secrets** setting or in an environment variable.
- Use a dedicated key for this project so it can be rotated without affecting other work.
