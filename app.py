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

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"] {
    background-color: #f0f2f5 !important;
}

[data-testid="stSidebar"] { background-color: #ffffff !important; }

[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background-color: #ffffff !important;
    border-top: 1px solid #eaecf0 !important;
    padding: 10px 16px !important;
}

[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div {
    background: #ffffff !important;
    border: 1.5px solid #dde0e6 !important;
    border-radius: 26px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}

[data-testid="stChatInputContainer"] textarea {
    color: #1a1a2e !important;
    caret-color: #c0182a !important;
    background: transparent !important;
}

[data-testid="stChatInputContainer"] textarea::placeholder { color: #adb5bd !important; }

[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px 0 !important;
}

.stChatMessage .stMarkdown p,
.stChatMessage .stMarkdown {
    font-size: 14px !important;
    line-height: 1.6 !important;
}

div[data-testid="stButton"] > button {
    background: #ffffff !important;
    border: 1px solid #eaecf0 !important;
    border-radius: 20px !important;
    color: #0a2240 !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 9px 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    transition: all 0.15s !important;
}

div[data-testid="stButton"] > button:hover {
    border-color: #c0182a !important;
    color: #c0182a !important;
    background: #fff0f1 !important;
}

.info-box {
    background-color: white;
    padding: 16px 18px;
    border-radius: 14px;
    border-left: 4px solid #c0182a;
    margin-bottom: 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}

.footer-text {
    text-align: center;
    color: #adb5bd;
    font-size: 11px;
    padding-top: 20px;
}

#MainMenu, footer { visibility: hidden; }

.bubble-user {
    display: flex;
    justify-content: flex-end;
    margin: 6px 0;
}
.bubble-user-inner {
    background: linear-gradient(135deg, #c0182a 0%, #0a2240 100%);
    color: #ffffff;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 16px;
    max-width: 68%;
    font-size: 14px;
    line-height: 1.55;
    box-shadow: 0 2px 8px rgba(192,24,42,0.18);
    word-wrap: break-word;
}
.bubble-bot {
    display: flex;
    justify-content: flex-start;
    margin: 6px 0;
}
.bubble-bot-inner {
    background: #ffffff;
    color: #1a1a2e;
    border-radius: 18px 18px 18px 4px;
    padding: 10px 16px;
    max-width: 72%;
    font-size: 14px;
    line-height: 1.65;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    word-wrap: break-word;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CONSTANTS & MODEL DEFINITIONS
# ============================================================

# Valid Groq Models
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
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

# Expanded Greetings Regex (Handles multilingual greetings & common casual openers)
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
# LOGO & HEADER
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
    st.markdown(" **AI Academic Advisor · Online**")

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 🎓 Student Profile")
    st.markdown("Enter your details to get personalized guidance.")
    st.markdown("---")

    program = st.selectbox(
        "Program",
        ["B.Tech", "BMS", "BA LLB", "BMS LLB", "B.A. Economics", "B.A. Psychology", "B.Des"]
    )

    semester = st.selectbox(
        "Current Semester",
        ["Not specified", "1st Semester", "2nd Semester", "3rd Semester",
         "4th Semester", "5th Semester", "6th Semester", "7th Semester",
         "8th Semester", "9th Semester", "10th Semester"]
    )

    completed_credits = st.number_input("Completed Credits", min_value=0, max_value=400, value=45, step=1)
    cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.1)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# API KEY & PROFILE
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

# Optimized Chunking: 280 words with 50-word overlap for better context retention
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
# TOKENIZATION & SMART RETRIEVAL
# ============================================================

STOPWORDS = {
    "the","a","an","is","are","am","i","me","my","to","of","in","on",
    "for","and","or","can","could","would","should","do","does","did",
    "be","it","this","that","with","from","at","as","what","which",
    "how","where","when","why","you","your","please","tell"
}

def simple_stem(word):
    # Simple suffix stripping to match variations like eligibility/eligible, requirement/requirements
    for suffix in ["ing", "ed", "es", "s", "ment", "ability", "ible"]:
        if len(word) > 5 and word.endswith(suffix):
            return word[:-len(suffix)]
    return word

def tokenize(text):
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [simple_stem(t) for t in tokens if t not in STOPWORDS]

def retrieve(query, documents, top_k=6, minimum_score=0.02):
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
        
        # TF-IDF Calculation
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
# CLASSIFY QUERY & CONTEXT
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

def profile_to_text():
    return (
        f"Program: {student_profile['program']}\n"
        f"Current Semester: {student_profile['semester']}\n"
        f"Completed Credits: {student_profile['completed_credits']}\n"
        f"CGPA: {student_profile['cgpa']}"
    )

def build_system_prompt():
    return f"""You are the official AI Academic Advisor for Vidyashilp University (VU), Bengaluru, India.

STUDENT PROFILE:
{profile_to_text()}

YOUR CORE DIRECTIVE:
1. You MUST ALWAYS speak as the VU AI Academic Advisor.
2. Even for small talk or standard greetings, introduce yourself as the VU AI Academic Advisor and ask how you can help academically. NEVER say generic things like "I'm doing well" without identifying your role.
3. Keep responses direct, helpful, and clear.
4. Compare numeric thresholds in retrieved rules directly against the student's profile (e.g. compare required CGPA vs student's CGPA).
5. If the exact rule or credit requirement is not in the documents, state that clearly and advise contacting the Academic Office.

CITATION RULE:
- Cite source documents like [Student_Handbook.pdf] when answering academic queries.
- Do NOT cite sources for greetings or general pleasantries."""


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

def generate_answer(client, user_question, context, category):
    user_prompt = f"""RETRIEVED UNIVERSITY CONTEXT:
{context}

STUDENT QUESTION:
{user_question}

Answer concisely as the VU AI Academic Advisor based on the context above."""

    last_error = None
    for model in GROQ_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=700
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            continue
    return f"I'm experiencing connectivity issues right now. Please try again shortly. (Error: {last_error})"


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
# SUGGESTIONS & MAIN CHAT DISPLAY
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

    # 1. Handle Greetings & Pleasantries cleanly without documents or generic chatter
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

    # 2. Handle Academic & University Queries via RAG
    if not api_key:
        answer = "Groq API key missing. Please configure GROQ_API_KEY in Streamlit Secrets or Environment Variables."
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

        with st.spinner("Analyzing regulations..."):
            answer = generate_answer(client, user_question, context, category)

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
