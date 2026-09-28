
import streamlit as st
from groq import Groq
from pypdf import PdfReader
import os
import re
import math
import base64
from collections import Counter


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Vidyashilp University AI Academic Advisor",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>
.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
    border-radius: 18px;
    padding: 28px 32px;
    margin-bottom: 25px;
    color: white;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.20);
}

.hero-inner {
    display: flex;
    align-items: center;
    gap: 24px;
}

.hero-logo {
    width: 95px;
    height: 95px;
    object-fit: contain;
    background: white;
    border-radius: 12px;
    padding: 8px;
    flex-shrink: 0;
}

.hero-title {
    color: white !important;
    font-size: 2.1rem !important;
    font-weight: 700;
    margin: 0 !important;
    padding: 0 !important;
}

.hero-subtitle {
    color: #dbeafe !important;
    font-size: 1rem;
    margin-top: 8px;
    margin-bottom: 0;
}

.sidebar-logo {
    display: block;
    width: 140px;
    height: 100px;
    object-fit: contain;
    margin: 0 auto 15px auto;
}

.status-badge {
    background: #dcfce7;
    color: #166534;
    padding: 9px 12px;
    border-radius: 8px;
    font-weight: 600;
    text-align: center;
    margin: 10px 0;
}

.source-box {
    background: #f8fafc;
    border-left: 4px solid #1e40af;
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 10px;
    line-height: 1.5;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOGO DETECTION
# ============================================================

def find_logo():
    """
    Search the current directory for a PNG/JPG/JPEG file
    containing 'logo' or 'b0d1fb' in its filename.
    """

    valid_extensions = (".png", ".jpg", ".jpeg")

    try:
        for filename in os.listdir("."):

            if filename.startswith("."):
                continue

            lower_name = filename.lower()

            if not lower_name.endswith(valid_extensions):
                continue

            if "logo" in lower_name or "b0d1fb" in lower_name:
                return os.path.join(".", filename)

    except Exception:
        pass

    return None


def image_to_base64(image_path):
    """
    Convert the logo image into a base64 data URL.
    """

    if not image_path:
        return None

    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        extension = os.path.splitext(
            image_path
        )[1].lower()

        if extension == ".png":
            mime_type = "image/png"
        elif extension in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        else:
            mime_type = "image/png"

        return f"data:{mime_type};base64,{encoded}"

    except Exception:
        return None


LOGO_PATH = find_logo()
LOGO_BASE64 = image_to_base64(LOGO_PATH)


# ============================================================
# HERO HEADER
# ============================================================

if LOGO_BASE64:

    hero_html = (
        '<div class="hero-banner">'
        '<div class="hero-inner">'
        f'<img src="{LOGO_BASE64}" '
        'class="hero-logo" '
        'alt="Vidyashilp University Logo">'
        '<div>'
        '<h1 class="hero-title">'
        'Vidyashilp University AI Academic Advisor'
        '</h1>'
        '<p class="hero-subtitle">'
        'Your RAG-powered academic assistant for course, '
        'curriculum and academic guidance.'
        '</p>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        hero_html,
        unsafe_allow_html=True
    )

else:

    hero_html = (
        '<div class="hero-banner">'
        '<div>'
        '<h1 class="hero-title">'
        'Vidyashilp University AI Academic Advisor'
        '</h1>'
        '<p class="hero-subtitle">'
        'Your RAG-powered academic assistant for course, '
        'curriculum and academic guidance.'
        '</p>'
        '</div>'
        '</div>'
    )

    st.markdown(
        hero_html,
        unsafe_allow_html=True
    )


# ============================================================
# STOPWORDS
# ============================================================

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being",
    "but", "by", "can", "could", "did", "do", "does", "for",
    "from", "had", "has", "have", "he", "her", "here", "hers",
    "him", "his", "how", "i", "if", "in", "into", "is", "it",
    "its", "me", "my", "no", "not", "of", "on", "or", "our",
    "ours", "she", "should", "so", "some", "than", "that",
    "the", "their", "theirs", "them", "then", "there", "these",
    "they", "this", "those", "to", "too", "was", "we", "were",
    "what", "when", "where", "which", "who", "why", "will",
    "with", "would", "you", "your", "yours"
}


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):
    """
    Tokenize text using [a-z0-9]+ and remove stopwords.
    """

    tokens = re.findall(
        r"[a-z0-9]+",
        text.lower()
    )

    return [
        token
        for token in tokens
        if token not in STOPWORDS
    ]


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

