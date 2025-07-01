#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from notion_client import Client
from pathlib import Path

script_dir = Path(__file__).parent.absolute()
env_path = script_dir / '.env'
load_dotenv(env_path, override=True)

api_key = os.getenv("NOTION_API_KEY")
page_id = os.getenv("NOTION_PAGE_ID", os.getenv("NOTION_DATABASE_ID"))  # Support both names

print(f"🔍 Testing Notion Page access")
print(f"Page ID: {page_id}")

client = Client(auth=api_key)

try:
    # Get page info
    page = client.pages.retrieve(page_id=page_id)
    print("✅ Successfully accessed page!")
    
    # Get page content
    print("\n📄 Getting page content...")
    blocks = client.blocks.children.list(block_id=page_id)
    
    print(f"Found {len(blocks['results'])} blocks")
    
    # Show first few blocks
    for i, block in enumerate(blocks['results'][:5]):
        block_type = block['type']
        print(f"\nBlock {i+1}: {block_type}")
        
        if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3']:
            text_content = block.get(block_type, {}).get('rich_text', [])
            if text_content:
                text = ''.join([t.get('plain_text', '') for t in text_content])
                print(f"  Content: {text[:100]}...")
                
except Exception as e:
    print(f"❌ Error: {e}")