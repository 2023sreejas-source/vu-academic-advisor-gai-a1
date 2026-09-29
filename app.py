# ============================================================
# VU AI ACADEMIC ADVISOR — Vidyashilp University
# ============================================================

import streamlit as st
from groq import Groq
from pypdf import PdfReader

import os
import re
import math
import base64
import json
import requests
import html

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
# CSS
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Google Sans', 'Google Sans Text', 'Product Sans', 'Inter', Arial, sans-serif;
}

.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"] {
    background: #ffffff !important;
}

/* Force dark colors on global headers/text */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
.stApp p, .stApp span, .stApp label, .stApp div,
[data-testid="stMarkdownContainer"] *,
.stMarkdown * {
    color: #172033 !important;
}

/* -------------------- Sidebar -------------------- */
[data-testid="stSidebar"] {
    background: #082f5b !important;
    border-right: 1px solid #dbe4ee !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: #082f5b !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.20) !important;
}
[data-testid="stSidebar"] label {
    color: #ffffff !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] input {
    color: #172033 !important;
    background: #ffffff !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div {
    background: #ffffff !important;
    border-color: #d9e2ec !important;
    color: #172033 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="input"] input {
    color: #172033 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #34516d !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.70) !important;
    color: #ffffff !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.10) !important;
    border-color: #ffffff !important;
    color: #ffffff !important;
}

