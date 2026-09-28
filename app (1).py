import streamlit as st
import os, re, math
from collections import Counter
from pypdf import PdfReader
from groq import Groq

# Page Setup
st.set_page_config(page_title="AI Academic Advisor", page_icon="🎓", layout="wide")
st.title("🎓 University AI Academic Advisor")

# API Key Handling (Reads from Streamlit Secrets or Sidebar Input)
api_key = st.secrets.get("GROQ_API_KEY", None)
if not api_key:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password", help="Get a free key at https://console.groq.com")

if not api_key:
    st.info("👈 Please enter a Groq API Key in the sidebar or set `GROQ_API_KEY` in Streamlit Secrets to proceed.")
    st.stop()

groq_client = Groq(api_key=api_key)

# 1. Load Knowledge Base & Build TF-IDF (Supports both root folder and DOCS subfolder)
@st.cache_resource
def load_knowledge_base():
    # Use 'DOCS' directory if it exists, otherwise scan the current folder '.'
    docs_dir = "DOCS" if os.path.exists("DOCS") else "."
    
    EXCLUDE_KEYWORDS = ["Evaluation_Dataset", "Held_Out", "results_", "before_after", 
                        "generalization_gap", "phase4", "advisor_scoring", "requirements"]
    
    kb = []
    for fname in os.listdir(docs_dir):
        # Skip hidden files, python scripts, requirements, and evaluation datasets
        if fname.startswith(".") or fname.endswith(".py") or fname.endswith(".md"):
            continue
        if any(k.lower() in fname.lower() for k in EXCLUDE_KEYWORDS):
            continue
            
        path = os.path.join(docs_dir, fname)
        text = ""
        try:
            if fname.lower().endswith(".pdf"):
                text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
            elif fname.lower().endswith((".txt", ".csv")):
                text = open(path, encoding="utf-8").read()
            else:
                continue
        except Exception:
            continue
        
        words = text.split()
        chunks = [" ".join(words[i:i+120]) for i in range(0, len(words), 120) if words[i:i+120]]
        for i, c in enumerate(chunks):
            kb.append({"id": f"{fname}#{i}", "source": fname, "text": c})
            
    return kb

KB = load_knowledge_base()

# Retrieval Engine
STOPWORDS = set("a an the is are was were be been to of in on for and or but if with as at by from".split())
def tokenize(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]

CHUNK_TOKENS = [set(tokenize(c["text"] + " " + c["source"])) for c in KB]
DOC_FREQ = Counter(t for toks in CHUNK_TOKENS for t in toks)
N_CHUNKS = len(KB) if len(KB) > 0 else 1

def retrieve(question, k=6):
    q_tokens = set(tokenize(question))
    scored = []
    for c, toks in zip(KB, CHUNK_TOKENS):
        score = sum(math.log((N_CHUNKS + 1) / (DOC_FREQ[t] + 1)) + 1 for t in q_tokens if t in toks)
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:k]]

# Guardrail Checkers (Deterministic filtering from Cell 5)
def is_gibberish(q):
    q_clean = re.sub(r'[^a-zA-Z0-9\s]', '', q.strip())
    if len(q_clean) == 0 or len(set(q_clean)) / len(q_clean) < 0.2:
        return True
    words = q_clean.split()
    return any(len(w) > 25 for w in words)

# Sidebar Configuration
st.sidebar.header("Student Profile Settings")
use_profile = st.sidebar.checkbox("Include Student Profile Context", value=True)
if use_profile:
    completed_courses = st.sidebar.text_input("Completed Courses", "CS101 Intro to CS, CS201 Data Structures")
    credits_earned = st.sidebar.number_input("Credits Earned", value=45)
    profile_str = f"Completed Courses: {completed_courses}, Credits Earned: {credits_earned}"
else:
    profile_str = "No profile context provided."

# Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask an academic advising question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Guardrail Filter
        if is_gibberish(prompt):
            resp_text = "I'm sorry, your input appears to be invalid or unreadable. Please ask a clear academic advising question."
            st.markdown(resp_text)
            st.session_state.messages.append({"role": "assistant", "content": resp_text})
        else:
            with st.spinner("Analyzing academic handbook & guidelines..."):
                chunks = retrieve(prompt, k=6)
                context = "\n\n".join(f"[{c['id']}] {c['text']}" for c in chunks) if chunks else "(No matching handbook excerpts found)"
                
                system_prompt = (
                    "You are the official University AI Academic Advisor.\n"
                    "Rules:\n"
                    "1. Rely ONLY on the document excerpts provided below.\n"
                    "2. Use the provided Student Profile context to personalize eligibility decisions.\n"
                    "3. If crucial student information (e.g., major, completed prerequisites) is missing to answer a course/graduation question, ask a clarifying follow-up question.\n"
                    "4. Include exact document source tags like [Student_Handbook.pdf#4] when citing rules."
                )
                
                user_payload = f"STUDENT PROFILE: {profile_str}\n\nEXCERPTS:\n{context}\n\nQUESTION: {prompt}"
                
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_payload}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.0
                )
                
                response_text = chat_completion.choices[0].message.content
                st.markdown(response_text)
                
                if chunks:
                    with st.expander("🔍 View Retrieved Handbook Excerpts"):
                        for c in chunks:
                            st.caption(f"**{c['id']}**: {c['text'][:150]}...")
                
                st.session_state.messages.append({"role": "assistant", "content": response_text})
