import json
import logging
import os
import re

import anthropic
import faiss
import streamlit as st
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("helixnova")

# ---------- Configuration ----------
CLAUDE_MODEL = "claude-3-5-sonnet-latest"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 4
PASS_THRESHOLD = 0.6  # share of expected key terms the answer must contain
EVAL_DATASET = os.path.join(os.path.dirname(__file__), "evaluation_dataset.json")
FALLBACK = "I could not find enough information in the uploaded document."

SYSTEM_PROMPT = f"""You are a pharmaceutical quality and regulatory policy assistant.
Answer the question using ONLY the document excerpts provided by the user.
Rules:
- Never use external knowledge.
- Never invent answers.
- Never speculate or make assumptions.
- If the excerpts do not contain enough information to answer, reply with exactly:
{FALLBACK}
- Keep the answer concise and stay close to the wording of the excerpts."""


# ---------- Helpers ----------
def get_api_key():
    """Read the API key from the environment, then from Streamlit secrets."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None


@st.cache_resource
def load_embedder():
    """Load the embedding model once and reuse it."""
    return SentenceTransformer(EMBEDDING_MODEL)


def extract_text(uploaded_file):
    """Return the plain text of a PDF or TXT upload."""
    if uploaded_file.name.lower().endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return uploaded_file.getvalue().decode("utf-8", errors="ignore")


def clean_text(text):
    """Remove control characters and collapse extra whitespace."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def chunk_text(text):
    """Split text into overlapping chunks of CHUNK_SIZE characters."""
    step = CHUNK_SIZE - CHUNK_OVERLAP
    chunks = []
    for start in range(0, len(text), step):
        piece = text[start:start + CHUNK_SIZE].strip()
        if piece:
            chunks.append(piece)
        if start + CHUNK_SIZE >= len(text):
            break
    return chunks


def build_index(uploaded_files):
    """Extract, chunk, embed and index the uploaded files."""
    docs = []    # one dict per file: filename, characters, chunks
    chunks = []  # one dict per chunk: filename, chunk_id, text
    for f in uploaded_files:
        text = clean_text(extract_text(f))
        if not text:
            st.warning(f"No extractable text found in {f.name}. File skipped.")
            continue
        pieces = chunk_text(text)
        docs.append({"filename": f.name, "characters": len(text), "chunks": len(pieces)})
        for number, piece in enumerate(pieces, start=1):
            chunks.append({"filename": f.name, "chunk_id": number, "text": piece})
    if not chunks:
        return None, [], []

    vectors = load_embedder().encode(
        [c["text"] for c in chunks], normalize_embeddings=True
    ).astype("float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index, chunks, docs


def retrieve(question, selected_files):
    """Return the top chunks (with similarity scores) from the selected files."""
    query = load_embedder().encode([question], normalize_embeddings=True).astype("float32")
    # Search every chunk, then filter, so the file filter never leaves us short
    scores, ids = st.session_state.index.search(query, st.session_state.index.ntotal)
    results = []
    for score, i in zip(scores[0], ids[0]):
        chunk = st.session_state.chunks[i]
        if selected_files and chunk["filename"] not in selected_files:
            continue
        results.append({**chunk, "score": float(score)})
        if len(results) == TOP_K:
            break
    return results


def ask_claude(question, retrieved, api_key):
    """Send only the retrieved chunks and the question to Claude."""
    context = "\n\n".join(
        f"[Source: {c['filename']}, chunk {c['chunk_id']}]\n{c['text']}" for c in retrieved
    )
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Document excerpts:\n\n{context}\n\nQuestion: {question}",
            }
        ],
    )
    return response.content[0].text.strip()


def is_fallback(answer):
    return answer.strip().strip('"') == FALLBACK


def answer_question(question, selected_files, api_key):
    """Retrieve, then ask Claude. Returns (answer, sources)."""
    retrieved = retrieve(question, selected_files)
    if not retrieved:
        return FALLBACK, []
    answer = ask_claude(question, retrieved, api_key)
    # No sources are shown when the fallback is returned
    return answer, ([] if is_fallback(answer) else retrieved)