@st.cache_data(show_spinner=False)
def load_knowledge_base():

    docs_directory = "DOCS"

    if os.path.isdir(docs_directory):
        base_directory = docs_directory
    else:
        base_directory = "."

    excluded_keywords = [
        "Evaluation_Dataset",
        "Held_Out",
        "results_",
        "before_after",
        "phase4",
        "advisor_scoring",
        "requirements"
    ]

    chunks = []

    try:
        filenames = os.listdir(base_directory)
    except Exception:
        filenames = []

    for filename in filenames:

        # Ignore hidden files.
        if filename.startswith("."):
            continue

        # Ignore Python and Markdown files.
        if filename.lower().endswith(".py"):
            continue

        if filename.lower().endswith(".md"):
            continue

        # Ignore evaluation-related files.
        if any(
            keyword.lower() in filename.lower()
            for keyword in excluded_keywords
        ):
            continue

        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension not in [".pdf", ".txt", ".csv"]:
            continue

        filepath = os.path.join(
            base_directory,
            filename
        )

        text = ""

        try:

            if extension == ".pdf":

                reader = PdfReader(filepath)

                pages = []

                for page in reader.pages:

                    page_text = page.extract_text()

                    if page_text:
                        pages.append(page_text)

                text = "\n".join(pages)

            else:

                with open(
                    filepath,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    text = file.read()

        except Exception:
            continue

        if not text.strip():
            continue

        # Normalize whitespace.
        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        words = text.split()

        # Approximately 120 words per chunk.
        chunk_size = 120

        for start in range(
            0,
            len(words),
            chunk_size
        ):

            chunk_words = words[
                start:start + chunk_size
            ]

            if not chunk_words:
                continue

            chunk_index = start // chunk_size

            chunk_id = (
                f"{filename}#{chunk_index}"
            )

            chunks.append(
                {
                    "id": chunk_id,
                    "filename": filename,
                    "text": " ".join(chunk_words)
                }
            )

    return chunks


# ============================================================
# BUILD DOCUMENT FREQUENCY INDEX
# ============================================================

@st.cache_data(show_spinner=False)
def build_tfidf_index(chunks):

    document_frequency = Counter()

    for chunk in chunks:

        tokens = set(
            tokenize(chunk["text"])
        )

        for token in tokens:
            document_frequency[token] += 1

    return document_frequency


# Load documents.
knowledge_base = load_knowledge_base()

# Build TF-IDF document frequency.
DOC_FREQ = build_tfidf_index(
    knowledge_base
)

N_CHUNKS = len(knowledge_base)


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_chunks(
    query,
    top_k=6
):

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    if not knowledge_base:
        return []

    query_tokens = set(query_tokens)

    scored_chunks = []

    for chunk in knowledge_base:

        chunk_tokens = set(
            tokenize(chunk["text"])
        )

        matching_tokens = (
            query_tokens.intersection(
                chunk_tokens
            )
        )

        score = 0.0

        for token in matching_tokens:

            score += (
                math.log(
                    (N_CHUNKS + 1)
                    /
                    (DOC_FREQ[token] + 1)
                )
                + 1
            )

        if score > 0:

            scored_chunks.append(
                (
                    score,
                    chunk
                )
            )

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        item[1]
        for item in scored_chunks[:top_k]
    ]


# ============================================================
# GIBBERISH GUARDRAIL
# ============================================================

def is_gibberish(prompt):

    if not prompt or not prompt.strip():

        return (
            True,
            "Please enter an academic question so I can help you."
        )

    cleaned = prompt.strip()

    # Character diversity ratio.
    unique_characters = len(
        set(cleaned.lower())
    )

    total_characters = len(cleaned)

    diversity_ratio = (
        unique_characters / total_characters
        if total_characters > 0
        else 0
    )

    if diversity_ratio < 0.2:

        return (
            True,
            "I couldn't understand that question. "
            "Please enter a clear academic question."
        )

    words = re.findall(
        r"\S+",
        cleaned
    )

    for word in words:

        clean_word = re.sub(
            r"^[^\w]+|[^\w]+$",
            "",
            word
        )

        if len(clean_word) > 25:

            return (
                True,
                "That question contains an unusually long word. "
                "Please rephrase it using simpler wording."
            )

    return False, None


