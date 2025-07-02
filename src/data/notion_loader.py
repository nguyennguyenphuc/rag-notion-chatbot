"""Notion page loader module - Load content from a specific Notion page."""

from typing import List, Dict, Any
from notion_client import Client
from langchain.schema import Document
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NotionLoader:
    """Load and process data from a specific Notion page."""
    
    def __init__(self, api_key: str, page_id: str):
        """Initialize Notion client.
        
        Args:
            api_key: Notion API key
            page_id: ID of the Notion page to load from
        """
        self.client = Client(auth=api_key)
        self.page_id = page_id
        
    def load_documents(self) -> List[Document]:
        """Load content from the Notion page and all its sub-pages.
        
        Returns:
            List of Document objects
        """
        try:
            documents = []
            
            # Load main page
            logger.info(f"Loading main page: {self.page_id}")
            main_doc = self._load_page(self.page_id)
            if main_doc:
                documents.append(main_doc)
            
            # Load all sub-pages
            sub_pages = self._get_sub_pages(self.page_id)
            logger.info(f"Found {len(sub_pages)} sub-pages")
            
            for sub_page_id in sub_pages:
                doc = self._load_page(sub_page_id)
                if doc:
                    documents.append(doc)
            
            logger.info(f"Loaded total {len(documents)} documents from Notion")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading Notion page: {str(e)}")
            raise
    
    def _load_page(self, page_id: str) -> Document:
        """Load a single Notion page.
        
        Args:
            page_id: ID of the page
            
        Returns:
            Document object or None if loading fails
        """
        try:
            # Get page metadata
            page = self.client.pages.retrieve(page_id=page_id)
            
            # Extract title from properties
            title = self._extract_title(page)
            
            # Get page content
            content = self._get_page_content(page_id)
            
            if content:
                return Document(
                    page_content=content,
                    metadata={
                        'source': f"notion://{page_id}",
                        'page_id': page_id,
                        'title': title,
                        'last_edited': page.get('last_edited_time', ''),
                        'created_time': page.get('created_time', ''),
                        'url': page.get('url', '')
                    }
                )
            return None
            
        except Exception as e:
            logger.error(f"Error loading page {page_id}: {str(e)}")
            return None
    
    def _extract_title(self, page: Dict[str, Any]) -> str:
        """Extract title from page properties or use a default.
        
        Args:
            page: Notion page object
            
        Returns:
            Page title
        """
        # Try to get title from properties
        properties = page.get('properties', {})
        
        # Look for title property
        for prop_name, prop_value in properties.items():
            if prop_value.get('type') == 'title':
                title_items = prop_value.get('title', [])
                if title_items:
                    return ''.join([item.get('plain_text', '') for item in title_items])
        
        # If in a database, try to get the first text property
        for prop_name, prop_value in properties.items():
            if prop_value.get('type') == 'rich_text':
                text_items = prop_value.get('rich_text', [])
                if text_items:
                    return ''.join([item.get('plain_text', '') for item in text_items])
        
        return "Untitled Page"
    
    def _get_sub_pages(self, parent_id: str) -> List[str]:
        """Get all sub-pages of a parent page.
        
        Args:
            parent_id: ID of the parent page
            
        Returns:
            List of sub-page IDs
        """
        sub_pages = []
        try:
            # Search for pages with this parent
            response = self.client.search(
                filter={
                    "property": "object",
                    "value": "page"
                }
            )
            
            # Filter for pages that have our page as parent
            for result in response.get('results', []):
                parent = result.get('parent', {})
                if parent.get('type') == 'page_id' and parent.get('page_id') == parent_id:
                    sub_pages.append(result['id'])
            
        except Exception as e:
            logger.error(f"Error getting sub-pages: {str(e)}")
        
        return sub_pages
    
    def _get_page_content(self, page_id: str) -> str:
        """Get the content of a Notion page.
        
        Args:
            page_id: ID of the page
            
        Returns:
            Page content as string
        """
        try:
            blocks = []
            has_more = True
            start_cursor = None
            
            while has_more:
                response = self.client.blocks.children.list(
                    block_id=page_id,
                    start_cursor=start_cursor
                )
                
                for block in response['results']:
                    text = self._extract_text_from_block(block)
                    if text:
                        blocks.append(text)
                    
                    # Recursively get content from nested blocks
                    if block.get('has_children', False):
                        child_blocks = self._get_child_blocks_content(block['id'])
                        if child_blocks:
                            blocks.append(child_blocks)
                
                has_more = response['has_more']
                start_cursor = response.get('next_cursor')
            
            return '\n\n'.join(blocks)
            
        except Exception as e:
            logger.error(f"Error getting page content for {page_id}: {str(e)}")
            return ""
    
    def _get_child_blocks_content(self, block_id: str, indent: int = 1) -> str:
        """Get content from child blocks recursively.
        
        Args:
            block_id: ID of the parent block
            indent: Indentation level
            
        Returns:
            Child blocks content as string
        """
        try:
            child_blocks = []
            response = self.client.blocks.children.list(block_id=block_id)
            
            for block in response['results']:
                text = self._extract_text_from_block(block)
                if text:
                    # Add indentation for nested blocks
                    indented_text = '  ' * indent + text
                    child_blocks.append(indented_text)
                
                # Recursively get nested children
                if block.get('has_children', False):
                    nested = self._get_child_blocks_content(block['id'], indent + 1)
                    if nested:
                        child_blocks.append(nested)
            
            return '\n'.join(child_blocks) if child_blocks else ""
            
        except Exception as e:
            logger.error(f"Error getting child blocks: {str(e)}")
            return ""
    
    def _extract_text_from_block(self, block: Dict[str, Any]) -> str:
        """Extract text from a Notion block.
        
        Args:
            block: Notion block object
            
        Returns:
            Extracted text
        """
        block_type = block.get('type')
        block_data = block.get(block_type, {})
        
        # Handle different block types
        if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3']:
            text_items = block_data.get('rich_text', [])
            prefix = ''
            if block_type == 'heading_1':
                prefix = '# '
            elif block_type == 'heading_2':
                prefix = '## '
            elif block_type == 'heading_3':
                prefix = '### '
            return prefix + ''.join([item.get('plain_text', '') for item in text_items])
            
        elif block_type == 'bulleted_list_item':
            text_items = block_data.get('rich_text', [])
            return '• ' + ''.join([item.get('plain_text', '') for item in text_items])
            
        elif block_type == 'numbered_list_item':
            text_items = block_data.get('rich_text', [])
            return '1. ' + ''.join([item.get('plain_text', '') for item in text_items])
            
        elif block_type == 'to_do':
            text_items = block_data.get('rich_text', [])
            checked = block_data.get('checked', False)
            checkbox = '☑' if checked else '☐'
            return f'{checkbox} ' + ''.join([item.get('plain_text', '') for item in text_items])
            
        elif block_type == 'toggle':
            text_items = block_data.get('rich_text', [])
            return '▸ ' + ''.join([item.get('plain_text', '') for item in text_items])
            
        elif block_type == 'code':
            text_items = block_data.get('rich_text', [])
            code = ''.join([item.get('plain_text', '') for item in text_items])
            language = block_data.get('language', 'plain text')
            return f"```{language}\n{code}\n```"
            
        elif block_type == 'quote':
            text_items = block_data.get('rich_text', [])
            return '> ' + ''.join([item.get('plain_text', '') for item in text_items])
            
        elif block_type == 'callout':
            text_items = block_data.get('rich_text', [])
            icon = block_data.get('icon', {})
            emoji = icon.get('emoji', '💡') if icon else '💡'
            return f'{emoji} ' + ''.join([item.get('plain_text', '') for item in text_items])
            
        elif block_type == 'divider':
            return '---'
            
        elif block_type == 'table_of_contents':
            return '[Table of Contents]'
            
        elif block_type == 'link_to_page':
            page_ref = block_data.get('page_id', '')
            return f'[Link to page: {page_ref}]'
            
        elif block_type == 'image':
            image_data = block_data.get('external', block_data.get('file', {}))
            url = image_data.get('url', '')
            caption = block_data.get('caption', [])
            caption_text = ''.join([item.get('plain_text', '') for item in caption])
            return f'![{caption_text}]({url})' if caption_text else f'![Image]({url})'
            
        # Add more block types as needed
        
        return ""