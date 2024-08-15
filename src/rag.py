import os
import streamlit as st
from llama_index.core import (
    Settings,
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    get_response_synthesizer,
    StorageContext,
    SummaryIndex
    )

from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts.base import ChatPromptTemplate
from llama_index.core.base.llms.types import ChatMessage, MessageRole

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, PydanticSingleSelector 


def setup_embed_model():
    print("Setting up embedding model...")
    try:
        from torch import cuda
        device = "cpu" if not cuda.is_available() else "cuda"
    except:
        device = "cpu"
    print("device: ", device)
    
    try:
        ollama_embedding = OllamaEmbedding(
            model_name="llama3.1",
            base_url="http://localhost:11434",
            ollama_additional_kwargs={"mirostat": 0},
        )
        Settings.embed_model = ollama_embedding

    except Exception as e:
        print(f"Error setting embedding model: {e}")


def setup_llm():
    print("Setting up llm...")
    try:
        Settings.llm = Ollama(model="llama3.1", request_timeout=600.0)
    except Exception as e:
        print(f"Error setting llm: {e}")


def load_documents(dir="/data"):
    print("Loading documents...")

    Settings.chunk_size = st.session_state["chunk_size"]
    Settings.chunk_overlap = st.session_state["chunk_overlap"]
    try:
        if st.session_state["file_list"]:   
            return SimpleDirectoryReader(input_dir=os.getcwd() + "/data", recursive=True).load_data()
        elif dir:
            return SimpleDirectoryReader(input_dir=os.getcwd() + dir, recursive=True).load_data()
    except Exception as e:
        print(f"Error load_documents: {e}")


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

        documents = load_documents()
        index = VectorStoreIndex.from_documents(documents, show_progress=True)
        st.caption("Index built!")

        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=st.session_state["top_k"],
        )

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

        return retriever_query_engine
    
    except Exception as e:
        print(f"Error setting up query engine: {e}")
        return None

def get_response_from_engine(prompt):
    try:
        # TODO: add Router Query Engine Streaming
        response = st.session_state["query_engine"].query(prompt)
        
        if response.metadata['selector_result']:
            print("----------Router Query Engine ----------")
            print(response.metadata['selector_result'])

        return response
        # stream = st.session_state["query_engine"].query(prompt)
        # for text in stream.response_gen:
        #     yield str(text)

    except Exception as e:
        print(f"Error getting response from engine: {e}")
        return

def router_query_engine():
    try:        
        documents = load_documents()

        nodes = Settings.node_parser.get_nodes_from_documents(documents)
        storage_context = StorageContext.from_defaults()
        storage_context.docstore.add_documents(nodes)

        summary_index = SummaryIndex(nodes, storage_context=storage_context)
        vector_index = VectorStoreIndex(nodes, storage_context=storage_context)        
        st.caption("Index built!")

        summary_query_engine = summary_index.as_query_engine(
            response_mode="tree_summarize", use_async=True
        )
        vector_query_engine = vector_index.as_query_engine(
            response_mode="tree_summarize", use_async=True
        )
        # initialize tools
        summary_tool = QueryEngineTool.from_defaults(
            query_engine=summary_query_engine,
            description="Useful for summarization questions related to the data source",
        )
        vector_tool = QueryEngineTool.from_defaults(
            query_engine=vector_query_engine,
            description="Useful for retrieving specific context related to the data source",
        )

        # initialize router query engine (single selection, llm)
        query_engine_single_selector = RouterQueryEngine(
            selector=LLMSingleSelector.from_defaults(),
            query_engine_tools=[
                summary_tool,
                vector_tool,
            ],
        )
        return query_engine_single_selector
    
    except Exception as e:
        print(f"Error setting up router query engine: {e}")
        return None
    

if __name__=="__main__":
    
    st.session_state["chunk_size"] = 1024
    st.session_state["chunk_overlap"]= 20
    st.session_state["top_k"]= 2
    st.session_state["file_list"] = []

    setup_embed_model()
    setup_llm()
    engine = router_query_engine()

    prompt = "whats the file about?"
    res = engine.query(prompt)
    print(res)