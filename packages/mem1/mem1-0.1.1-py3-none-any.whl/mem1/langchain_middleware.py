"""LangChain 1.0 中间件集成 - mem1 用户记忆"""
import logging
from typing import Any
from dataclasses import dataclass

from langchain.agents.middleware import AgentMiddleware, before_model, after_model
from langchain.agents.middleware.types import AgentState
from langgraph.runtime import Runtime

from mem1.memory_es import Mem1Memory

logger = logging.getLogger(__name__)


@dataclass
class Mem1Context:
    """mem1 上下文，用于传递 user_id"""
    user_id: str


class Mem1Middleware(AgentMiddleware):
    """
    mem1 记忆中间件
    
    功能：
    1. 模型调用前：注入用户画像到 system prompt
    2. 模型调用后：保存对话到记忆系统
    
    使用方式：
    ```python
    from langchain.agents import create_agent
    from mem1.langchain_middleware import Mem1Middleware, Mem1Context
    from mem1.memory_es import Mem1Memory
    
    memory = Mem1Memory(config)
    
    agent = create_agent(
        model="deepseek-chat",
        tools=[...],
        middleware=[Mem1Middleware(memory)],
        context_schema=Mem1Context
    )
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "你好"}]},
        context=Mem1Context(user_id="user001")
    )
    ```
    """
    
    def __init__(self, memory: Mem1Memory, inject_profile: bool = True):
        """
        Args:
            memory: Mem1Memory 实例
            inject_profile: 是否自动注入用户画像到 system prompt
        """
        self.memory = memory
        self.inject_profile = inject_profile
    
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """模型调用前：注入用户画像"""
        if not self.inject_profile:
            return None
        
        user_id = getattr(runtime.context, 'user_id', None)
        if not user_id:
            logger.warning("Mem1Middleware: 未提供 user_id，跳过记忆注入")
            return None
        
        # 获取最新用户消息作为 query
        query = ""
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'type') and msg.type == "human":
                query = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "user":
                query = msg.get("content", "")
                break
        
        # 获取记忆上下文
        ctx = self.memory.get_context(user_id=user_id, query=query)
        
        # 构建记忆提示
        memory_prompt = f"""
## 关于这位用户的重要信息（请务必参考）
{ctx['import_content']}
"""
        if ctx.get('need_normal') and ctx.get('normal_content'):
            memory_prompt += f"""
## 历史对话记录
{ctx['normal_content']}
"""
        
        # 注入到消息中（作为 system message 的补充）
        from langchain.messages import SystemMessage
        
        messages = list(state["messages"])
        # 在第一条消息后插入记忆
        if messages:
            messages.insert(1, SystemMessage(content=memory_prompt))
        
        logger.info(f"Mem1Middleware: 已注入用户画像 user_id={user_id}, need_normal={ctx.get('need_normal')}")
        
        return {"messages": messages}
    
    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """模型调用后：保存对话"""
        user_id = getattr(runtime.context, 'user_id', None)
        if not user_id:
            return None
        
        # 提取最近一轮对话
        messages = state["messages"]
        if len(messages) < 2:
            return None
        
        # 找到最近的 user 和 assistant 消息
        recent_conversation = []
        for msg in reversed(messages):
            if hasattr(msg, 'type'):
                if msg.type == "ai" and not recent_conversation:
                    recent_conversation.insert(0, {"role": "assistant", "content": msg.content})
                elif msg.type == "human" and len(recent_conversation) == 1:
                    recent_conversation.insert(0, {"role": "user", "content": msg.content})
                    break
        
        if len(recent_conversation) == 2:
            self.memory.add_conversation(
                messages=recent_conversation,
                user_id=user_id
            )
            logger.info(f"Mem1Middleware: 已保存对话 user_id={user_id}")
        
        return None


# 装饰器风格的简化版本
def create_mem1_middleware(memory: Mem1Memory):
    """
    创建 mem1 记忆中间件（装饰器风格）
    
    返回两个中间件函数：before_model 和 after_model
    """
    
    @before_model
    def inject_memory(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """注入用户画像"""
        user_id = getattr(runtime.context, 'user_id', None)
        if not user_id:
            return None
        
        query = ""
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'type') and msg.type == "human":
                query = msg.content
                break
        
        ctx = memory.get_context(user_id=user_id, query=query)
        
        memory_prompt = f"\n## 用户画像\n{ctx['import_content']}"
        if ctx.get('need_normal'):
            memory_prompt += f"\n## 历史对话\n{ctx['normal_content']}"
        
        from langchain.messages import SystemMessage
        messages = list(state["messages"])
        if messages:
            messages.insert(1, SystemMessage(content=memory_prompt))
        
        return {"messages": messages}
    
    @after_model
    def save_conversation(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """保存对话"""
        user_id = getattr(runtime.context, 'user_id', None)
        if not user_id:
            return None
        
        messages = state["messages"]
        if len(messages) >= 2:
            last_ai = messages[-1]
            last_human = None
            for msg in reversed(messages[:-1]):
                if hasattr(msg, 'type') and msg.type == "human":
                    last_human = msg
                    break
            
            if last_human and hasattr(last_ai, 'type') and last_ai.type == "ai":
                memory.add_conversation(
                    messages=[
                        {"role": "user", "content": last_human.content},
                        {"role": "assistant", "content": last_ai.content}
                    ],
                    user_id=user_id
                )
        
        return None
    
    return [inject_memory, save_conversation]
