"""Main Streamlit application."""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import (
    APP_CONFIG, EMBEDDING_MODEL_NAME, LLM_MODEL_NAME, 
    NOTION_API_KEY, NOTION_PAGE_ID, VECTOR_DB_PATH,
    COLLECTION_NAME, CHUNK_CONFIG, LLM_CONFIG, QUANTIZATION_CONFIG
)
from src.models.embeddings import EmbeddingsModel
from src.models.llm import LanguageModel
from src.data.notion_loader import NotionLoader
from src.data.text_processor import TextProcessor
from src.vectorstore.chroma_store import ChromaStore
from src.chains.rag_chain import RAGChain
from app.components.sidebar import Sidebar
from app.components.chat import ChatInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'models_loaded' not in st.session_state:
        st.session_state.models_loaded = False
    if 'embeddings' not in st.session_state:
        st.session_state.embeddings = None
    if 'llm' not in st.session_state:
        st.session_state.llm = None
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'rag_chain' not in st.session_state:
        st.session_state.rag_chain = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None


@st.cache_resource
def load_models():
    """Load embedding and language models."""
    # Load embeddings
    embeddings_model = EmbeddingsModel(EMBEDDING_MODEL_NAME)
    embeddings = embeddings_model.load()
    
    # Load LLM
    llm_model = LanguageModel(LLM_MODEL_NAME, LLM_CONFIG, QUANTIZATION_CONFIG)
    llm = llm_model.load()
    
    return embeddings, llm


def refresh_notion_data():
    """Refresh data from Notion."""
    try:
        # Check if API keys are configured
        if not NOTION_API_KEY or not NOTION_PAGE_ID:
            raise ValueError("Notion API key hoặc Database ID chưa được cấu hình trong file .env")
        
        # Load data from Notion
        notion_loader = NotionPageLoader(NOTION_API_KEY, NOTION_PAGE_ID)
        documents = notion_loader.load_documents()
        
        if not documents:
            raise ValueError("Không tìm thấy dữ liệu trong Notion database")
        
        # Process documents
        text_processor = TextProcessor(st.session_state.embeddings, CHUNK_CONFIG)
        chunks = text_processor.process_documents(documents)
        
        # Create/update vector store
        vector_store = ChromaStore(st.session_state.embeddings, VECTOR_DB_PATH, COLLECTION_NAME)
        vector_store.create_or_update(chunks)
        st.session_state.vector_store = vector_store
        
        # Create RAG chain
        retriever = vector_store.get_retriever()
        rag_chain = RAGChain(st.session_state.llm, retriever)
        st.session_state.rag_chain = rag_chain
        
        # Update session state
        st.session_state.data_loaded = True
        st.session_state.last_update = datetime.now()
        
        return len(documents), len(chunks)
        
    except Exception as e:
        logger.error(f"Error refreshing Notion data: {str(e)}")
        raise


def main():
    """Main application function."""
    # Page config
    st.set_page_config(
        page_title=APP_CONFIG['title'],
        page_icon=APP_CONFIG['page_icon'],
        layout=APP_CONFIG['layout'],
        initial_sidebar_state=APP_CONFIG['initial_sidebar_state']
    )
    
    # Initialize session state
    init_session_state()
    
    # Page title
    st.title(APP_CONFIG['title'])
    
    # Logo
    # if Path(APP_CONFIG['logo_path']).exists():
    #     st.logo(APP_CONFIG['logo_path'], size="large")
    
    # Initialize components
    sidebar = Sidebar()
    chat = ChatInterface()
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Cài đặt")
        
        # Load models if not loaded
        if not st.session_state.models_loaded:
            with sidebar.render_progress("Đang tải AI models..."):
                embeddings, llm = load_models()
                st.session_state.embeddings = embeddings
                st.session_state.llm = llm
                st.session_state.models_loaded = True
            st.rerun()
        
        sidebar.render_model_status(st.session_state.models_loaded)
        
        st.markdown("---")
        
        # Data status
        sidebar.render_data_status(
            st.session_state.data_loaded, 
            st.session_state.last_update
        )
        
        # Refresh button
        if sidebar.render_refresh_button():
            with sidebar.render_progress("Đang tải dữ liệu từ Notion..."):
                try:
                    num_docs, num_chunks = refresh_notion_data()
                    sidebar.render_success(
                        f"Đã tải {num_docs} tài liệu và tạo {num_chunks} chunks!"
                    )
                    # Clear chat history after refresh
                    chat.clear_history()
                    chat.add_message(
                        "assistant", 
                        f"✅ Đã cập nhật dữ liệu từ Notion thành công!\n\n"
                        f"📊 Đã xử lý {num_docs} tài liệu thành {num_chunks} phần. "
                        f"Bạn có thể bắt đầu đặt câu hỏi về nội dung."
                    )
                except Exception as e:
                    sidebar.render_error(str(e))
            st.rerun()
        
        st.markdown("---")
        
        # Chat controls
        if sidebar.render_chat_controls():
            chat.clear_history()
            st.rerun()
        
        st.markdown("---")
        
        # Instructions
        sidebar.render_instructions()
    
    # Main content
    st.markdown("*Trò chuyện với AI Assistant để tìm hiểu về nội dung từ Notion của bạn*")
    
    # Chat interface
    chat.display_chat()
    
    # Handle user input
    if st.session_state.models_loaded:
        if st.session_state.data_loaded:
            chat.handle_user_input(st.session_state.rag_chain)
        else:
            st.info("🔄 Vui lòng nhấn 'Refresh dữ liệu từ Notion' để bắt đầu!")
            st.chat_input("Nhập câu hỏi của bạn...", disabled=True)
    else:
        st.info("⏳ Đang tải AI models, vui lòng đợi...")
        st.chat_input("Nhập câu hỏi của bạn...", disabled=True)


if __name__ == "__main__":
    main()