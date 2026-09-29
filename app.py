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
    background: linear-gradient(135deg, #8b0000, #b5121b);
    padding: 18px 28px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    gap: 18px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
}

.vu-header-logo {
    width: 65px;
    height: 65px;
    object-fit: contain;
    background: white;
    border-radius: 10px;
    padding: 4px;
}

.vu-header-title {
    color: white !important;
    font-size: 28px;
    font-weight: 700;
    margin: 0 !important;
}

.vu-header-sub {
    color: #f8dede !important;
    font-size: 14px;
    margin: 5px 0 0 0 !important;
}

.vu-header-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #55d66b;
    border-radius: 50%;
    margin-right: 5px;
}


/* CHAT */

.chat-user {
    background: #ffffff;
    padding: 14px 18px;
    border-radius: 14px;
    margin: 10px 0;
    border: 1px solid #e2e5ea;
}

.chat-assistant {
    background: #fff8f8;
    padding: 16px 18px;
    border-radius: 14px;
    margin: 10px 0 18px 0;
    border-left: 4px solid #a00000;
}

.chat-label {
    font-size: 12px;
    font-weight: 700;
    color: #777;
    margin-bottom: 6px;
}


/* SOURCE BOX */

.source-box {
    background: #ffffff;
    border: 1px solid #e1e4e8;
    border-radius: 10px;
    padding: 10px 12px;
    margin-top: 8px;
    font-size: 12px;
}

.source-academic {
    color: #8b0000;
    font-weight: 600;
}

.source-website {
    color: #174a8b;
    font-weight: 600;
}


/* PROFILE */

.profile-card {
    background: white;
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #e2e5ea;
    margin-bottom: 12px;
}


/* SUGGESTIONS */

.suggestion-button button {
    border-radius: 10px !important;
}


/* SIDEBAR */

