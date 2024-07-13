import streamlit as st
from src.rag import setup_retriever_query_engine, setup_llm, get_response_from_engine
from streamlit_feedback import streamlit_feedback
import csv
import os


st.set_page_config(
    page_title='RAG Chatbot', 
    layout="wide",
    initial_sidebar_state="expanded"
    )


def sidebar():

    if "file_list" not in st.session_state:
        st.session_state["file_list"] = []

    with st.sidebar:
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
                    with st.spinner("Load..."):
                        save_to_dir_and_setup_engine()
                        st.write("You can start chatting!") 

def main_area():    
    
    if "retriever_query_engine" not in st.session_state:
        st.session_state["retriever_query_engine"] = None

    st.title("RAG Chatbot")
    st.caption("Leave feedback to help me improve!")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about your file."}]

    if "response" not in st.session_state:
        st.session_state["response"] = None

    if "prompt" not in st.session_state:
        st.session_state["prompt"] = None


    messages = st.session_state.messages
    for msg in messages:
        st.chat_message(msg["role"]).write(msg["content"])
    

    if prompt := st.chat_input("Enter your prompt..."):
        st.session_state["prompt"] = prompt
        messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if st.session_state["retriever_query_engine"]:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:                
                        resp = st.write_stream(
                                get_response_from_engine( prompt)  
                            )  
                        messages.append({"role": "assistant", "content": resp})
                        st.session_state["response"] = resp    
                    except Exception as e:
                        print(f"Error querying engine: {e}")
                        return                
        else:
            st.info("No uploads have been made yet. Please add your files.")
            st.stop()

            # popup_error_message("No uploads have been made yet.\nIt's only a language model and doesn't involve any RAG.")
            # try:
            #     llm = setup_llm()
            #     resp = llm.complete(prompt)
            # except Exception as err:
            #     print(f"Error setting up LLM: {err}")



    if st.session_state["retriever_query_engine"] and st.session_state["response"]:
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


     
            
@st.experimental_dialog("Error!")
def popup_error_message(msg):
    st.write(msg)
    if st.button("Got it"):
        st.rerun()


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


    st.caption("Files Uploaded!")
    setup_retriever_query_engine()


def main():    
    sidebar()
    main_area()

if __name__=="__main__":
    main()
