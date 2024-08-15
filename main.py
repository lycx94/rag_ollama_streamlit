from src.streamlit_app import sidebar, main_area
from src.rag import setup_embed_model, setup_llm

def main():    
    setup_embed_model()
    setup_llm()
    sidebar()
    main_area()


if __name__ == "__main__":
    main()