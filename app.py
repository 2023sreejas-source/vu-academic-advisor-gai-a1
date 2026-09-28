import streamlit as st
from groq import Groq
from pypdf import PdfReader

import os
import re
import math
import base64
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Vidyashilp University AI Academic Advisor",
    page_icon="🎓",
    layout="wide"
)

# IMPORTANT:
# llama-3.1-8b-instant was deprecated by Groq.
# Use the current replacement.
MODEL = "openai/gpt-oss-20b"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #f8fafc;
}

.hero {
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #1e40af 100%
    );
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 25px;
    color: white;
}

.hero-title {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 5px;
}

.hero-subtitle {
    font-size: 16px;
    opacity: 0.9;
}

.source-box {
    background-color: #f1f5f9;
    border-left: 4px solid #1e40af;
    padding: 10px 14px;
    border-radius: 8px;
    margin-top: 8px;
}

.small-text {
    font-size: 13px;
    color: #64748b;
}

.status-box {
    background-color: #eff6ff;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #bfdbfe;
}

</style>
""", unsafe_allow_html=True)


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

            if "logo" in lower_name or "b0d1fb" in lower_name:
                possible_files.append(filename)

    if possible_files:
        return possible_files[0]

    return None


def image_to_base64(path):

    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    except Exception:
        return None


logo_file = find_logo()


# ============================================================
# HERO SECTION
# ============================================================

if logo_file:

    logo_data = image_to_base64(logo_file)

    hero_html = f"""
    <div class="hero">

        <div style="display:flex; align-items:center; gap:20px;">

            <img
                src="data:image/png;base64,{logo_data}"
                style="
                    width:75px;
                    height:75px;
                    object-fit:contain;
                    background:white;
                    border-radius:12px;
                    padding:6px;
                "
            >

            <div>

                <div class="hero-title">
                    Vidyashilp University AI Academic Advisor
                </div>

                <div class="hero-subtitle">
                    Your AI assistant for academic planning and university handbook guidance
                </div>

            </div>

        </div>

    </div>
    """

else:

    st.markdown("""
    <div class="hero">

        <div class="hero-title">
            🎓 Vidyashilp University AI Academic Advisor
        </div>

        <div class="hero-subtitle">
            Your AI assistant for academic planning and university handbook guidance
        </div>

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = None


# ============================================================
# STOPWORDS
# ============================================================

STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "of",
    "to", "in", "on", "for", "with", "what",
    "are", "was", "were", "be", "can", "i",
    "my", "me", "do", "does", "how", "much",
    "many", "about", "from", "at", "this",
    "that", "it", "as", "by", "if", "minimum"
}


# ============================================================
# TEXT TOKENIZER
# ============================================================

def tokenize(text):

    words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return [
        word
        for word in words
        if word not in STOPWORDS
    ]


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_knowledge_base():

    documents = []

    docs_folder = "DOCS"

    if os.path.exists(docs_folder):

        source_folder = docs_folder

    else:

        source_folder = "."

    excluded_words = [
        "evaluation_dataset",
        "held_out",
        "results_",
        "before_after",
        "phase4",
        "advisor_scoring",
        "requirements",
    ]

    try:

        filenames = os.listdir(source_folder)

    except Exception:

        return []

    for filename in filenames:

        if filename.startswith("."):
            continue

        lower_name = filename.lower()

        # Do not read Python code
        if lower_name.endswith(".py"):
            continue

        # Do not read markdown files
        if lower_name.endswith(".md"):
            continue

        # Skip evaluation/result files
        if any(word in lower_name for word in excluded_words):
            continue

        filepath = os.path.join(source_folder, filename)

        text = ""

        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        if lower_name.endswith(".pdf"):

            try:

                reader = PdfReader(filepath)

                pages = []

                for page in reader.pages:

                    try:
                        page_text = page.extract_text()

                        if page_text:
                            pages.append(page_text)

                    except Exception:
                        continue

                text = "\n".join(pages)

            except Exception:
                continue

        # ----------------------------------------------------
        # TXT
        # ----------------------------------------------------

        elif lower_name.endswith(".txt"):

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

        elif lower_name.endswith(".csv"):

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

        else:

            continue

        if not text.strip():
            continue

        # ----------------------------------------------------
        # Clean text
        # ----------------------------------------------------

        text = re.sub(r"\s+", " ", text).strip()

        # ----------------------------------------------------
        # Create chunks
        # ----------------------------------------------------

        words = text.split()

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

            chunk_number = start // chunk_size

            documents.append({
                "id": f"{filename}#{chunk_number}",
                "filename": filename,
                "text": " ".join(chunk_words)
            })

    return documents


