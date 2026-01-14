"""基于 Markdown 的记忆管理系统

记忆框架与业务场景解耦设计：
- MarkdownMemory：通用的记忆存储、检索、更新能力
- ProfileTemplate：可插拔的业务场景模板

使用方式：
1. 默认模板：memory = MarkdownMemory(config)
2. 自定义业务：memory = MarkdownMemory(config, profile_template=YUQING_PROFILE_TEMPLATE)
"""
import json
import shutil
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from src.config import Mem1Config
from src.llm import LLMClient
from src.prompts import (
    ProfileTemplate,
    RECALL_DECISION_PROMPT,
    IMAGE_SEARCH_PROMPT,
)

logger = logging.getLogger(__name__)


class MarkdownMemory:
    """基于 Markdown 文件的用户记忆系统
    
    每个用户有两个文件：
    - _history.json: 历史对话记录
    - _profile.md: 用户画像，LLM 自动整理的重要事项
    """
    
    def __init__(
        self,
        config: Mem1Config,
        memory_dir: Optional[str] = None,
        auto_update_profile: Optional[bool] = None,
        max_workers: int = 2,
        max_profile_chars: Optional[int] = None,
        profile_template: Optional[ProfileTemplate] = None
    ):
        """
        初始化记忆系统
        
        Args:
            config: 配置对象
            memory_dir: 记忆文件存储目录（默认从 config.memory 读取）
            auto_update_profile: 是否在添加对话后自动异步更新用户画像
            max_workers: 异步线程池大小
            max_profile_chars: 用户画像最大字符数，超过则触发压缩
            profile_template: 用户画像模板（可选，用于自定义业务场景）
        """
        self.config = config
        # 优先使用参数，否则从 config.memory 读取
        self.memory_dir = Path(memory_dir or config.memory.memory_dir)
        self.llm = LLMClient(config.llm)
        self.auto_update_profile = auto_update_profile if auto_update_profile is not None else config.memory.auto_update_profile
        self.max_profile_chars = max_profile_chars or config.memory.max_profile_chars
        
        # 画像更新触发条件
        self.update_interval_rounds = config.memory.update_interval_rounds
        self.update_interval_minutes = config.memory.update_interval_minutes
        
        # 用户更新状态跟踪 {user_id: {"rounds": 0, "last_update": datetime}}
        self._user_update_state: Dict[str, Dict[str, Any]] = {}
        
        # 业务场景模板（解耦设计）
        self.profile_template = profile_template or ProfileTemplate()
        
        # 确保目录存在
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化线程池（用于异步更新画像）
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ProfileUpdater")
        self._pending_futures = []  # 跟踪进行中的任务
    
    def _get_user_dir(self, user_id: str) -> Path:
        """获取用户目录"""
        user_dir = self.memory_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def _get_history_path(self, user_id: str) -> Path:
        """获取历史对话文件路径"""
        return self._get_user_dir(user_id) / "_history.json"
    
    def _get_profile_path(self, user_id: str) -> Path:
        """获取用户画像文件路径"""
        return self._get_user_dir(user_id) / "_profile.md"
    
    def _get_user_images_dir(self, user_id: str) -> Path:
        """获取用户图片目录"""
        images_dir = self._get_user_dir(user_id) / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        return images_dir
    
    def _get_images_index_path(self, user_id: str) -> Path:
        """获取图片索引文件路径"""
        return self._get_user_dir(user_id) / "_images.json"
    
    def _load_images_index(self, user_id: str) -> List[Dict[str, str]]:
        """加载图片索引"""
        path = self._get_images_index_path(user_id)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return []
    
    def _save_images_index(self, user_id: str, index: List[Dict[str, str]]) -> None:
        """保存图片索引"""
        path = self._get_images_index_path(user_id)
        path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _init_history_file(self, user_id: str) -> None:
        """初始化历史对话文件"""
        path = self._get_history_path(user_id)
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
    
    def _init_profile_file(self, user_id: str) -> None:
        """初始化用户画像文件"""
        path = self._get_profile_path(user_id)
        if not path.exists():
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            content = self.profile_template.render(user_id, timestamp)
            path.write_text(content, encoding="utf-8")
    
    def add_conversation(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        images: Optional[List[Dict[str, Any]]] = None,
        save_assistant_messages: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        添加对话到沟通记录
        
        Args:
            messages: [{"role": "user", "content": "..."}, ...]
            user_id: 用户ID
            images: [{"filename": "xxx.png", "data": base64_str}, ...] 图片会附加到第一条用户消息
            save_assistant_messages: 是否保存助手回复（默认只保存用户消息，避免坏上下文污染）
            metadata: 元数据，如 {"topic": "舆情分析", "urgency": "high"}
            timestamp: 自定义时间戳（格式：'%Y-%m-%d %H:%M:%S'），默认使用当前时间
        
        Returns:
            {"status": "success", "file": "user001_normal.json"}
        """
        self._init_history_file(user_id)
        path = self._get_history_path(user_id)
        
        # 时间戳
        ts = timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 处理图片
        image_refs = []
        if images:
            user_images_dir = self._get_user_images_dir(user_id)
            images_index = self._load_images_index(user_id)
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for img in images:
                filename = f"{timestamp_str}_{img['filename']}"
                img_path = user_images_dir / filename
                
                # 保存图片
                if 'data' in img:
                    img_data = base64.b64decode(img['data'])
                    img_path.write_bytes(img_data)
                elif 'path' in img:
                    shutil.copy(img['path'], img_path)
                
                # 生成相对路径引用
                rel_path = f"./images/{filename}"
                image_refs.append(rel_path)
                
                # 添加到图片索引
                description = img.get('description', '')
                if not description:
                    # 从用户消息中提取描述
                    for msg in messages:
                        if msg["role"] == "user":
                            description = msg["content"][:100]  # 取前100字作为描述
                            break
                
                images_index.append({
                    "filename": filename,
                    "path": rel_path,
                    "description": description,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "original_name": img['filename']
                })
            
            self._save_images_index(user_id, images_index)
        
        # 构建对话记录对象
        conversation_entry = {
            "timestamp": ts,
            "messages": [],
            "metadata": metadata or {}
        }
        
        # 只保存需要的消息，图片附加到第一条用户消息
        first_user_msg = True
        for msg in messages:
            if msg["role"] == "user":
                msg_obj = {"role": "user", "content": msg["content"]}
                if first_user_msg and image_refs:
                    msg_obj["images"] = image_refs
                    first_user_msg = False
                conversation_entry["messages"].append(msg_obj)
            elif save_assistant_messages:
                conversation_entry["messages"].append({
                    "role": "assistant",
                    "content": msg["content"]
                })
        
        # 读取现有记录
        conversations = json.loads(path.read_text(encoding="utf-8"))
        
        # 追加新记录
        conversations.append(conversation_entry)
        
        # 写回文件
        path.write_text(json.dumps(conversations, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # 异步更新用户画像（不阻塞）
        if self.auto_update_profile:
            self._async_update_profile(user_id)
        
        return {"status": "success", "file": str(path)}
    
    def update_profile(self, user_id: str) -> Dict[str, Any]:
        """
        更新用户画像（LLM 从对话中提取重要信息）
        
        Args:
            user_id: 用户ID
        
        Returns:
            {"status": "success", "updated": True}
        """
        self._init_profile_file(user_id)
        
        # 读取对话记录
        history_path = self._get_history_path(user_id)
        if not history_path.exists():
            return {"status": "success", "updated": False, "reason": "no_conversation"}
        
        # 将 JSON 转换为可读文本
        conversations = json.loads(history_path.read_text(encoding="utf-8"))
        history_content = self._format_conversations_for_llm(conversations)
        
        # 读取现有用户画像
        profile_path = self._get_profile_path(user_id)
        profile_content = profile_path.read_text(encoding="utf-8")
        
        # 使用模板的提示词（业务场景解耦）
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        prompt = self.profile_template.get_update_prompt().format(
            user_id=user_id,
            normal_content=history_content,
            import_content=profile_content,
            timestamp=timestamp
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "请整理用户画像"}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        
        # 检查是否需要压缩
        if len(response) > self.max_profile_chars:
            logger.info(f"📦 用户画像超长({len(response)}>{self.max_profile_chars})，触发压缩...")
            response = self._compress_profile(user_id, response)
            logger.info(f"📦 压缩后长度: {len(response)}")
        
        # 更新用户画像
        profile_path.write_text(response, encoding="utf-8")
        
        return {"status": "success", "updated": True, "length": len(response)}
    
    def get_context(
        self,
        user_id: str,
        query: str,
        include_normal: Optional[bool] = None,
        days_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取记忆上下文（用于提示词）
        
        Args:
            user_id: 用户ID
            query: 当前用户问题
            include_normal: 是否包含沟通记录，None 表示自动判断
            days_limit: 只加载最近 N 天的对话，None 表示全部
        
        Returns:
            {
                "current_time": "2025-12-25 16:30 星期四",
                "import_content": "用户画像笔记内容",
                "normal_content": "用户沟通记录内容（可选）",
                "need_normal": True/False,
                "recall_reason": "回忆判断原因",
                "recall_triggered_by": "llm_decision/manual/auto",
                "profile_last_updated": "2025-12-25 10:30",
                "conversations_count": 10
            }
        """
        self._init_profile_file(user_id)
        self._init_history_file(user_id)
        
        # 当前时间（自动注入，便于理解"3天前"等相对时间）
        now = datetime.now()
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        current_time = f"{now.strftime('%Y-%m-%d %H:%M')} {weekdays[now.weekday()]}"
        
        # 读取用户画像笔记
        profile_path = self._get_profile_path(user_id)
        profile_content = profile_path.read_text(encoding="utf-8")
        
        # 获取画像最后更新时间
        profile_last_updated = "未更新"
        if profile_path.exists():
            mtime = profile_path.stat().st_mtime
            profile_last_updated = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        
        result = {
            "current_time": current_time,
            "import_content": profile_content,
            "normal_content": "",
            "need_history": False,
            "recall_reason": "",
            "recall_triggered_by": "none",
            "profile_last_updated": profile_last_updated,
            "conversations_count": 0
        }
        
        # 判断是否需要历史记录
        if include_normal is None:
            need_history, reason = self._should_include_history(query)
            result["recall_reason"] = reason
            result["recall_triggered_by"] = "llm_decision"
        elif include_normal:
            need_history = True
            result["recall_triggered_by"] = "manual"
        else:
            need_history = False
            result["recall_triggered_by"] = "manual"
        
        if need_history:
            history_path = self._get_history_path(user_id)
            if history_path.exists():
                conversations = json.loads(history_path.read_text(encoding="utf-8"))
                
                # 按时间过滤
                if days_limit:
                    cutoff_date = datetime.now() - timedelta(days=days_limit)
                    conversations = [
                        c for c in conversations 
                        if datetime.strptime(c.get("timestamp", ""), '%Y-%m-%d %H:%M:%S') >= cutoff_date
                    ]
                
                result["normal_content"] = self._format_conversations_for_llm(conversations)
                result["need_history"] = True
                result["conversations_count"] = len(conversations)
        
        return result
    
    def _compress_profile(self, user_id: str, profile_content: str) -> str:
        """
        压缩用户画像（LLM 智能精简）
        
        Args:
            user_id: 用户ID
            profile_content: 当前画像内容
        
        Returns:
            压缩后的画像内容
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        prompt = self.profile_template.get_compress_prompt().format(
            user_id=user_id,
            profile_content=profile_content,
            max_chars=self.max_profile_chars,
            timestamp=timestamp
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "请压缩用户画像"}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        return response
    
    def _should_include_history(self, query: str) -> tuple[bool, str]:
        """
        LLM 判断是否需要加载历史记录（回忆工具）
        
        Returns:
            (need_history, reason): 是否需要加载，以及原因
        """
        prompt = RECALL_DECISION_PROMPT.format(query=query)
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        
        # 解析 LLM 响应（改进3：返回判断原因）
        response_lower = response.strip().lower()
        need_history = "true" in response_lower or "是" in response_lower or "需要" in response_lower
        
        logger.info(f"🔍 回忆判断: query='{query[:50]}...', need_history={need_history}, response='{response.strip()}'")
        
        return need_history, response.strip()
    
    def get_user_list(self) -> List[str]:
        """获取所有用户ID列表"""
        users = []
        for d in self.memory_dir.iterdir():
            if d.is_dir() and not d.name.startswith('.'):
                users.append(d.name)
        return users
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """删除用户所有记忆"""
        user_dir = self.memory_dir / user_id
        if user_dir.exists():
            shutil.rmtree(user_dir)
            return {"status": "success", "deleted": str(user_dir)}
        return {"status": "success", "deleted": None}
    
    def search_images(self, user_id: str, query: str) -> List[Dict[str, str]]:
        """
        搜索用户图片（LLM 语义匹配）
        
        Args:
            user_id: 用户ID
            query: 用户的自然语言查询
        
        Returns:
            匹配的图片列表
        """
        images_index = self._load_images_index(user_id)
        if not images_index:
            return []
        
        # 构建图片列表描述
        images_desc = "\n".join([
            f"[{i}] 文件名: {img['original_name']}, 时间: {img['timestamp']}, 描述: {img['description'][:100]}"
            for i, img in enumerate(images_index)
        ])
        
        prompt = IMAGE_SEARCH_PROMPT.format(
            query=query,
            images_desc=images_desc
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        
        # 解析 LLM 返回的索引
        results = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.isdigit():
                idx = int(line)
                if 0 <= idx < len(images_index):
                    results.append(images_index[idx])
            elif line.startswith('[') and ']' in line:
                # 处理 [0] 这种格式
                try:
                    idx = int(line[1:line.index(']')])
                    if 0 <= idx < len(images_index):
                        results.append(images_index[idx])
                except ValueError:
                    pass
        
        logger.info(f"🖼️ 图片搜索: query='{query}', 找到 {len(results)} 张")
        return results
    
    def _should_trigger_update(self, user_id: str) -> bool:
        """
        判断是否应该触发画像更新（混合策略）
        
        触发条件（满足任一即触发）：
        1. 累积对话轮数 >= update_interval_rounds
        2. 距上次更新时间 >= update_interval_minutes
        
        Returns:
            是否应该触发更新
        """
        now = datetime.now()
        
        # 初始化用户状态
        if user_id not in self._user_update_state:
            self._user_update_state[user_id] = {
                "rounds": 0,
                "last_update": None
            }
        
        state = self._user_update_state[user_id]
        state["rounds"] += 1
        
        should_update = False
        reason = ""
        
        # 条件1：累积轮数达到阈值
        if state["rounds"] >= self.update_interval_rounds:
            should_update = True
            reason = f"轮数={state['rounds']} >= {self.update_interval_rounds}"
        
        # 条件2：距上次更新超过时间阈值
        if not should_update and state["last_update"] is not None:
            elapsed = (now - state["last_update"]).total_seconds() / 60
            if elapsed >= self.update_interval_minutes:
                should_update = True
                reason = f"时间={elapsed:.1f}分钟 >= {self.update_interval_minutes}"
        
        # 条件3：首次创建画像
        if not should_update and state["last_update"] is None:
            import_path = self._get_import_path(user_id)
            if not import_path.exists():
                should_update = True
                reason = "首次创建画像"
        
        if should_update:
            logger.info(f"📊 触发更新（{reason}）: {user_id}")
            # 立即重置轮数，避免重复触发
            state["rounds"] = 0
            return True
        
        logger.debug(f"📊 暂不更新（轮数={state['rounds']}/{self.update_interval_rounds}）: {user_id}")
        return False
    
    def _mark_update_complete(self, user_id: str) -> None:
        """标记更新完成（更新完成后调用）"""
        if user_id in self._user_update_state:
            self._user_update_state[user_id]["last_update"] = datetime.now()
    
    def _async_update_profile(self, user_id: str) -> None:
        """
        异步更新用户画像（不阻塞主流程）
        """
        # 检查是否应该触发更新
        if not self._should_trigger_update(user_id):
            return
        
        def _task():
            try:
                logger.info(f"🔄 开始异步更新用户画像: {user_id}")
                result = self.update_profile(user_id)
                self._mark_update_complete(user_id)
                logger.info(f"✅ 用户画像更新完成: {user_id}, result={result}")
            except Exception as e:
                logger.error(f"❌ 用户画像更新失败: {user_id}, error={e}")
        
        # 提交到线程池
        future = self._executor.submit(_task)
        self._pending_futures.append(future)
        
        # 清理已完成的 future
        self._pending_futures = [f for f in self._pending_futures if not f.done()]
    
    def wait_for_pending_updates(self, timeout: Optional[float] = None) -> None:
        """
        等待所有进行中的画像更新完成
        
        Args:
            timeout: 超时时间（秒），None 表示无限等待
        """
        from concurrent.futures import wait
        if self._pending_futures:
            logger.info(f"等待 {len(self._pending_futures)} 个画像更新任务完成...")
            wait(self._pending_futures, timeout=timeout)
            self._pending_futures = [f for f in self._pending_futures if not f.done()]
    
    def shutdown(self, wait: bool = True) -> None:
        """
        关闭线程池
        
        Args:
            wait: 是否等待进行中的任务完成
        """
        logger.info("正在关闭记忆系统线程池...")
        self._executor.shutdown(wait=wait)
        logger.info("记忆系统线程池已关闭")
    
    def _format_conversations_for_llm(self, conversations: List[Dict[str, Any]]) -> str:
        """
        将 JSON 对话记录格式化为 LLM 可读的文本
        
        Args:
            conversations: 对话记录列表
        
        Returns:
            格式化的文本
        """
        output = []
        for conv in conversations:
            timestamp = conv.get("timestamp", "未知时间")
            metadata = conv.get("metadata", {})
            
            # 构建标题
            title = f"### {timestamp}"
            if metadata:
                tags = " ".join([f"[{k}:{v}]" for k, v in metadata.items()])
                title += f" {tags}"
            
            output.append(title)
            output.append("")
            
            # 添加消息
            for msg in conv.get("messages", []):
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                role_name = "用户" if msg["role"] == "user" else "助手"
                output.append(f"**{role_icon} {role_name}**: {msg['content']}")
                # 图片在消息级别
                if msg.get("images"):
                    for img_path in msg["images"]:
                        output.append(f"![Image]({img_path})")
                output.append("")
            
            output.append("---")
            output.append("")
        
        return "\n".join(output)
    
    def get_conversations(
        self,
        user_id: str,
        days_limit: Optional[int] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        获取对话记录（原始 JSON 格式）
        
        Args:
            user_id: 用户ID
            days_limit: 只返回最近 N 天的对话
            metadata_filter: 元数据过滤条件，如 {"topic": "舆情分析", "urgency": "high"}
        
        Returns:
            对话记录列表
        """
        history_path = self._get_history_path(user_id)
        if not history_path.exists():
            return []
        
        conversations = json.loads(history_path.read_text(encoding="utf-8"))
        
        # 按时间过滤
        if days_limit:
            cutoff_date = datetime.now() - timedelta(days=days_limit)
            conversations = [
                c for c in conversations 
                if datetime.strptime(c.get("timestamp", ""), '%Y-%m-%d %H:%M:%S') >= cutoff_date
            ]
        
        # 按元数据过滤（支持多字段匹配）
        if metadata_filter:
            def match_metadata(conv):
                conv_meta = conv.get("metadata", {})
                return all(conv_meta.get(k) == v for k, v in metadata_filter.items())
            conversations = [c for c in conversations if match_metadata(c)]
        
        return conversations