def show_sources(sources):
    """Display filename, chunk number and score, with chunk text in an expander."""
    st.markdown("**Sources Used**")
    for s in sources:
        st.markdown(f"- {s['filename']} — chunk {s['chunk_id']} — score {s['score']:.3f}")
    with st.expander("View retrieved chunks"):
        for s in sources:
            st.markdown(f"**{s['filename']} — chunk {s['chunk_id']} — score {s['score']:.3f}**")
            st.text(s["text"])


def key_terms(text):
    """Lower-case words longer than 3 characters, plus all numbers."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) > 3 or w.isdigit()}


def answer_matches(expected, actual):
    """Simple check: the answer must contain most of the expected key terms."""
    if is_fallback(expected):
        return is_fallback(actual)
    terms = key_terms(expected)
    if not terms or is_fallback(actual):
        return False
    return len(terms & key_terms(actual)) / len(terms) >= PASS_THRESHOLD


def load_eval_cases(uploaded_file=None):
    """Load test cases from an uploaded JSON file, or the bundled dataset."""
    if uploaded_file is not None:
        cases = json.load(uploaded_file)
    else:
        with open(EVAL_DATASET, encoding="utf-8") as f:
            cases = json.load(f)
    if not isinstance(cases, list) or not cases or not all(
        isinstance(c, dict) and c.get("question") and c.get("expected_answer")
        for c in cases
    ):
        raise ValueError("Expected a non-empty list of objects with 'question' and 'expected_answer'.")
    return cases


def run_evaluation(cases, selected_files, api_key):
    """Retrieve context and call Claude for each test question, log and score the result."""
    rows = []
    for case in cases:
        try:
            actual, _ = answer_question(case["question"], selected_files, api_key)
        except Exception as e:
            actual = f"ERROR: {e}"
        passed = answer_matches(case["expected_answer"], actual)
        logger.info("EVAL %s | %s | %s", "PASS" if passed else "FAIL", case["question"], actual)
        rows.append(
            {
                "Question": case["question"],
                "Expected": case["expected_answer"],
                "Actual": actual,
                "Pass/Fail": "Pass" if passed else "Fail",
            }
        )
    accuracy = sum(r["Pass/Fail"] == "Pass" for r in rows) / len(rows)
    logger.info("EVAL accuracy: %.0f%% (%d questions)", accuracy * 100, len(rows))
    return rows, accuracy


# ---------- Page ----------
st.set_page_config(page_title="HelixNova Policy Assistant", page_icon="💊", layout="wide")
st.title("HelixNova Pharma Quality & Regulatory RAG Assistant")

defaults = {
    "messages": [],
    "index": None,
    "chunks": [],
    "docs": [],
    "indexed_files": None,
    "questions": 0,
    "fallbacks": 0,
    "top_scores": [],
    "eval_result": None,
    "eval_rows": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------- Document upload ----------
st.header("1. Upload Policy Documents")
uploaded = st.file_uploader(
    "Upload PDF or TXT policy documents", type=["pdf", "txt"], accept_multiple_files=True
)

if uploaded:
    signature = [(f.name, f.size) for f in uploaded]
    if signature != st.session_state.indexed_files:
        with st.spinner("Extracting text, creating embeddings and building index..."):
            try:
                index, chunks, docs = build_index(uploaded)
            except Exception as e:
                index, chunks, docs = None, [], []
                st.error(f"Could not process the uploaded files: {e}")
        st.session_state.index = index
        st.session_state.chunks = chunks
        st.session_state.docs = docs
        st.session_state.indexed_files = signature
else:
    # Files removed: drop the index so answers never rely on removed documents
    st.session_state.index = None
    st.session_state.chunks = []
    st.session_state.docs = []
    st.session_state.indexed_files = None

docs = st.session_state.docs
total_chars = sum(d["characters"] for d in docs)
total_chunks = len(st.session_state.chunks)

if docs:
    st.success("Documents indexed.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Uploaded files", len(docs))
    c2.metric("Total characters", f"{total_chars:,}")
    c3.metric("Total chunks", total_chunks)
    st.dataframe(docs, width="stretch")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Library")
    if docs:
        st.markdown("**Uploaded files**")
        for d in docs:
            st.markdown(f"- {d['filename']}")
    else:
        st.caption("No documents uploaded yet.")
    st.metric("Chunk count", total_chunks)
    st.metric("Total embeddings", st.session_state.index.ntotal if docs else 0)
    st.markdown(f"**Embedding model:** {EMBEDDING_MODEL}")
    st.markdown(f"**Claude model:** {CLAUDE_MODEL}")
    st.divider()
    selected_files = st.multiselect(
        "Filter retrieval by file",
        options=[d["filename"] for d in docs],
        help="Leave empty to search all files.",
    )

# ---------- Dashboard ----------
st.header("2. Dashboard")
scores = st.session_state.top_scores
d1, d2, d3, d4 = st.columns(4)
d1.metric("Documents uploaded", len(docs))
d2.metric("Chunks created", total_chunks)
d3.metric("Average retrieval score", f"{sum(scores) / len(scores):.3f}" if scores else "–")
d4.metric("Questions asked", st.session_state.questions)
d5, d6 = st.columns(2)
d5.metric("Fallback responses", st.session_state.fallbacks)
result = st.session_state.eval_result
d6.metric("Last evaluation accuracy", f"{result:.0%}" if result is not None else "–")

with st.expander("Evaluation testing", expanded=bool(st.session_state.eval_rows)):
    st.caption(
        "Runs each test question through retrieval and Claude, then marks Pass when the "
        "answer contains most of the key terms in the expected answer. Uses the bundled "
        "evaluation_dataset.json unless you upload your own JSON list of "
        '{"question": "...", "expected_answer": "..."} objects.'
    )
    eval_file = st.file_uploader("Evaluation dataset (JSON, optional)", type=["json"], key="eval_file")
    if st.button("Run evaluation"):
        api_key = get_api_key()
        if st.session_state.index is None:
            st.warning("Upload a policy document first.")
        elif not api_key:
            st.error("ANTHROPIC_API_KEY is not set.")
        else:
            try:
                cases = load_eval_cases(eval_file)
                with st.spinner("Running evaluation..."):
                    rows, accuracy = run_evaluation(cases, selected_files, api_key)
                st.session_state.eval_result = accuracy
                st.session_state.eval_rows = rows
                st.rerun()  # refresh the dashboard metric drawn above
            except (ValueError, OSError) as e:
                st.error(f"Invalid evaluation dataset: {e}")
    if st.session_state.eval_rows:
        st.metric("Accuracy", f"{st.session_state.eval_result:.0%}")
        st.dataframe(st.session_state.eval_rows, width="stretch")

# ---------- Ask your policy ----------
st.header("3. Ask Your Policy")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            show_sources(message["sources"])

question = st.chat_input("Ask a question about your policy documents")

if question and question.strip():
    question = question.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        api_key = get_api_key()
        if st.session_state.index is None:
            answer, sources = "Please upload a policy document first.", []
            st.markdown(answer)
        elif not api_key:
            answer, sources = (
                "ANTHROPIC_API_KEY is not set. Add it as an environment variable "
                "or in Streamlit secrets.",
                [],
            )
            st.error(answer)
        else:
            try:
                with st.spinner("Searching policy documents..."):
                    answer, sources = answer_question(question, selected_files, api_key)
                st.markdown(answer)
                if sources:
                    show_sources(sources)
                # Update dashboard figures
                st.session_state.questions += 1
                if not sources:
                    st.session_state.fallbacks += 1
                else:
                    st.session_state.top_scores.append(sources[0]["score"])
            except Exception as e:
                answer, sources = f"Something went wrong while answering: {e}", []
                st.error(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
    st.rerun()  # refresh the dashboard, which is drawn above the chat
