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

APP_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# DYNAMIC BACKGROUND & LOGO SETUP
# ============================================================

bg_path = None
for f in ["campus.jpg", "campus.png", "Vidyashilp.jpg", "vu_campus.jpg"]:
    p = os.path.join(APP_DIR, f)
    if os.path.isfile(p):
        bg_path = p
        break

bg_css = ""
if bg_path:
    with open(bg_path, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode("utf-8")
        ext = bg_path.split('.')[-1]
        bg_css = f"""
        <style>
        .stApp, [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(248, 250, 252, 0.90), rgba(248, 250, 252, 0.95)), url(data:image/{ext};base64,{bg_b64}) !important;
            background-size: cover !important;
            background-position: center center !important;
            background-attachment: fixed !important;
        }}
        </style>
        """
else:
    bg_css = """
    <style>
    .stApp, [data-testid="stAppViewContainer"] { background: #F8FAFC !important; }
    </style>
    """

logo_path = os.path.join(APP_DIR, "Logo.png")
if not os.path.isfile(logo_path):
    logo_path = os.path.join(APP_DIR, "logo.png")

logo_html = ""
if os.path.isfile(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 48px; width: auto; object-fit: contain;" alt="VU Logo" />'


# ============================================================
# CSS (UNIFIED VU BRANDING & FORCED LIGHT THEME OVERRIDES)
# ============================================================

st.markdown(bg_css, unsafe_allow_html=True)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="block-container"] { padding-top: 2rem !important; }

/* ========================= SIDEBAR ========================= */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
    background: #0B5394 !important;
}
[data-testid="stSidebar"] * { 
    color: #FFFFFF !important; 
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #E2E8F0 !important;
    font-size: 13px;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.18) !important;
    margin: 16px 0 !important;
}

/* Sidebar Selectboxes & Number Inputs */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] div[data-baseweb="input"] {
    background: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] input {
    background: transparent !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] input::placeholder {
    color: #E2E8F0 !important;
    opacity: 0.8 !important;
}

/* Clear Chat Button */
[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    font-weight: 500 !important;
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.2) !important;
    border-color: #FFFFFF !important;
}

.vu-sidebar-group-divider {
    height: 1px;
    background: rgba(255,255,255,0.18);
    margin: 16px 0;
}

/* ========================= HEADER & CARDS ========================= */
.vu-header-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(15,23,42,0.04);
    display: flex;
    align-items: center;
    gap: 20px;
}
.vu-header-info {
    display: flex;
    flex-direction: column;
}
.vu-sub-title {
    color: #64748B;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.vu-heading {
    color: #0B5394;
    font-size: 24px;
    line-height: 1.2;
    font-weight: 700;
    margin: 0;
}
.vu-status {
    color: #64748B;
    font-size: 13px;
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.vu-status-dot { 
    color: #22C55E; 
    font-size: 10px; 
}

.vu-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(15,23,42,0.03);
}
.vu-prompt-title {
    color: #0F172A;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 6px;
}
.vu-prompt-text {
    color: #475569;
    font-size: 14px;
    line-height: 1.5;
    margin: 0;
}
.vu-try {
    color: #334155;
    font-size: 13px;
    font-weight: 600;
    margin: 16px 0 10px;
}

/* Light Suggestion Buttons */
main div[data-testid="stButton"] > button {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    color: #0B5394 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    min-height: 48px !important;
    box-shadow: 0 1px 2px rgba(15,23,42,0.03) !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
}
main div[data-testid="stButton"] > button:hover {
    background: #F0F9FF !important;
    border-color: #0B5394 !important;
    color: #0B5394 !important;
    transform: translateY(-1px);
}
main div[data-testid="stButton"] > button * {
    color: #0B5394 !important;
}

/* ========================= CHAT BUBBLES ========================= */
.bubble-user { 
    display: flex; 
    justify-content: flex-end; 
    margin: 12px 0; 
}
.bubble-user-inner {
    background: #0B5394; 
    color: #FFFFFF;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 18px; 
    max-width: 72%;
    font-size: 14px; 
    line-height: 1.6;
    box-shadow: 0 2px 4px rgba(11,83,148,0.12);
}
.bubble-bot { 
    display: flex; 
    justify-content: flex-start; 
    margin: 12px 0; 
}
.bubble-bot-inner {
    background: #FFFFFF; 
    color: #1E293B;
    border: 1px solid #E2E8F0;
    border-radius: 16px 16px 16px 4px;
    padding: 14px 20px; 
    max-width: 80%;
    font-size: 14.5px; 
    line-height: 1.65;
    box-shadow: 0 2px 6px rgba(15,23,42,0.03);
}