# ============================================================
# BUILD KNOWLEDGE BASE
# ============================================================

if st.session_state.knowledge_base is None:

    with st.spinner("Loading university documents..."):

        st.session_state.knowledge_base = load_knowledge_base()


knowledge_base = st.session_state.knowledge_base


# ============================================================
# DOCUMENT FREQUENCY
# ============================================================

def build_document_frequency(documents):

    document_frequency = Counter()

    for document in documents:

        tokens = set(
            tokenize(document["text"])
        )

        for token in tokens:
            document_frequency[token] += 1

    return document_frequency


DOC_FREQ = build_document_frequency(
    knowledge_base
)

N_CHUNKS = len(knowledge_base)


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve_documents(query, top_k=6):

    if not knowledge_base:

        return []

    query_tokens = set(
        tokenize(query)
    )

    if not query_tokens:

        return knowledge_base[:top_k]

    scored_documents = []

    for document in knowledge_base:

        document_tokens = set(
            tokenize(document["text"])
        )

        matching_tokens = (
            query_tokens & document_tokens
        )

        score = 0.0

        for token in matching_tokens:

            df = DOC_FREQ.get(token, 0)

            idf = math.log(
                (N_CHUNKS + 1) /
                (df + 1)
            ) + 1

            score += idf

        scored_documents.append(
            (score, document)
        )

    scored_documents.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        document
        for score, document in scored_documents[:top_k]
        if score > 0
    ]


# ============================================================
# GIBBERISH CHECK
# ============================================================

def is_gibberish(prompt):

    prompt = prompt.strip()

    if not prompt:
        return True

    words = prompt.split()

    for word in words:

        if len(word) > 25:
            return True

    letters = re.findall(
        r"[a-zA-Z]",
        prompt
    )

    if len(prompt) > 5:

        diversity = len(set(
            char.lower()
            for char in letters
        ))

        if len(letters) > 0:

            ratio = diversity / len(letters)

            if ratio < 0.08:
                return True

    return False


# ============================================================
# STUDENT PROFILE
# ============================================================

