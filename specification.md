# specification.md — HelixNova Pharma Quality & Regulatory RAG Assistant

Derived from `requirements.md` and `CLAUDE.md`. It defines the architecture, workflow, and behavior, and contains no code.

## 1. Overview

A single-page Streamlit app. Users upload one or more PDF or TXT policy documents, optionally choose which documents to search, and ask questions in natural language. Claude answers using only the retrieved chunks. Each answer lists its sources with similarity scores. A quality dashboard and an evaluation framework measure how well the assistant performs.

## 2. Configuration

| Setting | Value |
|---|---|
| `chunk_size` | 800 characters |
| `chunk_overlap` | 100 characters |
| `top_k` | 4 |
| Embedding model | sentence-transformers/all-MiniLM-L6-v2 |
| Vector database | FAISS (in memory) |
| Supported formats | PDF, TXT (multiple files allowed) |
| LLM | Anthropic Claude (model name in one constant at the top of `app.py`) |
| API key | `ANTHROPIC_API_KEY` environment variable, else `st.secrets["ANTHROPIC_API_KEY"]` |
| Fallback text | I could not find enough information in the uploaded document. |

## 3. System Architecture

```
Document Upload
      |
Text Extraction
      |
Chunking
      |
Embedding Generation
      |
FAISS Index
      |
Question Input
      |
Similarity Search
      |
Top K Retrieval
      |
Document Filter
      |
Claude Prompt
      |
Grounded Answer
      |
Source Citations
```

The app is a single `app.py` with small, well-named functions. It has no other services and no database.

| Component | Responsibility |
|---|---|
| UI | Uploader, document filter, chat, sources, dashboard, evaluation panel |
| Loader and cleaner | Turn each file into clean plain text |
| Chunker | Create overlapping chunks and attach metadata |
| Embedder | Convert chunks and questions to vectors, using one cached model instance |
| FAISS index | Store chunk vectors and return nearest neighbors with scores |
| Retriever | Rank chunks, apply the document filter, keep the top K |
| Prompt builder | Combine instructions, retrieved chunks, and the question |
| Claude client | Send the prompt and return the answer |
| Evaluator | Run test questions through the same pipeline and score the results |
| Session state | Holds the documents, index, chat history, and dashboard figures |

## 4. Workflow

### 4.1 Indexing (on upload)

1. **Document Upload.** The user uploads one or more PDF or TXT files. Other types are rejected with a message.
2. **Text Extraction.** PDFs are read page by page with pypdf. TXT files are decoded as text. A file with no extractable text is skipped with a warning naming the file.
3. **Chunking.** Clean the text by removing control characters and collapsing extra whitespace, without changing wording or numbers. Then split it into 800-character chunks with a 100-character overlap. Number chunks per file starting at 1.
4. **Embedding Generation.** Embed all chunk texts with the model. Vectors are normalized so that similarity reflects cosine similarity.
5. **FAISS Index.** Add the vectors to an in-memory FAISS index. Keep the metadata list in the same order, so that vector position N maps to metadata entry N. Show the character count and chunk count per session.

### 4.2 Question answering (on each question)

6. **Question Input.** The user types a question. If no index exists, prompt the user to upload documents first.
7. **Similarity Search.** Embed the question and search the FAISS index. Search a candidate pool larger than `top_k` (the whole index is acceptable at this scale), so that filtering in step 9 does not leave too few results.
8. **Top K Retrieval.** Rank candidates by similarity score, highest first.
9. **Document Filter.** The user can select which uploaded documents to search. Drop candidates from unselected documents, then keep the first `top_k` that remain. With no selection made, all documents are searched. If no chunk remains, the fallback is returned.
10. **Claude Prompt.** Build the prompt from the grounding instructions (section 6), the retrieved chunks, each labelled with filename and chunk ID, and the question.
11. **Grounded Answer.** Send the prompt to Claude and receive the answer.
12. **Source Citations.** Display the answer, then the sources (section 7).

The question, answer, and sources are then appended to the chat history. Dashboard figures are updated.

## 5. Metadata

Each retrieved chunk carries these fields:

| Field | Description |
|---|---|
| `filename` | Name of the uploaded file |
| `chunk_id` | Position of the chunk in its file, starting at 1. The pair filename + chunk_id is unique. |
| `chunk_text` | The chunk's text |
| `similarity_score` | Cosine similarity between the question and the chunk |

`filename`, `chunk_id`, and `chunk_text` are stored at indexing time. `similarity_score` is calculated for each question during retrieval and is not stored in the index. None of these fields may be lost between retrieval and display.

## 6. Answer Generation Rules

- Only the retrieved chunks, the question, and the fixed instructions are sent to Claude. Full documents are never sent.
- The instructions tell Claude to:
  - answer only from the provided context
  - not assume, infer beyond the text, or use external knowledge
  - reply exactly with the fallback text when the context is insufficient
  - keep the answer short and close to the policy wording
- Earlier chat turns are not sent to Claude. Each question is answered on its own from its retrieved context.

