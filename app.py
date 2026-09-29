# ============================================================
# VU AI ACADEMIC ADVISOR
# Vidyashilp University
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

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #f0f2f5;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #f0f2f5;
    }

    [data-testid="block-container"] {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }

    .sidebar-title {
        color: #8b0000;
        font-size: 21px;
        font-weight: 700;
    }

    .sidebar-subtitle {
        color: #555555;
        font-size: 13px;
        line-height: 1.5;
    }

    .info-box {
        background-color: white;
        padding: 18px 20px;
        border-radius: 14px;
        border-left: 5px solid #8b0000;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .assistant-box {
        background-color: white;
        padding: 16px 18px;
        border-radius: 14px;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 8px;
    }

    .source-label {
        font-size: 12px;
        color: #666666;
        margin-top: 5px;
    }

    .footer-text {
        text-align: center;
        color: #777777;
        font-size: 12px;
        padding-top: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONSTANTS
# ============================================================

MODEL = "openai/gpt-oss-20b"

ACADEMIC_EXTENSIONS = (
    ".pdf",
    ".txt",
    ".csv",
    ".xlsx",
    ".xls"
)

EXCLUDED_FILES = (
    "advisor_eval",
    "eval_results",
    "phase4",
    "summary_metrics",
    "website_sources"
)


# ============================================================
# OFFICIAL VU WEBSITE SOURCES
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
        "name": "VU Data Science",
        "url": "https://vidyashilp.edu.in/data-science/"
    },
    {
        "name": "VU AI and Machine Learning",
        "url": "https://vidyashilp.edu.in/schools/b_tech_ai_ml/"
    },
    {
        "name": "VU B.Tech",
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
# LOGO
# ============================================================

def find_logo():

    possible_files = []

    for filename in os.listdir("."):

        if filename.startswith("."):
            continue

        lower_name = filename.lower()

        if lower_name.endswith(
            (".png", ".jpg", ".jpeg")
        ):
            possible_files.append(filename)

    logo_files = [
        filename
        for filename in possible_files
        if "logo" in filename.lower()
    ]

    if logo_files:
        return logo_files[0]

    if possible_files:
        return possible_files[0]

    return None


logo_path = find_logo()


# ============================================================
# HEADER
# ============================================================

header_col1, header_col2 = st.columns(
    [1, 7],
    vertical_alignment="center"
)

with header_col1:

    if logo_path:

        st.image(
            logo_path,
            width=90
        )

    else:

        st.markdown(
            "🎓"
        )


with header_col2:

    st.markdown(
        "## Vidyashilp University"
    )

    st.markdown(
        "🟢 **AI Academic Advisor · Online**"
    )


st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">🎓 Student Profile</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Enter basic information to help the advisor understand '
        'your academic context.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    program = st.selectbox(
        "Program",
        [
            "BMS",
            "B.Tech",
            "B.A. Economics",
            "B.A.",
            "Other / Not specified"
        ]
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

    completed_credits = st.number_input(
        "Completed Credits",
        min_value=0,
        max_value=300,
        value=45,
        step=1
    )

    cgpa = st.number_input(
        "CGPA",
        min_value=0.0,
        max_value=10.0,
        value=7.5,
        step=0.1
    )

    st.markdown("---")

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# GROQ API KEY
# ============================================================

def get_api_key():

    try:

        secret_key = st.secrets.get(
            "GROQ_API_KEY",
            ""
        )

        if secret_key:
            return secret_key

    except Exception:
        pass

    return os.getenv(
        "GROQ_API_KEY",
        ""
    )


api_key = get_api_key()


# ============================================================
# STUDENT PROFILE
# ============================================================

student_profile = {
    "program": program,
    "year": year,
    "semester": semester,
    "completed_credits": completed_credits,
    "cgpa": cgpa
}


# ============================================================
# FILE TEXT EXTRACTION
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = text.replace(
        "\x00",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_pdf_text(filepath):

    pages = []

    try:

        reader = PdfReader(filepath)

        for page in reader.pages:

            try:

                text = page.extract_text()

                if text:
                    pages.append(text)

            except Exception:
                continue

    except Exception:

        return ""

    return clean_text(
        "\n".join(pages)
    )


def extract_txt_text(filepath):

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            return clean_text(
                file.read()
            )

    except Exception:

        return ""


def extract_csv_text(filepath):

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            return clean_text(
                file.read()
            )

    except Exception:

        return ""


def extract_excel_text(filepath):

    try:

        from openpyxl import load_workbook

        workbook = load_workbook(
            filepath,
            read_only=True,
            data_only=True
        )

        all_text = []

        for sheet in workbook.worksheets:

            all_text.append(
                f"Sheet: {sheet.title}"
            )

            for row in sheet.iter_rows(
                values_only=True
            ):

                values = []

                for value in row:

                    if value is not None:

                        values.append(
                            str(value)
                        )

                if values:

                    all_text.append(
                        " | ".join(values)
                    )

        return clean_text(
            "\n".join(all_text)
        )

    except Exception:

        return ""


def extract_file_text(filepath):

    extension = os.path.splitext(
        filepath
    )[1].lower()

    if extension == ".pdf":

        return extract_pdf_text(
            filepath
        )

    if extension == ".txt":

        return extract_txt_text(
            filepath
        )

    if extension == ".csv":

        return extract_csv_text(
            filepath
        )

    if extension in [".xlsx", ".xls"]:

        return extract_excel_text(
            filepath
        )

    return ""


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(
    text,
    chunk_size=150,
    overlap=30
):

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():

            chunks.append(
                chunk.strip()
            )

        if end >= len(words):

            break

        start = end - overlap

    return chunks


# ============================================================
# LOAD ACADEMIC DOCUMENTS
# ============================================================

def load_academic_documents():

    documents = []

    for filename in sorted(
        os.listdir(".")
    ):

        if filename.startswith("."):
            continue

        lower_name = filename.lower()

        if not lower_name.endswith(
            ACADEMIC_EXTENSIONS
        ):
            continue

        if any(
            excluded in lower_name
            for excluded in EXCLUDED_FILES
        ):
            continue

        filepath = os.path.join(
            ".",
            filename
        )

        text = extract_file_text(
            filepath
        )

        if not text:
            continue

        chunks = chunk_text(
            text,
            chunk_size=150,
            overlap=30
        )

        for index, chunk in enumerate(
            chunks
        ):

            documents.append(
                {
                    "text": chunk,
                    "source": filename,
                    "type": "academic",
                    "chunk": index + 1
                }
            )

    return documents


# ============================================================
# WEBSITE SOURCES
# ============================================================

def load_website_sources():

    source_file = "website_sources.json"

    if os.path.exists(
        source_file
    ):

        try:

            with open(
                source_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if (
                isinstance(data, list)
                and len(data) > 0
            ):

                return data

        except Exception:

            pass

    return DEFAULT_WEBSITE_SOURCES


# ============================================================
# FETCH WEBSITE
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def fetch_webpage(url):

    try:

        headers = {
            "User-Agent":
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120 Safari/537.36"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

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
                "svg",
                "iframe"
            ]
        ):

            tag.decompose()

        text = soup.get_text(
            separator=" "
        )

        return clean_text(
            text
        )

    except Exception:

        return ""


# ============================================================
# LOAD WEBSITE KNOWLEDGE
# ============================================================

def load_website_documents():

    documents = []

    sources = load_website_sources()

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

        text = fetch_webpage(
            url
        )

        if not text:
            continue

        chunks = chunk_text(
            text,
            chunk_size=180,
            overlap=40
        )

        for index, chunk in enumerate(
            chunks
        ):

            documents.append(
                {
                    "text": chunk,
                    "source": name,
                    "url": url,
                    "type": "website",
                    "chunk": index + 1
                }
            )

    return documents


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

if not st.session_state.knowledge_loaded:

    with st.spinner(
        "Loading academic information..."
    ):

        st.session_state.academic_kb = (
            load_academic_documents()
        )

        st.session_state.knowledge_loaded = True


if not st.session_state.website_loaded:

    with st.spinner(
        "Loading official VU information..."
    ):

        st.session_state.website_kb = (
            load_website_documents()
        )

        st.session_state.website_loaded = True


academic_kb = (
    st.session_state.academic_kb
)

website_kb = (
    st.session_state.website_kb
)


# ============================================================
# TOKENIZER
# ============================================================

def tokenize(text):

    text = text.lower()

    tokens = re.findall(
        r"[a-zA-Z0-9]+",
        text
    )

    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "am",
        "i",
        "me",
        "my",
        "to",
        "of",
        "in",
        "on",
        "for",
        "and",
        "or",
        "can",
        "could",
        "would",
        "should",
        "do",
        "does",
        "did",
        "be",
        "it",
        "this",
        "that",
        "with",
        "from",
        "at",
        "as",
        "what",
        "which",
        "how",
        "where",
        "when",
        "why",
        "you",
        "your"
    }

    return [
        token
        for token in tokens
        if token not in stop_words
    ]


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(
    query,
    documents,
    top_k=5,
    minimum_score=0.05
):

    if not documents:

        return []

    query_tokens = tokenize(
        query
    )

    if not query_tokens:

        return []

    query_counter = Counter(
        query_tokens
    )

    document_frequency = Counter()

    tokenized_documents = []

    for document in documents:

        tokens = tokenize(
            document["text"]
        )

        token_set = set(
            tokens
        )

        for token in token_set:

            document_frequency[
                token
            ] += 1

        tokenized_documents.append(
            tokens
        )

    total_documents = len(
        documents
    )

    scored = []

    for index, document in enumerate(
        documents
    ):

        tokens = tokenized_documents[
            index
        ]

        if not tokens:

            continue

        token_counter = Counter(
            tokens
        )

        score = 0.0

        for token, query_count in (
            query_counter.items()
        ):

            if token not in token_counter:

                continue

            tf = (
                token_counter[token]
                / len(tokens)
            )

            df = document_frequency.get(
                token,
                0
            )

            idf = (
                math.log(
                    (total_documents + 1)
                    / (df + 1)
                )
                + 1
            )

            score += (
                tf
                * idf
                * query_count
            )

        query_lower = query.lower()
        text_lower = document[
            "text"
        ].lower()

        important_phrases = [
            "minimum cgpa",
            "attendance",
            "eligibility",
            "eligible",
            "prerequisite",
            "prerequisites",
            "minor",
            "semester",
            "admission",
            "application",
            "course",
            "courses",
            "credits",
            "programme",
            "program",
            "transfer"
        ]

        for phrase in important_phrases:

            if (
                phrase in query_lower
                and phrase in text_lower
            ):

                score += 0.15

        if score >= minimum_score:

            scored.append(
                (
                    score,
                    document
                )
            )

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    results = []

    for score, document in scored[
        :top_k
    ]:

        result = dict(
            document
        )

        result["_score"] = score

        results.append(
            result
        )

    return results


# ============================================================
# QUERY CLASSIFICATION
# ============================================================

def classify_query(query):

    q = query.lower().strip()

    casual_patterns = [
        "hi",
        "hello",
        "hey",
        "bro",
        "brooo",
        "thanks",
        "thank you",
        "good morning",
        "good afternoon",
        "good evening",
        "who are you",
        "what are you",
        "are you dumb",
        "lol",
        "haha"
    ]

    for pattern in casual_patterns:

        if (
            q == pattern
            or q.startswith(
                pattern + " "
            )
        ):

            return "casual"

    personal_patterns = [
        "your mom",
        "your mother",
        "your family",
        "where does your family",
        "where is your family",
        "your dad",
        "your father",
        "your home"
    ]

    for pattern in personal_patterns:

        if pattern in q:

            return "personal"

    out_of_scope_patterns = [
        "weather",
        "temperature today",
        "cricket",
        "football score",
        "movie",
        "restaurant",
        "stock price",
        "politics"
    ]

    for pattern in out_of_scope_patterns:

        if pattern in q:

            return "out_of_scope"

    website_patterns = [
        "admission",
        "apply",
        "application",
        "how do i join",
        "how can i join",
        "join vu",
        "contact",
        "phone number",
        "email",
        "address",
        "campus",
        "location",
        "where is vu",
        "where is vidyashilp",
        "programmes offered",
        "programme offered",
        "programs offered",
        "program offered",
        "about vu",
        "vidyashilp university"
    ]

    for pattern in website_patterns:

        if pattern in q:

            return "website"

    academic_patterns = [
        "course",
        "courses",
        "subject",
        "subjects",
        "semester",
        "credit",
        "credits",
        "cgpa",
        "gpa",
        "eligibility",
        "eligible",
        "prerequisite",
        "prerequisites",
        "minor",
        "major",
        "attendance",
        "exam",
        "examination",
        "progress",
        "year",
        "bms",
        "btech",
        "b.tech",
        "economics",
        "data science",
        "ai",
        "machine learning",
        "curriculum",
        "programme structure",
        "program structure",
        "transfer",
        "shift",
        "next sem",
        "next semester",
        "final year",
        "7th sem",
        "8th sem"
    ]

    for pattern in academic_patterns:

        if pattern in q:

            return "academic"

    return "academic"


# ============================================================
# FOLLOW-UP CONTEXT
# ============================================================

def get_previous_user_question():

    previous_messages = (
        st.session_state.messages[:-1]
    )

    for message in reversed(
        previous_messages
    ):

        if (
            message.get("role")
            == "user"
        ):

            return message.get(
                "content",
                ""
            )

    return ""


def is_short_followup(query):

    tokens = tokenize(
        query
    )

    if len(tokens) <= 5:

        return True

    followup_phrases = [
        "i am in",
        "im in",
        "i'm in",
        "my year is",
        "my semester is",
        "what about",
        "and what",
        "then what",
        "why then"
    ]

    for phrase in followup_phrases:

        if phrase in query.lower():

            return True

    return False


def build_contextual_question(query):

    if not is_short_followup(
        query
    ):

        return query

    previous = get_previous_user_question()

    if not previous:

        return query

    return (
        "Previous student question: "
        + previous
        + "\n"
        + "Student follow-up: "
        + query
    )


# ============================================================
# PROFILE TEXT
# ============================================================

def profile_to_text():

    return f"""
Student profile:

Program: {student_profile["program"]}
Year: {student_profile["year"]}
Semester: {student_profile["semester"]}
Completed credits: {student_profile["completed_credits"]}
CGPA: {student_profile["cgpa"]}
"""


# ============================================================
# DIRECT RESPONSES
# ============================================================

def direct_response(
    query,
    category
):

    q = query.lower().strip()

    if category == "casual":

        if (
            "are you dumb" in q
            or "dumb" in q
        ):

            return (
                "😂 Nope — I'm here to help with "
                "your VU academic questions. Ask me "
                "about courses, eligibility, semesters, "
                "credits, admissions or prerequisites."
            )

        if "thank" in q:

            return (
                "You're welcome! 😊 "
                "Ask me if you need help with "
                "anything related to VU academics."
            )

        return (
            "Hey! 👋 I'm your Vidyashilp University "
            "AI Academic Advisor. What would you "
            "like to know?"
        )

    if category == "personal":

        return (
            "I don't have a personal family or home "
            "because I'm an AI. 😊\n\n"
            "But I can help you with Vidyashilp "
            "University academic questions."
        )

    if category == "out_of_scope":

        return (
            "That is outside my academic-advisor scope. "
            "I can help with VU programmes, courses, "
            "prerequisites, eligibility, credits, "
            "semesters, admissions and related "
            "academic information."
        )

    return None


# ============================================================
# CREATE RETRIEVAL CONTEXT
# ============================================================

def create_context(
    academic_results,
    website_results
):

    context_parts = []

    if academic_results:

        context_parts.append(
            "ACADEMIC UNIVERSITY DOCUMENTS:"
        )

        for index, result in enumerate(
            academic_results,
            start=1
        ):

            context_parts.append(
                f"""
[Academic Source {index}]
File: {result["source"]}

Content:
{result["text"]}
"""
            )

    if website_results:

        context_parts.append(
            "OFFICIAL VU WEBSITE:"
        )

        for index, result in enumerate(
            website_results,
            start=1
        ):

            context_parts.append(
                f"""
[Official Website Source {index}]
Page: {result["source"]}
URL: {result.get("url", "")}

Content:
{result["text"]}
"""
            )

    return "\n".join(
        context_parts
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

def build_system_prompt():

    return f"""
You are the AI Academic Advisor for Vidyashilp University.

Your role is to help students understand university
academic information using the available university
documents and official VU website information.

{profile_to_text()}

SOURCE PRIORITY:

1. Academic university documents are the PRIMARY source for:
   - academic regulations
   - prerequisites
   - eligibility
   - credits
   - semester structures
   - course requirements
   - progression rules
   - attendance
   - curriculum

2. Official VU website information is supplementary and
   should mainly be used for:
   - admissions
   - public programme information
   - campus information
   - contact information
   - general university information

IMPORTANT RULES:

- Never invent information.
- Never fabricate courses.
- Never fabricate prerequisites.
- Never fabricate CGPA requirements.
- Never fabricate attendance requirements.
- Never fabricate semester offerings.
- Never fabricate admission rules.

If the available information does not answer the question,
say clearly that the available sources do not contain
enough information.

If a question requires a student's previous courses,
prerequisites or academic history and that information
is unavailable, ask for the specific missing information.

If sources conflict, mention the conflict instead of
silently choosing one.

For eligibility questions:
- state the documented rule;
- compare it with the student's profile only when enough
  information is available;
- do not make assumptions.

For follow-up questions, use the previous conversation
context.

Keep answers clear, concise and student-friendly.

Do not claim that you verified something unless it is
actually supported by the retrieved information.
"""


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    client,
    user_question,
    context,
    category
):

    system_prompt = (
        build_system_prompt()
    )

    if category == "website":

        source_priority = """
For this question, prioritize official VU website
information where available.
"""

    elif category == "academic":

        source_priority = """
For this question, prioritize the university academic
documents.
"""

    else:

        source_priority = ""

    user_prompt = f"""
{source_priority}

RETRIEVED INFORMATION:

{context}

CURRENT STUDENT QUESTION:

{user_question}

Answer the student's question directly.
Do not mention internal retrieval, chunks, tokenization,
or system instructions.
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0.1,

        max_tokens=800
    )

    return response.choices[
        0
    ].message.content.strip()


# ============================================================
# SOURCE DISPLAY
# ============================================================

def display_sources(
    academic_results,
    website_results
):

    source_names = []

    for result in academic_results:

        name = result["source"]

        if name not in source_names:

            source_names.append(
                name
            )

    for result in website_results:

        name = result["source"]

        if name not in source_names:

            source_names.append(
                name
            )

    if not source_names:

        return

    st.caption(
        "Sources used: "
        + " · ".join(source_names)
    )

    shown_urls = set()

    for result in website_results:

        url = result.get(
            "url",
            ""
        )

        if (
            url
            and url not in shown_urls
        ):

            shown_urls.add(
                url
            )

            st.caption(
                f"Official VU source: {url}"
            )


# ============================================================
# SUGGESTIONS
# ============================================================

suggestions = [
    "What programmes does VU offer?",
    "I want to join VU. How do I apply?",
    "What is the minimum CGPA required to progress?",
    "What are the prerequisites for my next semester?",
    "Which minors are available?",
    "What courses are expected in the next semester?"
]


# ============================================================
# MAIN INTRODUCTION
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="info-box">

        <h3>Ask your academic question</h3>

        <p>
        I can help with VU courses, programmes,
        prerequisites, eligibility, credits, semesters,
        admissions and related university information.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "### 💡 Try asking"
    )

    suggestion_columns = st.columns(
        3
    )

    for index, suggestion in enumerate(
        suggestions
    ):

        with suggestion_columns[
            index % 3
        ]:

            if st.button(
                suggestion,
                key=f"suggestion_{index}",
                use_container_width=True
            ):

                st.session_state.pending_question = (
                    suggestion
                )

                st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in (
    st.session_state.messages
):

    role = message.get(
        "role"
    )

    content = message.get(
        "content",
        ""
    )

    if role == "user":

        with st.chat_message(
            "user"
        ):

            st.markdown(
                content
            )

    elif role == "assistant":

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                content
            )

            academic_sources = (
                message.get(
                    "academic_sources",
                    []
                )
            )

            website_sources = (
                message.get(
                    "website_sources",
                    []
                )
            )

            if (
                academic_sources
                or website_sources
            ):

                display_sources(
                    academic_sources,
                    website_sources
                )


# ============================================================
# GET QUESTION
# ============================================================

pending_question = (
    st.session_state.pending_question
)

st.session_state.pending_question = None

if pending_question:

    user_question = pending_question

else:

    user_question = st.chat_input(
        "Ask your academic question..."
    )


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_question:

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_question
        )

    # --------------------------------------------------------
    # CLASSIFY QUESTION
    # --------------------------------------------------------

    category = classify_query(
        user_question
    )

    # --------------------------------------------------------
    # DIRECT RESPONSE
    # --------------------------------------------------------

    direct = direct_response(
        user_question,
        category
    )

    if direct:

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                direct
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": direct,
                "academic_sources": [],
                "website_sources": []
            }
        )

    else:

        # ----------------------------------------------------
        # API KEY CHECK
        # ----------------------------------------------------

        if not api_key:

            error_message = (
                "The advisor is not configured yet. "
                "Please contact the administrator."
            )

            with st.chat_message(
                "assistant"
            ):

                st.warning(
                    error_message
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "academic_sources": [],
                    "website_sources": []
                }
            )

        else:

            try:

                client = Groq(
                    api_key=api_key
                )

                # --------------------------------------------
                # FOLLOW-UP CONTEXT
                # --------------------------------------------

                contextual_question = (
                    build_contextual_question(
                        user_question
                    )
                )

                # --------------------------------------------
                # RETRIEVAL
                # --------------------------------------------

                if category == "website":

                    website_results = retrieve(
                        contextual_question,
                        website_kb,
                        top_k=6,
                        minimum_score=0.05
                    )

                    academic_results = retrieve(
                        contextual_question,
                        academic_kb,
                        top_k=3,
                        minimum_score=0.08
                    )

                else:

                    academic_results = retrieve(
                        contextual_question,
                        academic_kb,
                        top_k=6,
                        minimum_score=0.05
                    )

                    website_results = retrieve(
                        contextual_question,
                        website_kb,
                        top_k=3,
                        minimum_score=0.06
                    )

                # --------------------------------------------
                # CREATE CONTEXT
                # --------------------------------------------

                context = create_context(
                    academic_results,
                    website_results
                )

                # --------------------------------------------
                # GENERATE ANSWER
                # --------------------------------------------

                if not context.strip():

                    answer = (
                        "I don't have enough information "
                        "in the available VU academic "
                        "documents or official website "
                        "sources to answer that accurately."
                    )

                else:

                    with st.spinner(
                        "Thinking..."
                    ):

                        answer = generate_answer(
                            client,
                            contextual_question,
                            context,
                            category
                        )

                # --------------------------------------------
                # DISPLAY ANSWER
                # --------------------------------------------

                with st.chat_message(
                    "assistant"
                ):

                    st.markdown(
                        answer
                    )

                    if (
                        academic_results
                        or website_results
                    ):

                        display_sources(
                            academic_results,
                            website_results
                        )

                # --------------------------------------------
                # SAVE ANSWER
                # --------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "academic_sources":
                            academic_results,
                        "website_sources":
                            website_results
                    }
                )

            except Exception as error:

                error_message = (
                    "I couldn't process that request "
                    "right now. Please try again."
                )

                with st.chat_message(
                    "assistant"
                ):

                    st.error(
                        error_message
                    )

                    with st.expander(
                        "Technical details"
                    ):

                        st.code(
                            str(error)
                        )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "academic_sources": [],
                        "website_sources": []
                    }
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer-text">'
    'Vidyashilp University · AI Academic Advisor'
    '</div>',
    unsafe_allow_html=True
)
