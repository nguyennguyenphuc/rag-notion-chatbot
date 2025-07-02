"""Embeddings model module."""

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmbeddingsModel:
    """Wrapper for embeddings model."""
    
    def __init__(self, model_name: str):
        """Initialize embeddings model.
        
        Args:
            model_name: Name of the HuggingFace model to use
        """
        self.model_name = model_name
        self._embeddings: Optional[HuggingFaceEmbeddings] = None
        
    def load(self) -> HuggingFaceEmbeddings:
        """Load embeddings model.
        
        Returns:
            Loaded embeddings model
        """
        if self._embeddings is None:
            logger.info(f"Loading embeddings model: {self.model_name}")
            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=self.model_name,
                    model_kwargs={'device': 'cuda'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.info("Embeddings model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading embeddings model: {str(e)}")
                # Fallback to CPU
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=self.model_name,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.warning("Loaded embeddings model on CPU")
                
        return self._embeddings
    
    @property
    def embeddings(self) -> HuggingFaceEmbeddings:
        """Get embeddings model, loading if necessary.
        
        Returns:
            Embeddings model
        """
        if self._embeddings is None:
            self.load()
        return self._embeddings