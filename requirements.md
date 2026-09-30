# requirements.md — HelixNova Pharma Quality & Regulatory RAG Assistant

## 1. Business Problem

HelixNova Pharma employees regularly search lengthy SOPs and policy documents by hand. This is slow and can lead to inconsistent compliance decisions. The documents cover:

- Deviations
- CAPA
- Batch Release
- Cold-chain excursions
- Change Control
- Complaints
- Recalls
- Audit Trails
- Data Integrity
- Training Records
- Supplier Quality
- Escalation Timelines

**Goal:** a Retrieval-Augmented Generation (RAG) application where users upload policy documents and ask natural language questions. They get answers grounded in those documents, with source evidence.

## 2. Scope

**In scope:** document upload, indexing, question answering with evidence, session chat history, fallback handling, retrieval transparency, and RAG quality evaluation.

**Out of scope:** user authentication, storage that persists across sessions, document editing, OCR for scanned files, multi-language support, and integration with QMS or ERP systems.

## 3. Users

| User | Need |
|---|---|
| Quality Assurance staff | Confirm procedures for deviations, CAPA, and batch release |
| Regulatory Affairs staff | Verify escalation timelines and recall requirements |
| Manufacturing and Supply Chain staff | Check cold-chain, supplier, and change-control rules |
| Auditors and Trainers | Trace every answer back to the source policy text |
| Project owner | Measure how well the assistant answers |

## 4. Mandatory Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Upload PDF and TXT documents. Reject other file types with a clear message. |
| FR-02 | Extract document text. Warn when a file has no extractable text, such as a scanned PDF. |
| FR-03 | Chunk the text. Each chunk keeps its source filename and chunk number. |
| FR-04 | Generate embeddings using sentence-transformers. |
| FR-05 | Store vectors in FAISS. |
| FR-06 | Retrieve the top matching chunks for each question. |
| FR-07 | Send only the retrieved context to Claude, never the full documents. |
| FR-08 | Return grounded answers that use only the retrieved context, with no outside knowledge or guessing. |
| FR-09 | Display the source filename and chunk numbers with every answer. |
| FR-10 | Maintain chat history during the current Streamlit session. |
| FR-11 | When the answer cannot be found, return exactly: "I could not find enough information in the uploaded document." |

## 5. Advanced Requirements

| ID | Requirement |
|---|---|
| AR-01 | **Multiple documents.** Users can upload and query several documents at once. |
| AR-02 | **Document-level filtering.** Users can limit retrieval to one or more selected uploaded documents. |
| AR-03 | **Similarity scores.** Each retrieved chunk is shown with its similarity score. |
| AR-04 | **Retrieval metadata.** Each retrieved chunk is shown with its filename, chunk number, and rank, along with the chunk text. |
| AR-05 | **RAG quality dashboard.** A simple view of session quality: questions asked, how many answers were grounded and how many returned the fallback, average similarity of retrieved chunks, and results from the last evaluation run. |
| AR-06 | **Evaluation dataset testing.** Users can run a set of test questions with expected answers or expected source documents through the pipeline. The app reports each result as pass or fail and shows overall accuracy. |
| AR-07 | **Streamlit Community Cloud deployment.** The app runs there with the API key supplied through secrets. |

## 6. Non-Functional Requirements

- **Grounding and accuracy:** answers must not include facts outside the retrieved context. This matters most in a regulated setting.
- **Security:** the Anthropic API key is supplied through an environment variable or Streamlit secrets. It is never hard-coded or committed.
- **Data handling:** only retrieved excerpts and the question are sent to the external API. Uploaded files are not stored permanently.
- **Performance:** a typical question returns an answer within a few seconds after indexing. The embedding model loads once and is reused.
- **Usability:** a single-page Streamlit interface that stays simple for non-technical users.
- **Reliability:** API, parsing, and empty-input failures show readable messages, not crashes.
- **Portability:** runs locally and on Streamlit Community Cloud with pinned dependencies.

## 7. Technology

Python, Streamlit, Anthropic Claude API, sentence-transformers, FAISS, pypdf.

## 8. Assumptions and Constraints

- Uploaded documents are text-based.
- The index, chat history, and dashboard figures live only for the active session.
- A valid Anthropic API key is available.
- The evaluation dataset is supplied by the user, or a small sample set ships with the project.
- The assistant supports policy lookup and does not replace formal QA or regulatory judgment.

## 9. Deliverables

| Deliverable | Description |
|---|---|
| requirements.md | This document |
| CLAUDE.md | Project guidance and conventions |
| specification.md | Technical design and behavior |
| app.py | Streamlit application |
| requirements.txt | Pinned dependencies |
| .gitignore | Excludes secrets, virtual environments, and caches |
| README.md | Setup, run, and deploy instructions |
| QA validation report | Test results against the acceptance criteria |
| GitHub-ready repository | Clean structure and no secrets |
| Streamlit Community Cloud-ready solution | Deployable with secrets set in the platform |

## 10. Acceptance Criteria

1. PDF and TXT files upload and index successfully, several at once. Unsupported types are rejected.
2. Every answer shows at least one source filename and chunk number.
3. The request sent to Claude contains only retrieved chunks and the question.
4. A question unrelated to the documents returns the exact fallback response and no sources.
5. Chat history stays visible during the session and is empty in a new session.
6. Filtering to one document returns sources only from that document.
7. Similarity scores and retrieval metadata show for every retrieved chunk.
8. The dashboard shows the session figures listed in AR-05.
9. Running the evaluation dataset produces a per-question pass/fail and an overall score.
10. No API key appears in the repository.
11. The app deploys and runs on Streamlit Community Cloud.
12. The QA report shows every requirement passed.