/* -------------------- Bottom chat input -------------------- */
[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background: #ffffff !important;
    border-top: 1px solid #e7ebf0 !important;
    padding: 10px 16px !important;
}
[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div {
    background: #ffffff !important;
    border: 1.5px solid #d9e1ea !important;
    border-radius: 26px !important;
    box-shadow: 0 2px 8px rgba(8,47,91,0.07) !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: #172033 !important;
    caret-color: #0b4f8a !important;
    background: transparent !important;
    font-size: 15px !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #9aa7b5 !important;
}

/* -------------------- General buttons -------------------- */
div[data-testid="stButton"] > button {
    background: #ffffff !important;
    border: 1px solid #d9e2ec !important;
    border-radius: 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    transition: all 0.15s !important;
}
div[data-testid="stButton"] > button * {
    color: #0b4f8a !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #0b4f8a !important;
    background: #f3f7fb !important;
}

/* -------------------- Header Styling Fix -------------------- */
.vu-header-container {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 10px 0 18px 0;
    border-bottom: 2px solid #e2e8f0;
    margin-bottom: 24px;
}
.vu-header-logo {
    max-width: 110px;
    height: auto;
    object-fit: contain;
}
.vu-header-title {
    margin: 0 !important;
    color: #0b4f8a !important;
    font-size: 30px !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
}
.vu-header-subtitle {
    margin: 4px 0 0 0 !important;
    color: #475569 !important;
    font-size: 15px !important;
    font-weight: 500 !important;
}

/* -------------------- Welcome card -------------------- */
.info-box {
    background: #ffffff;
    padding: 18px 22px;
    border-radius: 14px;
    border: 1px solid #e1e7ee;
    border-left: 5px solid #0b4f8a;
    margin-bottom: 22px;
    box-shadow: 0 2px 8px rgba(8,47,91,0.05);
}
.info-box h3, .info-box h3 * {
    color: #0b4f8a !important;
    font-weight: 700 !important;
    margin: 0 0 6px 0 !important;
}
.info-box p, .info-box p * {
    color: #334155 !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    margin: 0 !important;
}

/* Section Header Fix */
.section-heading, .section-heading * {
    color: #0b4f8a !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    margin-bottom: 12px !important;
}

/* -------------------- Chat Bubbles -------------------- */
.bubble-user {
    display: flex;
    justify-content: flex-end;
    margin: 11px 0 14px;
}
.bubble-user-inner {
    background: #0b4f8a;
    color: #ffffff !important;
    border-radius: 18px 18px 5px 18px;
    padding: 11px 17px;
    max-width: 68%;
    font-size: 15px;
    line-height: 1.65;
    box-shadow: 0 2px 8px rgba(8,47,91,0.14);
    word-wrap: break-word;
}
.bubble-user-inner * {
    color: #ffffff !important;
}

.bubble-bot {
    display: flex;
    justify-content: flex-start;
    margin: 11px 0 14px;
}
.bubble-bot-inner {
    background: #f7f9fc;
    color: #172033 !important;
    border: 1px solid #dfe6ee;
    border-radius: 18px 18px 18px 5px;
    padding: 12px 17px;
    max-width: 76%;
    font-size: 15px;
    line-height: 1.7;
    box-shadow: 0 2px 7px rgba(8,47,91,0.05);
    word-wrap: break-word;
}
.bubble-bot-inner * {
    color: #172033 !important;
}

.footer-text {
    text-align: center;
    color: #9aa7b5 !important;
    font-size: 12px;
    padding-top: 24px;
}

#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CONSTANTS & REGEX PATTERNS
# ============================================================

MODEL = "llama-3.3-70b-versatile"

ACADEMIC_EXTENSIONS = (".pdf", ".txt", ".csv", ".xlsx", ".xls")
EXCLUDED_FILES = ("advisor_eval", "eval_results", "phase4", "summary_metrics", "website_sources")

DEFAULT_WEBSITE_SOURCES = [
    {"name": "VU Official Website", "url": "https://vidyashilp.edu.in/"},
    {"name": "VU Admissions", "url": "https://vidyashilp.edu.in/admission-enquiryform/"},
    {"name": "VU Contact", "url": "https://vidyashilp.edu.in/contact/"},
    {"name": "VU B.Tech AI/ML", "url": "https://vidyashilp.edu.in/schools/b_tech_ai_ml/"},
    {"name": "VU BMS", "url": "https://vidyashilp.edu.in/schools/b-m-s-hons-hons-with-research-in-digital-business/"},
    {"name": "VU B.A., LL.B. (Hons.)", "url": "https://vidyashilp.edu.in/ba-llb/"},
    {"name": "VU B.M.S., LL.B. (Hons.)", "url": "https://vidyashilp.edu.in/schools/bachelor-of-management-studies-bachelor-of-laws-hons/"},
]

SOCIAL_RE = re.compile(
    r"^\s*(h+i+|h+e+l+o+|hey+|hola|yo+|sup|bro|wsp|wsup|what'?s\s*up|wassup|"
    r"good\s*(morning|afternoon|evening|night)|namaste|namaskaram|"
    r"thank(s|\s*you|u)|thx|ty|ok(ay)?|got\s*it|sure|great|nice|cool|"
    r"bye|goodbye|see\s*you|take\s*care|cya)\s*[!.?]*\s*$",
    re.I
)

GREETING_REPLY = (
    "Hey! 👋 I'm VU's AI Academic Advisor. "
    "I can help with attendance, credits, prerequisites, registration, "
    "course eligibility, progression rules and more. "
    "What would you like to know?"
)

THANKS_REPLY = "Happy to help! 😊 Feel free to ask anything else about your academics at VU."

OUT_OF_SCOPE_RE = re.compile(
    r"\b(weather|temperature|rain|forecast|cricket|football|soccer|match|movie|movies|"
    r"song|music|restaurant|recipe|stock market|politics|election|celebrity|"
    r"who will win|score today|bitcoin|share price)\b",
    re.I
)

PERSONAL_RE = re.compile(
    r"\b(your mom|your mother|your dad|your father|your family|your girlfriend|"
    r"your boyfriend|are you dumb|are u dumb|are you stupid|are u stupid|"
    r"who are you|what are you)\b",
    re.I
)

OUT_OF_SCOPE_REPLY = (
    "I’m VU’s AI Academic Advisor, so I can help with Vidyashilp University "
    "academic and programme-related questions, but not that topic. 😊"
)

PERSONAL_REPLY = (
    "I’m an AI academic advisor, so I don’t have a personal family or personal life. "
    "But I can definitely help with your VU academic questions. 😊"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "academic_kb" not in st.session_state:
    st.session_state.academic_kb = []
if "website_kb" not in st.session_state:
    st.session_state.website_kb = []
if "knowledge_loaded" not in st.session_state:
    st.session_state.knowledge_loaded = False
if "website_loaded" not in st.session_state:
    st.session_state.website_loaded = False
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ============================================================
# HEADER & LOGO RENDER
# ============================================================

def get_image_base64(filepath):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

def find_logo_path():
    for filename in os.listdir("."):
        if filename.startswith("."):
            continue
        lower = filename.lower()
        if lower.endswith((".png", ".jpg", ".jpeg")) and "logo" in lower:
            return filename
    for filename in os.listdir("."):
        lower = filename.lower()
        if lower.endswith((".png", ".jpg", ".jpeg")):
            return filename
    return None

logo_file = find_logo_path()
logo_html = ""

if logo_file:
    b64_str = get_image_base64(logo_file)
    ext = os.path.splitext(logo_file)[1].replace(".", "")
    if ext == "jpg":
        ext = "jpeg"
    if b64_str:
        logo_html = f'<img src="data:image/{ext};base64,{b64_str}" class="vu-header-logo" alt="VU Logo"/>'

st.markdown(f"""
<div class="vu-header-container">
    {logo_html}
    <div>
        <h1 class="vu-header-title">Vidyashilp University</h1>
        <p class="vu-header-subtitle">AI Academic Advisor · Online</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 🎓 Student Profile")
    st.markdown("Enter your details to get personalized guidance (Optional).")
    st.markdown("---")

    program = st.selectbox(
        "Program",
        ["Not specified", "B.Tech", "BMS", "BA LLB", "BMS LLB", "B.A. Economics", "B.A. Psychology", "B.Des"],
        index=0
    )

    semester = st.selectbox(
        "Current Semester",
        ["Not specified", "1st Semester", "2nd Semester", "3rd Semester",
         "4th Semester", "5th Semester", "6th Semester", "7th Semester",
         "8th Semester", "9th Semester", "10th Semester"],
        index=0
    )

    completed_credits = st.number_input(
        "Completed Credits",
        min_value=0, max_value=400,
        value=None,
        placeholder="Optional"
    )

    cgpa = st.number_input(
        "CGPA",
        min_value=0.0, max_value=10.0,
        value=None, step=0.1,
        placeholder="Optional"
    )

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# API KEY & PROFILE FORMATTING
# ============================================================

def get_api_key():
    try:
        secret_key = st.secrets.get("GROQ_API_KEY", "")
        if secret_key:
            return secret_key
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")

api_key = get_api_key()

student_profile = {
    "program": program,
    "semester": semester,
    "completed_credits": completed_credits,
    "cgpa": cgpa
}

def profile_to_text():
    details = []
    if student_profile["program"] != "Not specified":
        details.append(f"Program: {student_profile['program']}")
    if student_profile["semester"] != "Not specified":
        details.append(f"Current Semester: {student_profile['semester']}")
    if student_profile["completed_credits"] is not None:
        details.append(f"Completed Credits: {student_profile['completed_credits']}")
    if student_profile["cgpa"] is not None:
        details.append(f"CGPA: {student_profile['cgpa']}")

    return "\n".join(details) if details else "No specific student profile provided."


# ============================================================
# TEXT EXTRACTION & CHUNKING
# ============================================================

def clean_text(text):
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_pdf_text(filepath):
    pages = []
    try:
        reader = PdfReader(filepath)
        for page in reader.pages:
            try:
                t = page.extract_text()
                if t:
                    pages.append(t)
            except Exception:
                continue
    except Exception:
        return ""
    return clean_text("\n".join(pages))

def extract_file_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_pdf_text(filepath)
    if ext in [".txt", ".csv"]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return clean_text(f.read())
        except Exception:
            return ""
    if ext in [".xlsx", ".xls"]:
        try:
            from openpyxl import load_workbook
            wb = load_workbook(filepath, read_only=True, data_only=True)
            rows = []
            for sheet in wb.worksheets:
                rows.append(f"Sheet: {sheet.title}")
                for row in sheet.iter_rows(values_only=True):
                    values = [str(v) for v in row if v is not None]
                    if values:
                        rows.append(" | ".join(values))
            return clean_text("\n".join(rows))
        except Exception:
            return ""
    return ""

def chunk_text(text, chunk_size=280, overlap=50):
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        if end >= len(words):
            break
        start = end - overlap
    return chunks


# ============================================================
# KNOWLEDGE BASE LOADING
# ============================================================

def load_academic_documents():
    documents = []
    for filename in sorted(os.listdir(".")):
        if filename.startswith("."):
            continue
        lower = filename.lower()
        if not lower.endswith(ACADEMIC_EXTENSIONS) or any(ex in lower for ex in EXCLUDED_FILES):
            continue
        text = extract_file_text(os.path.join(".", filename))
        if not text:
            continue
        for i, chunk in enumerate(chunk_text(text)):
            documents.append({
                "text": chunk,
                "source": filename,
                "type": "academic",
                "chunk": i + 1
            })
    return documents

def load_website_sources():
    source_file = "website_sources.json"
    if os.path.exists(source_file):
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception:
            pass
    return DEFAULT_WEBSITE_SOURCES

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_webpage(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
            tag.decompose()
        return clean_text(soup.get_text(separator=" "))
    except Exception:
        return ""

def load_website_documents():
    documents = []
    for source in load_website_sources():
        name = source.get("name", "VU Website")
        url = source.get("url", "")
        if not url:
            continue
        text = fetch_webpage(url)
        if not text:
            continue
        for i, chunk in enumerate(chunk_text(text, chunk_size=250, overlap=40)):
            documents.append({
                "text": chunk,
                "source": name,
                "url": url,
                "type": "website",
                "chunk": i + 1
            })
    return documents

if not st.session_state.knowledge_loaded:
    with st.spinner("Loading academic knowledge base..."):
        st.session_state.academic_kb = load_academic_documents()
        st.session_state.knowledge_loaded = True

if not st.session_state.website_loaded:
    with st.spinner("Loading website sources..."):
        st.session_state.website_kb = load_website_documents()
        st.session_state.website_loaded = True

academic_kb = st.session_state.academic_kb
website_kb = st.session_state.website_kb


# ============================================================
# TOKENIZATION & RETRIEVAL
# ============================================================

STOPWORDS = {
    "the","a","an","is","are","am","i","me","my","to","of","in","on",
    "for","and","or","can","could","would","should","do","does","did",
    "be","it","this","that","with","from","at","as","what","which",
    "how","where","when","why","you","your","please","tell"
}

def simple_stem(word):
    for suffix in ["ing", "ed", "es", "s", "ment", "ability", "ible"]:
        if len(word) > 5 and word.endswith(suffix):
            return word[:-len(suffix)]
    return word

def tokenize(text):
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [simple_stem(t) for t in tokens if t not in STOPWORDS]

def retrieve(query, documents, top_k=5, minimum_score=0.02):
    if not documents:
        return []
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    query_counter = Counter(query_tokens)
    doc_freq = Counter()
    tokenized_docs = []

    for doc in documents:
        tokens = tokenize(doc["text"])
        for t in set(tokens):
            doc_freq[t] += 1
        tokenized_docs.append(tokens)

    total = len(documents)
    scored = []

    for i, doc in enumerate(documents):
        tokens = tokenized_docs[i]
        if not tokens:
            continue
        tc = Counter(tokens)

        score = sum(
            (tc[t] / len(tokens)) *
            (math.log((total + 1) / (doc_freq.get(t, 0) + 1)) + 1) *
            qc
            for t, qc in query_counter.items() if t in tc
        )

        if score >= minimum_score:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, doc in scored[:top_k]:
        r = dict(doc)
        r["_score"] = score
        results.append(r)
    return results


# ============================================================
# CLASSIFY QUERY & SYSTEM PROMPT
# ============================================================

def classify_query(query):
    q = query.lower().strip()
    website_keywords = [
        "admission", "apply", "application", "contact", "phone number", "email",
        "campus", "location", "address", "where is vu", "law programme", "phd"
    ]
    for word in website_keywords:
        if word in q:
            return "website"
    return "academic"

def build_system_prompt():
    return f"""You are the official AI Academic Advisor for Vidyashilp University (VU), Bengaluru, India.

STUDENT PROFILE:
{profile_to_text()}

YOUR CORE DIRECTIVE:
1. Always act as the VU AI Academic Advisor.
2. For academic questions, answer directly using the provided retrieved context.
3. If asked off-topic questions, respond politely, acknowledge briefly, and redirect to academic guidance.
4. If exact requirements or rules are missing from context, state that clearly and advise contacting the Academic Office.
5. Reference rules concisely."""


def create_context(academic_results, website_results):
    parts = []
    if academic_results:
        parts.append("UNIVERSITY ACADEMIC DOCUMENTS:")
        for i, r in enumerate(academic_results, 1):
            parts.append(f"[Academic Source {i}] File: {r['source']}\n{r['text']}")
    if website_results:
        parts.append("OFFICIAL VU WEBSITE INFORMATION:")
        for i, r in enumerate(website_results, 1):
            parts.append(f"[Website Source {i}] Page: {r['source']} ({r.get('url','')})\n{r['text']}")
    return "\n\n".join(parts)


# ============================================================
# LLM RESPONSE GENERATION
# ============================================================

def generate_answer(client, user_question, context):
    user_prompt = f"""RETRIEVED UNIVERSITY CONTEXT:
{context}

STUDENT QUESTION:
{user_question}

Answer concisely as the VU AI Academic Advisor."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=650
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I am experiencing connectivity issues right now. Please try again shortly. (Error: {e})"


# ============================================================
# UI HELPERS
# ============================================================

def display_sources(academic_results):
    names = list({r["source"] for r in academic_results if "source" in r})
    if names:
        st.caption("📄 **Sources:** " + " · ".join(names))

def show_user_bubble(text):
    st.markdown(
        f'<div class="bubble-user"><div class="bubble-user-inner">{html.escape(text)}</div></div>',
        unsafe_allow_html=True
    )

def show_bot_bubble(text):
    st.markdown(
        f'<div class="bubble-bot"><div class="bubble-bot-inner">{html.escape(text)}</div></div>',
        unsafe_allow_html=True
    )


# ============================================================
# FAQ SUGGESTIONS & CHAT HISTORY
# ============================================================

SUGGESTIONS = [
    "What programmes does VU offer?",
    "How do I apply to VU?",
    "What is the minimum CGPA to progress?",
    "What are the attendance requirements?",
    "Which minors are available for B.Tech?",
    "What courses are offered next semester?"
]

if not st.session_state.messages:
    st.markdown("""
    <div class="info-box">
    <h3>Ask your academic question</h3>
    <p>I can help with VU courses, programmes, prerequisites, eligibility, credits, semesters, admissions and related university information.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-heading">💡 Try asking</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_question = suggestion
                st.rerun()

for msg in st.session_state.messages:
    if msg.get("role") == "user":
        show_user_bubble(msg.get("content", ""))
    else:
        show_bot_bubble(msg.get("content", ""))
        if msg.get("academic_sources"):
            display_sources(msg.get("academic_sources"))


# ============================================================
# PROCESS USER INPUT
# ============================================================

pending = st.session_state.pending_question
st.session_state.pending_question = None
user_question = pending or st.chat_input("Ask an academic question...")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    show_user_bubble(user_question)

    q_clean = user_question.strip()

    # 1. Direct Regex Rules (Greetings, Out-of-Scope, Personal)
    if SOCIAL_RE.match(q_clean):
        reply = GREETING_REPLY if "hi" in q_clean.lower() or "hello" in q_clean.lower() or "hey" in q_clean.lower() else THANKS_REPLY
        show_bot_bubble(reply)
        st.session_state.messages.append({
            "role": "assistant", "content": reply,
            "academic_sources": [], "website_sources": []
        })
        st.stop()

    if OUT_OF_SCOPE_RE.search(q_clean):
        show_bot_bubble(OUT_OF_SCOPE_REPLY)
        st.session_state.messages.append({
            "role": "assistant", "content": OUT_OF_SCOPE_REPLY,
            "academic_sources": [], "website_sources": []
        })
        st.stop()

    if PERSONAL_RE.search(q_clean):
        show_bot_bubble(PERSONAL_REPLY)
        st.session_state.messages.append({
            "role": "assistant", "content": PERSONAL_REPLY,
            "academic_sources": [], "website_sources": []
        })
        st.stop()

    # 2. RAG & LLM Response
    if not api_key:
        answer = "Groq API key missing. Please set GROQ_API_KEY in Streamlit Secrets or environment variables."
        show_bot_bubble(answer)
        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "academic_sources": [], "website_sources": []
        })
    else:
        category = classify_query(user_question)
        client = Groq(api_key=api_key)

        if category == "website":
            website_results = retrieve(user_question, website_kb, top_k=5)
            academic_results = retrieve(user_question, academic_kb, top_k=2)
        else:
            academic_results = retrieve(user_question, academic_kb, top_k=5)
            website_results = retrieve(user_question, website_kb, top_k=2)

        context = create_context(academic_results, website_results)

        with st.spinner("Thinking..."):
            answer = generate_answer(client, user_question, context)

        show_bot_bubble(answer)
        if category == "academic" and academic_results:
            display_sources(academic_results)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "academic_sources": academic_results if category == "academic" else [],
            "website_sources": []
        })


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer-text">Vidyashilp University · AI Academic Advisor</div>',
    unsafe_allow_html=True
)