## 7. Source Display and Fallback

For each answer the user sees a **Sources Used** list, with one line per retrieved chunk: filename, chunk ID, rank, and similarity score. An expander shows the full chunk text for each of these.

**Fallback.** The reply is exactly: **"I could not find enough information in the uploaded document."** It applies when Claude judges the context insufficient, or when no chunks remain after filtering. It is never reworded or extended. No sources are shown with the fallback.

## 8. Session Features

All of the following live in Streamlit session state and last only for the active browser session:

| Feature | Behavior |
|---|---|
| Chat history | Ordered list of questions and answers. Each answer keeps its sources and scores. Redisplayed on every rerun. |
| Uploaded documents | The list of indexed files and their chunks. Removing a file drops its chunks from the index. |
| FAISS index | Rebuilt whenever the set of uploaded files changes. |
| Dashboard figures | Counters and scores collected as questions are answered. |

No file or database is written.

## 9. Advanced Features

### 9.1 Multi-document retrieval
Several files can be indexed at once. A single question searches across all selected documents, and the sources can come from different files.

### 9.2 Retrieval score display
Every retrieved chunk is shown with its similarity score. Higher means more similar. Scores indicate relevance, not correctness.

### 9.3 Quality dashboard
A simple panel showing session figures:

| Figure | Meaning |
|---|---|
| Questions asked | Count in this session |
| Grounded answers | Answers that were not the fallback |
| Fallback responses | Count of fallback replies |
| Fallback rate | Fallback responses divided by questions asked |
| Average top similarity | Mean similarity of the best retrieved chunk per question |
| Last evaluation result | Accuracy and pass/fail counts from the most recent evaluation run |

### 9.4 Evaluation framework
Runs a set of test questions through the same retrieval and answer pipeline.

- **Dataset:** a user-supplied file, or a small sample set included with the project. Each test case has a question and one of: an expected source filename (optionally with a chunk ID) for answerable questions, or a flag that the question must return the fallback.
- **Pass rules:**
  - Answerable question: passes when the answer is not the fallback and the expected source appears among the retrieved chunks.
  - Unanswerable question: passes when the exact fallback is returned.
- **Output:** a per-question table (question, expected, retrieved sources, top score, pass/fail) and overall accuracy. The result feeds the dashboard.
- Evaluation does not add to the chat history.

## 10. Error Handling

| Situation | Behavior |
|---|---|
| Unsupported file type | Rejected with a message |
| No extractable text in a file | Warning naming the file, and the file is skipped |
| No usable files after upload | Nothing indexed, and the user is told why |
| Question before any indexing | Prompt to upload documents |
| Missing API key | Clear error in the UI, and no API call is made |
| Claude API failure | Readable error message, and the app keeps running |
| Empty question | Ignored |
| Malformed evaluation dataset | Readable error naming the problem, and no run |

## 11. Security and Privacy

- No API key in code or in the repository. `.env` and `secrets.toml` are git-ignored.
- Only the retrieved chunks and the question leave the app.
- Uploaded files are processed in memory and never written to a fixed path.

## 12. Deployment (Streamlit Community Cloud)

- Entry point: `app.py` at the repository root.
- `requirements.txt` lists all dependencies with pinned versions: streamlit, anthropic, sentence-transformers, faiss-cpu, pypdf.
- The API key is set in the platform's secrets settings.
- No local file dependencies and no database.
- The embedding model downloads on first run, so the first start is slow.

## 13. Requirements Traceability

| Requirement | Covered in |
|---|---|
| FR-01, FR-02 Upload and extraction | 4.1 steps 1–2, 10 |
| FR-03 Chunking with metadata | 4.1 step 3, 5 |
| FR-04, FR-05 Embeddings and FAISS | 4.1 steps 4–5 |
| FR-06 Retrieval | 4.2 steps 7–8 |
| FR-07, FR-08 Only retrieved context, grounded answers | 6 |
| FR-09 Sources | 7 |
| FR-10 Chat history | 8 |
| FR-11 Fallback | 7 |
| AR-01 Multiple documents | 9.1 |
| AR-02 Document filter | 4.2 step 9 |
| AR-03, AR-04 Scores and retrieval metadata | 5, 7, 9.2 |
| AR-05 Dashboard | 9.3 |
| AR-06 Evaluation | 9.4 |
| AR-07 Cloud deployment | 12 |

## 14. Acceptance Checks

1. Several PDF and TXT files index with correct filenames and chunk IDs.
2. An answerable question returns an answer with 1 to 4 sources, each showing a similarity score.
3. Filtering to one document returns sources only from that document.
4. An unrelated question returns the exact fallback and no sources.
5. The Claude request contains only retrieved chunks and the question.
6. Chat history is visible during the session and empty in a new session.
7. The dashboard figures match the questions asked.
8. An evaluation run shows a per-question result and an overall accuracy.
9. The app runs on Streamlit Community Cloud with the key supplied through secrets.
