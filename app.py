import streamlit as st
from groq import Groq
from pypdf import PdfReader

import os
import re
import math
import base64
import json
import html
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

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* APP BACKGROUND */

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


/* HEADER */

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


/* CHAT */

.vu-chat-area {
    background: #f0f2f5;
    padding: 8px 0;
}

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

.vu-msg-bot {
    background: #ffffff;
    color: #1a1a2e;
    border-radius: 20px 20px 20px 4px;
    padding: 13px 18px;
    max-width: 78%;
    margin-right: auto;
    margin-left: 0;
    font-size: 14px;
    line-height: 1.65;
    margin-bottom: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    word-wrap: break-word;
}

.vu-msg-bot strong {
    color: #0a2240;
}

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


/* SOURCE CHIPS */

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

.vu-web-chip {
    display: inline-block;
    background: #eef4ff;
    color: #0a4a8a;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 20px;
    margin: 2px 3px 2px 0;
    border: 1px solid #c8daf5;
    font-weight: 500;
}


/* SIDEBAR */

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

.vu-profile-badge span {
    color: #c0182a;
    font-weight: 600;
}

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


/* INPUT */

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
.stBottom,
.stBottom > div {
    background-color: #ffffff !important;
    border-top: 1px solid #eaecf0 !important;
}

