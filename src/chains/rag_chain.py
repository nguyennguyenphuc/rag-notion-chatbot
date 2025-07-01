"""RAG chain module."""

from typing import Optional, List
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)


class RAGChain:
    """RAG chain for question answering."""
    
    def __init__(self, llm, retriever):
        """Initialize RAG chain.
        
        Args:
            llm: Language model
            retriever: Document retriever
        """
        self.llm = llm
        self.retriever = retriever
        self._chain = None
        
    def build(self):
        """Build the RAG chain."""
        try:
            # Load prompt template
            prompt = hub.pull("rlm/rag-prompt")
            
            # Create chain
            self._chain = (
                {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
            
            logger.info("RAG chain built successfully")
            
        except Exception as e:
            logger.error(f"Error building RAG chain: {str(e)}")
            raise
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Format documents for context.
        
        Args:
            docs: List of documents
            
        Returns:
            Formatted string
        """
        return "\n\n".join(doc.page_content for doc in docs)
    
    def invoke(self, question: str) -> str:
        """Invoke the RAG chain with a question.
        
        Args:
            question: User question
            
        Returns:
            Generated answer
        """
        if self._chain is None:
            self.build()
            
        try:
            response = self._chain.invoke(question)
            
            # Clean up response
            if 'Answer:' in response:
                answer = response.split('Answer:')[1].strip()
            else:
                answer = response.strip()
                
            return answer
            
        except Exception as e:
            logger.error(f"Error invoking RAG chain: {str(e)}")
            raise
    
    def get_context(self, question: str) -> List[Document]:
        """Get relevant context for a question.
        
        Args:
            question: User question
            
        Returns:
            List of relevant documents
        """
        try:
            return self.retriever.get_relevant_documents(question)
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return []
            