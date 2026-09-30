# CLAUDE.md — HelixNova Pharma Quality & Regulatory RAG Assistant

A Streamlit RAG assistant. Users upload PDF/TXT policy documents and ask questions. Claude answers only from retrieved context and shows its evidence. See `requirements.md` for business requirements and `specification.md` for design.

**Stack:** Python, Streamlit, Anthropic Claude API, sentence-transformers, FAISS, pypdf.

## Development Principles

- Beginner friendly.
- Keep application logic simple.
- Keep most logic in `app.py`.
- Modularize only when useful.
- No over-engineering.

## Security Requirements

- Never hardcode secrets.
- Read `ANTHROPIC_API_KEY` from the environment.
- Support Streamlit Community Cloud secrets (`st.secrets["ANTHROPIC_API_KEY"]`).
- Keep `.env` and `secrets.toml` out of the repository via `.gitignore`.

## Retrieval Rules

- Always retrieve before generating.
- Claude must answer only using retrieved context.
- Never send whole documents to Claude, only the retrieved chunks and the question.
- Never use external knowledge.
- When evidence is missing, return exactly:

> I could not find enough information in the uploaded document.

Do not reword, extend, or add to this sentence.

## Document Rules

- Support PDF files.
- Support TXT files.
- Support multiple files.
- Preserve filename metadata.
- Preserve chunk metadata.

## User Experience

- Show retrieved chunks.
- Show chunk IDs.
- Show source filenames.
- Show similarity scores.
- Keep explanations simple.

## Deployment Rules

- Compatible with Streamlit Community Cloud.
- No local file dependencies.
- No database required.
- Chat history lives in Streamlit session state for the active session only.
- Keep `requirements.txt` complete, with pinned versions that install on the Cloud Python version.
