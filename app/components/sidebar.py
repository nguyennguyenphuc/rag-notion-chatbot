"""Sidebar component."""

import streamlit as st
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Sidebar:
    """Manage sidebar interface."""
    
    def __init__(self):
        """Initialize sidebar."""
        pass
    
    def render_model_status(self, models_loaded: bool):
        """Render model loading status.
        
        Args:
            models_loaded: Whether models are loaded
        """
        if models_loaded:
            st.success("✅ Models đã sẵn sàng!")
        else:
            st.warning("⏳ Đang tải models...")
    
    def render_data_status(self, data_loaded: bool, last_update: datetime = None):
        """Render data loading status.
        
        Args:
            data_loaded: Whether data is loaded
            last_update: Last update time
        """
        st.subheader("📊 Trạng thái dữ liệu")
        
        if data_loaded:
            st.success("✅ Dữ liệu đã được tải")
            if last_update:
                st.info(f"🕒 Cập nhật lần cuối: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("⚠️ Chưa có dữ liệu từ Notion")
    
    def render_refresh_button(self) -> bool:
        """Render refresh button.
        
        Returns:
            True if button clicked
        """
        return st.button("🔄 Refresh dữ liệu từ Notion", use_container_width=True)
    
    def render_chat_controls(self) -> bool:
        """Render chat control buttons.
        
        Returns:
            True if clear button clicked
        """
        st.subheader("💬 Điều khiển Chat")
        return st.button("🗑️ Xóa lịch sử chat", use_container_width=True)
    
    def render_instructions(self):
        """Render usage instructions."""
        st.subheader("📋 Hướng dẫn")
        st.markdown("""
        **Cách sử dụng:**
        1. **Refresh dữ liệu** - Nhấn nút để tải dữ liệu từ Notion
        2. **Đặt câu hỏi** - Nhập câu hỏi trong ô chat
        3. **Nhận trả lời** - AI sẽ trả lời dựa trên dữ liệu Notion
        
        **Lưu ý:**
        - Dữ liệu được tải từ Notion database đã cấu hình
        - Bạn có thể refresh để cập nhật dữ liệu mới nhất
        - Chat history sẽ được lưu trong phiên làm việc
        """)
    
    def render_error(self, error_message: str):
        """Render error message.
        
        Args:
            error_message: Error message to display
        """
        st.error(f"❌ Lỗi: {error_message}")
    
    def render_success(self, success_message: str):
        """Render success message.
        
        Args:
            success_message: Success message to display
        """
        st.success(f"✅ {success_message}")
    
    def render_progress(self, message: str):
        """Render progress spinner.
        
        Args:
            message: Progress message
        """
        return st.spinner(message)