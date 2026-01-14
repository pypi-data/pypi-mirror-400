"""记忆系统的 LangChain Tools（改进2：工具化记忆访问）

让 Agent 可以主动决定何时查询记忆，提升透明度和灵活性
"""
import logging
from typing import Optional
from langchain_core.tools import tool
from src.memory_md import MarkdownMemory

logger = logging.getLogger(__name__)


def create_memory_tools(memory: MarkdownMemory, user_id: str):
    """
    为指定用户创建记忆工具集
    
    Args:
        memory: MarkdownMemory 实例
        user_id: 用户ID
    
    Returns:
        [search_user_profile, recall_conversation_history, search_user_images]
    """
    
    @tool
    def search_user_profile(query: str) -> str:
        """搜索用户画像信息
        
        当需要了解用户的基本信息、偏好习惯、重要事项时使用此工具。
        例如：用户的报告风格偏好、沟通方式、职位信息等。
        
        Args:
            query: 查询内容，如"用户的报告偏好"、"用户职位"
        
        Returns:
            用户画像内容
        """
        logger.info(f"🔍 [Tool] search_user_profile: user_id={user_id}, query='{query}'")
        
        import_path = memory._get_import_path(user_id)
        if not import_path.exists():
            return "暂无用户画像信息"
        
        content = import_path.read_text(encoding="utf-8")
        
        # 返回完整画像（后续可以优化为语义检索）
        return content
    
    @tool
    def recall_conversation_history(query: str, days_limit: int = 30) -> str:
        """回忆历史对话
        
        当用户询问之前聊过的内容、想回顾历史对话时使用此工具。
        例如：用户说"上次说的那个案例"、"之前讨论的方案"。
        
        Args:
            query: 查询内容，如"上次讨论的舆情案例"、"之前提到的数据"
            days_limit: 只查询最近 N 天的对话（默认 30 天）
        
        Returns:
            历史对话记录
        """
        logger.info(f"🔍 [Tool] recall_conversation_history: user_id={user_id}, query='{query}', days_limit={days_limit}")
        
        conversations = memory.get_conversations(user_id, days_limit=days_limit)
        
        if not conversations:
            return "暂无历史对话记录"
        
        # 格式化为可读文本
        content = memory._format_conversations_for_llm(conversations)
        return content
    
    @tool
    def search_user_images(query: str) -> str:
        """搜索用户上传的图片
        
        当用户询问之前上传的图片、截图时使用此工具。
        例如：用户说"之前那个截图"、"上次发的图片"。
        
        Args:
            query: 查询内容，如"之前的舆情截图"、"上次的数据图表"
        
        Returns:
            匹配的图片列表（JSON 格式）
        """
        logger.info(f"🔍 [Tool] search_user_images: user_id={user_id}, query='{query}'")
        
        results = memory.search_images(user_id, query)
        
        if not results:
            return "未找到匹配的图片"
        
        # 格式化返回
        output = f"找到 {len(results)} 张图片：\n\n"
        for i, img in enumerate(results, 1):
            output += f"{i}. {img['original_name']}\n"
            output += f"   时间: {img['timestamp']}\n"
            output += f"   路径: {img['path']}\n"
            output += f"   描述: {img['description']}\n\n"
        
        return output
    
    return [search_user_profile, recall_conversation_history, search_user_images]
