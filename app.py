import streamlit as st
from groq import Groq
from pypdf import PdfReader

import os
import re
import math
import base64
from collections import Counter

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Academic Advisor — Vidyashilp University",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS — clean, professional university look
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #f5f6fa;
}

/* ---- Top header bar ---- */
.vu-header {
    background: #0a2240;
    padding: 18px 28px;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 18px;
}

.vu-header-logo {
    width: 56px;
    height: 56px;
    object-fit: contain;
    background: white;
    border-radius: 8px;
    padding: 5px;
    flex-shrink: 0;
}

.vu-header-text {}

.vu-header-title {
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
    line-height: 1.2;
    margin: 0;
}

.vu-header-sub {
    color: #94b8d6;
    font-size: 13px;
    margin: 3px 0 0 0;
}

/* ---- Chat messages ---- */
.vu-msg-user {
    background: #0a2240;
    color: #ffffff;
    border-radius: 14px 14px 4px 14px;
    padding: 12px 16px;
    max-width: 78%;
    margin-left: auto;
    font-size: 14.5px;
    line-height: 1.55;
    margin-bottom: 14px;
}

.vu-msg-bot {
    background: #ffffff;
    color: #1a1a2e;
    border-radius: 14px 14px 14px 4px;
    padding: 14px 18px;
    max-width: 82%;
    font-size: 14.5px;
    line-height: 1.6;
    margin-bottom: 14px;
    border: 1px solid #e4e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.vu-msg-bot strong {
    color: #0a2240;
}

/* ---- Source chip ---- */
.vu-source-chip {
    display: inline-block;
    background: #eef3fb;
    color: #1e4a8a;
    font-size: 11.5px;
    padding: 3px 9px;
    border-radius: 20px;
    margin: 2px 3px 2px 0;
    border: 1px solid #c8d9f5;
    font-weight: 500;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e4e8f0;
}

.vu-sidebar-section {
    font-size: 11px;
    font-weight: 700;
    color: #8492a6;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 18px 0 8px 0;
}

.vu-profile-badge {
    background: #f0f4ff;
    border: 1px solid #c8d9f5;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 13px;
    color: #2c3e50;
    margin-bottom: 10px;
}

.vu-profile-badge span {
    color: #1e4a8a;
    font-weight: 600;
}

.vu-status {
    background: #f0faf4;
    border: 1px solid #b8dfc8;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 12.5px;
    color: #2d6a4f;
}

/* ---- Input area ---- */
.stChatInput > div {
    border-radius: 12px !important;
    border: 1.5px solid #c8d9f5 !important;
    background: #ffffff !important;
}

/* ---- Suggested questions ---- */
.vu-suggestion {
    background: #ffffff;
    border: 1px solid #dde4f0;
    border-radius: 8px;
    padding: 9px 13px;
    font-size: 13px;
    color: #1e4a8a;
    cursor: pointer;
    margin-bottom: 6px;
    transition: background 0.15s;
}

.vu-suggestion:hover {
    background: #eef3fb;
}

/* ---- Divider ---- */
.vu-divider {
    border: none;
    border-top: 1px solid #e4e8f0;
    margin: 16px 0;
}

