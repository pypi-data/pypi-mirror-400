import os
import json
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

API_URL = "https://data.covid19india.org/v4/timeseries.json"
DOC_FILE = "documents.txt"

MAX_TEXT_CHARS = 200_000
MAX_CONTEXT_CHARS = 3_000

# --------------------------------------------------
# STREAMLIT STATE
# --------------------------------------------------

st.title("RAG Chat App")

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "ready" not in st.session_state:
    st.session_state.ready = False

if "messages" not in st.session_state:
    st.session_state.messages = []

st.sidebar.title("Controls")

# --------------------------------------------------
# CREATE VECTOR DATABASE
# --------------------------------------------------

if st.sidebar.button("CREATE vector database"):

    st.write("Preparing data...")

    full_text = ""

    if os.path.exists(DOC_FILE):
        with open(DOC_FILE, "r", encoding="utf-8") as f:
            full_text = f.read()

    else:
        response = requests.get(API_URL, timeout=60)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame.from_dict(data, orient="index").reset_index()

        for col in df.columns:
            df[col] = df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, dict) else x
            )
            if df[col].dtype in ["int64", "float64"]:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna("unknown").astype(str)

        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.lower().str.strip()

        for _, row in df.iterrows():
            row_text = " | ".join(
                [f"{col}: {row[col]}" for col in df.columns]
            )
            full_text += row_text + "\\n"

        with open(DOC_FILE, "w", encoding="utf-8") as f:
            f.write(full_text)

    # --------------------------------------------------
    # TEXT-LEVEL TRIMMING
    # --------------------------------------------------

    text_len = len(full_text)

    if text_len > MAX_TEXT_CHARS:
        st.warning(
            f"Data is large ({text_len} characters). Trimming text for performance."
        )

        part = MAX_TEXT_CHARS // 3
        middle = text_len // 2

        full_text = (
            full_text[:part]
            + "\\n...\\n"
            + full_text[middle - part//2 : middle + part//2]
            + "\\n...\\n"
            + full_text[-part:]
        )

    # --------------------------------------------------
    # TEXT SPLITTING & VECTOR DB
    # --------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )

    documents = splitter.create_documents([full_text])

    embeddings = OpenAIEmbeddings(api_key=API_KEY)
    st.session_state.vector_db = FAISS.from_documents(documents, embeddings)
    st.session_state.ready = True

    st.success("Vector database is ready. You can now chat.")

# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("context"):
            with st.expander("Retrieved Context"):
                st.markdown(msg["context"])

# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_input = st.chat_input("Ask something about the data")

if user_input:

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    retrieved_context = ""

    if not st.session_state.ready:
        bot_reply = "Please create the vector database first."

    else:
        llm = ChatOpenAI(model="gpt-4o-mini")

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a data analyst assistant.\\n"
                "Use the provided context to answer the question.\\n"
                "Do NOT use external knowledge."
            ),
            ("human", "Question: {question}\\n\\nContext:\\n{context}")
        ])

        results = st.session_state.vector_db.similarity_search(
            user_input, k=1
        )

        retrieved_context = "\\n\\n".join(
            [doc.page_content for doc in results]
        )

        response = llm.invoke(
            prompt.format(
                question=user_input,
                context=retrieved_context
            )
        )
        bot_reply = response.content

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": bot_reply,
            "context": retrieved_context
        }
    )

    with st.chat_message("assistant"):
        st.markdown(bot_reply)