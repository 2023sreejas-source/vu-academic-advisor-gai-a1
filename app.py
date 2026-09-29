# ============================================================
# VU AI ACADEMIC ADVISOR — Vidyashilp University
# ============================================================

import streamlit as st
from groq import Groq
from pypdf import PdfReader

import os
import re
import math
import json
import requests
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

/* Force Font & App Background */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp, [data-testid="stAppViewContainer"], [data-testid="block-container"] {
    background-color: #f0f2f5 !important;
    color: #1a1a2e !important;
}

/* Force All Global Headers & Body Text to Dark Navy/Charcoal */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
.stApp p, .stApp span, .stApp label, .stApp div,
[data-testid="stMarkdownContainer"] *,
.stMarkdown * {
    color: #1a1a2e !important;
}

/* Sidebar Styling & Text Visibility */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

[data-testid="stSidebar"] *,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
    color: #0a2240 !important;
}

/* Form Controls & Dropdown Inputs Text Visibility */
[data-testid="stWidgetLabel"] *, [data-testid="stWidgetLabel"] p {
    color: #0a2240 !important;
    font-weight: 600 !important;
}

div[data-baseweb="select"] *, 
div[data-baseweb="input"] *,
input, textarea {
    color: #1a1a2e !important;
    background-color: #ffffff !important;
}