/* hide streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MODEL
# ============================================================

MODEL = "llama-3.3-70b-versatile"

# ============================================================
# LOGO HELPER
# ============================================================

def find_logo():
    for filename in os.listdir("."):
        if filename.startswith("."):
            continue
        lower = filename.lower()
        if lower.endswith((".png", ".jpg", ".jpeg")) and ("logo" in lower or "b0d1fb" in lower):
            return filename
    return None

def image_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

# ============================================================
# HEADER
# ============================================================

logo_file = find_logo()
logo_html = ""
if logo_file:
    b64 = image_to_base64(logo_file)
    if b64:
        logo_html = f'<img class="vu-header-logo" src="data:image/png;base64,{b64}">'

st.markdown(f"""
<div class="vu-header">
    {logo_html}
    <div class="vu-header-text">
        <p class="vu-header-title">AI Academic Advisor</p>
        <p class="vu-header-sub">Vidyashilp University &nbsp;·&nbsp; Powered by Retrieval-Augmented Generation</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = None

# ============================================================
# STOPWORDS & TOKENIZER
# ============================================================

STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "of", "to", "in", "on",
    "for", "with", "what", "are", "was", "were", "be", "can", "i",
    "my", "me", "do", "does", "how", "much", "many", "about",
    "from", "at", "this", "that", "it", "as", "by", "if", "minimum"
}

def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]

# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

EXCLUDE_KEYWORDS = [
    "evaluation_dataset", "held_out", "results_", "before_after",
    "phase4", "advisor_scoring", "requirements", "synthetic_student",
    "manual_spot", "question_bank", "generalization"
]

def load_knowledge_base():
    documents = []
    source_folder = "DOCS" if os.path.exists("DOCS") else "."

    try:
        filenames = os.listdir(source_folder)
    except Exception:
        return []

    for filename in filenames:
        if filename.startswith("."):
            continue
        lower = filename.lower()
        if lower.endswith((".py", ".md", ".ipynb", ".csv")):
            continue
        if any(w in lower for w in EXCLUDE_KEYWORDS):
            continue

        filepath = os.path.join(source_folder, filename)
        text = ""

        if lower.endswith(".pdf"):
            try:
                reader = PdfReader(filepath)
                pages = [p.extract_text() for p in reader.pages if p.extract_text()]
                text = "\n".join(pages)
            except Exception:
                continue

        elif lower.endswith(".txt"):
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception:
                continue

        elif lower.endswith(".csv"):
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception:
                continue

        else:
            continue

        if not text.strip():
            continue

        text = re.sub(r"\s+", " ", text).strip()
        words = text.split()
        chunk_size = 120

        for start in range(0, len(words), chunk_size):
            chunk = words[start:start + chunk_size]
            if chunk:
                documents.append({
                    "id": f"{filename}#{start // chunk_size}",
                    "filename": filename,
                    "text": " ".join(chunk)
                })

    return documents

# ============================================================
# BUILD KB
# ============================================================

if st.session_state.knowledge_base is None:
    with st.spinner("Loading university documents…"):
        st.session_state.knowledge_base = load_knowledge_base()

knowledge_base = st.session_state.knowledge_base

# ============================================================
# TF-IDF RETRIEVAL
# ============================================================

def build_doc_freq(docs):
    df = Counter()
    for doc in docs:
        for tok in set(tokenize(doc["text"])):
            df[tok] += 1
    return df

DOC_FREQ = build_doc_freq(knowledge_base)
N_CHUNKS = len(knowledge_base)

def retrieve(query, top_k=6):
    if not knowledge_base:
        return []
    q_tokens = set(tokenize(query))
    if not q_tokens:
        return knowledge_base[:top_k]

    scored = []
    for doc in knowledge_base:
        doc_tokens = set(tokenize(doc["text"]))
        score = sum(
            math.log((N_CHUNKS + 1) / (DOC_FREQ.get(t, 0) + 1)) + 1
            for t in q_tokens if t in doc_tokens
        )
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]

# ============================================================
# GUARDRAIL
# ============================================================

def is_gibberish(prompt):
    prompt = prompt.strip()
    if not prompt:
        return True
    words = prompt.split()
    for word in words:
        if len(word) > 25:
            return True
    letters = re.findall(r"[a-zA-Z]", prompt)
    if len(prompt) > 5 and letters:
        diversity = len(set(c.lower() for c in letters))
        if diversity / len(letters) < 0.08:
            return True
    return False

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown('<p class="vu-sidebar-section">Student Profile</p>', unsafe_allow_html=True)

    include_profile = st.checkbox("Include my profile in queries", value=True)

    completed_courses = st.text_area(
        "Completed courses",
        value="CS101 Intro to CS, CS201 Data Structures",
        height=90,
        help="Comma-separated list of completed course codes and names."
    )
    credits = st.number_input("Completed credits", min_value=0, max_value=250, value=45)
    cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.1)

    if include_profile:
        st.markdown(f"""
        <div class="vu-profile-badge">
            <span>{credits} credits</span> completed &nbsp;·&nbsp; CGPA <span>{cgpa}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="vu-divider">', unsafe_allow_html=True)
    st.markdown('<p class="vu-sidebar-section">API Key</p>', unsafe_allow_html=True)

    api_key = None
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        api_key = st.text_input("Groq API key", type="password", placeholder="gsk_…")

    st.markdown('<hr class="vu-divider">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vu-status">
        ✅ &nbsp;<strong>{N_CHUNKS}</strong> document chunks indexed<br>
        <span style="font-size:11px; color:#555;">Student Handbook · Course Plans · SOP · Programme Structure</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================================
# PROFILE TEXT
# ============================================================

profile_text = ""
if include_profile:
    profile_text = (
        f"Student profile: completed {credits} credits, CGPA {cgpa}, "
        f"completed courses: {completed_courses}."
    )

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """You are the AI Academic Advisor for Vidyashilp University.

Your role is to help students with academic questions — courses, credits, prerequisites,
attendance, progression rules, graduation requirements, and semester planning.

RULES:
1. Answer ONLY using the retrieved document excerpts provided. Do not use general knowledge
   about universities or invent any rules, numbers, or course codes.
2. Cite the source excerpt after each factual claim, like this: [Student_Handbook.pdf#3]
3. If the documents do not contain enough information to answer, say so clearly and ask
   a specific follow-up question rather than guessing.
4. If a question needs student-specific details (credits, courses completed, CGPA) that
   were not given, ask for them before answering.
5. If excerpts conflict, say so explicitly — do not silently pick one.
6. For questions outside academics (weather, personal topics, general trivia), respond:
   "I can only help with academic questions related to Vidyashilp University."
7. Keep answers concise and direct. Use bullet points only when listing multiple items.
8. Never fabricate course codes, credit numbers, or policy rules."""

# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(question, retrieved_docs):
    if not api_key:
        return "Please enter your Groq API key in the sidebar to get started."

    context_parts = []
    for doc in retrieved_docs:
        context_parts.append(f"[{doc['id']}]\n{doc['text']}")
    context = "\n\n".join(context_parts) or "No relevant documents found."

    user_prompt = f"""University document excerpts:

{context}

{profile_text}

Student question: {question}

Answer using only the excerpts above. Cite sources. If the answer is not in the excerpts, say so."""

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=800
        )
        answer = response.choices[0].message.content
        return answer if answer else "The model returned an empty response. Please try again."

    except Exception as e:
        return f"Error connecting to the AI service: {str(e)}"

# ============================================================
# SUGGESTED QUESTIONS (shown when chat is empty)
# ============================================================

SUGGESTIONS = [
    "What are the minimum credits required to graduate?",
    "What is the attendance requirement per course?",
    "Can I register for a course if I failed a prerequisite?",
    "How is CGPA calculated and what is the grading scale?",
    "What courses are offered in the upcoming semester?",
]

if not st.session_state.messages:
    st.markdown("**Suggested questions — click to ask:**")
    cols = st.columns(2)
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i % 2]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()
    st.markdown("")

# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        st.markdown(f'<div class="vu-msg-user">{content}</div>', unsafe_allow_html=True)

    else:
        st.markdown(f'<div class="vu-msg-bot">{content}</div>', unsafe_allow_html=True)

        sources = msg.get("sources", [])
        if sources:
            chips = "".join(
                f'<span class="vu-source-chip">📄 {s["filename"]}</span>'
                for s in sources
            )
            with st.expander("Sources used", expanded=False):
                st.markdown(chips, unsafe_allow_html=True)
                for s in sources:
                    st.markdown(
                        f"**[{s['id']}]** — {s['text'][:300]}…",
                        help=s["text"]
                    )

# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input("Ask an academic question…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    if is_gibberish(prompt):
        answer = "I couldn't understand that. Please ask a clear academic question — for example, about courses, credits, prerequisites, or attendance."
        retrieved_docs = []
    else:
        retrieved_docs = retrieve(prompt, top_k=6)

        with st.spinner("Checking university documents…"):
            answer = generate_answer(prompt, retrieved_docs)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": retrieved_docs
    })
    st.rerun()