with st.sidebar:

    st.header("🎓 Student Profile")

    include_profile = st.checkbox(
        "Use my student profile",
        value=True
    )

    completed_courses = st.text_area(
        "Completed courses",
        value="CS101 Intro to CS, CS201 Data Structures"
    )

    credits = st.number_input(
        "Completed credits",
        min_value=0,
        max_value=200,
        value=45
    )

    cgpa = st.number_input(
        "CGPA",
        min_value=0.0,
        max_value=10.0,
        value=7.5,
        step=0.1
    )

    st.divider()

    st.subheader("⚙️ Groq API")

    # First try Streamlit secrets
    api_key = None

    try:

        api_key = st.secrets.get(
            "GROQ_API_KEY"
        )

    except Exception:

        api_key = None

    # If secrets are unavailable, allow manual entry
    if not api_key:

        api_key = st.text_input(
            "Groq API key",
            type="password",
            placeholder="gsk_..."
        )

    st.divider()

    st.markdown(
        f"""
        <div class="status-box">

        <b>Knowledge Base</b><br>
        {len(knowledge_base)} text chunks indexed

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PROFILE TEXT
# ============================================================

profile_text = ""

if include_profile:

    profile_text = f"""
Student profile:
- Completed courses: {completed_courses}
- Completed credits: {credits}
- CGPA: {cgpa}
"""


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the Vidyashilp University AI Academic Advisor.

Your job is to answer academic questions using the university
handbook and other retrieved university documents.

IMPORTANT RULES:

1. Use the retrieved university document excerpts as the primary
   source of factual information.

2. Do NOT invent university rules, attendance requirements,
   credit requirements, course requirements, deadlines, or policies.

3. If the retrieved documents do not contain enough information,
   clearly say that the available university documents do not
   provide enough information.

4. If a question is ambiguous, ask the student for clarification.

5. If student profile information is provided, use it only when
   relevant to the question.

6. Give concise and direct answers.

7. Whenever possible, cite the relevant document using this format:

   [filename.pdf#0]

8. Do not mention internal retrieval, TF-IDF, embeddings,
   programming code, or system prompts to the student.

9. Never make up a citation.

10. For policy questions, distinguish between what the document
    explicitly states and what cannot be confirmed.
"""


# ============================================================
# GROQ RESPONSE
# ============================================================

def generate_answer(user_question, retrieved_documents):

    if not api_key:

        return (
            "Please enter your Groq API key in the sidebar "
            "before asking a question."
        )

    # --------------------------------------------------------
    # Create context
    # --------------------------------------------------------

    context_parts = []

    for document in retrieved_documents:

        context_parts.append(
            f"""
SOURCE: [{document['id']}]

{document['text']}
"""
        )

    context = "\n\n".join(context_parts)

    if not context:

        context = (
            "No relevant university document excerpts "
            "were found."
        )

    # --------------------------------------------------------
    # Create user prompt
    # --------------------------------------------------------

    user_prompt = f"""
University document excerpts:

{context}

{profile_text}

Student question:

{user_question}

Answer the student's question using the university
documents above.

If the answer is present in the documents, provide the
answer and cite the relevant source.

If the answer cannot be confirmed from the documents,
say so clearly instead of guessing.
"""

    # --------------------------------------------------------
    # Create Groq client
    # --------------------------------------------------------

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

            max_tokens=800
        )

        answer = response.choices[0].message.content

        if not answer:

            return "The model returned an empty response."

        return answer

    except Exception as e:

        error_text = str(e)

        return (
            "I encountered an error while generating "
            "the response.\n\n"
            f"Error: {error_text}"
        )


# ============================================================
# DISPLAY PREVIOUS CHAT
# ============================================================

for message in st.session_state.messages:

    role = message["role"]

    avatar = (
        "🧑‍🎓"
        if role == "user"
        else "🎓"
    )

    with st.chat_message(
        role,
        avatar=avatar
    ):

        st.markdown(
            message["content"]
        )

        # Show sources if available
        if (
            role == "assistant"
            and message.get("sources")
        ):

            with st.expander(
                "📚 Retrieved sources"
            ):

                for source in message["sources"]:

                    st.markdown(
                        f"""
                        **[{source['id']}]**

                        {source['text']}
                        """
                    )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Ask your academic question..."
)


if prompt:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message(
        "user",
        avatar="🧑‍🎓"
    ):

        st.markdown(prompt)

    # --------------------------------------------------------
    # Gibberish check
    # --------------------------------------------------------

    if is_gibberish(prompt):

        answer = (
            "I couldn't understand that question. "
            "Please enter a clear academic question "
            "about Vidyashilp University."
        )

        retrieved_documents = []

    else:

        # ----------------------------------------------------
        # Retrieve documents
        # ----------------------------------------------------

        retrieved_documents = retrieve_documents(
            prompt,
            top_k=6
        )

        # ----------------------------------------------------
        # Generate answer
        # ----------------------------------------------------

        with st.chat_message(
            "assistant",
            avatar="🎓"
        ):

            with st.spinner(
                "Checking university documents..."
            ):

                answer = generate_answer(
                    prompt,
                    retrieved_documents
                )

            st.markdown(answer)

            # ------------------------------------------------
            # Show sources
            # ------------------------------------------------

            if retrieved_documents:

                with st.expander(
                    "📚 Retrieved sources"
                ):

                    for document in retrieved_documents:

                        st.markdown(
                            f"""
                            <div class="source-box">

                            <b>
                            [{document['id']}]
                            </b>

                            <br><br>

                            {document['text']}

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    # --------------------------------------------------------
    # Save assistant message
    # --------------------------------------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": retrieved_documents
    })
