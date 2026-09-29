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
    page_icon=None,
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
    font-family: 'Inter', 'Google Sans', 'Google Sans Text', Arial, sans-serif;
}

.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"] {
    background: #F5F7FA !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stSidebar"] {
    background: #0B5394 !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: #0B5394 !important;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #D9ECFA !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.24) !important;
}

/* Sidebar selectboxes: dark controls, matching the requested design. */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #22252A !important;
    border-color: #22252A !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #FFFFFF !important;
}

/* Sidebar numeric inputs: white fields. */
[data-testid="stSidebar"] [data-testid="stNumberInput"] > div {
    background: #FFFFFF !important;
    border-radius: 7px !important;
}
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    color: #22252A !important;
    background: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
    background: #FFFFFF !important;
    color: #0B5394 !important;
}

/* Clear Chat button. */
[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    background: transparent !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.85) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}

/* Main cards. */
.vu-card {
    background: #FFFFFF;
    border: 1px solid #E2E7ED;
    border-radius: 12px;
    padding: 22px 24px;
    margin: 0 0 16px 0;
    box-shadow: 0 1px 3px rgba(16,24,40,0.04);
}

.vu-top-card {
    padding: 18px 22px;
}
.vu-accent {
    width: 42px;
    height: 4px;
    background: #C9474E;
    border-radius: 3px;
    margin-bottom: 10px;
}
.vu-heading {
    color: #123B63;
    font-size: 28px;
    font-weight: 700;
    margin: 0;
}
.vu-status {
    color: #7A858F;
    font-size: 13px;
    margin-top: 6px;
}
.vu-status-dot {
    color: #28A745;
    font-size: 11px;
}
.vu-logo img {
    max-height: 70px !important;
    width: auto !important;
    object-fit: contain !important;
}
.vu-campus img {
    width: 100% !important;
    height: auto !important;
    max-height: 170px !important;
    object-fit: contain !important;
    object-position: center right !important;
    border-radius: 10px !important;
}

.vu-prompt-title {
    color: #27364A;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 6px;
}
.vu-prompt-text {
    color: #66717D;
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
}
.vu-try {
    color: #4E5965;
    font-size: 13px;
    font-weight: 600;
    margin: 4px 0 8px;
}

/* Suggested-question buttons. */
main div[data-testid="stButton"] > button {
    background: #FFFFFF !important;
    border: 1px solid #DCE3EB !important;
    border-radius: 10px !important;
    color: #174B78 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    min-height: 54px !important;
    box-shadow: none !important;
    padding: 10px 12px !important;
}
main div[data-testid="stButton"] > button:hover {
    background: #F7FAFD !important;
    border-color: #0B5394 !important;
}

/* Chat history bubbles. */
.bubble-user {
    display: flex;
    justify-content: flex-end;
    margin: 10px 0 12px;
}
.bubble-user-inner {
    background: #0B5394;
    color: #FFFFFF;
    border-radius: 16px 16px 4px 16px;
    padding: 10px 15px;
    max-width: 68%;
    font-size: 15px;
    line-height: 1.6;
}
.bubble-bot {
    display: flex;
    justify-content: flex-start;
    margin: 10px 0 12px;
}
.bubble-bot-inner {
    background: #FFFFFF;
    color: #1F2933;
    border: 1px solid #E2E7ED;
    border-radius: 16px 16px 16px 4px;
    padding: 11px 16px;
    max-width: 76%;
    font-size: 15px;
    line-height: 1.65;
}

