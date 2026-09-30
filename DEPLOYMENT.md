# DEPLOYMENT.md — HelixNova Pharma Quality & Regulatory RAG Assistant

How to publish the project. For status, see `GitHub_Ready_Checklist.md` and `Streamlit_Cloud_Ready_Checklist.md`.

## 1. Push to GitHub

1. Create a GitHub personal access token with `repo` scope (classic), or Contents read/write for the repository (fine-grained).
2. In PowerShell, run `git push -u origin main`. Enter your GitHub username when asked, and paste the token as the password.
3. If the remote already holds commits (for example a README created by GitHub), the push is rejected. Pull and merge first. Do not force-push.

## 2. Deploy to Streamlit Community Cloud

1. Push the repository to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), choose **Create app** and select the repository, the `main` branch, and `app.py`.
3. In **Advanced settings**, open **Secrets** and add:
   ```
   ANTHROPIC_API_KEY = "your-key"
   ```
   Use `.streamlit/secrets.toml.example` as a template for local runs. Copy it to `.streamlit/secrets.toml`, which is git-ignored.
4. If the build fails installing packages, set the Python version to 3.12 or 3.13 here.
5. Deploy. The first start is slow, because the embedding model downloads and loads.
6. To let anyone open the app, set **Settings → Sharing** to public.
7. Upload `sample_policy.txt`, ask a question, and check that the answer shows sources.
8. Open **Evaluation testing** and run the bundled `evaluation_dataset.json` against `sample_policy.txt`.

## 3. Open Items

1. **Cloud results not captured.** Grounding and the exact fallback sentence are reported working on the deployed app, but the answers were not recorded. Record one answerable question with its sources, one unrelated question with its exact reply, and the evaluation table, then update `QA_Report.md`.
2. **Claude model name.** `CLAUDE_MODEL` in `app.py` is `claude-sonnet-5-5`. If questions ever fail with a model error, check the name against Anthropic's current model list.
3. **Pinned versions.** They were tested locally on Python 3.14. The Cloud build succeeded, but the Python version it used was not recorded.

## 4. Security Reminders

- Never commit `.env` or `.streamlit/secrets.toml`.
- Keep the API key only in the Cloud **Secrets** setting or in an environment variable.
- Use a dedicated key for this project so it can be rotated without affecting other work.