[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    margin-top: 6px !important;
}
[data-testid="stExpander"] summary { color: #64748B !important; font-size: 12px !important; }

/* Dynamic Floating Composer */
[data-testid="stBottom"] {
    background: transparent !important;
    border-top: none !important;
    padding: 10px 0 16px !important;
}
[data-testid="stChatInputContainer"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 16px rgba(15,23,42,0.08) !important;
}
[data-testid="stChatInputContainer"] > div {
    background: transparent !important;
    border: none !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: #0F172A !important;
    caret-color: #0B5394 !important;
    background-color: #FFFFFF !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}
[data-testid="stChatInputContainer"] button {
    color: #FFFFFF !important;
    background: #0B5394 !important;
    border-radius: 8px !important;
}

.ai-disclaimer {
    position: fixed; left: 0; right: 0; bottom: 2px;
    z-index: 999999; text-align: center;
    color: #64748B; font-size: 10.5px; pointer-events: none;
}
.footer-text {
    text-align: center; color: #64748B;
    font-size: 12px; padding: 12px 0 24px;
}
#MainMenu, footer { visibility: hidden; }

@media (max-width: 900px) {
    .vu-header-card { flex-direction: column; align-items: flex-start; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CONSTANTS & REGEXES
# ============================================================

# Model fallback chain in case one model is unavailable on the API key
MODEL_CANDIDATES = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192"
]

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
    r"how\s*are\s*(you|u)|how\s*r\s*u|how\s*do\s*you\s*do|how'?s\s*it\s*going|"
    r"thank(s|\s*you|u)|thx|ty|ok(ay)?|got\s*it|sure|great|nice|cool|"
    r"bye|goodbye|see\s*you|take\s*care|cya|bonjour)\s*[!.?]*\s*$",
    re.I
)

GREETING_REPLY = (
    "I'm doing well, thank you! 😊 I'm VU's AI Academic Advisor. "
    "I can help with attendance, credits, prerequisites, registration, "
    "course eligibility, progression rules and more. "
    "What would you like to know today?"
)

THANKS_REPLY = "Happy to help! Feel free to ask anything else about your academics at VU."

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
    "academic and programme-related questions, but not that topic."
)

PERSONAL_REPLY = (
    "I’m an AI academic advisor, so I don’t have a personal family or personal life. "
    "But I can definitely help with your VU academic questions."
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
# HEADER
# ============================================================

st.markdown(
    f'''
    <div class="vu-header-card">
        {logo_html}
        <div class="vu-header-info">
            <div class="vu-sub-title">Vidyashilp University</div>
            <div class="vu-heading">AI Academic Advisor</div>
            <div class="vu-status"><span class="vu-status-dot">●</span> Online · Student Assistant</div>
        </div>
    </div>
    ''',
    unsafe_allow_html=True
)


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

    st.markdown('<div class="vu-sidebar-group-divider"></div>', unsafe_allow_html=True)

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
# STUDENT PROFILE & DYNAMIC OVERRIDES
# ============================================================

student_profile = {
    "program": program,
    "semester": semester,
    "completed_credits": completed_credits,
    "cgpa": cgpa
}

def effective_profile_for_question(user_query, sidebar_profile):
    effective = dict(sidebar_profile)
    q_lower = user_query.lower()
    
    prog_map = {
        "b.tech": "B.Tech", "btech": "B.Tech", 
        "bms": "BMS", "b.m.s": "BMS",
        "ba llb": "BA LLB", "ba.llb": "BA LLB", 
        "bms llb": "BMS LLB", "bms.llb": "BMS LLB",
        "economics": "B.A. Economics", "psychology": "B.A. Psychology",
        "b.des": "B.Des", "bdes": "B.Des"
    }
    for key, val in prog_map.items():
        if key in q_lower:
            effective["program"] = val
            break

    sem_match = re.search(r"\b([1-9]|10)(?:st|nd|rd|th)?\s*(?:sem|semester)\b", q_lower)
    if sem_match:
        num = sem_match.group(1)
        suffix = {"1": "1st", "2": "2nd", "3": "3rd"}.get(num, f"{num}th")
        effective["semester"] = f"{suffix} Semester"

    cgpa_match = re.search(r"\b(?:cgpa|gpa)\s*(?:of|=|:)?\s*([0-9]\.[0-9]{1,2})\b", q_lower)
    if cgpa_match:
        try:
            effective["cgpa"] = float(cgpa_match.group(1))
        except ValueError:
            pass

    cred_match = re.search(r"\b([0-9]{1,3})\s*(?:completed\s*)?credits?\b", q_lower)
    if cred_match:
        try:
            effective["completed_credits"] = int(cred_match.group(1))
        except ValueError:
            pass

    return effective


# ============================================================
# TEXT EXTRACTION & SECTION HEADING GUESS
# ============================================================

def clean_text(text):
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def guess_section(raw_text):
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
    if not os.path.exists("."):
        return documents

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
        response = requests.get(url, headers=headers, timeout=15)
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
# CLASSIFY QUERY & CONTEXT UTILS
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

def is_follow_up_question(query):
    q = query.lower().strip()
    follow_up_indicators = [
        "what about", "and for", "how about", "which one", "which ones",
        "what are the prerequisites", "are there any prerequisites",
        "tell me more", "can you elaborate", "why", "how so", "is it required"
    ]
    if len(q.split()) <= 6 and any(ind in q for ind in follow_up_indicators):
        return True
    return False

def conversation_context_for(messages):
    if not messages:
        return ""
    recent = messages[-2:]
    formatted = []
    for m in recent:
        role = "Student" if m["role"] == "user" else "Advisor"
        formatted.append(f"{role}: {m['content']}")
    return "\n".join(formatted)


# ============================================================
# PROFILE TEXT & SYSTEM PROMPT
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
  may refer to the immediately preceding academic topic. Use that context only when it is clearly connected.
- If the student starts a new topic, ignore the old topic.
- Do not carry an old topic into an unrelated question.

BEHAVIOUR RULES:
1. Greetings, casual openers, "bonjour", and "how are you" messages should receive a friendly response without retrieval.
2. Personal questions about the AI should be answered briefly and redirected to academics.
3. Completely non-academic questions should be declined politely without university sources.
4. If the student asks about Summer Term, do not invent Summer Term offerings, fees or rules.
   Say that the available information is insufficient and advise checking the academic office/registrar.
5. For Law programmes, use the specific Law programme sources when available.
6. IMPORTANT LAW DISTINCTION: In VU's integrated B.A., LL.B. and B.M.S., LL.B. programmes,
   Law is the core legal education component. Do NOT tell a Law student that they can simply choose
   "Law" as their own major or minor.
7. If a BMS student asks about minors, use the BMS-specific source because the current VU BMS page
   explicitly lists minors including Law, Data Science, Economics, Design and Psychology.
8. For fees or financial queries, say: "Please contact the Accounts office directly."
9. For specific professors/HODs, say: "Please contact the department office directly."
10. If a question has multiple parts, answer each part separately.
11. If the sources do not contain enough information, say so clearly instead of guessing.
12. If sources disagree, explicitly mention the disagreement and avoid silently choosing one rule.
13. When a source gives a numeric threshold and the student gives their own number, compare them directly.
14. Academic documents are primary for regulations, prerequisites, attendance, credits and progression.
15. When the answer depends on a specific retrieved source, naturally mention the exact source name once.

SOURCE RULES:
- Do not put technical source placeholders such as [Academic Source 1] in the answer text.
- Source references will be rendered in a separate source drawer below the chat response.
"""


# ============================================================
# SOURCE DISPLAY DRAWER
# ============================================================

def display_sources(retrieved_docs):
    if not retrieved_docs:
        return
    
    seen = set()
    unique_sources = []
    for doc in retrieved_docs:
        src_name = doc.get("source", "VU Reference Document")
        page = doc.get("page")
        section = doc.get("section", "")
        url = doc.get("url", "")
        doc_type = doc.get("type", "academic")
        
        key = (src_name, page, section, url)
        if key not in seen:
            seen.add(key)
            unique_sources.append({
                "source": src_name,
                "page": page,
                "section": section,
                "url": url,
                "type": doc_type
            })

    if not unique_sources:
        return

    with st.expander("📚 Referenced VU Official Sources"):
        for s in unique_sources:
            if s["type"] == "website" and s["url"]:
                st.markdown(f"- **[{s['source']}]({s['url']})**: {s['section'] or 'Official Page'}")
            else:
                details = []
                if s["page"]:
                    details.append(f"Page {s['page']}")
                if s["section"]:
                    details.append(f"Section: {s['section']}")
                detail_str = f" ({', '.join(details)})" if details else ""
                st.markdown(f"- **{s['source']}**{detail_str}")


# ============================================================
# LLM GENERATION WITH AUTOMATIC FALLBACK
# ============================================================

def generate_response(user_query, effective_profile):
    if not api_key:
        return "⚠️ **Groq API key not found.** Please configure `GROQ_API_KEY` in your environment or `.streamlit/secrets.toml`.", []

    client = Groq(api_key=api_key)

    # 1. Intent pre-filtering
    if SOCIAL_RE.match(user_query):
        if re.search(r"thank(s|\s*you|u)|thx|ty", user_query, re.I):
            return THANKS_REPLY, []
        return GREETING_REPLY, []

    if OUT_OF_SCOPE_RE.search(user_query):
        return OUT_OF_SCOPE_REPLY, []

    if PERSONAL_RE.search(user_query):
        return PERSONAL_REPLY, []

    # 2. Select KB and retrieve
    q_type = classify_query(user_query)
    target_kb = website_kb if q_type == "website" else academic_kb
    if not target_kb:
        target_kb = academic_kb + website_kb

    retrieved = retrieve(user_query, target_kb, top_k=5)
    
    if not retrieved and q_type == "website":
        retrieved = retrieve(user_query, academic_kb, top_k=5)

    # 3. Build Context String
    context_blocks = []
    if is_follow_up_question(user_query):
        conv_ctx = conversation_context_for(st.session_state.messages)
        if conv_ctx:
            context_blocks.append(f"Recent Conversation Context:\n{conv_ctx}")

    for idx, doc in enumerate(retrieved, start=1):
        src_label = doc.get("source", "VU Source")
        p_str = f", Page {doc['page']}" if doc.get("page") else ""
        s_str = f", Section: {doc['section']}" if doc.get("section") else ""
        context_blocks.append(f"[Source {idx}: {src_label}{p_str}{s_str}]\n{doc['text']}")

    kb_context = "\n\n".join(context_blocks) if context_blocks else "No matching VU official documents found."

    messages = [
        {"role": "system", "content": build_system_prompt(effective_profile)},
        {"role": "user", "content": f"Information retrieved from VU databases:\n{kb_context}\n\nStudent question: {user_query}"}
    ]

    # 4. Attempt model loop with automatic fallback
    response = None
    last_error = None

    for model_name in MODEL_CANDIDATES:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2,
                max_tokens=600
            )
            break
        except Exception as e:
            last_error = e
            err_msg = str(e).lower()
            if "model_not_found" in err_msg or "404" in err_msg or "does not exist" in err_msg:
                continue
            else:
                break

    if response:
        return response.choices[0].message.content, retrieved
    else:
        return f"⚠️ An error occurred while communicating with the AI service: {str(last_error)}", []


# ============================================================
# MAIN CHAT INTERFACE
# ============================================================

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="bubble-user"><div class="bubble-user-inner">{html.escape(msg["content"])}</div></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="bubble-bot"><div class="bubble-bot-inner">{msg["content"]}</div></div>',
            unsafe_allow_html=True
        )
        if msg.get("sources"):
            display_sources(msg["sources"])

if not st.session_state.messages:
    st.markdown('''
    <div class="vu-card">
        <div class="vu-prompt-title">Welcome! How can I assist you today?</div>
        <div class="vu-prompt-text">Ask me anything about attendance criteria, course credits, prerequisites, or degree requirements at Vidyashilp University.</div>
        <div class="vu-try">Try asking:</div>
    </div>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("What is the minimum attendance requirement at VU?", use_container_width=True):
            st.session_state.pending_question = "What is the minimum attendance requirement at VU?"
            st.rerun()
        if st.button("How many credits do I need to graduate from B.Tech?", use_container_width=True):
            st.session_state.pending_question = "How many credits do I need to graduate from B.Tech?"
            st.rerun()
    with col2:
        if st.button("What are the prerequisites for AI/ML specialization?", use_container_width=True):
            st.session_state.pending_question = "What are the prerequisites for AI/ML specialization?"
            st.rerun()
        if st.button("Can I choose a minor in BMS programme?", use_container_width=True):
            st.session_state.pending_question = "Can I choose a minor in BMS programme?"
            st.rerun()

user_input = st.chat_input("Type your academic question here...")

if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None

if user_input:
    effective_prof = effective_profile_for_question(user_input, student_profile)

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(
        f'<div class="bubble-user"><div class="bubble-user-inner">{html.escape(user_input)}</div></div>',
        unsafe_allow_html=True
    )

    with st.spinner("Consulting VU academic regulations..."):
        answer, sources = generate_response(user_input, effective_prof)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    st.markdown(
        f'<div class="bubble-bot"><div class="bubble-bot-inner">{answer}</div></div>',
        unsafe_allow_html=True
    )
    if sources:
        display_sources(sources)


# ============================================================
# FOOTER
# ============================================================

st.markdown('<div class="ai-disclaimer">AI-generated responses can occasionally vary. Please verify official policies with the VU Academic Office.</div>', unsafe_allow_html=True)
st.markdown('<div class="footer-text">Vidyashilp University Academic Advisor © 2026</div>', unsafe_allow_html=True)
