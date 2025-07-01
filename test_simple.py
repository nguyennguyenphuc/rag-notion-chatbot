import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Print để debug
api_key = os.getenv("NOTION_API_KEY")
db_id = os.getenv("NOTION_DATABASE_ID")

print(f"API Key loaded: {api_key is not None}")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key prefix: {api_key[:10] if api_key else 'None'}")
print(f"Database ID: {db_id}")

# Test trực tiếp
from notion_client import Client

try:
    client = Client(auth=api_key)
    # Test với một API call đơn giản
    user = client.users.me()
    print(f"✅ Connected as: {user}")
except Exception as e:
    print(f"❌ Error: {e}")