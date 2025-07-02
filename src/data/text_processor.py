"""Text processing and chunking module."""

from typing import List
from langchain.schema import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)


class TextProcessor:
    """Process and chunk text documents."""
    
    def __init__(self, embeddings: HuggingFaceEmbeddings, chunk_config: dict):
        """Initialize text processor.
        
        Args:
            embeddings: Embedding model for semantic chunking
            chunk_config: Configuration for chunking
        """
        self.embeddings = embeddings
        self.chunk_config = chunk_config
        self.splitter = self._create_splitter()
        
    def _create_splitter(self) -> SemanticChunker:
        """Create semantic text splitter.
        
        Returns:
            Configured SemanticChunker
        """
        return SemanticChunker(
            embeddings=self.embeddings,
            buffer_size=self.chunk_config['buffer_size'],
            breakpoint_threshold_type=self.chunk_config['breakpoint_threshold_type'],
            breakpoint_threshold_amount=self.chunk_config['breakpoint_threshold_amount'],
            min_chunk_size=self.chunk_config['min_chunk_size'],
            add_start_index=True
        )
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """Process and chunk documents.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of chunked documents
        """
        try:
            # Pre-process documents if needed
            processed_docs = self._preprocess_documents(documents)
            
            # Chunk documents
            chunks = self.splitter.split_documents(processed_docs)
            
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            raise
    
    def _preprocess_documents(self, documents: List[Document]) -> List[Document]:
        """Pre-process documents before chunking.
        
        Args:
            documents: List of documents
            
        Returns:
            Preprocessed documents
        """
        processed = []
        
        for doc in documents:
            # Clean content
            content = doc.page_content.strip()
            
            # Skip empty documents
            if not content:
                continue
            
            # Remove excessive whitespace
            content = ' '.join(content.split())
            
            # Create new document with cleaned content
            processed.append(Document(
                page_content=content,
                metadata=doc.metadata
            ))
        
        return processed