/* Welcome Info Box Fix */
.info-box {
    background-color: #ffffff !important;
    padding: 18px 20px !important;
    border-radius: 12px !important;
    border-left: 5px solid #c0182a !important;
    margin-bottom: 20px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

.info-box h3, .info-box h3 * {
    color: #0a2240 !important;
    font-weight: 700 !important;
    margin-top: 0 !important;
    margin-bottom: 6px !important;
}

.info-box p, .info-box p * {
    color: #4a5568 !important;
    margin: 0 !important;
    font-size: 14px !important;
}

/* FAQ Buttons */
div[data-testid="stButton"] > button {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    padding: 10px 14px !important;
}

div[data-testid="stButton"] > button * {
    color: #0a2240 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}

div[data-testid="stButton"] > button:hover {
    border-color: #c0182a !important;
    background-color: #fff0f1 !important;
}

/* Bottom Chat Input Bar */
[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background-color: #ffffff !important;
    border-top: 1px solid #e2e8f0 !important;
}

[data-testid="stChatInputContainer"] {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 24px !important;
}

[data-testid="stChatInputContainer"] textarea {
    color: #1a1a2e !important;
    background: transparent !important;
}

/* Custom Chat Bubbles */
.bubble-user {
    display: flex;
    justify-content: flex-end;
    margin: 8px 0;
}
.bubble-user-inner {
    background: linear-gradient(135deg, #c0182a 0%, #0a2240 100%);
    color: #ffffff !important;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    max-width: 70%;
    font-size: 14px;
    line-height: 1.55;
    box-shadow: 0 2px 8px rgba(192,24,42,0.18);
    word-wrap: break-word;
}
.bubble-user-inner * {
    color: #ffffff !important;
}

.bubble-bot {
    display: flex;
    justify-content: flex-start;
    margin: 8px 0;
}
.bubble-bot-inner {
    background: #ffffff;
    color: #1a1a2e !important;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    max-width: 75%;
    font-size: 14px;
    line-height: 1.65;
    box-shadow: 0 1px 5px rgba(0,0,0,0.08);
    word-wrap: break-word;
}
.bubble-bot-inner * {
    color: #1a1a2e !important;
}

.footer-text {
    text-align: center;
    color: #8898aa !important;
    font-size: 11px;
    padding-top: 20px;
}

#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# ACTIVE GROQ MODELS & CONSTANTS
# ============================================================

# Strictly active Groq models (decommissioned models like mixtral-8x7b-32768 removed)
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]

ACADEMIC_EXTENSIONS = (".pdf", ".txt", ".csv", ".xlsx", ".xls")
EXCLUDED_FILES = ("advisor_eval", "eval_results", "phase4", "summary_metrics", "website_sources")

DEFAULT_WEBSITE_SOURCES = [
    {"name": "VU Official Website", "url": "https://vidyashilp.edu.in/"},
    {"name": "VU Admissions", "url": "https://vidyashilp.edu.in/admissions/"},
    {"name": "VU Contact", "url": "https://vidyashilp.edu.in/contact/"},
    {"name": "VU Data Science", "url": "https://vidyashilp.edu.in/data-science/"},
    {"name": "VU AI and Machine Learning", "url": "https://vidyashilp.edu.in/schools/b_tech_ai_ml/"},
    {"name": "VU B.Tech", "url": "https://vidyashilp.edu.in/btech/"},
    {"name": "VU About", "url": "https://vidyashilp.edu.in/about/"},
    {"name": "VU Law", "url": "https://vidyashilp.edu.in/law/"},
    {"name": "VU PhD", "url": "https://vidyashilp.edu.in/phd/"},
    {"name": "VU Programmes", "url": "https://vidyashilp.edu.in/programmes/"}
]

GREETING_PATTERNS = re.compile(
    r"^\s*(h+i+|h+e+l+o+|hey+|hola|yo+|sup|bro|wsp|wsup|wassup|bonjour|namaste|namaskaram|halo|howdy|"
    r"good\s*(morning|afternoon|evening|night|day)|"
    r"how\s*are\s*you|how\s*r\s*u|how\s*do\s*you\s*do|what'?s\s*up)\s*[!.?]*\s*$",
    re.I
)

THANKS_PATTERNS = re.compile(
    r"^\s*(thank(s|\s*you|\s*u)?|thx|ty|ok(ay)?|got\s*it|sure|great|nice|cool|bye|goodbye|cya)\s*[!.?]*\s*$",
    re.I
)

GREETING_REPLY = (
    "Hello! I am Vidyashilp University's AI Academic Advisor. "
    "I can assist you with attendance rules, credit requirements, prerequisites, registration, "
    "course eligibility, and general academic regulations. "
    "How can I help you today?"
)

THANKS_REPLY = "You're very welcome! Feel free to ask if you have any more academic questions."


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
# HEADER & LOGO
# ============================================================

def find_logo():
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

logo_path = find_logo()

header_col1, header_col2 = st.columns([1, 7], vertical_alignment="center")

with header_col1:
    if logo_path:
        st.image(logo_path, width=90)

with header_col2:
    st.markdown("## Vidyashilp University")
    st.markdown("**AI Academic Advisor · Online**")

st.divider()


# ============================================================
# SIDEBAR (OPTIONAL DEFAULTS)
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

    last_error = None
    for model in GROQ_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=650
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            continue
    return f"I am unable to answer right now due to a network connection issue. Please try again shortly. (Error: {last_error})"


# ============================================================
# UI HELPERS
# ============================================================

def display_sources(academic_results):
    names = list({r["source"] for r in academic_results if "source" in r})
    if names:
        st.caption("📄 **Sources:** " + " · ".join(names))

def show_user_bubble(text):
    st.markdown(
        f'<div class="bubble-user"><div class="bubble-user-inner">{text}</div></div>',
        unsafe_allow_html=True
    )

def show_bot_bubble(text):
    st.markdown(
        f'<div class="bubble-bot"><div class="bubble-bot-inner">{text}</div></div>',
        unsafe_allow_html=True
    )


# ============================================================
# FAQ SUGGESTIONS & CHAT HISTORY
# ============================================================

SUGGESTIONS = [
    "What programmes does VU offer?",
    "How do I apply for admission?",
    "What is the minimum CGPA requirement?",
    "What are the attendance regulations?",
    "Which minor courses are available?",
    "How are credits calculated?"
]

if not st.session_state.messages:
    st.markdown("""
    <div class="info-box">
    <h3>Welcome! Ask your academic questions below</h3>
    <p>I can assist with course regulations, credit transfers, attendance rules, prerequisites, and general university information.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💡 Frequently Asked Questions")
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

    # 1. Direct Regex Small Talk / Greetings
    if GREETING_PATTERNS.match(q_clean):
        show_bot_bubble(GREETING_REPLY)
        st.session_state.messages.append({
            "role": "assistant", "content": GREETING_REPLY,
            "academic_sources": [], "website_sources": []
        })
        st.stop()

    if THANKS_PATTERNS.match(q_clean):
        show_bot_bubble(THANKS_REPLY)
        st.session_state.messages.append({
            "role": "assistant", "content": THANKS_REPLY,
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
