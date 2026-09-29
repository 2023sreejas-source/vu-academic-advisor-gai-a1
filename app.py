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
# DYNAMIC BACKGROUND & LOGO INJECTION
# ============================================================

# 1. Background Image Setup (Frosted Glass Effect)
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

# 2. Logo Setup
logo_path = os.path.join(APP_DIR, "Logo.png")
if not os.path.isfile(logo_path):
    logo_path = os.path.join(APP_DIR, "logo.png")

logo_html = ""
if os.path.isfile(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 48px; width: auto; object-fit: contain;" alt="VU Logo" />'


# ============================================================
# CSS (UI/UX POLISH & FORCED LIGHT THEME)
# ============================================================

st.markdown(bg_css, unsafe_allow_html=True)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="block-container"] { padding-top: 2rem !important; }

/* ========================= SIDEBAR ========================= */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background: #0B5394 !important;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }

/* Override Dark Mode in Sidebar Dropdowns */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-baseweb="popover"] { background-color: #0B5394 !important; }

/* Override Dark Mode in Sidebar Inputs */
[data-testid="stSidebar"] [data-testid="stNumberInput"] > div {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
    color: #FFFFFF !important;
}

/* Clear Chat Button */
[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.2) !important;
}

/* ========================= HEADER & CARDS ========================= */
.vu-header-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(15,23,42,0.05);
    display: flex;
    align-items: center;
    gap: 20px;
}
.vu-header-info { display: flex; flex-direction: column; }
.vu-sub-title { color: #64748B; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }
.vu-heading { color: #0B5394; font-size: 24px; font-weight: 700; margin: 0; }
.vu-status { color: #64748B; font-size: 13px; margin-top: 4px; display: flex; align-items: center; gap: 6px; }
.vu-status-dot { color: #22C55E; font-size: 10px; }

.vu-card {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(15,23,42,0.04);
}
.vu-prompt-title { color: #0F172A; font-size: 18px; font-weight: 700; margin-bottom: 6px; }
.vu-prompt-text { color: #475569; font-size: 14px; margin: 0; }

/* Override Dark Mode on Suggestion Buttons */
main div[data-testid="stButton"] > button {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    color: #0B5394 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 2px rgba(15,23,42,0.03) !important;
    padding: 12px 14px !important;
}
main div[data-testid="stButton"] > button:hover {
    background: #F0F9FF !important;
    border-color: #0B5394 !important;
    transform: translateY(-1px);
}
main div[data-testid="stButton"] > button * { color: #0B5394 !important; }

/* ========================= CHAT INTERFACE ========================= */
.bubble-user { display: flex; justify-content: flex-end; margin: 12px 0; }
.bubble-user-inner {
    background: #0B5394; color: #FFFFFF;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 18px; max-width: 72%;
    font-size: 14px; box-shadow: 0 2px 4px rgba(11,83,148,0.12);
}
.bubble-bot { display: flex; justify-content: flex-start; margin: 12px 0; }
.bubble-bot-inner {
    background: #FFFFFF; color: #1E293B;
    border: 1px solid #E2E8F0; border-radius: 16px 16px 16px 4px;
    padding: 14px 20px; max-width: 80%;
    font-size: 14.5px; box-shadow: 0 2px 6px rgba(15,23,42,0.04);
}

/* Override Dark Mode on Chat Input */
[data-testid="stBottom"] { background: transparent !important; }
[data-testid="stChatInputContainer"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 24px rgba(15,23,42,0.08) !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: #0F172A !important;
    background-color: #FFFFFF !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #94A3B8 !important;
}
[data-testid="stChatInputContainer"] button {
    background: #0B5394 !important;
    color: #FFFFFF !important;
}
[data-testid="stChatInputContainer"] button svg {
    fill: #FFFFFF !important;
}

.ai-disclaimer {
    position: fixed; left: 0; right: 0; bottom: 2px;
    text-align: center; color: #64748B; font-size: 10px; pointer-events: none;
}
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


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
# STATE & CONSTANTS (Hidden Logic)
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

MODEL = "llama-3.3-70b-versatile"
ACADEMIC_EXTENSIONS = (".pdf", ".txt", ".csv", ".xlsx", ".xls")
EXCLUDED_FILES = ("advisor_eval", "eval_results", "phase4", "summary_metrics", "website_sources")

SOCIAL_RE = re.compile(r"^\s*(hi+|hello+|hey+|hola|yo+|good\s*(morning|afternoon|evening)|thank(s|you)|ty)\s*[!.?]*\s*$", re.I)

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
        index=None, placeholder="Select if needed"
    )

    semester = st.selectbox(
        "Current Semester",
        ["1st Semester", "2nd Semester", "3rd Semester", "4th Semester", "5th Semester", "6th Semester", "7th Semester", "8th Semester"],
        index=None, placeholder="Select if needed"
    )

    completed_credits = st.number_input("Completed Credits", min_value=0, max_value=400, value=None, step=1)
    cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=None, step=0.1, format="%.2f")

    st.markdown("---")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

def get_api_key():
    try:
        if st.secrets.get("GROQ_API_KEY", ""): return st.secrets["GROQ_API_KEY"]
    except: pass
    return os.getenv("GROQ_API_KEY", "")

api_key = get_api_key()

# ============================================================
# CORE LOGIC (Text Parsing, Chunking, Retrieval)
# ============================================================
def clean_text(text): return re.sub(r"\s+", " ", str(text).replace("\x00", " ")).strip() if text else ""

def chunk_text(text, chunk_size=150, overlap=30):
    words = text.split(); chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip(): chunks.append(chunk.strip())
        if end >= len(words): break
        start = end - overlap
    return chunks

def load_academic_documents():
    documents = []
    for filename in sorted(os.listdir(".")):
        if filename.startswith(".") or not filename.lower().endswith(ACADEMIC_EXTENSIONS) or any(ex in filename.lower() for ex in EXCLUDED_FILES):
            continue
        try:
            if filename.lower().endswith(".pdf"):
                reader = PdfReader(filename)
                text = " ".join(clean_text(p.extract_text() or "") for p in reader.pages)
            else:
                with open(filename, "r", encoding="utf-8", errors="ignore") as f: text = clean_text(f.read())
            
            for i, chunk in enumerate(chunk_text(text)):
                documents.append({"text": chunk, "source": filename, "type": "academic"})
        except Exception: pass
    return documents

if not st.session_state.knowledge_loaded:
    with st.spinner("Loading knowledge base..."):
        st.session_state.academic_kb = load_academic_documents()
        st.session_state.knowledge_loaded = True

def tokenize(text): return [t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if t not in {"the","a","is","to","in","of","and","for"}]

def retrieve(query, documents, top_k=5):
    if not documents: return []
    query_tokens = tokenize(query)
    query_counter = Counter(query_tokens)
    scored = []
    for doc in documents:
        tokens = tokenize(doc["text"])
        tc = Counter(tokens)
        score = sum((tc[t] / len(tokens)) * qc for t, qc in query_counter.items() if t in tc)
        if score > 0.01: scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in scored[:top_k]]

# ============================================================
# UI RENDER HELPER
# ============================================================

def render_bubble_text(text):
    safe = html.escape(str(text)).replace("\n", "<br>")
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)

def show_user_bubble(text):
    st.markdown(f'<div class="bubble-user"><div class="bubble-user-inner">{render_bubble_text(text)}</div></div>', unsafe_allow_html=True)

def show_bot_bubble(text):
    st.markdown(f'<div class="bubble-bot"><div class="bubble-bot-inner">{render_bubble_text(text)}</div></div>', unsafe_allow_html=True)

# ============================================================
# INTRO SCREEN
# ============================================================

if not st.session_state.messages:
    st.markdown("""
    <div class="vu-card">
        <div class="vu-prompt-title">Ask your academic question</div>
        <p class="vu-prompt-text">I can help with VU courses, programmes, prerequisites, eligibility, credits, semesters, admissions and related university information.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="color: #334155; font-size: 13px; font-weight: 600; margin: 16px 0 10px;">Try asking</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    suggestions = ["What programmes does VU offer?", "How do I apply to VU?", "What is the minimum CGPA to progress?", "What are the attendance requirements?", "Which minors are available for B.Tech?", "What courses are offered next semester?"]
    
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_question = suggestion
                st.rerun()

# ============================================================
# CHAT EXECUTION
# ============================================================

for msg in st.session_state.messages:
    if msg["role"] == "user": show_user_bubble(msg["content"])
    else: show_bot_bubble(msg["content"])

user_question = st.session_state.pending_question or st.chat_input("Ask your academic question...")
st.session_state.pending_question = None

st.markdown('<div class="ai-disclaimer">AI-generated responses can make mistakes. Please verify important academic information with official VU sources.</div>', unsafe_allow_html=True)

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    show_user_bubble(user_question)

    if not api_key:
        answer = "API Key missing. Please set GROQ_API_KEY in secrets."
    elif SOCIAL_RE.match(user_question):
        answer = "Hello! I am the VU Academic Advisor. How can I help you today?"
    else:
        client = Groq(api_key=api_key)
        docs = retrieve(user_question, st.session_state.academic_kb)
        context = "\n\n".join([f"Source: {d['source']}\n{d['text']}" for d in docs])
        
        prompt = f"""You are the VU AI Academic Advisor. Answer strictly based on the text below. 
        Keep it concise and friendly.
        
        Context:
        {context}
        
        Question: {user_question}"""

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            answer = response.choices[0].message.content.strip()
        except:
            answer = "Sorry, I am having trouble connecting right now."

    show_bot_bubble(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
