import streamlit as st
from src.rag import setup_retriever_query_engine, get_response_from_engine, router_query_engine
from streamlit_feedback import streamlit_feedback
import csv
import os


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


def sidebar():

    with st.sidebar:
            
        if "file_list" not in st.session_state:
            st.session_state["file_list"] = []

        st.session_state["chunk_size"] = st.number_input("Chunk size", value=1024)
        st.session_state["chunk_overlap"]= st.number_input("Chunk overlap", value=20)
        st.session_state["top_k"]= st.number_input("top_k", value=2)
    
        st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
        
        st.markdown("Upload Your Data Files")
        with st.expander("Files", expanded=True):
            uploaded_files = st.file_uploader(
                "Upload files", 
                accept_multiple_files=True,            
                type=["pdf", "txt", "csv","json"]
            )
            if len(uploaded_files) > 0:
                st.session_state["file_list"] = uploaded_files
                if st.button("Load", key="load_file_button"):
                    with st.spinner("Loading..."):
                        save_to_dir_and_setup_engine()

def main_area():    

    st.title("Chat with documents")
    st.caption("Leave feedback to help me improve!")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about your file."}]

    if "query_engine" not in st.session_state:
        st.session_state["query_engine"] = None
    
    if "response" not in st.session_state:
        st.session_state["response"] = None

    if "prompt" not in st.session_state:
        st.session_state["prompt"] = None

    messages = st.session_state.messages
    for msg in messages:
        st.chat_message(msg["role"]).write(msg["content"])
    

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state["prompt"] = prompt
        messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if st.session_state["query_engine"]:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:                
                        # TODO: add Router Query Engine Streaming
                        # resp = st.write_stream(
                        #         get_response_from_engine( prompt)  
                        #     )  
                        resp = get_response_from_engine( prompt) 
                        st.write(str(resp))
                        messages.append({"role": "assistant", "content": resp})
                        st.session_state["response"] = resp    
                    except Exception as e:
                        print(f"Error querying engine: {e}")
                        return                
        else:
            st.info("No uploads have been made yet. Upload a PDF to start chatting.")
            st.stop()


    if st.session_state["query_engine"] and st.session_state["response"]:
        feedback = streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="[Optional] Please provide an explanation",
            key=f"feedback_{len(messages)}",
        )
        
        if feedback:
            with open('feedback.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(["User Prompt", "Engine Response", "Feedback Type", "Feedback Score", "Feedback Text"])
                writer.writerow([st.session_state["prompt"], st.session_state["response"], feedback['type'], feedback['score'], feedback['text']])


def save_to_dir_and_setup_engine():
    save_dir = os.getcwd() + "/data"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    for file in st.session_state["file_list"]:
        print(f"File name: {file.name}")
        try:
            with open(os.path.join(save_dir, file.name), "wb") as f:
                f.write(file.getbuffer())
                print(f"File {file.name} saved to disk")

        except Exception:
            print("Error saving upload to disk.")

    st.caption("Files uploaded!")
    # setup_retriever_query_engine()
    st.session_state["query_engine"] = router_query_engine()
    st.write("You can start chatting!") 
