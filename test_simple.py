
from dotenv import load_dotenv
from pathlib import Path

script_dir = Path(__file__).parent.absolute()
env_path = script_dir / '.env'
load_dotenv(env_path, override=True)

from config.settings import (
    APP_CONFIG, EMBEDDING_MODEL_NAME, LLM_MODEL_NAME, 
    NOTION_API_KEY, NOTION_PAGE_ID, VECTOR_DB_PATH,
    COLLECTION_NAME, CHUNK_CONFIG, LLM_CONFIG, QUANTIZATION_CONFIG
)

print(NOTION_PAGE_ID)