"""Chat interface component."""

import streamlit as st
import time
from typing import Optional


class ChatInterface:
    """Manage chat interface."""
    
    def __init__(self):
        """Initialize chat interface."""
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state for chat."""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def add_message(self, role: str, content: str):
        """Add message to chat history.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        st.session_state.chat_history.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
    
    def clear_history(self):
        """Clear chat history."""
        st.session_state.chat_history = []
    
    def display_chat(self):
        """Display chat history."""
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write("Xin chào! Tôi là AI Assistant. Hãy refresh dữ liệu từ Notion và bắt đầu đặt câu hỏi nhé! 😊")
    
    def handle_user_input(self, rag_chain: Optional[object]) -> Optional[str]:
        """Handle user input and generate response.
        
        Args:
            rag_chain: RAG chain for generating responses
            
        Returns:
            User input if any
        """
        if rag_chain:
            user_input = st.chat_input("Nhập câu hỏi của bạn...")
            
            if user_input:
                # Add user message
                self.add_message("user", user_input)
                
                # Display user message
                with st.chat_message("user"):
                    st.write(user_input)
                
                # Generate response
                with st.chat_message("assistant"):
                    with st.spinner("Đang suy nghĩ..."):
                        try:
                            response = rag_chain.invoke(user_input)
                            st.write(response)
                            self.add_message("assistant", response)
                            
                        except Exception as e:
                            error_msg = f"Xin lỗi, đã có lỗi xảy ra: {str(e)}"
                            st.error(error_msg)
                            self.add_message("assistant", error_msg)
                
                return user_input
        else:
            st.chat_input("Nhập câu hỏi của bạn...", disabled=True)
            
        return None