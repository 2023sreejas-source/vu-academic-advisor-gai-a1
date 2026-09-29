# ============================================================
# VU AI ACADEMIC ADVISOR — Vidyashilp University (corrected)
if bg_path:
    with open(bg_path, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = bg_path.split(".")[-1].lower()
    ext = "jpeg" if ext == "jpg" else ext
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

logo_path = None
for name in ("Logo.png", "logo.png"):
    candidate = os.path.join(APP_DIR, name)
    if os.path.isfile(candidate):
        logo_path = candidate
        break

logo_html = ""
if logo_path:
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 48px; width: auto; object-fit: contain;" alt="VU Logo" />'


# ============================================================
# CSS
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
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #E2E8F0 !important;
    font-size: 13px;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.18) !important;
    margin: 16px 0 !important;
}
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
[data-testid="stSidebar"] [data-baseweb="select"] span { color: #FFFFFF !important; }
[data-testid="stSidebar"] input::placeholder {
    color: #E2E8F0 !important;
    opacity: 0.8 !important;
}
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
    transform: translateY(-1px);
}
main div[data-testid="stButton"] > button * { color: #0B5394 !important; }

/* ========================= CHAT BUBBLES ========================= */
.bubble-user { display: flex; justify-content: flex-end; margin: 12px 0; }
.bubble-user-inner {
    background: #0B5394; color: #FFFFFF;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 18px; max-width: 72%;
    font-size: 14px; line-height: 1.6;
    box-shadow: 0 2px 4px rgba(11,83,148,0.12);
}
.bubble-bot { display: flex; justify-content: flex-start; margin: 12px 0; }
.bubble-bot-inner {
    background: #FFFFFF; color: #1E293B;
    border: 1px solid #E2E8F0;
    border-radius: 16px 16px 16px 4px;
    padding: 14px 20px; max-width: 80%;
    font-size: 14.5px; line-height: 1.65;
    box-shadow: 0 2px 6px rgba(15,23,42,0.03);
}
.bubble-bot-inner ul { margin: 6px 0 6px 18px; padding: 0; }
.bubble-bot-inner li { margin-bottom: 3px; }

[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    margin-top: 6px !important;
}
[data-testid="stExpander"] summary { color: #64748B !important; font-size: 12px !important; }

/* Floating composer (covers old and new Streamlit test ids) */
[data-testid="stBottom"] {
    background: transparent !important;
    border-top: none !important;
    padding: 10px 0 16px !important;
}
[data-testid="stBottom"] > div { background: transparent !important; }
[data-testid="stChatInputContainer"],
[data-testid="stChatInput"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 16px rgba(15,23,42,0.08) !important;
}
[data-testid="stChatInputContainer"] textarea,
[data-testid="stChatInput"] textarea {
    color: #0F172A !important;
    caret-color: #0B5394 !important;
    background-color: #FFFFFF !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}
[data-testid="stChatInputContainer"] button,
[data-testid="stChatInput"] button {
    color: #FFFFFF !important;
    background: #0B5394 !important;
    border-radius: 8px !important;
}

.ai-disclaimer {
    position: fixed; left: 0; right: 0; bottom: 2px;
    z-index: 999999; text-align: center;
    color: #64748B; font-size: 10.5px; pointer-events: none;
}
.footer-text { text-align: center; color: #64748B; font-size: 12px; padding: 12px 0 24px; }
#MainMenu, footer { visibility: hidden; }

@media (max-width: 900px) {
    .vu-header-card { flex-direction: column; align-items: flex-start; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CONSTANTS & REGEXES
# ============================================================

# Decommissioned models removed. Fallback chain of currently available Groq models.
MODEL_CANDIDATES = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

ACADEMIC_EXTENSIONS = (".pdf", ".txt", ".csv", ".xlsx", ".xls")
# "requirements" added so requirements.txt is not loaded as an academic document
EXCLUDED_FILES = ("advisor_eval", "eval_results", "phase4", "summary_metrics",
                  "website_sources", "requirements", "readme")

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
THANKS_RE = re.compile(r"\b(thank(s|\s*you|u)?|thx|ty)\b", re.I)

GREETING_REPLY = (
    "I'm doing well, thank you! 😊 I'm VU's AI Academic Advisor. "
    "I can help with attendance, credits, prerequisites, registration, "
    "course eligibility, progression rules and more. "
    "What would you like to know today?"
)
THANKS_REPLY = "Happy to help! Feel free to ask anything else about your academics at VU."

# removed overly generic words ("match", "rain") that could hit academic questions
OUT_OF_SCOPE_RE = re.compile(
    r"\b(weather|temperature|forecast|cricket|football|soccer|movie|movies|"
    r"song|songs|music|restaurant|recipe|stock market|politics|election|celebrity|"
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
        st.session_state.pending_question = None
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
# STUDENT PROFILE & PER-QUESTION OVERRIDES
# ============================================================

student_profile = {
    "program": program,
    "semester": semester,
    "completed_credits": completed_credits,
    "cgpa": cgpa
}

# Ordered most-specific first so "BMS LLB" is not swallowed by "BMS"
PROGRAM_PATTERNS = [
    ("BMS LLB", r"\bb\.?\s?m\.?\s?s\.?,?\s*ll\.?\s?b"),
    ("BA LLB", r"\bb\.?\s?a\.?,?\s*ll\.?\s?b"),
    ("B.Tech", r"\bb\.?\s?tech\b"),
    ("BMS", r"\bb\.?\s?m\.?\s?s\b"),
    ("B.A. Economics", r"\bb\.?\s?a\.?\s*(?:\(hons\.?\)\s*)?economics\b|\beconomics\s+(?:major|student|programme|program|degree)\b"),
    ("B.A. Psychology", r"\bb\.?\s?a\.?\s*(?:\(hons\.?\)\s*)?psychology\b|\bpsychology\s+(?:major|student|programme|program|degree)\b"),
    ("B.Des", r"\bb\.?\s?des\b"),
]

ORDINAL_WORDS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10
}

def ordinal(n):
    if n in (1, 2, 3):
        return {1: "1st", 2: "2nd", 3: "3rd"}[n]
    return f"{n}th"

def effective_profile_for_question(user_query, sidebar_profile):
    effective = dict(sidebar_profile)
    q = user_query.lower()

    for label, pattern in PROGRAM_PATTERNS:
        if re.search(pattern, q):
            effective["program"] = label
            break

    sem_num = None
    m = re.search(r"\b(10|[1-9])(?:st|nd|rd|th)?\s*(?:sem|semester)\b", q)
    if m:
        sem_num = int(m.group(1))
    else:
        m = re.search(r"\bsem(?:ester)?\s*(10|[1-9])\b", q)
        if m:
            sem_num = int(m.group(1))
        else:
            m = re.search(r"\b(" + "|".join(ORDINAL_WORDS) + r")\s+sem(?:ester)?\b", q)
            if m:
                sem_num = ORDINAL_WORDS[m.group(1)]
    if sem_num:
        effective["semester"] = f"{ordinal(sem_num)} Semester"

    m = re.search(r"\b(?:cgpa|gpa)\s*(?:of|is|=|:)?\s*(10(?:\.0+)?|[0-9](?:\.[0-9]{1,2})?)\b", q)
    if m:
        try:
            effective["cgpa"] = float(m.group(1))
        except ValueError:
            pass

    # Only treat a number as "completed" credits when the wording says so;
    # otherwise "160 credits to graduate" would wrongly overwrite the profile.
    m = re.search(r"\b(?:completed|earned|finished|done|have|has|got)\s+(\d{1,3})\s*credits?\b", q) \
        or re.search(r"\b(\d{1,3})\s*credits?\s+(?:completed|earned|done|so far)\b", q)
    if m:
        try:
            effective["completed_credits"] = int(m.group(1))
        except ValueError:
            pass

    return effective


# ============================================================
# TEXT EXTRACTION
def extract_plain_text(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return clean_text(f.read())
    except Exception:
        return ""

def extract_excel_sheets(filepath):
    sheets = []
    try:
        if filepath.lower().endswith(".xlsx"):
            from openpyxl import load_workbook
            wb = load_workbook(filepath, read_only=True, data_only=True)
            for sheet in wb.worksheets:
                rows = []
                for row in sheet.iter_rows(values_only=True):
                    values = [str(v) for v in row if v is not None]
                    if values:
                        rows.append(" | ".join(values))
                text = clean_text("\n".join(rows))
                if text:
                    sheets.append({"sheet": sheet.title, "text": text})
        else:  # .xls needs pandas + xlrd; skip quietly if unavailable
            import pandas as pd
            for name, df in pd.read_excel(filepath, sheet_name=None, header=None).items():
                text = clean_text(df.fillna("").astype(str).to_string(index=False, header=False))
                if text:
                    sheets.append({"sheet": str(name), "text": text})
    except Exception:
        return sheets
    return sheets


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(text, chunk_size=150, overlap=30):
    words = text.split()
    if not words:
        return []
    overlap = min(overlap, chunk_size - 1)
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap
    return chunks


# ============================================================
# LOAD ACADEMIC DOCUMENTS (always relative to the app folder)
# ============================================================

def load_academic_documents():
    documents = []
    for filename in sorted(os.listdir(APP_DIR)):
        if filename.startswith("."):
            continue
        lower = filename.lower()
        if not lower.endswith(ACADEMIC_EXTENSIONS):
            continue
        if any(ex in lower for ex in EXCLUDED_FILES):
            continue

        filepath = os.path.join(APP_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            for page_info in extract_pdf_pages(filepath):
                for i, chunk in enumerate(chunk_text(page_info["text"]), start=1):
                    documents.append({
                        "text": chunk, "source": filename, "type": "academic",
                        "chunk": i, "page": page_info.get("page"),
                        "section": page_info.get("section", "")
                    })
        elif ext in (".xlsx", ".xls"):
            for sheet_info in extract_excel_sheets(filepath):
                for i, chunk in enumerate(chunk_text(sheet_info["text"]), start=1):
                    documents.append({
                        "text": chunk, "source": filename, "type": "academic",
                        "chunk": i, "section": sheet_info.get("sheet", "")
                    })
        else:  # .txt / .csv
            text = extract_plain_text(filepath)
            for i, chunk in enumerate(chunk_text(text), start=1):
                documents.append({"text": chunk, "source": filename, "type": "academic", "chunk": i})
    return documents


# ============================================================
# WEBSITE SOURCES
# ============================================================

def load_website_sources():
    source_file = os.path.join(APP_DIR, "website_sources.json")
    if os.path.exists(source_file):
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass
    return DEFAULT_WEBSITE_SOURCES

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_webpage_raw(url):
    """Raises on failure so failed fetches are NOT cached for an hour."""
    from bs4 import BeautifulSoup
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
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
    if not sections:
        sections = [{"section": title or "VU Official Website",
                     "text": clean_text(soup.get_text(separator=" "))}]
    return {"title": title, "sections": sections}

def fetch_webpage(url):
    try:
        return _fetch_webpage_raw(url)
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
                    "text": chunk, "source": name, "url": url,
                    "title": page.get("title", ""),
                    "section": section_info.get("section", ""),
                    "type": "website", "chunk": i
                })
    return documents


# ============================================================
# TOKENIZER, INDEX & RETRIEVAL (index built once, not per question)
# ============================================================

STOPWORDS = {
    "the","a","an","is","are","am","i","me","my","to","of","in","on",
    "for","and","or","can","could","would","should","do","does","did",
    "be","it","this","that","with","from","at","as","what","which",
    "how","where","when","why","you","your"
}

BOOST_PHRASES = [
    "minimum cgpa", "attendance", "eligibility", "eligible",
    "prerequisite", "minor", "semester", "admission", "course",
    "credits", "programme", "program", "transfer", "law",
    "summer", "summer term"
]

def tokenize(text):
    return [t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if t not in STOPWORDS]

def build_index(documents):
    tokenized = [tokenize(d["text"]) for d in documents]
    df = Counter()
    for toks in tokenized:
        df.update(set(toks))
    return {
        "docs": documents,
        "counters": [Counter(t) for t in tokenized],
        "lengths": [len(t) for t in tokenized],
        "lower": [d["text"].lower() for d in documents],
        "df": df,
    }

@st.cache_resource(show_spinner="Loading VU academic documents and official information...")
def load_knowledge():
    return {
        "academic": build_index(load_academic_documents()),
        "website": build_index(load_website_documents()),
    }

def retrieve(query, index, top_k=5, minimum_score=0.05):
    docs = index["docs"]
    if not docs:
        return []
    query_counter = Counter(tokenize(query))
    if not query_counter:
        return []

    total = len(docs)
    ql = query.lower()
    active_boosts = [p for p in BOOST_PHRASES if p in ql]
    scored = []
    for i, doc in enumerate(docs):
        length = index["lengths"][i]
        if not length:
            continue
        tc = index["counters"][i]
        score = 0.0
        for t, qc in query_counter.items():
            if t in tc:
                idf = math.log((total + 1) / (index["df"].get(t, 0) + 1)) + 1
                score += (tc[t] / length) * idf * qc
        for phrase in active_boosts:
            if phrase in index["lower"][i]:
                score += 0.15
        if score >= minimum_score:
            scored.append((score, i))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, i in scored[:top_k]:
        r = dict(docs[i])
        r["_score"] = score
        results.append(r)
    return results


# ============================================================
# QUERY CLASSIFICATION & CONVERSATION CONTEXT
# ============================================================

def classify_query(query):
    q = query.lower().strip()
    website_patterns = [
        "admission", "apply", "application", "how do i join", "join vu",
        "contact", "phone number", "email", "address", "campus", "location",
        "where is vu", "where is vidyashilp", "programmes offered",
        "about vu", "vidyashilp university", "law programme"
    ]
    return "website" if any(p in q for p in website_patterns) else "academic"

def is_follow_up_question(query):
    q = query.lower().strip()
    indicators = [
        "what about", "and for", "how about", "which one", "which ones",
        "what are the prerequisites", "are there any prerequisites",
        "tell me more", "can you elaborate", "why", "how so", "is it required",
        "and that", "what else", "then"
    ]
    return len(q.split()) <= 7 and any(ind in q for ind in indicators)

def conversation_context_for(history, max_messages=4):
    if not history:
        return ""
    lines = []
    for m in history[-max_messages:]:
        role = "Student" if m["role"] == "user" else "Advisor"
        lines.append(f"{role}: {m['content'][:600]}")
    return "\n".join(lines)

def last_user_message(history):
    for m in reversed(history):
        if m["role"] == "user":
            return m["content"]
    return ""


# ============================================================
# PROFILE TEXT & SYSTEM PROMPT
# ============================================================

def profile_to_text(p):
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

def build_system_prompt(effective_profile):
    return f"""You are the AI Academic Advisor for Vidyashilp University (VU), Bengaluru, India.

Student profile for this question:
{profile_to_text(effective_profile)}

YOUR ROLE:
Help students with VU undergraduate academic questions — courses, credits, prerequisites,
attendance, progression, graduation requirements, semester planning, admissions and programmes.

RESPONSE STYLE:
- Keep responses short, clear and conversational.
- No tables and no long report-style answers.
- Use at most 4-5 bullets (start each bullet with "- ") when useful.
- Friendly and warm, but accurate.
- Never guess a rule, number, course, eligibility condition or programme structure.
- Answer ONLY from the retrieved information provided. Do not use outside knowledge for VU rules.

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

BEHAVIOUR RULES:
1. Greetings and casual openers get a friendly response.
2. Personal questions about the AI should be answered briefly and redirected to academics.
3. Completely non-academic questions should be declined politely.
4. If the student asks about Summer Term, do not invent offerings, fees or rules.
   Say the available information is insufficient and advise checking the academic office/registrar.
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
- Do not put technical source placeholders such as [Source 1] in the answer text.
- Source references will be rendered in a separate source drawer below the chat response.
"""


# ============================================================
# SAFE RENDERING OF MODEL OUTPUT (escape HTML, support **bold** and bullets)
# ============================================================

def format_answer(text):
    text = html.escape(text or "")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    out, in_list = [], False
    for line in text.split("\n"):
        stripped = line.strip()
        bullet = re.match(r"^(?:[-*•]|\d+[.)])\s+(.*)$", stripped)
        if bullet:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{bullet.group(1)}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            if stripped:
                out.append(stripped + "<br>")
    if in_list:
        out.append("</ul>")
    result = "".join(out)
    return re.sub(r"(<br>)+$", "", result)

def render_user(content):
    st.markdown(
        f'<div class="bubble-user"><div class="bubble-user-inner">{html.escape(content)}</div></div>',
        unsafe_allow_html=True
    )

def render_bot(content):
    st.markdown(
        f'<div class="bubble-bot"><div class="bubble-bot-inner">{format_answer(content)}</div></div>',
        unsafe_allow_html=True
    )


# ============================================================
# SOURCE DISPLAY DRAWER
# ============================================================

def display_sources(retrieved_docs):
    if not retrieved_docs:
        return
    seen, unique_sources = set(), []
    for doc in retrieved_docs:
        key = (doc.get("source", "VU Reference Document"), doc.get("page"),
               doc.get("section", ""), doc.get("url", ""))
        if key not in seen:
            seen.add(key)
            unique_sources.append({
                "source": key[0], "page": key[1], "section": key[2],
                "url": key[3], "type": doc.get("type", "academic")
            })

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

def generate_response(user_query, effective_profile, history, knowledge):
    # 1. Intent pre-filtering (no API key / retrieval needed)
    if SOCIAL_RE.match(user_query):
        return (THANKS_REPLY if THANKS_RE.search(user_query) else GREETING_REPLY), []
    if OUT_OF_SCOPE_RE.search(user_query):
        return OUT_OF_SCOPE_REPLY, []
    if PERSONAL_RE.search(user_query):
        return PERSONAL_REPLY, []

    if not api_key:
        return ("⚠️ Groq API key not found. Please set GROQ_API_KEY in your environment "
                "or in .streamlit/secrets.toml."), []

    # 2. Retrieve
    follow_up = is_follow_up_question(user_query)
    retrieval_query = user_query
    if follow_up:
        prev = last_user_message(history)
        if prev:
            retrieval_query = f"{prev} {user_query}"

    q_type = classify_query(user_query)
    primary, secondary = ("website", "academic") if q_type == "website" else ("academic", "website")
    retrieved = retrieve(retrieval_query, knowledge[primary], top_k=5)
    if not retrieved:
        retrieved = retrieve(retrieval_query, knowledge[secondary], top_k=5)

    # 3. Build context
    context_blocks = []
    if follow_up:
        conv_ctx = conversation_context_for(history)
        if conv_ctx:
            context_blocks.append(f"Recent Conversation Context:\n{conv_ctx}")
    for idx, doc in enumerate(retrieved, start=1):
        p_str = f", Page {doc['page']}" if doc.get("page") else ""
        s_str = f", Section: {doc['section']}" if doc.get("section") else ""
        context_blocks.append(f"[Source {idx}: {doc.get('source', 'VU Source')}{p_str}{s_str}]\n{doc['text']}")
    kb_context = "\n\n".join(context_blocks) if context_blocks else "No matching VU official documents found."

    messages = [
        {"role": "system", "content": build_system_prompt(effective_profile)},
        {"role": "user", "content": f"Information retrieved from VU databases:\n{kb_context}\n\nStudent question: {user_query}"}
    ]

    # 4. Call the model, falling back to the next one on model/rate-limit errors
    client = Groq(api_key=api_key)
    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            response = client.chat.completions.create(
                model=model_name, messages=messages, temperature=0.2, max_tokens=600
            )
            return response.choices[0].message.content, retrieved
        except Exception as e:
            last_error = e
            err = str(e).lower()
            if "401" in err or "invalid_api_key" in err or "invalid api key" in err:
                return "⚠️ The Groq API key appears to be invalid. Please check GROQ_API_KEY.", []
            # model missing / decommissioned / rate limited / overloaded -> try next model
            continue

    return f"⚠️ Could not reach the AI service right now. Please try again shortly. ({last_error})", []


# ============================================================
# MAIN CHAT INTERFACE
# ============================================================

knowledge = load_knowledge()

# Read input first so the welcome card can disappear immediately
user_input = st.chat_input("Type your academic question here...")
if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None

# Render existing history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        render_user(msg["content"])
    else:
        render_bot(msg["content"])
        if msg.get("sources"):
            display_sources(msg["sources"])

# Welcome card + suggestion buttons (only when the chat is empty and nothing is being asked)
if not st.session_state.messages and not user_input:
    st.markdown('''
    <div class="vu-card">
        <div class="vu-prompt-title">Welcome! How can I assist you today?</div>
        <div class="vu-prompt-text">Ask me anything about attendance criteria, course credits, prerequisites, or degree requirements at Vidyashilp University.</div>
        <div class="vu-try">Try asking:</div>
    </div>
    ''', unsafe_allow_html=True)

    suggestions = [
        "What is the minimum attendance requirement at VU?",
        "How many credits do I need to graduate from B.Tech?",
        "What are the prerequisites for AI/ML specialization?",
        "Can I choose a minor in BMS programme?",
    ]
    col1, col2 = st.columns(2)
    for i, text in enumerate(suggestions):
        with (col1 if i % 2 == 0 else col2):
            if st.button(text, key=f"sugg_{i}", use_container_width=True):
                st.session_state.pending_question = text
                st.rerun()

# Handle a new question
if user_input:
    history = list(st.session_state.messages)  # history BEFORE this question
    effective_prof = effective_profile_for_question(user_input, student_profile)

    st.session_state.messages.append({"role": "user", "content": user_input})
    render_user(user_input)

    with st.spinner("Consulting VU academic regulations..."):
        answer, sources = generate_response(user_input, effective_prof, history, knowledge)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    render_bot(answer)
    if sources:
        display_sources(sources)


# ============================================================
# FOOTER
# ============================================================

st.markdown('<div class="ai-disclaimer">AI-generated responses can occasionally vary. Please verify official policies with the VU Academic Office.</div>', unsafe_allow_html=True)
st.markdown('<div class="footer-text">Vidyashilp University Academic Advisor © 2026</div>', unsafe_allow_html=True)
