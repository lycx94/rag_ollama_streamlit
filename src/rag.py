import os
import streamlit as st
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader, get_response_synthesizer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts.base import ChatPromptTemplate
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.llms.ollama import Ollama


EMDED_MODEL = "BAAI/bge-small-en-v1.5"
TOP_K = 2


def setup_embed_model():
    print("Setting up embedding model...")
    try:
        from torch import cuda
        device = "cpu" if not cuda.is_available() else "cuda"
    except:
        device = "cpu"

    try:
        Settings.embed_model = HuggingFaceEmbedding(
            model_name = EMDED_MODEL,
            device = device
        )
    except Exception as e:
        print(f"Error loading model: {e}")


def load_documents():
    print("Loading documents...")
    if st.session_state["file_list"]:
        return SimpleDirectoryReader(input_dir=os.getcwd() + "/data", recursive=True).load_data()


def build_vector_db():
    setup_embed_model()
    st.caption("Embedding model loaded!")
    
    Settings.chunk_size = st.session_state["chunk_size"]
    Settings.chunk_overlap = st.session_state["chunk_overlap"]
    documents = load_documents()
    try:
        index = VectorStoreIndex.from_documents(documents, show_progress=True)
        st.caption("Index built!")
        return index
    except Exception as e:
        print(f"Error building index: {e}")
        return None
    


TEXT_QA_SYSTEM_PROMPT = ChatMessage(
    content=(
        "You are an expert Q&A system that is trusted around the world.\n"
        "Always answer the query using the provided context information, "
        "and not prior knowledge.\n"
        "Here are some important rules for the interaction:\n"
        "1. Never directly reference the given context in your answer.\n"
        "2. Only answer questions that are covered in the Context. If the user's question is not in the context or is not on topic, don't make an answer.\n"
    ),
    role=MessageRole.SYSTEM,
)

TEXT_QA_PROMPT_TMPL_MSGS = [
    TEXT_QA_SYSTEM_PROMPT,
    ChatMessage(
        content=(
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the query.\n"
            "Query: {query_str}\n"
            "Answer: "
        ),
        role=MessageRole.USER,
    ),
]

CUSTOM_QA_PROMPT = ChatPromptTemplate(message_templates=TEXT_QA_PROMPT_TMPL_MSGS)

def setup_retriever_query_engine():
    try:
        index = build_vector_db()

        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=TOP_K,
        )

        Settings.llm = Ollama(model=st.session_state["model_name"], request_timeout=60.0)

        response_synthesizer = get_response_synthesizer(
            llm=Settings.llm,
            text_qa_template=CUSTOM_QA_PROMPT,
            streaming=True,
            response_mode="compact", 
        )

        retriever_query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer
        )

        st.session_state["retriever_query_engine"] = retriever_query_engine

        return retriever_query_engine
    
    except Exception as e:
        print(f"Error setting up query engine: {e}")
        return None

def get_response_from_engine(prompt):
    try:
        stream = st.session_state["retriever_query_engine"].query(prompt)
        for text in stream.response_gen:
            yield str(text)
    except Exception as e:
        print(f"Error getting response from engine: {e}")
        return


def setup_llm():
    Settings.llm = Ollama(model=st.session_state["model_name"], request_timeout=60.0)
    return Settings.llm