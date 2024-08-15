# Retrieval-Augmented Generation (RAG) Chatbot

![RAG Chatbot demo](https://github.com/lycx94/rag_ollama_streamlit/blob/main/demo.gif)

This project implements a Retrieval-Augmented Generation (RAG) chatbot using Streamlit, LlamaIndex, and Ollama. 

The LlamaIndex LLM Router enables the model to choose the most suitable data source. It decides whether to summarize (e.g., with a summary index query engine) or perform a semantic search (e.g., with a vector index query engine), ensuring the responses are both accurate and aligned with the user's query.

With Ollama, the model can be run locally, which offers several advantages:

## Advantages of Local Deployment with Ollama

1. **Cost Efficiency**
   - Running the model locally eliminates the need for costly API calls to external services, significantly reducing operational expenses.

2. **Data Privacy**
   - Local deployment ensures that sensitive data remains within the user's infrastructure, enhancing data security and privacy.

3. **Reliability**
   - Local deployment mitigates risks associated with external service outages or rate limits, ensuring consistent availability and performance.


## Quick Start

1. Clone the repository

2. Install the required packages

    ```sh
    pip install -r requirements.txt
    ```

3. Download and run the model 
    - Install [Ollama](https://ollama.com/library) on your system
    - Pull and run the Llama3 model
    ```sh
    ollama run llama3.1
    ```

4. Run the Streamlit Application

    ```sh
    streamlit run main.py
    ```

5. Use the Chatbot
    - Open your web browser and navigate to the provided local URL
    - Upload your documents through the interface
    - Start interacting with the RAG-powered chatbot!


### Additional Information

- **WSL on Windows**  
  If you are using Windows, you need to set up Windows Subsystem for Linux (WSL). Follow [this guide](https://docs.microsoft.com/en-us/windows/wsl/install) to install WSL and set up a Linux distribution on your Windows machine.

- **Model Customization**  
  If you need to use a different model or customize the current model, refer to the [Ollama documentation](https://ollama.com/blog) for more details.