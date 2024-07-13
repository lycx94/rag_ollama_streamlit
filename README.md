# RAG Chatbot Project

This project implements a Retrieval-Augmented Generation (RAG) chatbot using Streamlit and Ollama. 
<br>This project allows you to use the chatbot offline, so you don’t have to worry about data leakage.

![RAG Chatbot demo](https://github.com/lycx94/rag_ollama_streamlit/blob/main/demo.gif)

## Quick Start

1. Clone the repository

2. Install the required packages

    ```sh
    pip install -r requirements.txt
    ```

3. Download the model using [Ollama](https://ollama.com/library). For this repository, `llama3` is used. 
    <br>**Ensure you use WSL on Windows as it is not directly supported.** 

    ```sh
    ollama run llama3
    ```

4. Run the application offline

    ```sh
    streamlit run main.py
    ```

5. Upload your documents and start chatting!
