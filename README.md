# Notion RAG Chatbot

AI-powered chatbot that answers questions based on your Notion database content using RAG (Retrieval-Augmented Generation).

## Features

- 🔄 **Real-time Notion Integration**: Sync and refresh data from your Notion database
- 🤖 **Advanced RAG System**: Uses semantic search and LLM for accurate answers
- 💬 **Interactive Chat Interface**: User-friendly Streamlit interface
- 🔍 **Semantic Chunking**: Intelligent document splitting for better context
- ⚡ **Quantized Models**: 4-bit quantization for efficient GPU usage
- 🇻🇳 **Vietnamese Support**: Using Vietnamese-optimized embedding model

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Notion    │────►│ Text Process │────►│  ChromaDB    │
│  Database   │     │  & Chunking  │     │Vector Store  │
└─────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Streamlit  │◄────│  RAG Chain   │◄────│  Retriever   │
│     UI      │     │   + LLM      │     │              │
└─────────────┘     └──────────────┘     └──────────────┘
```

## Prerequisites

- Python 3.8+
- CUDA-capable GPU (recommended) or CPU
- Notion API access
- At least 8GB RAM (16GB recommended)

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd rag-notion-chatbot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Notion Integration**
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Copy the API key
   - Share your Notion database with the integration

5. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your Notion credentials:
```env
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_database_id_here
```

## Project Structure

```
rag-notion-chatbot/
├── config/          # Configuration files
├── src/             # Source code
│   ├── models/      # ML models (embeddings, LLM)
│   ├── data/        # Data loading and processing
│   ├── vectorstore/ # Vector database management
│   └── chains/      # RAG chain implementation
├── app/             # Streamlit application
│   └── components/  # UI components
└── notebooks/       # Jupyter notebooks for testing
```

## Usage

1. **Run the application**
```bash
streamlit run app/streamlit_app.py
```

2. **Using the chatbot**
   - Wait for models to load (first time may take a few minutes)
   - Click "Refresh dữ liệu từ Notion" to sync your data
   - Start asking questions about your Notion content
   - Use "Xóa lịch sử chat" to clear conversation history

## Configuration

### Model Settings (in `.env`)

- `EMBEDDING_MODEL_NAME`: HuggingFace embedding model
- `LLM_MODEL_NAME`: Language model for generation
- `MAX_NEW_TOKENS`: Maximum tokens in response
- `TEMPERATURE`: Control randomness (0-1)

### Chunking Settings

- `CHUNK_MIN_SIZE`: Minimum chunk size in characters
- `CHUNK_BREAKPOINT_THRESHOLD_TYPE`: Method for splitting
- `CHUNK_BREAKPOINT_THRESHOLD_AMOUNT`: Threshold value

## Development

### Adding New Features

1. **New Data Sources**: Implement loader in `src/data/`
2. **Different Models**: Add model wrapper in `src/models/`
3. **UI Components**: Create component in `app/components/`

### Testing

Run tests using the notebook:
```bash
jupyter notebook notebooks/test_rag.ipynb
```

## Troubleshooting

### Common Issues

1. **CUDA out of memory**
   - Reduce `MAX_NEW_TOKENS`
   - Use CPU instead (slower)

2. **Notion sync fails**
   - Check API key and database ID
   - Ensure integration has access to database

3. **Slow performance**
   - Enable GPU acceleration
   - Reduce chunk size
   - Use smaller models

### Logging

Check logs in the terminal for detailed error messages.

## Performance Tips

- Use GPU for 10x faster inference
- Adjust chunk size based on your content
- Cache models to avoid reloading
- Limit chat history for better performance

## Security

- Never commit `.env` file
- Use environment variables for sensitive data
- Restrict Notion integration permissions
- Regular security updates

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- LangChain for RAG framework
- HuggingFace for models
- Streamlit for UI
- ChromaDB for vector storage