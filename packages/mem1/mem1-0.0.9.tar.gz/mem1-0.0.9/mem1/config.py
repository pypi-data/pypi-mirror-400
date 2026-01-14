"""配置管理"""
import os
from typing import Optional
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: str
    model: str
    api_key: str
    base_url: str
    temperature: float


class VLConfig(BaseModel):
    """视觉语言模型配置（可选，配置了 provider 即启用）
    
    支持的 provider:
    - qwen: 使用 dashscope SDK 调用 Qwen-VL
    - doubao: 使用 OpenAI 兼容接口调用豆包视觉模型
    """
    provider: str = ""  # qwen / doubao
    model: str = ""
    api_key: str = ""
    base_url: str = ""  # doubao 需要
    
    @property
    def enabled(self) -> bool:
        """配置了 provider 就启用"""
        return bool(self.provider)


class MemoryConfig(BaseModel):
    """记忆系统配置"""
    memory_dir: str
    auto_update_profile: bool
    max_profile_chars: int
    update_interval_rounds: int      # 每 N 轮对话触发更新
    update_interval_minutes: int     # 距上次更新超过 M 分钟触发
    save_assistant_messages: bool    # 是否保存 assistant 回复
    max_assistant_chars: int         # assistant 回复超过此长度触发摘要
    context_days_limit: int          # get_context 检索最近几天的对话


class ESConfig(BaseModel):
    """Elasticsearch 配置"""
    hosts: list[str]
    index_name: str


class ImagesConfig(BaseModel):
    """图片存储配置"""
    images_dir: str


class Mem1Config(BaseModel):
    """Mem1 总配置"""
    llm: LLMConfig
    vl: VLConfig
    memory: MemoryConfig
    es: ESConfig
    images: ImagesConfig
    
    @classmethod
    def from_env(cls) -> "Mem1Config":
        """从环境变量加载配置
        
        必需的环境变量：
        - MEM1_LLM_API_KEY: LLM API 密钥
        - MEM1_LLM_BASE_URL: LLM API 地址（OpenAI 兼容）
        - MEM1_LLM_MODEL: LLM 模型名
        - MEM1_ES_HOSTS: ES 地址
        - MEM1_ES_INDEX: ES 索引名
        - MEM1_MEMORY_DIR: 记忆存储目录
        - MEM1_AUTO_UPDATE_PROFILE: 是否自动更新画像 (true/false)
        - MEM1_MAX_PROFILE_CHARS: 画像最大字符数
        - MEM1_UPDATE_INTERVAL_ROUNDS: 画像更新间隔轮数
        - MEM1_UPDATE_INTERVAL_MINUTES: 画像更新间隔分钟数
        
        可选的环境变量（VL 模型，使用 dashscope SDK）：
        - MEM1_VL_MODEL: VL 模型名（如 qwen-vl-max），配置即启用
        - MEM1_VL_API_KEY: dashscope API 密钥
        """
        # 必需配置检查
        required_vars = {
            "MEM1_LLM_API_KEY": os.getenv("MEM1_LLM_API_KEY"),
            "MEM1_LLM_BASE_URL": os.getenv("MEM1_LLM_BASE_URL"),
            "MEM1_LLM_MODEL": os.getenv("MEM1_LLM_MODEL"),
            "MEM1_ES_HOSTS": os.getenv("MEM1_ES_HOSTS"),
            "MEM1_ES_INDEX": os.getenv("MEM1_ES_INDEX"),
            "MEM1_MEMORY_DIR": os.getenv("MEM1_MEMORY_DIR"),
            "MEM1_AUTO_UPDATE_PROFILE": os.getenv("MEM1_AUTO_UPDATE_PROFILE"),
            "MEM1_MAX_PROFILE_CHARS": os.getenv("MEM1_MAX_PROFILE_CHARS"),
            "MEM1_UPDATE_INTERVAL_ROUNDS": os.getenv("MEM1_UPDATE_INTERVAL_ROUNDS"),
            "MEM1_UPDATE_INTERVAL_MINUTES": os.getenv("MEM1_UPDATE_INTERVAL_MINUTES"),
            "MEM1_SAVE_ASSISTANT_MESSAGES": os.getenv("MEM1_SAVE_ASSISTANT_MESSAGES"),
            "MEM1_MAX_ASSISTANT_CHARS": os.getenv("MEM1_MAX_ASSISTANT_CHARS"),
            "MEM1_LLM_TEMPERATURE": os.getenv("MEM1_LLM_TEMPERATURE"),
            "MEM1_CONTEXT_DAYS_LIMIT": os.getenv("MEM1_CONTEXT_DAYS_LIMIT"),
        }
        
        missing = [k for k, v in required_vars.items() if not v]
        if missing:
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing)}")
        
        # ES hosts 支持逗号分隔的多个地址
        es_hosts = [h.strip() for h in required_vars["MEM1_ES_HOSTS"].split(",")]
        
        # 图片目录基于记忆目录
        memory_dir = required_vars["MEM1_MEMORY_DIR"]
        images_dir = f"{memory_dir}/images"
        
        # VL 模型配置（可选，配置了 provider 即启用）
        vl_config = VLConfig(
            provider=os.getenv("MEM1_VL_PROVIDER", ""),
            model=os.getenv("MEM1_VL_MODEL", ""),
            api_key=os.getenv("MEM1_VL_API_KEY", ""),
            base_url=os.getenv("MEM1_VL_BASE_URL", "")
        )
        
        return cls(
            llm=LLMConfig(
                provider="openai",
                model=required_vars["MEM1_LLM_MODEL"],
                api_key=required_vars["MEM1_LLM_API_KEY"],
                base_url=required_vars["MEM1_LLM_BASE_URL"],
                temperature=float(required_vars["MEM1_LLM_TEMPERATURE"])
            ),
            vl=vl_config,
            memory=MemoryConfig(
                memory_dir=memory_dir,
                auto_update_profile=required_vars["MEM1_AUTO_UPDATE_PROFILE"].lower() == "true",
                max_profile_chars=int(required_vars["MEM1_MAX_PROFILE_CHARS"]),
                update_interval_rounds=int(required_vars["MEM1_UPDATE_INTERVAL_ROUNDS"]),
                update_interval_minutes=int(required_vars["MEM1_UPDATE_INTERVAL_MINUTES"]),
                save_assistant_messages=required_vars["MEM1_SAVE_ASSISTANT_MESSAGES"].lower() == "true",
                max_assistant_chars=int(required_vars["MEM1_MAX_ASSISTANT_CHARS"]),
                context_days_limit=int(required_vars["MEM1_CONTEXT_DAYS_LIMIT"])
            ),
            es=ESConfig(
                hosts=es_hosts,
                index_name=required_vars["MEM1_ES_INDEX"]
            ),
            images=ImagesConfig(
                images_dir=images_dir
            )
        )