.source-panel, .source-panel * { color: #7A858F !important; }
.source-panel .source-label { color: #0B5394 !important; font-weight: 600; }
[data-testid="stExpander"] summary { color: #7A858F !important; font-size: 12px !important; }

/* Dark Streamlit chat composer. */
[data-testid="stBottom"] {
    background: #F5F7FA !important;
    border-top: none !important;
    padding: 8px 16px 30px !important;
}
[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div {
    background: #22252A !important;
    border: 1px solid #22252A !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10) !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: #FFFFFF !important;
    caret-color: #FFFFFF !important;
    background: transparent !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #B8BEC5 !important;
}
[data-testid="stChatInputContainer"] button {
    color: #FFFFFF !important;
    background: #17191C !important;
    border-radius: 8px !important;
}

.ai-disclaimer {
    position: fixed;
    left: 20%;
    right: 0;
    bottom: 3px;
    z-index: 999999;
    text-align: center;
    color: #A0A7AF;
    font-size: 10px;
    pointer-events: none;
}

.footer-text {
    text-align: center;
    color: #A0A7AF;
    font-size: 11px;
    padding: 8px 0 60px;
}

#MainMenu, footer { visibility: hidden; }

@media (max-width: 900px) {
    .ai-disclaimer { left: 0; }
    .vu-heading { font-size: 24px; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CONSTANTS
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
# Greetings and social messages — handled without any document retrieval
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
# LOGO & HEADER
# ============================================================

APP_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(APP_DIR, "logo.png")
campus_path = os.path.join(APP_DIR, "uni pic.jpg")

header_left, header_right = st.columns([1.35, 2.65], gap="large", vertical_alignment="center")

with header_left:
    st.markdown('<div class="vu-card vu-top-card">', unsafe_allow_html=True)
    if os.path.isfile(logo_path):
        st.markdown('<div class="vu-logo">', unsafe_allow_html=True)
        st.image(logo_path, width=150)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="vu-accent"></div>'
        '<div class="vu-heading">Academic Advisor</div>'
        '<div class="vu-status"><span class="vu-status-dot">●</span> AI Academic Advisor · Online</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with header_right:
    if os.path.isfile(campus_path):
        st.markdown('<div class="vu-campus">', unsafe_allow_html=True)
        st.image(campus_path, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### Student Profile")
    st.markdown("Enter your details to get personalised answers.")
    st.markdown("---")

    program = st.selectbox(
        "Program",
        ["B.Tech", "BMS", "BA LLB", "BMS LLB", "B.A. Economics", "B.A. Psychology", "B.Des"],
        index=None,
        placeholder="Select if needed"
    )

    semester = st.selectbox(
        "Current Semester",
        ["1st Semester", "2nd Semester", "3rd Semester", "4th Semester",
         "5th Semester", "6th Semester", "7th Semester", "8th Semester",
         "9th Semester", "10th Semester"],
        index=None,
        placeholder="Select if needed"
    )

    completed_credits = st.number_input(
        "Completed Credits", min_value=0, max_value=400, value=None, step=1,
        placeholder="Optional"
    )
    cgpa = st.number_input(
        "CGPA", min_value=0.0, max_value=10.0, value=None, step=0.1,
        format="%.2f", placeholder="Optional"
    )

    st.markdown("---")

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# API KEY
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


# ============================================================
# STUDENT PROFILE
# ============================================================

student_profile = {
    "program": program,
    "semester": semester,
    "completed_credits": completed_credits,
    "cgpa": cgpa
}


# ============================================================
# TEXT EXTRACTION
# ============================================================

def clean_text(text):
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def guess_section(raw_text):
    """Return only an explicit-looking heading; otherwise return blank."""
    for line in raw_text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line or len(line) > 100:
            continue
        if re.match(r"^(?:\d+(?:\.\d+)*\s+.+|[A-Z][A-Z0-9 &:/()\-]{4,})$", line):
            return line
        words = line.split()
        if 2 <= len(words) <= 10 and not re.search(r"[.!?]$", line):
            title_case = sum(1 for w in words if w[:1].isupper())
            if title_case >= max(2, len(words) // 2):
                return line
    return ""

def extract_pdf_pages(filepath):
    pages = []
    try:
        reader = PdfReader(filepath)
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                raw = page.extract_text() or ""
                text = clean_text(raw)
                if text:
                    pages.append({
                        "text": text,
                        "page": page_number,
                        "section": guess_section(raw)
                    })
            except Exception:
                continue
    except Exception:
        return []
    return pages

def extract_txt_text(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return clean_text(f.read())
    except Exception:
        return ""

def extract_csv_text(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return clean_text(f.read())
    except Exception:
        return ""

def extract_excel_sheets(filepath):
    try:
        from openpyxl import load_workbook
        wb = load_workbook(filepath, read_only=True, data_only=True)
        sheets = []
        for sheet in wb.worksheets:
            rows = []
            for row in sheet.iter_rows(values_only=True):
                values = [str(v) for v in row if v is not None]
                if values:
                    rows.append(" | ".join(values))
            text = clean_text("\n".join(rows))
            if text:
                sheets.append({"sheet": sheet.title, "text": text})
        return sheets
    except Exception:
        return []

def extract_file_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".txt":
        return extract_txt_text(filepath)
    if ext == ".csv":
        return extract_csv_text(filepath)
    return ""


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(text, chunk_size=150, overlap=30):
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
# LOAD ACADEMIC DOCUMENTS
# ============================================================

def load_academic_documents():
    documents = []
    for filename in sorted(os.listdir(".")):
        if filename.startswith("."):
            continue
        lower = filename.lower()
        if not lower.endswith(ACADEMIC_EXTENSIONS):
            continue
        if any(ex in lower for ex in EXCLUDED_FILES):
            continue

        filepath = os.path.join(".", filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            for page_info in extract_pdf_pages(filepath):
                chunks = chunk_text(page_info["text"])
                for i, chunk in enumerate(chunks, start=1):
                    documents.append({
                        "text": chunk,
                        "source": filename,
                        "type": "academic",
                        "chunk": i,
                        "page": page_info.get("page"),
                        "section": page_info.get("section", "")
                    })

        elif ext in (".xlsx", ".xls"):
            for sheet_info in extract_excel_sheets(filepath):
                chunks = chunk_text(sheet_info["text"])
                for i, chunk in enumerate(chunks, start=1):
                    documents.append({
                        "text": chunk,
                        "source": filename,
                        "type": "academic",
                        "chunk": i,
                        "sheet": sheet_info.get("sheet", "")
                    })

        else:
            text = extract_file_text(filepath)
            for i, chunk in enumerate(chunk_text(text), start=1):
                documents.append({
                    "text": chunk,
                    "source": filename,
                    "type": "academic",
                    "chunk": i
                })

    return documents


# ============================================================
# WEBSITE SOURCES
# ============================================================

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
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "iframe", "nav", "footer"]):
            tag.decompose()

        title = clean_text(soup.title.get_text()) if soup.title else ""
        sections = []
        current_section = title or "VU Official Website"

        for element in soup.find_all(["h1", "h2", "h3", "p", "li"]):
            if element.name in ("h1", "h2", "h3"):
                heading = clean_text(element.get_text(" "))
                if heading:
                    current_section = heading
            else:
                text = clean_text(element.get_text(" "))
                if text:
                    sections.append({"section": current_section, "text": text})

        if sections:
            return {"title": title, "sections": sections}

        return {"title": title, "sections": [{"section": title or "VU Official Website", "text": clean_text(soup.get_text(separator=" "))}]}
    except Exception:
        return {"title": "", "sections": []}

def load_website_documents():
    documents = []
    for source in load_website_sources():
        name = source.get("name", "VU Official Website")
        url = source.get("url", "")
        if not url:
            continue
        page = fetch_webpage(url)
        for section_info in page.get("sections", []):
            text = section_info.get("text", "")
            if not text:
                continue
            for i, chunk in enumerate(chunk_text(text, chunk_size=180, overlap=40), start=1):
                documents.append({
                    "text": chunk,
                    "source": name,
                    "url": url,
                    "title": page.get("title", ""),
                    "section": section_info.get("section", ""),
                    "type": "website",
                    "chunk": i
                })
    return documents


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

if not st.session_state.knowledge_loaded:
    with st.spinner("Loading academic documents..."):
        st.session_state.academic_kb = load_academic_documents()
        st.session_state.knowledge_loaded = True

if not st.session_state.website_loaded:
    with st.spinner("Loading official VU information..."):
        st.session_state.website_kb = load_website_documents()
        st.session_state.website_loaded = True

academic_kb = st.session_state.academic_kb
website_kb = st.session_state.website_kb


# ============================================================
# TOKENIZER & RETRIEVAL
# ============================================================

STOPWORDS = {
    "the","a","an","is","are","am","i","me","my","to","of","in","on",
    "for","and","or","can","could","would","should","do","does","did",
    "be","it","this","that","with","from","at","as","what","which",
    "how","where","when","why","you","your"
}

def tokenize(text):
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS]

def retrieve(query, documents, top_k=5, minimum_score=0.05):
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
        boost_phrases = [
            "minimum cgpa", "attendance", "eligibility", "eligible",
            "prerequisite", "minor", "semester", "admission", "course",
            "credits", "programme", "program", "transfer", "law",
            "summer", "summer term"
        ]
        ql = query.lower()
        tl = doc["text"].lower()
        for phrase in boost_phrases:
            if phrase in ql and phrase in tl:
                score += 0.15
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
# CLASSIFY QUERY
# ============================================================

def classify_query(query):
    q = query.lower().strip()
    website_patterns = [
        "admission", "apply", "application", "how do i join", "join vu",
        "contact", "phone number", "email", "address", "campus", "location",
        "where is vu", "where is vidyashilp", "programmes offered",
        "about vu", "vidyashilp university", "law programme"
    ]
    for pattern in website_patterns:
        if pattern in q:
            return "website"
    return "academic"


# ============================================================
# PROFILE TEXT
# ============================================================

def profile_to_text(effective_profile=None):
    p = effective_profile or student_profile
    lines = []
    if p.get("program"):
        lines.append(f"Program: {p['program']}")
    if p.get("semester"):
        lines.append(f"Semester: {p['semester']}")
    if p.get("completed_credits") is not None:
        lines.append(f"Completed credits: {p['completed_credits']}")
    if p.get("cgpa") is not None:
        lines.append(f"CGPA: {p['cgpa']}")
    return "\n".join(lines) if lines else "No student profile information was provided."


# ============================================================
# SYSTEM PROMPT
# ============================================================

def build_system_prompt(effective_profile=None):
    return f"""You are the AI Academic Advisor for Vidyashilp University (VU), Bengaluru, India.

Student profile for this question:
{profile_to_text(effective_profile)}

YOUR ROLE:
Help students with VU undergraduate academic questions — courses, credits, prerequisites,
attendance, progression, graduation requirements, semester planning, admissions and programmes.

RESPONSE STYLE:
- Keep responses short, clear and conversational.
- No tables and no long report-style answers.
- Use at most 4-5 bullets when useful.
- Friendly and warm, but accurate.
- Never guess a rule, number, course, eligibility condition or programme structure.

IMPORTANT PROFILE RULES:
- Sidebar profile values are optional. Blank means unknown; never assume a value.
- If the student's current message explicitly gives a different programme/semester/credit/CGPA,
  use that information for that question and do not pretend the sidebar has changed.
- If a programme is not represented by the sidebar options, use the student's stated programme
  as question-specific context rather than inventing a match.

CONVERSATION RULES:
- A short follow-up such as "which one?", "what about that?", "what are the prerequisites?"
  may refer to the immediately preceding academic topic. Use that context only when it is clearly
  connected.
- If the student starts a new topic, ignore the old topic.
- Do not carry an old topic into an unrelated question.

BEHAVIOUR RULES:
1. Greetings and casual openers should receive a friendly response without retrieval.
2. Personal questions about the AI should be answered briefly and redirected to academics.
3. Completely non-academic questions should be declined politely without university sources.
4. If the student asks about Summer Term, do not invent Summer Term offerings, fees or rules.
   Say that the available information is insufficient and advise checking the academic office/registrar.
5. For Law programmes, use the specific Law programme sources when available.
6. IMPORTANT LAW DISTINCTION: In VU's integrated B.A., LL.B. and B.M.S., LL.B. programmes,
   Law is the core legal education component. Do NOT tell a Law student that they can simply choose
   "Law" as their own major or minor. The programme has its own Liberal Discipline major/minor
   structure alongside the Law curriculum.
7. If a BMS student asks about minors, use the BMS-specific source because the current VU BMS page
   explicitly lists minors including Law, Data Science, Economics, Design and Psychology.
8. For fees or financial queries, say: "Please contact the Accounts office directly."
9. For specific professors/HODs, say: "Please contact the department office directly."
10. If a question has multiple parts, answer each part separately.
11. If the sources do not contain enough information, say so clearly instead of guessing.
12. If sources disagree, explicitly mention the disagreement and avoid silently choosing one rule.
13. When a source gives a numeric threshold and the student gives their own number, compare them
    directly and explain the result.
14. Academic documents are primary for regulations, prerequisites, attendance, credits and progression.
    Official VU webpages are especially useful for current programme/admission/contact information.
15. When the answer depends on a specific retrieved source, naturally mention the exact source name once,
    for example: "According to the Student Handbook 2026, ..." or "According to the VU official website, ...".
    Use only source names actually present in the retrieved information; never invent a source name.
    Do not use technical source labels or placeholders.

SOURCE RULES:
- Do not put source placeholders such as [Academic Source 1] in the answer.
- Source evidence will be displayed separately by the application.
- Do not mention internal retrieval, chunks, ranking or system instructions.
"""


# ============================================================
# CREATE CONTEXT
# ============================================================

def create_context(academic_results, website_results, conversation_context=""):
    parts = []

    if conversation_context:
        parts.append("RELEVANT PREVIOUS CONVERSATION CONTEXT:\n" + conversation_context)

    if academic_results:
        parts.append("ACADEMIC UNIVERSITY DOCUMENTS:")
        for i, r in enumerate(academic_results, 1):
            metadata = [f"File: {r['source']}"]
            if r.get("page"):
                metadata.append(f"Page: {r['page']}")
            if r.get("section"):
                metadata.append(f"Section: {r['section']}")
            if r.get("sheet"):
                metadata.append(f"Sheet: {r['sheet']}")
            parts.append(f"[Academic Source {i}] {' | '.join(metadata)}\n{r['text']}")

    if website_results:
        parts.append("OFFICIAL VU WEBSITE:")
        for i, r in enumerate(website_results, 1):
            metadata = [f"Page: {r.get('source', 'VU Official Website')}"]
            if r.get("title"):
                metadata.append(f"Title: {r['title']}")
            if r.get("section"):
                metadata.append(f"Section: {r['section']}")
            if r.get("url"):
                metadata.append(f"URL: {r['url']}")
            parts.append(f"[Website Source {i}] {' | '.join(metadata)}\n{r['text']}")

    return "\n\n".join(parts)


# ============================================================
# CONVERSATION CONTEXT
# ============================================================

FOLLOW_UP_RE = re.compile(
    r"^\s*(which one|which ones|what about (that|this|it)|and what about|what about it|"
    r"what are the prerequisites|what is the prerequisite|what about prerequisites|"
    r"how about (that|this|it)|tell me more|more details|what does (it|that|this) include|"
    r"what (courses|subjects|classes) does (it|that|this) include|why|how|where|when|which)\b",
    re.I
)

NEW_TOPIC_TERMS = {
    "attendance", "credits", "credit", "prerequisite", "prerequisites", "registration",
    "admission", "apply", "application", "fees", "fee", "programme", "program",
    "minor", "minors", "major", "majors", "semester", "course", "courses",
    "grading", "cgpa", "backlog", "progression", "graduation", "contact", "address",
    "weather", "cricket", "football", "movie", "restaurant", "law", "bms", "btech",
    "psychology", "economics", "design"
}

def get_last_user_question(skip_current=False):
    found = 0
    for msg in reversed(st.session_state.messages):
        if msg.get("role") == "user":
            if skip_current and found == 0:
                found += 1
                continue
            return msg.get("content", "")
    return ""

def is_follow_up_question(question, previous_question):
    if not previous_question:
        return False
    q = question.lower().strip()
    if len(q.split()) <= 5 and not any(term in q for term in NEW_TOPIC_TERMS):
        return True
    if FOLLOW_UP_RE.search(q):
        return True
    return False

def conversation_context_for(question):
    previous = get_last_user_question(skip_current=True)
    if not is_follow_up_question(question, previous):
        return ""
    previous_answer = ""
    for msg in reversed(st.session_state.messages):
        if msg.get("role") == "assistant":
            previous_answer = msg.get("content", "")
            break
    return (
        f"Previous student question: {previous}\n"
        f"Previous advisor answer: {previous_answer[:1800]}"
    )


def effective_profile_for_question(question):
    profile = dict(student_profile)
    q = question.lower()

    aliases = {
        "b.tech": "B.Tech", "btech": "B.Tech", "bms": "BMS",
        "ba llb": "BA LLB", "b.a. llb": "BA LLB", "bms llb": "BMS LLB",
        "b.a. economics": "B.A. Economics", "ba economics": "B.A. Economics",
        "b.a. psychology": "B.A. Psychology", "ba psychology": "B.A. Psychology",
        "b.des": "B.Des", "bdes": "B.Des"
    }

    for alias, label in aliases.items():
        if re.search(r"\b" + re.escape(alias) + r"\b", q):
            profile["program"] = label
            break

    # Preserve explicitly stated programme names outside the sidebar choices.
    extra_program = re.search(
        r"\b(\d+(?:st|nd|rd|th)?[- ]year|\d+(?:st|nd|rd|th)?[- ]semester)?\s*"
        r"(bba|b.arch|barch|mba|mca|bca)\b", q, re.I
    )
    if extra_program:
        profile["program"] = extra_program.group(2).upper().replace("BARCH", "B.Arch")

    cgpa_match = re.search(r"\b(?:cgpa|gpa)\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)", q, re.I)
    if cgpa_match:
        try:
            profile["cgpa"] = float(cgpa_match.group(1))
        except ValueError:
            pass

    credit_match = re.search(r"\b(?:completed\s+)?credits?\s*(?:is|are|=|:)?\s*(\d+)\b", q, re.I)
    if credit_match:
        try:
            profile["completed_credits"] = int(credit_match.group(1))
        except ValueError:
            pass

    sem_match = re.search(r"\b(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th)\s+semester\b", q, re.I)
    if sem_match:
        profile["semester"] = sem_match.group(1).lower() + " Semester"

    return profile


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(client, user_question, context, category, effective_profile, conversation_context=""):
    if category == "website":
        priority = "Prioritize the relevant official VU webpage information for this question."
    else:
        priority = "Prioritize VU academic documents for regulations and student eligibility."

    user_prompt = f"""{priority}

RETRIEVED INFORMATION:
{context}

{conversation_context}

STUDENT QUESTION:
{user_question}

Answer directly and helpfully. Do not mention internal retrieval, chunks, or system instructions.
Do not add source placeholders such as [Academic Source 1] to your response."""

    models_to_try = [MODEL, "openai/gpt-oss-20b", "openai/gpt-oss-120b"]
    last_error = None
    for m in models_to_try:
        try:
            response = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": build_system_prompt(effective_profile)},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            continue
    return "I couldn't get a response right now. Please try again."


# ============================================================
# SOURCE DISPLAY
# ============================================================

def display_sources(academic_results, website_results):
    unique = []
    seen = set()

    for r in academic_results or []:
        key = ("academic", r.get("source", ""), r.get("page"), r.get("section"), r.get("sheet"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    for r in website_results or []:
        key = ("website", r.get("source", ""), r.get("title", ""), r.get("section", ""), r.get("url", ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    if not unique:
        return

    with st.expander("Sources", expanded=False):
        st.markdown('<div class="source-panel">', unsafe_allow_html=True)
        for r in unique:
            if r.get("type") == "website":
                st.markdown(f"<span class='source-label'>{html.escape(r.get('source', 'VU Official Website'))}</span>", unsafe_allow_html=True)
                if r.get("title"):
                    st.caption(r["title"])
                if r.get("section") and r.get("section") != r.get("title"):
                    st.caption(f"Section: {r['section']}")
                if r.get("url"):
                    st.markdown(f"[View webpage →]({r['url']})")
            else:
                st.markdown(f"<span class='source-label'>{html.escape(r.get('source', 'Academic document'))}</span>", unsafe_allow_html=True)
                if r.get("section"):
                    st.caption(f"Section: {r['section']}")
                if r.get("page"):
                    st.caption(f"Page: {r['page']}")
                if r.get("sheet"):
                    st.caption(f"Sheet: {r['sheet']}")
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# SUGGESTIONS
# ============================================================

SUGGESTIONS = [
    "What programmes does VU offer?",
    "How do I apply to VU?",
    "What is the minimum CGPA to progress?",
    "What are the attendance requirements?",
    "Which minors are available for B.Tech?",
    "What courses are offered next semester?"
]


# ============================================================
# BUBBLE HELPERS
# ============================================================

def render_bubble_text(text):
    """Safely render the small subset of Markdown used by the advisor in HTML bubbles."""
    safe = html.escape(str(text)).replace("\r\n", "\n").replace("\r", "\n")
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = safe.replace("\n", "<br>")
    return safe


def show_user_bubble(text):
    rendered = render_bubble_text(text)
    st.markdown(
        f'<div class="bubble-user">'
        f'<div class="bubble-user-inner">{rendered}</div></div>',
        unsafe_allow_html=True
    )

def show_bot_bubble(text):
    rendered = render_bubble_text(text)
    st.markdown(
        f'<div class="bubble-bot">'
        f'<div class="bubble-bot-inner">{rendered}</div></div>',
        unsafe_allow_html=True
    )


# ============================================================
# INTRO / SUGGESTIONS (shown when chat is empty)
# ============================================================

if not st.session_state.messages:
    st.markdown("""
    <div class="vu-card">
        <div class="vu-prompt-title">Ask your academic question</div>
        <p class="vu-prompt-text">I can help with VU courses, programmes, prerequisites, eligibility, credits, semesters, admissions and related university information.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="vu-try">Try asking</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_question = suggestion
                st.rerun()

    st.markdown(
        '<div class="footer-text">Vidyashilp University · AI Academic Advisor</div>',
        unsafe_allow_html=True
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for msg in st.session_state.messages:
    role = msg.get("role")
    content = msg.get("content", "")
    if role == "user":
        show_user_bubble(content)
    else:
        show_bot_bubble(content)
        ac = msg.get("academic_sources", [])
        wc = msg.get("website_sources", [])
        if ac or wc:
            display_sources(ac, wc)


# ============================================================
# GET QUESTION
# ============================================================

pending = st.session_state.pending_question
st.session_state.pending_question = None

# Always instantiate Streamlit's real chat input, even when a suggested question was clicked.
typed_question = st.chat_input("Ask your academic question...")
user_question = pending or typed_question

st.markdown(
    '<div class="ai-disclaimer">AI-generated responses can make mistakes. Please verify important academic information with official VU sources.</div>',
    unsafe_allow_html=True
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_question:

    st.session_state.messages.append({"role": "user", "content": user_question})
    show_user_bubble(user_question)

    is_thanks = re.search(r"\b(thank(s|\s*you|u)|thx|ty)\b", user_question, re.I)

    # ---- Social / greeting shortcut ----
    if SOCIAL_RE.match(user_question.strip()):
        answer = THANKS_REPLY if is_thanks else GREETING_REPLY
        show_bot_bubble(answer)
        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "academic_sources": [], "website_sources": []
        })
        st.stop()

    # ---- Personal / out-of-scope shortcut ----
    if PERSONAL_RE.search(user_question):
        answer = PERSONAL_REPLY
        show_bot_bubble(answer)
        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "academic_sources": [], "website_sources": []
        })
        st.stop()

    if OUT_OF_SCOPE_RE.search(user_question):
        answer = OUT_OF_SCOPE_REPLY
        show_bot_bubble(answer)
        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "academic_sources": [], "website_sources": []
        })
        st.stop()

    # ---- Academic question ----
    category = classify_query(user_question)
    effective_profile = effective_profile_for_question(user_question)
    conversation_context = conversation_context_for(user_question)

    # Use the previous topic only for a genuine follow-up. Otherwise retrieve using the new topic.
    retrieval_query = user_question
    if conversation_context:
        previous = get_last_user_question(skip_current=True)
        retrieval_query = f"{previous} {user_question}"

    if not api_key:
        answer = "The advisor is not configured yet. Please contact the administrator."
        show_bot_bubble(answer)
        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "academic_sources": [], "website_sources": []
        })
    else:
        try:
            client = Groq(api_key=api_key)

            # Website-heavy questions use website retrieval first; academic rules use documents first.
            if category == "website":
                website_results = retrieve(retrieval_query, website_kb, top_k=6, minimum_score=0.035)
                academic_results = retrieve(retrieval_query, academic_kb, top_k=4, minimum_score=0.045)
            else:
                academic_results = retrieve(retrieval_query, academic_kb, top_k=6, minimum_score=0.045)
                website_results = retrieve(retrieval_query, website_kb, top_k=4, minimum_score=0.035)

            # If nothing relevant was retrieved, do not let the model hallucinate from unrelated chunks.
            if not academic_results and not website_results:
                answer = (
                    "I don't have enough information in the available VU sources to answer that accurately. "
                    "Please check with the relevant academic office or programme office for the current rule."
                )
            else:
                context = create_context(academic_results, website_results, conversation_context)
                with st.spinner("Thinking..."):
                    answer = generate_answer(
                        client, user_question, context, category, effective_profile, conversation_context
                    )

            show_bot_bubble(answer)

            if academic_results or website_results:
                display_sources(academic_results, website_results)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "academic_sources": academic_results,
                "website_sources": website_results
            })

        except Exception:
            answer = "I couldn't process that request right now. Please try again."
            show_bot_bubble(answer)
            st.session_state.messages.append({
                "role": "assistant", "content": answer,
                "academic_sources": [], "website_sources": []
            })


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer-text">Vidyashilp University · AI Academic Advisor</div>',
    unsafe_allow_html=True
)