[data-testid="stSidebar"] {
    background-color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = "openai/gpt-oss-20b"

EXCLUDED_FILES = [
    "advisor_eval_results",
    "phase4_summary_metrics",
    "evaluation",
    "eval_results",
    "results"
]

WEBSITE_CACHE_SECONDS = 3600


# ============================================================
# DEFAULT WEBSITE SOURCES
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


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = []

if "website_knowledge_base" not in st.session_state:
    st.session_state.website_knowledge_base = []

if "website_loaded" not in st.session_state:
    st.session_state.website_loaded = False

if "academic_loaded" not in st.session_state:
    st.session_state.academic_loaded = False


# ============================================================
# LOGO
# ============================================================

def find_logo():

    possible_files = []

    for filename in os.listdir("."):

        if filename.startswith("."):
            continue

        lower_name = filename.lower()

        if (
            lower_name.endswith(".png")
            or lower_name.endswith(".jpg")
            or lower_name.endswith(".jpeg")
        ):

            if "logo" in lower_name:
                possible_files.append(filename)

    if possible_files:
        return possible_files[0]

    return None


def image_to_base64(path):

    try:

        with open(path, "rb") as f:
            image_bytes = f.read()

        return base64.b64encode(image_bytes).decode()

    except Exception:
        return None


# ============================================================
# VU HEADER
# ============================================================

def display_header():

    logo_file = find_logo()

    if logo_file:

        logo_base64 = image_to_base64(logo_file)

        if logo_base64:

            extension = logo_file.lower().split(".")[-1]

            if extension == "jpg":
                extension = "jpeg"

            logo_html = (
                f'<img class="vu-header-logo" '
                f'src="data:image/{extension};base64,{logo_base64}">'
            )

        else:

            logo_html = ""

    else:

        logo_html = ""

    header_html = f"""
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
    """

    # IMPORTANT:
    # unsafe_allow_html=True is required so Streamlit
    # renders the image/header instead of displaying
    # the HTML code as plain text.

    st.markdown(
        header_html,
        unsafe_allow_html=True
    )


display_header()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🎓 Student Profile")

    st.caption(
        "Enter basic information to help the advisor "
        "understand your academic context."
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

    cgpa = st.number_input(
        "CGPA",
        min_value=0.0,
        max_value=10.0,
        value=7.5,
        step=0.1
    )

    credits = st.number_input(
        "Completed Credits",
        min_value=0,
        max_value=300,
        value=45,
        step=1
    )

    st.markdown("---")

    st.markdown("### 🔑 Groq API Key")

    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="Enter your Groq API key"
    )

    st.markdown("---")

    if st.button(
        "🔄 Reload Knowledge Base",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.session_state.knowledge_base = []
        st.session_state.website_knowledge_base = []

        st.session_state.academic_loaded = False
        st.session_state.website_loaded = False

        st.rerun()


# ============================================================
# FILE HELPERS
# ============================================================

def should_exclude_file(filename):

    lower_name = filename.lower()

    for word in EXCLUDED_FILES:

        if word in lower_name:
            return True

    return False


# ============================================================
# TEXT EXTRACTION
# ============================================================

def read_pdf(path):

    text = ""

    try:

        reader = PdfReader(path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception:
        pass

    return text


def read_text_file(path):

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            return f.read()

    except Exception:

        return ""


def read_csv_file(path):

    try:

        import csv

        text = ""

        with open(
            path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            reader = csv.reader(f)

            for row in reader:

                text += " | ".join(row) + "\n"

        return text

    except Exception:

        return ""


def read_excel_file(path):

    try:

        from openpyxl import load_workbook

        workbook = load_workbook(
            path,
            data_only=True
        )

        text = ""

        for sheet in workbook.worksheets:

            text += f"\nSHEET: {sheet.title}\n"

            for row in sheet.iter_rows(
                values_only=True
            ):

                values = []

                for value in row:

                    if value is not None:

                        values.append(str(value))

                if values:

                    text += " | ".join(values) + "\n"

        return text

    except Exception:

        return ""


# ============================================================
# DOCUMENT LOADING
# ============================================================

def load_academic_documents():

    documents = []

    root = "."

    for filename in os.listdir(root):

        if filename.startswith("."):
            continue

        if should_exclude_file(filename):
            continue

        path = os.path.join(root, filename)

        if not os.path.isfile(path):
            continue

        lower_name = filename.lower()

        text = ""

        if lower_name.endswith(".pdf"):

            text = read_pdf(path)

        elif lower_name.endswith(".txt"):

            text = read_text_file(path)

        elif lower_name.endswith(".csv"):

            text = read_csv_file(path)

        elif (
            lower_name.endswith(".xlsx")
            or lower_name.endswith(".xlsm")
        ):

            text = read_excel_file(path)

        if text.strip():

            documents.append(
                {
                    "source": filename,
                    "text": text
                }
            )

    return documents


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(
    text,
    chunk_words=150,
    overlap_words=30
):

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_words,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        if end == len(words):
            break

        start = max(
            end - overlap_words,
            start + 1
        )

    return chunks


def build_academic_knowledge_base():

    documents = load_academic_documents()

    knowledge = []

    for document in documents:

        chunks = chunk_text(
            document["text"],
            chunk_words=150,
            overlap_words=30
        )

        for i, chunk in enumerate(chunks):

            knowledge.append(
                {
                    "text": chunk,
                    "source": document["source"],
                    "chunk": i + 1,
                    "type": "academic"
                }
            )

    return knowledge


# ============================================================
# WEBSITE SOURCES
# ============================================================

def load_website_sources():

    filename = "website_sources.json"

    if os.path.exists(filename):

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            if isinstance(data, list) and data:

                return data

        except Exception:

            pass

    return DEFAULT_WEBSITE_SOURCES


# ============================================================
# WEBSITE FETCHING
# ============================================================

@st.cache_data(
    ttl=WEBSITE_CACHE_SECONDS,
    show_spinner=False
)
def fetch_webpage(url):

    try:

        headers = {
            "User-Agent":
            "Mozilla/5.0 Academic Advisor Bot"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "svg"
            ]
        ):

            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    except Exception:

        return ""


def build_website_knowledge_base():

    sources = load_website_sources()

    knowledge = []

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

        text = fetch_webpage(url)

        if not text:
            continue

        chunks = chunk_text(
            text,
            chunk_words=180,
            overlap_words=40
        )

        for i, chunk in enumerate(chunks):

            knowledge.append(
                {
                    "text": chunk,
                    "source": name,
                    "url": url,
                    "chunk": i + 1,
                    "type": "website"
                }
            )

    return knowledge


# ============================================================
# LOAD KNOWLEDGE BASES
# ============================================================

if not st.session_state.academic_loaded:

    with st.spinner(
        "Loading university academic documents..."
    ):

        st.session_state.knowledge_base = (
            build_academic_knowledge_base()
        )

        st.session_state.academic_loaded = True


if not st.session_state.website_loaded:

    with st.spinner(
        "Loading official VU website sources..."
    ):

        st.session_state.website_knowledge_base = (
            build_website_knowledge_base()
        )

        st.session_state.website_loaded = True


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):

    return re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(
    query,
    knowledge_base,
    top_k=5,
    min_score=0.08
):

    if not knowledge_base:
        return []

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    query_counter = Counter(
        query_tokens
    )

    document_frequency = Counter()

    for item in knowledge_base:

        unique_tokens = set(
            tokenize(item["text"])
        )

        for token in unique_tokens:
            document_frequency[token] += 1

    total_documents = len(
        knowledge_base
    )

    scored = []

    for item in knowledge_base:

        document_tokens = tokenize(
            item["text"]
        )

        if not document_tokens:
            continue

        document_counter = Counter(
            document_tokens
        )

        score = 0.0

        for token, q_count in query_counter.items():

            if token not in document_counter:
                continue

            tf = (
                document_counter[token]
                /
                len(document_tokens)
            )

            df = document_frequency.get(
                token,
                1
            )

            idf = math.log(
                (1 + total_documents)
                /
                (1 + df)
            ) + 1

            score += tf * idf * q_count

        if score >= min_score:

            scored.append(
                (
                    score,
                    item
                )
            )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        item
        for score, item in scored[:top_k]
    ]


# ============================================================
# QUERY CLASSIFICATION
# ============================================================

def classify_query(query):

    q = query.lower().strip()

    # --------------------------------------------------------
    # CASUAL
    # --------------------------------------------------------

    casual_patterns = [
        "hi",
        "hello",
        "hey",
        "bro",
        "brooo",
        "good morning",
        "good afternoon",
        "good evening",
        "thanks",
        "thank you",
        "bye",
        "who are you",
        "what are you"
    ]

    if any(
        pattern in q
        for pattern in casual_patterns
    ):

        return "casual"


    # --------------------------------------------------------
    # OUT OF SCOPE
    # --------------------------------------------------------

    out_of_scope_patterns = [
        "weather",
        "temperature today",
        "rain today",
        "cricket score",
        "football score",
        "movie",
        "song",
        "joke",
        "politics"
    ]

    if any(
        pattern in q
        for pattern in out_of_scope_patterns
    ):

        return "out_of_scope"


    # --------------------------------------------------------
    # WEBSITE
    # --------------------------------------------------------

    website_patterns = [
        "apply",
        "application",
        "admission",
        "admissions",
        "join vu",
        "join vidyashilp",
        "how do i join",
        "how can i join",
        "how do i apply",
        "how can i apply",
        "contact",
        "phone number",
        "email",
        "address",
        "campus",
        "location",
        "school",
        "faculty",
        "programme offered",
        "program offered",
        "programmes offered",
        "programs offered",
        "what courses are offered"
    ]

    if any(
        pattern in q
        for pattern in website_patterns
    ):

        return "website"


    # --------------------------------------------------------
    # ACADEMIC
    # --------------------------------------------------------

    academic_patterns = [
        "course",
        "courses",
        "credit",
        "credits",
        "cgpa",
        "gpa",
        "semester",
        "sem",
        "year",
        "minor",
        "major",
        "prerequisite",
        "prerequisite",
        "eligibility",
        "eligible",
        "attendance",
        "exam",
        "examination",
        "academic",
        "curriculum",
        "programme structure",
        "program structure",
        "course structure",
        "semester spread",
        "regulation",
        "policy",
        "student handbook",
        "bms",
        "btech",
        "b.tech",
        "data science",
        "artificial intelligence",
        "ai",
        "transfer",
        "shift",
        "progress",
        "failed",
        "passed",
        "backlog"
    ]

    if any(
        pattern in q
        for pattern in academic_patterns
    ):

        return "academic"


    # --------------------------------------------------------
    # FOLLOW-UP
    # --------------------------------------------------------

    if len(q.split()) <= 8:

        return "followup"


    # Default to academic because this is an
    # academic advisor.

    return "academic"


# ============================================================
# CONTEXTUAL FOLLOW-UP
# ============================================================

def build_contextual_question(query):

    if not st.session_state.messages:
        return query

    recent_user_messages = []

    for message in reversed(
        st.session_state.messages[:-1]
    ):

        if message["role"] == "user":

            recent_user_messages.append(
                message["content"]
            )

        if len(recent_user_messages) >= 2:
            break

    if not recent_user_messages:
        return query

    previous = " ".join(
        reversed(recent_user_messages)
    )

    return (
        f"Previous conversation context: "
        f"{previous}\n\n"
        f"Current question: {query}"
    )


# ============================================================
# PROFILE
# ============================================================

def get_student_profile():

    return f"""
Student profile:

Program: {program}
Year: {year}
Semester: {semester}
CGPA: {cgpa}
Completed Credits: {credits}
"""


# ============================================================
# DIRECT RESPONSES
# ============================================================

def get_direct_response(query):

    q = query.lower().strip()

    if (
        "mom" in q
        or "mother" in q
        or "family" in q
        or "dad" in q
        or "father" in q
    ):

        return (
            "I’m an AI Academic Advisor, so I don’t have a "
            "family or personal life. 😄 I can help you with "
            "Vidyashilp University academic questions, courses, "
            "eligibility, programmes, admissions, and related "
            "university information."
        )

    if (
        "are u dumb" in q
        or "are you dumb" in q
        or "stupid" in q
    ):

        return (
            "No 😄 — but I can definitely make mistakes. "
            "For academic questions, I’ll use the available "
            "VU documents and official VU website sources rather "
            "than guessing."
        )

    if (
        q == "hi"
        or q == "hello"
        or q == "hey"
        or q.startswith("bro")
    ):

        return (
            "Hey! 👋 I’m your VU Academic Advisor. "
            "Ask me about courses, minors, prerequisites, "
            "eligibility, semesters, credits, admissions, "
            "or other academic questions."
        )

    return None


# ============================================================
# OUT OF SCOPE RESPONSE
# ============================================================

def get_out_of_scope_response(query):

    return (
        "I’m focused on Vidyashilp University academic and "
        "university-related information. I don’t have a reliable "
        "live source for that question, so I don’t want to guess."
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

def build_system_prompt():

    return f"""
You are an AI Academic Advisor for Vidyashilp University.

Your job is to answer student questions using the supplied
university academic documents and official Vidyashilp University
website information.

{get_student_profile()}

IMPORTANT RULES:

1. Do not invent university rules.

2. Do not assume information that is not supported by the
   retrieved sources.

3. Academic university documents are the PRIMARY source for:
   - academic regulations
   - eligibility
   - prerequisites
   - credits
   - course requirements
   - semester structures
   - progression rules
   - academic policies
   - attendance rules
   - programme structures

4. Official VU website sources are SUPPLEMENTARY sources for:
   - admissions
   - application process
   - programme descriptions
   - schools
   - faculty/general information
   - campus/contact information

5. If the supplied sources do not contain enough information,
   clearly say that the information is insufficient.

6. Do not make up an answer just to satisfy the student.

7. If a student's question depends on information that is
   missing from their profile, ask for that specific information.

8. Use the student's profile when answering eligibility or
   progression questions.

9. If the question refers to a previous question in the
   conversation, maintain the conversation context.

10. Do not forget the student's current year or semester when
    answering follow-up questions.

11. If two sources conflict, explicitly mention the conflict
    instead of silently choosing one.

12. Keep answers clear and practical.

13. When possible, mention the source name at the end.

14. Never claim that a rule exists unless it is supported by
    the retrieved context.

15. If the question is unrelated to university academics,
    politely say that it is outside your scope.

Answer only using the information provided in the context below.
"""


# ============================================================
# CONTEXT BUILDER
# ============================================================

def build_context(
    academic_results,
    website_results
):

    context_parts = []

    for item in academic_results:

        context_parts.append(
            f"""
ACADEMIC SOURCE:
Source: {item["source"]}
Chunk: {item["chunk"]}

{item["text"]}
"""
        )

    for item in website_results:

        context_parts.append(
            f"""
OFFICIAL VU WEBSITE SOURCE:
Source: {item["source"]}
URL: {item["url"]}
Chunk: {item["chunk"]}

{item["text"]}
"""
        )

    if not context_parts:

        return (
            "No relevant source information was retrieved."
        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# SOURCE DISPLAY
# ============================================================

def display_sources(
    academic_results,
    website_results
):

    if not academic_results and not website_results:
        return

    st.markdown(
        "<div class='source-box'>"
        "<b>Sources used</b>"
        "</div>",
        unsafe_allow_html=True
    )

    for item in academic_results:

        source = html.escape(
            item["source"]
        )

        st.markdown(
            f"""
            <div class="source-box">
                <span class="source-academic">
                    📄 Academic document
                </span>
                <br>
                {source}
            </div>
            """,
            unsafe_allow_html=True
        )

    for item in website_results:

        source = html.escape(
            item["source"]
        )

        url = html.escape(
            item["url"]
        )

        st.markdown(
            f"""
            <div class="source-box">
                <span class="source-website">
                    🌐 Official VU website
                </span>
                <br>
                <a href="{url}" target="_blank">
                    {source}
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# GROQ RESPONSE
# ============================================================

def generate_answer(
    client,
    user_question,
    context
):

    messages = [
        {
            "role": "system",
            "content": build_system_prompt()
        }
    ]

    # Add a small amount of conversation history
    # so follow-up questions maintain context.

    for message in st.session_state.messages[-6:]:

        messages.append(
            {
                "role": message["role"],
                "content": message["content"]
            }
        )

    messages.append(
        {
            "role": "user",
            "content": f"""
Retrieved information:

{context}

Student question:

{user_question}

Answer the student clearly.
"""
        }
    )

    response = client.chat.completions.create(

        model=MODEL,

        messages=messages,

        temperature=0.1,

        max_tokens=900
    )

    return response.choices[0].message.content


# ============================================================
# MAIN TITLE
# ============================================================

st.markdown(
    """
    <div style="
        font-size:18px;
        font-weight:600;
        color:#333;
        margin-bottom:8px;
    ">
        Ask your academic question
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "I can help with VU courses, programmes, prerequisites, "
    "eligibility, credits, semesters, admissions and related "
    "university information."
)


# ============================================================
# KNOWLEDGE BASE STATUS
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        f"""
        <div class="profile-card">
        📚 <b>Academic sources:</b>
        {len(st.session_state.knowledge_base)}
        chunks
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="profile-card">
        🌐 <b>Official website:</b>
        {len(st.session_state.website_knowledge_base)}
        chunks
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SUGGESTIONS
# ============================================================

st.markdown("### 💡 Try asking")

suggestions = [

    "I want to join VU, how do I apply?",

    "What minors are available for BMS students?",

    "What is the minimum CGPA required to progress?",

    "What are the prerequisites for this course?"

]

suggestion_cols = st.columns(4)

for i, suggestion in enumerate(suggestions):

    with suggestion_cols[i]:

        if st.button(
            suggestion,
            key=f"suggestion_{i}",
            use_container_width=True
        ):

            st.session_state.pending_question = suggestion


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        st.markdown(
            f"""
            <div class="chat-user">
                <div class="chat-label">YOU</div>
                {html.escape(message["content"])}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        answer = message.get(
            "content",
            ""
        )

        st.markdown(
            f"""
            <div class="chat-assistant">
                <div class="chat-label">
                    VU AI ACADEMIC ADVISOR
                </div>
                {answer}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# USER INPUT
# ============================================================

user_question = st.chat_input(
    "Ask your academic question..."
)


# Handle suggestion buttons.

if (
    "pending_question" in st.session_state
    and st.session_state.pending_question
):

    user_question = (
        st.session_state.pending_question
    )

    st.session_state.pending_question = ""


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_question:

    user_question = user_question.strip()

    if not user_question:
        st.stop()

    # Add user message first so conversation history
    # is preserved.

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    # --------------------------------------------------------
    # DIRECT RESPONSES
    # --------------------------------------------------------

    direct_response = get_direct_response(
        user_question
    )

    if direct_response:

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": direct_response
            }
        )

        st.rerun()


    # --------------------------------------------------------
    # CLASSIFY
    # --------------------------------------------------------

    query_type = classify_query(
        user_question
    )


    # --------------------------------------------------------
    # OUT OF SCOPE
    # --------------------------------------------------------

    if query_type == "out_of_scope":

        answer = get_out_of_scope_response(
            user_question
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.rerun()


    # --------------------------------------------------------
    # API KEY CHECK
    # --------------------------------------------------------

    if not api_key:

        answer = (
            "Please enter your Groq API key in the sidebar "
            "before asking an academic question."
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.rerun()


    # --------------------------------------------------------
    # GROQ CLIENT
    # --------------------------------------------------------

    try:

        client = Groq(
            api_key=api_key
        )

    except Exception as e:

        answer = (
            "There was a problem connecting to Groq. "
            "Please check your API key."
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.rerun()


    # --------------------------------------------------------
    # CONTEXTUAL QUESTION
    # --------------------------------------------------------

    contextual_question = (
        build_contextual_question(
            user_question
        )
    )


    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    academic_results = []
    website_results = []


    if query_type == "website":

        website_results = retrieve(
            contextual_question,
            st.session_state.website_knowledge_base,
            top_k=5,
            min_score=0.015
        )


        # Also allow academic documents to support
        # programme-related questions.

        academic_results = retrieve(
            contextual_question,
            st.session_state.knowledge_base,
            top_k=3,
            min_score=0.015
        )


    elif query_type == "academic":

        academic_results = retrieve(
            contextual_question,
            st.session_state.knowledge_base,
            top_k=6,
            min_score=0.015
        )


        # Website can supplement academic questions
        # when relevant.

        website_results = retrieve(
            contextual_question,
            st.session_state.website_knowledge_base,
            top_k=2,
            min_score=0.015
        )


    elif query_type == "followup":

        academic_results = retrieve(
            contextual_question,
            st.session_state.knowledge_base,
            top_k=6,
            min_score=0.015
        )

        website_results = retrieve(
            contextual_question,
            st.session_state.website_knowledge_base,
            top_k=3,
            min_score=0.015
        )


    # --------------------------------------------------------
    # NO RELEVANT INFORMATION
    # --------------------------------------------------------

    if (
        not academic_results
        and not website_results
    ):

        answer = (
            "I don't have enough reliable information in the "
            "available VU sources to answer that accurately. "
            "I don't want to guess or invent a university rule."
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.rerun()


    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    context = build_context(
        academic_results,
        website_results
    )


    # --------------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------------

    try:

        with st.spinner(
            "Thinking..."
        ):

            answer = generate_answer(
                client,
                contextual_question,
                context
            )

    except Exception as e:

        answer = (
            "I couldn't generate the answer because of a "
            "temporary model/API error.\n\n"
            "Please check your Groq API key and try again."
        )


    # --------------------------------------------------------
    # SAVE ANSWER
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    st.rerun()