[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div,
.stChatInput,
.stChatInput > div {
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


/* BUTTONS */

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


#MainMenu,
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# MODEL
# ============================================================

MODEL = "openai/gpt-oss-20b"


# ============================================================
# LOGO
# ============================================================

def find_logo():

    for filename in os.listdir("."):

        if filename.startswith("."):
            continue

        lower = filename.lower()

        if lower.endswith((".png", ".jpg", ".jpeg")):

            if "logo" in lower or "b0d1fb" in lower:
                return filename

    return None


def image_to_base64(path):

    try:

        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    except Exception:

        return None


logo_file = find_logo()

logo_html = ""

if logo_file:

    b64 = image_to_base64(logo_file)

    if b64:

        logo_html = (
            '<img class="vu-header-logo" '
            f'src="data:image/png;base64,{b64}">'
        )

else:

    logo_html = (
        '<div style="width:52px;height:52px;border-radius:50%;'
        'background:linear-gradient(135deg,#c0182a,#0a2240);'
        'flex-shrink:0;"></div>'
    )


st.markdown(
    f"""
    <div class="vu-header">

        {logo_html}

        <div>

            <p class="vu-header-title">
                Vidyashilp University
            </p>

            <p class="vu-header-sub">
                <span class="vu-header-dot"></span>
                AI Academic Advisor &nbsp;·&nbsp; Online
            </p>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = None

if "website_base" not in st.session_state:
    st.session_state.website_base = None

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ============================================================
# STOPWORDS
# ============================================================

STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "of", "to", "in", "on",
    "for", "with", "what", "are", "was", "were", "be", "can", "i",
    "my", "me", "do", "does", "how", "much", "many", "about",
    "from", "at", "this", "that", "it", "as", "by", "if",
    "minimum", "please", "tell", "give", "would", "could",
    "should", "you", "your", "we", "our", "they", "their"
}


def tokenize(text):

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )

    return [
        w for w in words
        if w not in STOPWORDS
    ]


# ============================================================
# EXCLUDE FILES FROM RAG
# ============================================================

EXCLUDE_KEYWORDS = [

    "evaluation_dataset",
    "held_out",
    "results_",
    "before_after",
    "phase4",
    "advisor_scoring",
    "synthetic_student",
    "manual_spot",
    "question_bank",
    "generalization",
    "website_sources"

]


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# CHUNK DOCUMENTS
# ============================================================

def create_chunks(
    text,
    filename,
    chunk_size=150,
    overlap=30
):

    words = text.split()

    chunks = []

    if not words:
        return chunks

    step = chunk_size - overlap

    chunk_number = 0

    for start in range(
        0,
        len(words),
        step
    ):

        chunk_words = words[
            start:start + chunk_size
        ]

        if not chunk_words:
            continue

        chunks.append({

            "id": f"{filename}#{chunk_number}",

            "filename": filename,

            "text": " ".join(chunk_words),

            "source_type": "academic_document"

        })

        chunk_number += 1

    return chunks


# ============================================================
# LOAD ACADEMIC KNOWLEDGE BASE
# ============================================================

def load_knowledge_base():

    documents = []

    source_folder = (
        "DOCS"
        if os.path.exists("DOCS")
        else "."
    )

    try:

        filenames = os.listdir(
            source_folder
        )

    except Exception:

        return []


    for filename in filenames:

        if filename.startswith("."):
            continue

        lower = filename.lower()


        # Ignore code and hidden project files

        if lower.endswith(
            (".py", ".md", ".ipynb")
        ):
            continue


        if any(
            word in lower
            for word in EXCLUDE_KEYWORDS
        ):
            continue


        filepath = os.path.join(
            source_folder,
            filename
        )


        text = ""


        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        if lower.endswith(".pdf"):

            try:

                reader = PdfReader(filepath)

                pages = []

                for page_number, page in enumerate(
                    reader.pages,
                    start=1
                ):

                    page_text = page.extract_text()

                    if page_text:

                        pages.append(
                            f"[Page {page_number}] "
                            f"{page_text}"
                        )

                text = "\n".join(pages)

            except Exception:

                continue


        # ----------------------------------------------------
        # TXT
        # ----------------------------------------------------

        elif lower.endswith(".txt"):

            try:

                with open(
                    filepath,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    text = f.read()

            except Exception:

                continue


        # ----------------------------------------------------
        # CSV
        # ----------------------------------------------------

        elif lower.endswith(".csv"):

            try:

                with open(
                    filepath,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    text = f.read()

            except Exception:

                continue


        # ----------------------------------------------------
        # XLSX
        # ----------------------------------------------------

        elif lower.endswith(".xlsx"):

            try:

                import openpyxl

                wb = openpyxl.load_workbook(
                    filepath,
                    data_only=True
                )

                rows = []

                for sheet in wb.worksheets:

                    rows.append(
                        f"[Sheet: {sheet.title}]"
                    )

                    for row in sheet.iter_rows(
                        values_only=True
                    ):

                        row_text = " | ".join(
                            str(c)
                            for c in row
                            if c is not None
                        )

                        if row_text.strip():

                            rows.append(
                                row_text
                            )

                text = "\n".join(rows)

            except Exception:

                continue


        else:

            continue


        if not text.strip():
            continue


        text = clean_text(text)


        documents.extend(
            create_chunks(
                text,
                filename
            )
        )


    return documents


# ============================================================
# WEBSITE SOURCES
# ============================================================

DEFAULT_WEBSITE_SOURCES = [

    {
        "name": "VU Official Website",
        "url": "https://vidyashilp.edu.in/"
    },

    {
        "name": "VU Admissions",
        "url": "https://vidyashilp.edu.in/admissions/"
    },

    {
        "name": "VU Contact",
        "url": "https://vidyashilp.edu.in/contact/"
    },

    {
        "name": "VU B.Tech Data Science",
        "url": "https://vidyashilp.edu.in/data-science/"
    },

    {
        "name": "VU B.Tech AI and Machine Learning",
        "url": "https://vidyashilp.edu.in/schools/b_tech_ai_ml/"
    },

    {
        "name": "VU B.Tech Overview",
        "url": "https://vidyashilp.edu.in/btech/"
    },

    {
        "name": "VU About",
        "url": "https://vidyashilp.edu.in/about/"
    }

]


def load_website_sources():

    filepath = "website_sources.json"

    if not os.path.exists(filepath):

        return DEFAULT_WEBSITE_SOURCES


    try:

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as f:

            sources = json.load(f)

        if isinstance(
            sources,
            list
        ):

            return sources

    except Exception:

        pass


    return DEFAULT_WEBSITE_SOURCES


# ============================================================
# FETCH WEBSITE PAGE
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def fetch_webpage(
    name,
    url
):

    try:

        headers = {

            "User-Agent":
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/120 Safari/537.36"

        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()


        # Try BeautifulSoup

        try:

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            for tag in soup(
                [
                    "script",
                    "style",
                    "noscript",
                    "svg"
                ]
            ):

                tag.decompose()

            text = soup.get_text(
                separator=" ",
                strip=True
            )

        except Exception:

            text = re.sub(
                r"<[^>]+>",
                " ",
                response.text
            )


        text = clean_text(text)


        return {

            "success": True,

            "name": name,

            "url": url,

            "text": text

        }


    except Exception as e:

        return {

            "success": False,

            "name": name,

            "url": url,

            "text": "",

            "error": str(e)

        }


# ============================================================
# LOAD WEBSITE KNOWLEDGE
# ============================================================

def load_website_knowledge():

    sources = load_website_sources()

    documents = []


    for source in sources:

        name = source.get(
            "name",
            "VU Website"
        )

        url = source.get(
            "url",
            ""
        )


        if not url:
            continue


        result = fetch_webpage(
            name,
            url
        )


        if not result["success"]:
            continue


        text = result["text"]


        if not text:
            continue


        chunks = create_chunks(
            text,
            name,
            chunk_size=180,
            overlap=40
        )


        for chunk in chunks:

            chunk["source_type"] = (
                "official_vu_website"
            )

            chunk["url"] = url

            chunk["filename"] = name


        documents.extend(chunks)


    return documents


# ============================================================
# LOAD KNOWLEDGE BASES
# ============================================================

if st.session_state.knowledge_base is None:

    with st.spinner(
        "Loading university documents…"
    ):

        st.session_state.knowledge_base = (
            load_knowledge_base()
        )


if st.session_state.website_base is None:

    with st.spinner(
        "Loading official VU website information…"
    ):

        st.session_state.website_base = (
            load_website_knowledge()
        )


knowledge_base = (
    st.session_state.knowledge_base
)

website_base = (
    st.session_state.website_base
)


# ============================================================
# RETRIEVAL
# ============================================================

def build_doc_freq(docs):

    df = Counter()

    for doc in docs:

        for tok in set(
            tokenize(doc["text"])
        ):

            df[tok] += 1

    return df


DOC_FREQ = build_doc_freq(
    knowledge_base
)

N_CHUNKS = len(
    knowledge_base
)


def retrieve(
    query,
    docs,
    top_k=6,
    min_score=1.5
):

    if not docs:
        return []


    q_tokens = set(
        tokenize(query)
    )


    if not q_tokens:
        return []


    doc_freq = build_doc_freq(
        docs
    )

    n_docs = len(docs)


    scored = []


    query_lower = query.lower()


    for doc in docs:

        text_lower = doc[
            "text"
        ].lower()


        doc_tokens = set(
            tokenize(doc["text"])
        )


        overlap = q_tokens.intersection(
            doc_tokens
        )


        if not overlap:
            continue


        score = 0.0


        # ----------------------------------------------------
        # TF-IDF-like score
        # ----------------------------------------------------

        for token in overlap:

            score += (
                math.log(
                    (n_docs + 1)
                    /
                    (doc_freq.get(
                        token,
                        0
                    ) + 1)
                )
                + 1
            )


        # ----------------------------------------------------
        # Exact phrase bonus
        # ----------------------------------------------------

        meaningful_tokens = [
            t for t in q_tokens
            if len(t) > 2
        ]


        if len(
            meaningful_tokens
        ) >= 2:

            phrase = " ".join(
                meaningful_tokens
            )

            if phrase in text_lower:

                score += 3.0


        # ----------------------------------------------------
        # Important academic terms bonus
        # ----------------------------------------------------

        important_terms = {

            "cgpa",
            "credit",
            "credits",
            "attendance",
            "prerequisite",
            "prerequisites",
            "graduation",
            "semester",
            "course",
            "courses",
            "eligibility",
            "minor",
            "major",
            "progression",
            "withdrawal",
            "registration",
            "exam"

        }


        score += (
            0.5 *
            len(
                overlap.intersection(
                    important_terms
                )
            )
        )


        if score >= min_score:

            scored.append(
                (
                    score,
                    doc
                )
            )


    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )


    return [
        doc
        for score, doc
        in scored[:top_k]
    ]


# ============================================================
# ROUTER
# ============================================================

def classify_query(question):

    q = question.lower().strip()


    # --------------------------------------------------------
    # Greeting / casual
    # --------------------------------------------------------

    casual_patterns = [

        r"^(hi|hii|hiii|hiiii|hey|heyy|hello|helo|hlo)$",

        r"^what('?s| is) your name",

        r"^who (are|r) you",

        r"^what (are|r) you",

        r"^what do you do",

        r"^what can you do",

        r"^sup$",

        r"^wsp$",

        r"^how are you",

        r"^are you dumb",

        r"^r u dumb",

        r"^what is your mom",

        r"^what('?s| is) your family",

        r"^where does your family"

    ]


    for pattern in casual_patterns:

        if re.search(
            pattern,
            q
        ):

            return "casual"


    # --------------------------------------------------------
    # Weather / unrelated
    # --------------------------------------------------------

    out_of_scope_terms = [

        "weather",
        "temperature outside",
        "cricket score",
        "football score",
        "stock price",
        "bitcoin",
        "movie recommendation",
        "dating",
        "recipe",
        "joke"

    ]


    if any(
        term in q
        for term in out_of_scope_terms
    ):

        return "out_of_scope"


    # --------------------------------------------------------
    # Website / university information
    # --------------------------------------------------------

    website_terms = [

        "admission",
        "admissions",
        "apply",
        "application",
        "join vu",
        "join vidyashilp",
        "how do i join",
        "how can i join",
        "programmes",
        "programs",
        "programme",
        "program",
        "btech",
        "b.tech",
        "bms",
        "b.m.s",
        "economics",
        "psychology",
        "data science",
        "ai/ml",
        "artificial intelligence",
        "machine learning",
        "faculty",
        "professor",
        "professors",
        "address",
        "location",
        "phone number",
        "contact number",
        "contact details",
        "email",
        "campus",
        "school of",
        "what courses does vu offer",
        "courses does vu offer"

    ]


    if any(
        term in q
        for term in website_terms
    ):

        return "website"


    # --------------------------------------------------------
    # Academic questions
    # --------------------------------------------------------

    academic_terms = [

        "cgpa",
        "credit",
        "credits",
        "attendance",
        "exam",
        "course",
        "courses",
        "semester",
        "prerequisite",
        "prerequisites",
        "minor",
        "major",
        "eligibility",
        "eligible",
        "graduate",
        "graduation",
        "degree",
        "progress",
        "progression",
        "failed",
        "fail",
        "backlog",
        "register",
        "registration",
        "withdraw",
        "withdrawal",
        "corequisite",
        "corequisite",
        "academic",
        "course offering",
        "semester offering",
        "can i take",
        "can i register",
        "can i write",
        "requirements"

    ]


    if any(
        term in q
        for term in academic_terms
    ):

        return "academic"


    # --------------------------------------------------------
    # Follow-up / context-dependent
    # --------------------------------------------------------

    short_followups = [

        "yes",
        "no",
        "maybe",
        "3rd year",
        "third year",
        "2nd year",
        "second year",
        "1st year",
        "first year",
        "4th year",
        "fourth year",
        "7th sem",
        "7th semester",
        "8th sem",
        "8th semester",
        "that's me",
        "im in 3rd year",
        "i am in 3rd year",
        "i'm in 3rd year"

    ]


    if (
        q in short_followups
        or len(q.split()) <= 5
    ):

        if st.session_state.messages:

            return "followup"


    # --------------------------------------------------------
    # General university question
    # --------------------------------------------------------

    university_terms = [

        "vu",
        "vidyashilp",
        "university",
        "student"

    ]


    if any(
        term in q
        for term in university_terms
    ):

        return "academic"


    return "academic"


# ============================================================
# FOLLOW-UP CONTEXT
# ============================================================

def get_recent_conversation():

    history = []

    for msg in st.session_state.messages[-6:]:

        role = msg.get(
            "role",
            ""
        )

        content = msg.get(
            "content",
            ""
        )

        if role in [
            "user",
            "assistant"
        ]:

            history.append(
                f"{role.upper()}: {content}"
            )


    return "\n".join(history)


# ============================================================
# PROFILE
# ============================================================

with st.sidebar:

    st.markdown(
        '<p class="vu-sidebar-section">'
        'Student Profile'
        '</p>',
        unsafe_allow_html=True
    )


    include_profile = st.checkbox(
        "Include my profile in queries",
        value=True
    )


    program = st.text_input(
        "Program",
        value="BMS"
    )


    year = st.selectbox(
        "Year",
        [
            "Not specified",
            "1st Year",
            "2nd Year",
            "3rd Year",
            "4th Year"
        ]
    )


    semester = st.selectbox(
        "Semester",
        [
            "Not specified",
            "1st Semester",
            "2nd Semester",
            "3rd Semester",
            "4th Semester",
            "5th Semester",
            "6th Semester",
            "7th Semester",
            "8th Semester"
        ]
    )


    credits = st.number_input(
        "Completed credits",
        min_value=0,
        max_value=250,
        value=45
    )


    cgpa = st.number_input(
        "CGPA",
        min_value=0.0,
        max_value=10.0,
        value=7.5,
        step=0.1
    )


    if include_profile:

        st.markdown(
            f"""
            <div class="vu-profile-badge">

                <span>{program}</span><br>

                {year} · {semester}<br>

                <span>{credits}</span> credits
                · CGPA <span>{cgpa}</span>

            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        '<hr class="vu-divider">',
        unsafe_allow_html=True
    )


    # API KEY

    st.markdown(
        '<p class="vu-sidebar-section">'
        'API Key'
        '</p>',
        unsafe_allow_html=True
    )


    api_key = None

    try:

        api_key = st.secrets.get(
            "GROQ_API_KEY"
        )

    except Exception:

        api_key = None


    if not api_key:

        api_key = st.text_input(
            "Groq API key",
            type="password",
            placeholder="gsk_…"
        )


    st.markdown(
        '<hr class="vu-divider">',
        unsafe_allow_html=True
    )


    # STATUS

    st.markdown(
        f"""
        <div class="vu-status">

            <strong>{len(knowledge_base)}</strong>
            academic chunks indexed

            <br>

            <strong>{len(website_base)}</strong>
            VU website chunks indexed

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown("")


    if st.button(
        "🗑 Clear conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.pending_question = None

        st.rerun()


# ============================================================
# PROFILE TEXT
# ============================================================

profile_text = ""

if include_profile:

    profile_text = f"""
Student profile:

Program: {program}

Year: {year}

Semester: {semester}

Completed credits: {credits}

CGPA: {cgpa}
"""


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """

You are the Vidyashilp University AI Academic Advisor.

Your job is to help students with university academic and university-information questions.

IMPORTANT SOURCE RULES:

1. Academic regulations, eligibility, progression, attendance, credits,
   graduation requirements, prerequisites, course registration and semester
   rules MUST be answered from the university-provided academic documents
   whenever those documents contain the information.

2. Official VU website information may be used for:
   - admissions
   - application process
   - programme information
   - current programme descriptions
   - faculty information
   - campus/contact information
   - general university information

3. Never use general world knowledge to invent university rules.

4. Never invent:
   - course codes
   - credits
   - prerequisites
   - attendance thresholds
   - CGPA rules
   - graduation requirements
   - transfer rules
   - programme rules

5. If the provided sources do not contain enough information,
   clearly say that the available information is insufficient.

6. If a student-specific answer requires information that is missing,
   ask for only the missing information.

7. If two official sources conflict, explicitly mention the conflict.
   Do not silently choose one.

8. Do not make unsupported recommendations.
   If a student asks "Which minor should I choose?",
   explain the documented options and ask for relevant academic
   information if a personalized recommendation requires it.

9. If the student gives a follow-up answer such as:
   "3rd year", "BMS", "yes", or "that's me",
   use the previous conversation to understand what they are answering.

10. Never forget the student's original question simply because they
    answered a follow-up question.

11. Be concise and useful.

12. Use bullet points for multiple items.

13. If the student is stressed about academic problems,
    respond empathetically before giving the factual answer.

14. For fees and payments, direct the student to the Finance/Accounts office.

15. For staff-specific administrative matters, direct the student
    to the relevant department office.

16. If the student asks about mental health or medical matters,
    do not provide professional advice. Encourage them to contact
    the appropriate university support service.

17. For casual conversation, do not search the academic documents.

18. If information comes from the website, make it clear that it is
    from the official VU website.

19. Do not claim that a website page is a university academic regulation
    unless the source itself is an academic regulation.

20. Answer naturally. Do not sound robotic.
"""


# ============================================================
# DIRECT CASUAL RESPONSE
# ============================================================

def casual_response(question):

    q = question.lower().strip()


    if (
        q.startswith("what is your mom")
        or
        q.startswith("what's your mom")
        or
        "your family" in q
    ):

        return (
            "I don't have a family or personal life 😄. "
            "I'm the Vidyashilp University AI Academic Advisor, "
            "and I'm here to help with university-related questions."
        )


    if (
        "are you dumb" in q
        or
        "r u dumb" in q
    ):

        return (
            "Haha, hopefully not 😄. "
            "If I get something wrong, tell me and I'll check "
            "the available university information again."
        )


    return (
        "Hi! I'm the Vidyashilp University AI Academic Advisor. "
        "I can help with courses, credits, prerequisites, "
        "attendance, graduation requirements, semester planning, "
        "admissions and general VU information. "
        "What can I help you with?"
    )


# ============================================================
# OUT OF SCOPE RESPONSE
# ============================================================

def out_of_scope_response():

    return (
        "I’m focused on Vidyashilp University academic and "
        "university-related information. I can help with courses, "
        "credits, prerequisites, attendance, graduation, "
        "semester planning, admissions and VU information."
    )


# ============================================================
# WEBSITE RETRIEVAL
# ============================================================

def retrieve_website(
    query,
    top_k=5
):

    return retrieve(
        query,
        website_base,
        top_k=top_k,
        min_score=1.0
    )


# ============================================================
# ACADEMIC RETRIEVAL
# ============================================================

def retrieve_academic(
    query,
    top_k=6
):

    return retrieve(
        query,
        knowledge_base,
        top_k=top_k,
        min_score=1.5
    )


# ============================================================
# COMBINE FOLLOW-UP QUESTION
# ============================================================

def build_contextual_question(question):

    history = get_recent_conversation()


    if not history:

        return question


    # For very short follow-ups, combine with previous question

    if len(
        question.split()
    ) <= 6:

        previous_user_questions = [

            msg["content"]

            for msg in st.session_state.messages[:-1]

            if msg.get("role") == "user"

        ]


        if previous_user_questions:

            previous = previous_user_questions[-1]

            return (
                f"Previous student question: {previous}\n"
                f"Student follow-up: {question}"
            )


    return question


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    question,
    retrieved_docs,
    source_type="academic"
):

    if not api_key:

        return (
            "Please enter your Groq API key in the sidebar "
            "to get started."
        )


    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    context_parts = []


    for doc in retrieved_docs:

        if source_type == "website":

            context_parts.append(
                f"""
[SOURCE: Official VU Website]
[NAME: {doc['filename']}]
[URL: {doc.get('url', '')}]
[ID: {doc['id']}]

{doc['text']}
"""
            )

        else:

            context_parts.append(
                f"""
[SOURCE: University Academic Document]
[ID: {doc['id']}]

{doc['text']}
"""
            )


    context = "\n\n".join(
        context_parts
    )


    if not context:

        context = (
            "NO RELEVANT SOURCE INFORMATION WAS FOUND."
        )


    # --------------------------------------------------------
    # Conversation
    # --------------------------------------------------------

    conversation = get_recent_conversation()


    user_prompt = f"""

AVAILABLE SOURCE INFORMATION:

{context}


STUDENT PROFILE:

{profile_text}


RECENT CONVERSATION:

{conversation}


CURRENT STUDENT MESSAGE:

{question}


TASK:

Answer the student's current question.

Use the recent conversation when the current message is a
follow-up to an earlier question.

Use the student profile only when relevant.

Use ONLY the available source information for factual
university claims.

If the source information is insufficient, say that clearly.

Do not invent missing information.

If a follow-up answer completes an earlier question,
answer the original question rather than asking the student
to repeat it.

Keep the answer concise.
"""


    try:

        client = Groq(
            api_key=api_key
        )


        response = client.chat.completions.create(

            model=MODEL,

            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": user_prompt
                }

            ],

            temperature=0.0,

            max_tokens=900

        )


        answer = (
            response
            .choices[0]
            .message
            .content
        )


        if answer:

            return answer


        return (
            "I couldn't generate a response. "
            "Please try asking the question again."
        )


    except Exception as e:

        return (
            "Error connecting to the AI service: "
            f"{str(e)}"
        )


# ============================================================
# GIBBERISH CHECK
# ============================================================

def is_gibberish(prompt):

    prompt = prompt.strip()


    if not prompt:

        return True


    words = prompt.split()


    for word in words:

        if len(word) > 40:

            return True


    letters = re.findall(
        r"[a-zA-Z]",
        prompt
    )


    if len(prompt) > 8 and letters:

        diversity = len(
            set(
                c.lower()
                for c in letters
            )
        )


        if (
            diversity /
            len(letters)
        ) < 0.08:

            return True


    return False


# ============================================================
# SUGGESTIONS
# ============================================================

SUGGESTIONS = [

    "What are the minimum credits required to graduate?",

    "What is the attendance requirement per course?",

    "Can I register for a course if I failed a prerequisite?",

    "How is CGPA calculated and what is the grading scale?",

    "What courses are offered in the upcoming semester?",

    "How can I apply to Vidyashilp University?"

]


# ============================================================
# PROCESS QUESTION
# ============================================================

def process_question(prompt):

    prompt = prompt.strip()


    if not prompt:

        return (
            "",
            [],
            "none"
        )


    # --------------------------------------------------------
    # Gibberish
    # --------------------------------------------------------

    if is_gibberish(prompt):

        return (

            "I couldn't understand that. "
            "Please ask a clear question about "
            "VU, your courses, credits, "
            "prerequisites, attendance, "
            "graduation or admissions.",

            [],

            "none"

        )


    # --------------------------------------------------------
    # Route question
    # --------------------------------------------------------

    route = classify_query(
        prompt
    )


    # --------------------------------------------------------
    # Casual
    # --------------------------------------------------------

    if route == "casual":

        return (
            casual_response(prompt),
            [],
            "casual"
        )


    # --------------------------------------------------------
    # Out of scope
    # --------------------------------------------------------

    if route == "out_of_scope":

        return (
            out_of_scope_response(),
            [],
            "out_of_scope"
        )


    # --------------------------------------------------------
    # Follow-up
    # --------------------------------------------------------

    contextual_question = (
        build_contextual_question(prompt)
    )


    # --------------------------------------------------------
    # WEBSITE
    # --------------------------------------------------------

    if route == "website":

        docs = retrieve_website(
            contextual_question,
            top_k=5
        )


        if not docs:

            return (

                "I couldn't find enough information about "
                "that on the official VU website pages "
                "currently available to me. "
                "Please check the relevant VU office or "
                "official programme page.",

                [],

                "website"

            )


        answer = generate_answer(

            contextual_question,

            docs,

            source_type="website"

        )


        return (
            answer,
            docs,
            "website"
        )


    # --------------------------------------------------------
    # ACADEMIC
    # --------------------------------------------------------

    docs = retrieve_academic(
        contextual_question,
        top_k=6
    )


    if not docs:

        return (

            "I don't have enough information in the "
            "available university academic documents "
            "to answer that accurately. "
            "Please provide the relevant course/program "
            "details or ask me a more specific academic question.",

            [],

            "academic"

        )


    answer = generate_answer(

        contextual_question,

        docs,

        source_type="academic"

    )


    return (
        answer,
        docs,
        "academic"
    )


# ============================================================
# SUGGESTION BUTTONS
# ============================================================

if not st.session_state.messages:

    st.markdown(
        '<p class="vu-suggest-label">'
        'Try asking'
        '</p>',
        unsafe_allow_html=True
    )


    cols = st.columns(2)


    for i, suggestion in enumerate(
        SUGGESTIONS
    ):

        with cols[
            i % 2
        ]:

            if st.button(
                suggestion,
                key=f"sug_{i}",
                use_container_width=True
            ):

                st.session_state.pending_question = (
                    suggestion
                )

                st.rerun()


# ============================================================
# PROCESS PENDING SUGGESTION
# ============================================================

if st.session_state.pending_question:

    prompt = (
        st.session_state.pending_question
    )

    st.session_state.pending_question = None


    st.session_state.messages.append({

        "role": "user",

        "content": prompt

    })


    with st.spinner(
        "Checking university information…"
    ):

        answer, sources, source_type = (
            process_question(prompt)
        )


    st.session_state.messages.append({

        "role": "assistant",

        "content": answer,

        "sources": sources,

        "source_type": source_type

    })


    st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for msg in st.session_state.messages:

    role = msg.get(
        "role",
        ""
    )

    content = msg.get(
        "content",
        ""
    )


    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    if role == "user":

        safe_content = html.escape(
            content
        )


        st.markdown(

            f"""
            <div class="vu-row-user">

                <div class="vu-msg-user">

                    {safe_content}

                </div>

            </div>
            """,

            unsafe_allow_html=True

        )


    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    else:

        # Allow markdown generated by the model
        # but do not inject raw HTML from sources.

        st.markdown(

            f"""
            <div class="vu-row-bot">

                <div class="vu-msg-bot">

                    {content}

                </div>

            </div>
            """,

            unsafe_allow_html=True

        )


        sources = msg.get(
            "sources",
            []
        )


        source_type = msg.get(
            "source_type",
            "academic"
        )


        if sources:

            if source_type == "website":

                chips = "".join(

                    f'''
                    <span class="vu-web-chip">
                        🌐 {html.escape(
                            s["filename"]
                        )}
                    </span>
                    '''

                    for s in sources

                )

            else:

                chips = "".join(

                    f'''
                    <span class="vu-source-chip">
                        📄 {html.escape(
                            s["filename"]
                        )}
                    </span>
                    '''

                    for s in sources

                )


            with st.expander(
                "Sources used",
                expanded=False
            ):

                st.markdown(
                    chips,
                    unsafe_allow_html=True
                )


                for s in sources:

                    source_name = html.escape(
                        s["filename"]
                    )


                    source_id = html.escape(
                        s["id"]
                    )


                    preview = html.escape(
                        s["text"][:400]
                    )


                    st.markdown(

                        f"""
                        **[{source_id}]**
                        — {source_name}
                        """
                    )


                    st.caption(
                        preview + "…"
                    )


                    if source_type == "website":

                        url = s.get(
                            "url",
                            ""
                        )


                        if url:

                            st.markdown(
                                f"[Open official VU source]({url})"
                            )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Message VU Advisor…"
)


if prompt:

    st.session_state.messages.append({

        "role": "user",

        "content": prompt

    })


    with st.spinner(
        "Checking university information…"
    ):

        answer, sources, source_type = (
            process_question(prompt)
        )


    st.session_state.messages.append({

        "role": "assistant",

        "content": answer,

        "sources": sources,

        "source_type": source_type

    })


    st.rerun()
