"""ChromaDB vector store module."""

from typing import List, Optional
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class ChromaStore:
    """Manage ChromaDB vector store."""
    
    def __init__(self, embeddings: HuggingFaceEmbeddings, persist_directory: str, collection_name: str):
        """Initialize ChromaDB store.
        
        Args:
            embeddings: Embeddings model
            persist_directory: Directory to persist the database
            collection_name: Name of the collection
        """
        self.embeddings = embeddings
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self._vectorstore: Optional[Chroma] = None
        
        # Create directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
    def create_or_update(self, documents: List[Document]) -> Chroma:
        """Create or update vector store with documents.
        
        Args:
            documents: List of documents to index
            
        Returns:
            Updated vector store
        """
        try:
            # Clear existing database
            self.clear()
            
            # Create new vector store
            logger.info(f"Creating vector store with {len(documents)} chunks")
            self._vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=str(self.persist_directory),
                collection_name=self.collection_name
            )
            
            logger.info("Vector store created successfully")
            return self._vectorstore
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def load(self) -> Optional[Chroma]:
        """Load existing vector store.
        
        Returns:
            Loaded vector store or None if not exists
        """
        try:
            if self._vectorstore is None and self.exists():
                logger.info("Loading existing vector store")
                self._vectorstore = Chroma(
                    persist_directory=str(self.persist_directory),
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
                logger.info("Vector store loaded successfully")
                
            return self._vectorstore
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return None
    
    def clear(self):
        """Clear the vector store."""
        try:
            if self.persist_directory.exists():
                logger.info("Clearing existing vector store")
                shutil.rmtree(self.persist_directory)
                self.persist_directory.mkdir(parents=True, exist_ok=True)
                self._vectorstore = None
                logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            
    def exists(self) -> bool:
        """Check if vector store exists.
        
        Returns:
            True if exists, False otherwise
        """
        return (self.persist_directory / "chroma.sqlite3").exists()
    
    def get_retriever(self, k: int = 4):
        """Get retriever from vector store.
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            Retriever or None if vector store not loaded
        """
        if self._vectorstore is None:
            self.load()
            
        if self._vectorstore:
            return self._vectorstore.as_retriever(search_kwargs={"k": k})
        return None
    
    @property
    def vectorstore(self) -> Optional[Chroma]:
        """Get vector store, loading if necessary.
        
        Returns:
            Vector store or None
        """
        if self._vectorstore is None:
            self.load()
        return self._vectorstore