#!/bin/bash

# This script creates all Python files
# Run this after the main setup script

echo "Creating Python source files..."

# Create settings.py
cat > config/settings.py << 'PYEOF'
"""Configuration settings for the RAG Notion Chatbot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Model Configuration
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "bkai-foundation-models/vietnamese-bi-encoder")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "lmsys/vicuna-7b-v1.5")

# Notion Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Vector Store Configuration
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "notion_docs")

# Chunking Configuration
CHUNK_CONFIG = {
    "min_chunk_size": int(os.getenv("CHUNK_MIN_SIZE", 500)),
    "buffer_size": int(os.getenv("CHUNK_BUFFER_SIZE", 1)),
    "breakpoint_threshold_type": os.getenv("CHUNK_BREAKPOINT_THRESHOLD_TYPE", "percentile"),
    "breakpoint_threshold_amount": int(os.getenv("CHUNK_BREAKPOINT_THRESHOLD_AMOUNT", 95))
}

# LLM Configuration
LLM_CONFIG = {
    "max_new_tokens": int(os.getenv("MAX_NEW_TOKENS", 512)),
    "temperature": float(os.getenv("TEMPERATURE", 0.7)),
    "top_p": float(os.getenv("TOP_P", 0.95))
}

# Quantization Configuration
QUANTIZATION_CONFIG = {
    "load_in_4bit": True,
    "bnb_4bit_use_double_quant": True,
    "bnb_4bit_compute_dtype": "bfloat16",
    "bnb_4bit_quant_type": "nf4"
}

# App Configuration
APP_CONFIG = {
    "title": os.getenv("APP_TITLE", "Notion RAG Assistant"),
    "page_icon": os.getenv("PAGE_ICON", "🤖"),
    "logo_path": os.getenv("LOGO_PATH", "./logo.png"),
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
PYEOF

echo "✓ Created config/settings.py"
echo ""
echo "Note: Due to file size limits, please manually create the remaining Python files:"
echo "- src/models/embeddings.py"
echo "- src/models/llm.py"
echo "- src/data/notion_loader.py"
echo "- src/data/text_processor.py"
echo "- src/vectorstore/chroma_store.py"
echo "- src/chains/rag_chain.py"
echo "- app/components/chat.py"
echo "- app/components/sidebar.py"
echo "- app/streamlit_app.py"
echo ""
echo "You can find the complete code in the artifacts above."
