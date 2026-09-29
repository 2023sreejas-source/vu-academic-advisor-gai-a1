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
# CSS — Instagram-style chat, VU red+navy gradient
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ---- App background ---- */
.stApp,
.stApp > div,
.main,
.main > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"] {
    background-color: #f0f2f5 !important;
    color: #1a1a2e !important;
}

/* ---- Top header — like Instagram DM header ---- */
.vu-header {
    display: flex;
    align-items: center;
    gap: 16px;
    background: #ffffff;
    padding: 14px 20px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border-bottom: 3px solid #c0182a;
}

.vu-header-logo {
    width: 52px;
    height: 52px;
    object-fit: contain;
    border-radius: 50%;
    border: 2.5px solid #c0182a;
    padding: 3px;
    background: #fff;
    flex-shrink: 0;
}

.vu-header-title {
    color: #0a2240;
    font-size: 17px;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
}

.vu-header-sub {
    color: #8a9bb0;
    font-size: 12px;
    margin: 2px 0 0 0;
}

.vu-header-dot {
    width: 9px;
    height: 9px;
    background: #22c55e;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
}

/* ---- Chat area background ---- */
.vu-chat-area {
    background: #f0f2f5;
    padding: 8px 0;
}

/* ---- User message — right side, red→navy gradient ---- */
.vu-msg-user {
    background: linear-gradient(135deg, #c0182a 0%, #0a2240 100%);
    color: #ffffff;
    border-radius: 20px 20px 4px 20px;
    padding: 12px 18px;
    max-width: 68%;
    margin-left: auto;
    margin-right: 0;
    font-size: 14px;
    line-height: 1.55;
    margin-bottom: 6px;
    box-shadow: 0 2px 8px rgba(192,24,42,0.18);
    word-wrap: break-word;
}

/* ---- Bot message — left side, white bubble ---- */
.vu-msg-bot {
    background: #ffffff;
    color: #1a1a2e;
    border-radius: 20px 20px 20px 4px;
    padding: 13px 18px;
    max-width: 74%;
    margin-right: auto;
    margin-left: 0;
    font-size: 14px;
    line-height: 1.65;
    margin-bottom: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    word-wrap: break-word;
}

.vu-msg-bot strong { color: #0a2240; }

/* ---- Message wrapper for alignment ---- */
.vu-row-user {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
    padding: 0 4px;
}

.vu-row-bot {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 10px;
    padding: 0 4px;
}

/* ---- Source chip ---- */
.vu-source-chip {
    display: inline-block;
    background: #fff0f1;
    color: #c0182a;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 20px;
    margin: 2px 3px 2px 0;
    border: 1px solid #f5c0c5;
    font-weight: 500;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #eaecf0;
}

.vu-sidebar-section {
    font-size: 10.5px;
    font-weight: 700;
    color: #9aa3af;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin: 20px 0 8px 0;
}

.vu-profile-badge {
    background: #f7f8fa;
    border: 1px solid #eaecf0;
    border-left: 3px solid #c0182a;
    border-radius: 6px;
    padding: 9px 12px;
    font-size: 13px;
    color: #2c3e50;
    margin-bottom: 10px;
}

.vu-profile-badge span { color: #c0182a; font-weight: 600; }

.vu-status {
    background: #f7f8fa;
    border: 1px solid #eaecf0;
    border-radius: 6px;
    padding: 9px 12px;
    font-size: 12px;
    color: #4a5568;
}

.vu-divider {
    border: none;
    border-top: 1px solid #eaecf0;
    margin: 14px 0;
}

.vu-suggest-label {
    font-size: 12px;
    color: #9aa3af;
    font-weight: 500;
    margin-bottom: 10px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ---- Bottom input bar ---- */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
.stBottom, .stBottom > div {
    background-color: #ffffff !important;
    border-top: 1px solid #eaecf0 !important;
}

[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div,
.stChatInput, .stChatInput > div {
    background: #f0f2f5 !important;
    border: 1.5px solid #eaecf0 !important;
    border-radius: 24px !important;
    color: #1a1a2e !important;
}

[data-testid="stChatInputContainer"] textarea,
.stChatInput textarea {
    color: #1a1a2e !important;
    background: transparent !important;
    caret-color: #c0182a !important;
}

[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #9aa3af !important;
}

/* ---- Suggestion buttons ---- */
div[data-testid="stButton"] > button {
    background: #ffffff !important;
    border: 1px solid #eaecf0 !important;
    border-radius: 20px !important;
    color: #0a2240 !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 9px 14px !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}

div[data-testid="stButton"] > button:hover {
    border-color: #c0182a !important;
    color: #c0182a !important;
    background: #fff0f1 !important;
}

#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MODEL
# ============================================================

MODEL = "openai/gpt-oss-20b"

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
# HEADER — logo standalone on left, like Instagram
# ============================================================

logo_file = find_logo()
logo_html = ""
if logo_file:
    b64 = image_to_base64(logo_file)
    if b64:
        logo_html = f'<img class="vu-header-logo" src="data:image/png;base64,{b64}">'
else:
    logo_html = '<div style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#c0182a,#0a2240);flex-shrink:0;"></div>'

st.markdown(f"""
<div class="vu-header">
    {logo_html}
    <div>
        <p class="vu-header-title">Vidyashilp University</p>
        <p class="vu-header-sub"><span class="vu-header-dot"></span>AI Academic Advisor &nbsp;·&nbsp; Online</p>
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
    "phase4", "advisor_scoring", "synthetic_student",
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
        if lower.endswith((".py", ".md", ".ipynb")):
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

        elif lower.endswith(".xlsx"):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(filepath, data_only=True)
                rows = []
                for sheet in wb.worksheets:
                    rows.append(f"[Sheet: {sheet.title}]")
                    for row in sheet.iter_rows(values_only=True):
                        row_text = " | ".join(str(c) for c in row if c is not None)
                        if row_text.strip():
                            rows.append(row_text)
                text = "\n".join(rows)
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
            <span>{credits}</span> credits &nbsp;·&nbsp; CGPA <span>{cgpa}</span>
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
        <strong>{N_CHUNKS}</strong> chunks indexed &nbsp;·&nbsp; Handbook · SOP · Courses · Semester
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

SYSTEM_PROMPT = """You are the AI Academic Advisor for Vidyashilp University (VU), a private university in Bengaluru, India.

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
6. If the message is a greeting, casual opener, or someone asking who you are or what
   you do (in any phrasing, formal or informal — hi, hii, hiii, hiiii, hey, heyy, hlo,
   hello, wsp, sup, who r u, what r u, ur name, wht u do, etc.), ALWAYS respond warmly:
   "Hi! I'm the Vidyashilp University AI Academic Advisor. I'm here to help you with
   courses, credits, prerequisites, attendance, graduation requirements, and semester
   planning. What can I help you with today?"
   Never search documents for this. Answer directly from this instruction.
7. Keep answers concise and direct. Use bullet points only when listing multiple items.
8. Never fabricate course codes, credit numbers, or policy rules.
9. If a student seems stressed or mentions failing, backlogs, or academic trouble,
   respond with empathy first before giving information. Example: "I understand
   that's stressful — let me help you figure this out."
10. Never give medical, legal, financial, or mental health advice. If a student
    mentions mental health struggles, respond with: "I'd encourage you to reach
    out to the university counselling centre for support. I can only help with
    academic queries."
11. If a question has multiple parts, answer each part clearly and separately.
12. Always respond in the same language or style the student uses — if they write
    informally, respond in a friendly but professional tone. Never be robotic.
13. If a student asks about fees, payments, or financial matters, say: "For fee-related
    queries, please contact the Accounts or Finance office directly."
14. If a student asks about a specific professor, HOD, or staff member, say:
    "For staff-specific queries, please contact the department office directly." """

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
# SUGGESTED QUESTIONS
# ============================================================

SUGGESTIONS = [
    "What are the minimum credits required to graduate?",
    "What is the attendance requirement per course?",
    "Can I register for a course if I failed a prerequisite?",
    "How is CGPA calculated and what is the grading scale?",
    "What courses are offered in the upcoming semester?",
]

if not st.session_state.messages:
    st.markdown('<p class="vu-suggest-label">Try asking</p>', unsafe_allow_html=True)
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
        st.markdown(
            f'<div class="vu-row-user"><div class="vu-msg-user">{content}</div></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="vu-row-bot"><div class="vu-msg-bot">{content}</div></div>',
            unsafe_allow_html=True
        )
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

prompt = st.chat_input("Message VU Advisor…")

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
