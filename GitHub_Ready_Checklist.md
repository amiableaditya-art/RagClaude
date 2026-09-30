# GitHub Ready Checklist — HelixNova Pharma Quality & Regulatory RAG Assistant

Repository: https://github.com/amiableaditya-art/RagClaude

## Repository setup

- [x] Git repository initialized, with `main` as the branch
- [x] Remote `origin` points to the GitHub repository
- [x] Commits made with a real author name and email
- [x] Commit messages are descriptive
- [x] Code pushed to GitHub (remote `main` matched local `main` when last checked)

## Secrets and safety

- [x] `.gitignore` excludes `.env` and `.streamlit/secrets.toml`
- [x] `.gitignore` excludes virtual environments, `__pycache__`, and caches
- [x] No API keys, passwords, or tokens in any file (all files scanned)
- [x] No `.env` or `secrets.toml` committed
- [x] `.streamlit/secrets.toml.example` holds a placeholder only, never a real key

## Project files

- [x] `README.md` with features, run steps, and deploy steps
- [x] `requirements.txt` with pinned dependencies
- [x] `requirements.md`, `specification.md`, and `CLAUDE.md`
- [x] `QA_Report.md`
- [x] `evaluation_dataset.json` and `sample_policy.txt`
- [x] Checklists: this file and `Streamlit_Cloud_Ready_Checklist.md`
- [x] `.gitattributes` keeps line endings consistent
- [ ] `LICENSE` file. Not added. Choose a license if the repository will be shared

## Final checks

- [ ] Working tree clean and pushed. Re-check with `git status -sb` after committing the newest files
- [ ] Repository page viewed in a browser to confirm the README renders. Not checked from the development environment

## Quick commands

```
git status -sb
git add -A
git commit -m "Describe the change"
git push
```

Run these in PowerShell. If the push asks for credentials, use your GitHub username and a personal access token as the password.
