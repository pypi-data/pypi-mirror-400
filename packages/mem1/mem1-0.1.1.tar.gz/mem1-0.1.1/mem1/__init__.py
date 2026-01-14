"""
Mem1 - 用户记忆系统（支持可插拔存储后端）
"""
import logging

__version__ = "0.1.1"

# 屏蔽第三方库的详细日志（必须在导入前设置）
logging.getLogger("elastic_transport").setLevel(logging.WARNING)
logging.getLogger("elastic_transport.transport").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

from mem1.memory import Mem1Memory
from mem1.config import Mem1Config, LLMConfig
from mem1.storage import StorageBackend, ESStorage

__all__ = ["Mem1Memory", "Mem1Config", "LLMConfig", "StorageBackend", "ESStorage"]