# ============================================================
# GROQ API KEY
# ============================================================

def get_groq_api_key():

    # First try Streamlit secrets.
    try:

        secret_key = st.secrets.get(
            "GROQ_API_KEY",
            ""
        )

        if secret_key:
            return secret_key

    except Exception:
        pass

    # Otherwise use sidebar input.
    return st.session_state.get(
        "groq_key_input",
        ""
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # SIDEBAR LOGO
    # --------------------------------------------------------

    if LOGO_BASE64:

        sidebar_logo_html = (
            '<img '
            f'src="{LOGO_BASE64}" '
            'class="sidebar-logo" '
            'alt="Vidyashilp University Logo">'
        )

        st.markdown(
            sidebar_logo_html,
            unsafe_allow_html=True
        )

    st.header("🎓 Student Profile")

    st.caption(
        "Add your academic information to receive "
        "more relevant guidance."
    )

    # --------------------------------------------------------
    # GROQ API KEY
    # --------------------------------------------------------

    try:

        secret_key = st.secrets.get(
            "GROQ_API_KEY",
            ""
        )

    except Exception:

        secret_key = ""

    if secret_key:

        st.success(
            "Groq API key loaded from secrets."
        )

    else:

        st.text_input(
            "Groq API Key",
            type="password",
            placeholder="Enter your Groq API key",
            key="groq_key_input"
        )

    st.divider()

    # --------------------------------------------------------
    # STUDENT PROFILE
    # --------------------------------------------------------

    include_profile = st.checkbox(
        "Include Student Profile",
        value=True
    )

    completed_courses = st.text_input(
        "Completed Courses",
        value=(
            "CS101 Intro to CS, "
            "CS201 Data Structures"
        )
    )

    credits_earned = st.number_input(
        "Credits Earned",
        min_value=0,
        value=45,
        step=1
    )

    cgpa_status = st.text_input(
        "CGPA/Status",
        value=""
    )

    st.divider()

    # --------------------------------------------------------
    # KNOWLEDGE BASE STATUS
    # --------------------------------------------------------

    st.subheader("Knowledge Base")

    st.markdown(
        f'<div class="status-badge">'
        f'📚 {N_CHUNKS} active indexed text chunks'
        f'</div>',
        unsafe_allow_html=True
    )

    if N_CHUNKS > 0:

        st.caption(
            "Knowledge base loaded successfully."
        )

    else:

        st.warning(
            "No PDF, TXT, or CSV knowledge files were found."
        )


# ============================================================
# STUDENT PROFILE
# ============================================================

def build_student_profile():

    if not include_profile:
        return "Student Profile: Not provided."

    status = (
        cgpa_status.strip()
        if cgpa_status.strip()
        else "Not provided"
    )

    return f"""
Student Profile:
- Completed Courses: {completed_courses}
- Credits Earned: {credits_earned}
- CGPA/Status: {status}
""".strip()


student_profile = build_student_profile()


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the Vidyashilp University AI Academic Advisor.

Your job is to provide accurate academic guidance using ONLY the
provided Vidyashilp University handbook excerpts.

STRICT RULES:

1. Use only the provided handbook excerpts.
2. Do not use outside knowledge.
3. Do not invent university policies, courses, prerequisites,
   credit requirements, deadlines, faculty information, or rules.
4. If the handbook excerpts do not contain enough information,
   clearly state that the available handbook information is
   insufficient.
5. Ask a clarifying question when critical information is missing.
6. Use the Student Profile only when it helps determine course
   eligibility or academic relevance.
7. Never claim that a student is eligible for a course unless the
   provided handbook information supports that conclusion.
8. Cite handbook information using source tags such as:
   [filename.pdf#0]
9. Keep answers clear and student-friendly.
10. When multiple sources support an answer, cite the relevant
    source tags.
11. If the question is unrelated to Vidyashilp University academic
    guidance, politely explain that you are designed for academic
    advising.
"""


# ============================================================
# GENERATE GROQ RESPONSE
# ============================================================

def generate_answer(
    user_prompt,
    retrieved_chunks
):

    api_key = get_groq_api_key()

    if not api_key:

        return (
            "Please enter your Groq API key in the sidebar "
            "or configure GROQ_API_KEY in Streamlit secrets."
        )

    try:

        groq_client = Groq(
            api_key=api_key
        )

    except Exception as error:

        return (
            "I could not initialize the Groq client. "
            "Please check your API key.\n\n"
            f"Error: {error}"
        )

    # --------------------------------------------------------
    # CREATE HANDBOOK CONTEXT
    # --------------------------------------------------------

    handbook_parts = []

    for chunk in retrieved_chunks:

        handbook_parts.append(
            f"""
SOURCE: [{chunk["id"]}]
CONTENT:
{chunk["text"]}
"""
        )

    handbook_context = "\n".join(
        handbook_parts
    )

    if not handbook_context:

        handbook_context = (
            "No relevant handbook excerpts were retrieved."
        )

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    user_message = f"""
STUDENT PROFILE:

{student_profile}


HANDBOOK EXCERPTS:

{handbook_context}


STUDENT QUESTION:

{user_prompt}


Answer the student's question using only the handbook excerpts.

If the information is available, provide a direct and clear answer.

If the information is not available, say that the handbook excerpts
provided do not contain enough information.

Use source tags such as [filename.pdf#0] for factual claims.
"""

    # --------------------------------------------------------
    # GROQ CALL
    # --------------------------------------------------------

    try:

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.0,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as error:

        return (
            "I encountered an error while generating the response.\n\n"
            f"Error: {error}"
        )


# ============================================================
# DISPLAY RETRIEVED SOURCES
# ============================================================

def display_sources(
    retrieved_chunks
):

    if not retrieved_chunks:

        with st.expander(
            "📚 Retrieved Handbook Excerpts"
        ):

            st.info(
                "No matching handbook excerpts were found."
            )

        return

    with st.expander(
        "📚 Retrieved Handbook Excerpts"
    ):

        for chunk in retrieved_chunks:

            st.markdown(
                f'<div class="source-box">'
                f'<strong>[{chunk["id"]}]</strong>'
                f'<br><br>'
                f'{chunk["text"]}'
                f'</div>',
                unsafe_allow_html=True
            )


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message(
            "user",
            avatar="🧑‍🎓"
        ):

            st.markdown(
                message["content"]
            )

    else:

        with st.chat_message(
            "assistant",
            avatar="🎓"
        ):

            st.markdown(
                message["content"]
            )

            display_sources(
                message.get(
                    "retrieved_chunks",
                    []
                )
            )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Ask about courses, prerequisites, credits, curriculum, or academic rules..."
)


if prompt:

    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message(
        "user",
        avatar="🧑‍🎓"
    ):

        st.markdown(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # --------------------------------------------------------
    # GIBBERISH CHECK
    # --------------------------------------------------------

    gibberish, fallback_message = is_gibberish(
        prompt
    )

    if gibberish:

        retrieved_chunks = []

        answer = fallback_message

        with st.chat_message(
            "assistant",
            avatar="🎓"
        ):

            st.markdown(answer)

    else:

        # ----------------------------------------------------
        # RETRIEVE HANDBOOK CHUNKS
        # ----------------------------------------------------

        retrieved_chunks = retrieve_chunks(
            prompt,
            top_k=6
        )

        # ----------------------------------------------------
        # GENERATE RESPONSE
        # ----------------------------------------------------

        with st.chat_message(
            "assistant",
            avatar="🎓"
        ):

            with st.spinner(
                "Checking the university handbook..."
            ):

                answer = generate_answer(
                    prompt,
                    retrieved_chunks
                )

            st.markdown(answer)

            display_sources(
                retrieved_chunks
            )

    # --------------------------------------------------------
    # SAVE ASSISTANT RESPONSE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "retrieved_chunks": retrieved_chunks
        }
    )

