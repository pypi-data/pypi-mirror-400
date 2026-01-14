"""基于可插拔存储层的记忆管理系统"""
import re
import shutil
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from mem1.config import Mem1Config
from mem1.llm import LLMClient, VLClient
from mem1.prompts import ProfileTemplate, RECALL_DECISION_PROMPT, IMAGE_SEARCH_PROMPT, ASSISTANT_SUMMARY_PROMPT, CONTEXT_SUFFICIENT_PROMPT
from mem1.storage import StorageBackend, ESStorage

logger = logging.getLogger(__name__)


class Mem1Memory:
    """用户记忆系统（支持可插拔存储后端）
    
    数据存储：
    - 存储后端: 历史对话记录 + 用户状态 + 用户画像
    - 本地文件: 图片文件存储
    """
    
    def __init__(
        self,
        config: Mem1Config,
        user_id: str,
        topic_id: str = "default",
        memory_dir: Optional[str] = None,
        profile_template: Optional[ProfileTemplate] = None,
        storage: Optional[StorageBackend] = None
    ):
        """初始化记忆系统
        
        Args:
            config: 配置对象
            user_id: 用户ID（必填）
            topic_id: 话题ID（默认 "default"），同一用户可有多个话题
            memory_dir: 记忆文件存储目录
            profile_template: 用户画像模板
            storage: 存储后端（可选，默认使用 ESStorage）
        """
        self.config = config
        self.user_id = user_id
        self.topic_id = topic_id
        self.memory_dir = Path(memory_dir or config.memory.memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 图片存储目录
        self.images_dir = Path(config.images.images_dir)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 存储后端（可插拔）
        if storage:
            self.storage = storage
        else:
            self.storage = ESStorage(config.es.hosts, config.es.index_name)
        
        # LLM 客户端
        self.llm = LLMClient(config.llm)
        
        # VL 客户端（可选）
        self.vl = VLClient(config.vl) if config.vl.enabled else None
        
        # 业务场景模板
        self.profile_template = profile_template or ProfileTemplate()
        
        # 配置参数
        self.max_profile_chars = config.memory.max_profile_chars
        self.auto_update_profile = config.memory.auto_update_profile
        self.update_interval_rounds = config.memory.update_interval_rounds
        self.update_interval_minutes = config.memory.update_interval_minutes
        self.save_assistant_messages = config.memory.save_assistant_messages
        self.max_assistant_chars = config.memory.max_assistant_chars
    
    # ========== 图片处理 ==========
    
    def _get_user_images_dir(self, user_id: str) -> Path:
        """获取用户图片目录"""
        images_dir = self.images_dir / user_id
        images_dir.mkdir(parents=True, exist_ok=True)
        return images_dir
    
    def _load_images_index(self, user_id: str) -> List[Dict[str, str]]:
        """从对话记录中提取用户所有图片"""
        if hasattr(self.storage, 'get_conversations_with_images'):
            conversations = self.storage.get_conversations_with_images(user_id)
        else:
            conversations = self.storage.get_conversations(user_id)
        
        images = []
        for conv in conversations:
            conv_images = conv.get("images", [])
            images.extend(conv_images)
        return images
    
    def _save_image_to_conversation(self, conversation_entry: Dict, image_doc: Dict[str, str]) -> None:
        """将图片信息添加到对话记录"""
        if "images" not in conversation_entry:
            conversation_entry["images"] = []
        conversation_entry["images"].append(image_doc)
    
    # ========== 用户画像 ==========
    
    def _get_profile(self, user_id: str) -> Optional[str]:
        """获取用户画像"""
        result = self.storage.get_profile(user_id)
        return result["content"] if result else None
    
    def _save_profile(self, user_id: str, content: str) -> None:
        """保存用户画像"""
        self.storage.save_profile(user_id, content)
    
    def _init_profile(self, user_id: str) -> str:
        """初始化用户画像（不存在则创建）"""
        content = self._get_profile(user_id)
        if content is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            content = self.profile_template.render(user_id, timestamp)
            self._save_profile(user_id, content)
            logger.info(f"✓ 创建用户画像: {user_id}")
        return content
    
    # ========== 用户状态 ==========
    
    def _get_user_state(self, user_id: str) -> Dict[str, Any]:
        """获取用户更新状态"""
        state = self.storage.get_user_state(user_id)
        if state is None:
            return {"user_id": user_id, "rounds": 0, "last_update": None}
        return state
    
    def _update_user_state(self, user_id: str, rounds: int, last_update: Optional[str] = None) -> None:
        """更新用户状态"""
        self.storage.save_user_state(user_id, rounds, last_update)
    
    def _should_trigger_update(self, user_id: str) -> bool:
        """判断是否应该触发画像更新"""
        state = self._get_user_state(user_id)
        rounds = state.get("rounds", 0) + 1
        last_update_str = state.get("last_update")
        
        should_update = False
        reason = ""
        
        if rounds >= self.update_interval_rounds:
            should_update = True
            reason = f"轮数={rounds} >= {self.update_interval_rounds}"
        
        if not should_update and last_update_str:
            try:
                last_update = datetime.strptime(last_update_str, '%Y-%m-%d %H:%M:%S')
                elapsed = (datetime.now() - last_update).total_seconds() / 60
                if elapsed >= self.update_interval_minutes:
                    should_update = True
                    reason = f"时间={elapsed:.1f}分钟 >= {self.update_interval_minutes}"
            except ValueError:
                pass
        
        if not should_update and last_update_str is None:
            should_update = True
            reason = "首次创建画像"
        
        if should_update:
            logger.info(f"📊 触发画像更新（{reason}）: {user_id}")
            self._update_user_state(user_id, 0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            self._update_user_state(user_id, rounds, last_update_str)
            logger.debug(f"📊 暂不更新（轮数={rounds}/{self.update_interval_rounds}）: {user_id}")
        
        return should_update

    
    # ========== 对话管理 ==========
    
    def add_conversation(
        self,
        messages: List[Dict[str, str]],
        images: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """添加对话"""
        ts = timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_id = self.user_id
        topic_id = self.topic_id
        
        conversation_entry = {
            "user_id": user_id,
            "topic_id": topic_id,
            "timestamp": ts,
            "messages": [],
            "metadata": metadata or {}
        }
        
        # 处理图片
        image_refs = []
        if images:
            user_images_dir = self._get_user_images_dir(user_id)
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for img in images:
                filename = f"{timestamp_str}_{img['filename']}"
                img_path = user_images_dir / filename
                
                if 'data' in img:
                    img_data = base64.b64decode(img['data'])
                    img_path.write_bytes(img_data)
                elif 'path' in img:
                    shutil.copy(img['path'], img_path)
                
                image_refs.append(filename)
                
                user_desc = ""
                for msg in messages:
                    if msg["role"] == "user":
                        user_desc = msg["content"]
                        break
                
                if self.vl:
                    try:
                        vl_result = self.vl.understand_image(str(img_path), user_desc)
                        description = f"【用户描述】{user_desc}\n\n{vl_result}" if user_desc else vl_result
                        logger.info(f"🖼️ VL 图片理解完成: {filename}")
                    except Exception as e:
                        logger.warning(f"⚠️ VL 图片理解失败: {e}, 使用用户描述")
                        description = user_desc or img['filename']
                else:
                    description = user_desc or img['filename']
                
                self._save_image_to_conversation(conversation_entry, {
                    "filename": filename,
                    "description": description,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "original_name": img['filename']
                })
        
        # 处理消息
        first_user_msg = True
        for msg in messages:
            if msg["role"] == "user":
                msg_obj = {"role": "user", "content": msg["content"]}
                if first_user_msg and image_refs:
                    msg_obj["image_refs"] = image_refs
                    first_user_msg = False
                conversation_entry["messages"].append(msg_obj)
            elif self.save_assistant_messages and msg["role"] == "assistant":
                content = msg["content"]
                if len(content) > self.max_assistant_chars:
                    content = self._summarize_assistant_response(content)
                conversation_entry["messages"].append({"role": "assistant", "content": content})
        
        # 保存到存储后端
        record_id = self.storage.save_conversation(conversation_entry)
        logger.info(f"✓ 对话已存储: user={user_id}, topic={topic_id}, timestamp={ts}, id={record_id}")
        
        # 自动更新画像
        if self.auto_update_profile and self._should_trigger_update(user_id):
            try:
                self.update_profile()
            except Exception as e:
                logger.error(f"❌ 画像更新失败: {user_id}, error={e}")
        
        return {"status": "success", "id": record_id}
    
    def get_conversations(
        self,
        days_limit: Optional[int] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        size: int = 1000
    ) -> List[Dict[str, Any]]:
        """获取当前话题的对话记录"""
        start_time = None
        if days_limit:
            start_time = datetime.now() - timedelta(days=days_limit)
        
        conversations = self.storage.get_conversations(
            user_id=self.user_id,
            topic_id=self.topic_id,
            start_time=start_time,
            metadata_filter=metadata_filter,
            limit=size
        )
        logger.info(f"📖 读取对话: user={self.user_id}, topic={self.topic_id}, count={len(conversations)}")
        return conversations
    
    def get_all_conversations(
        self,
        days_limit: Optional[int] = None,
        size: int = 1000
    ) -> List[Dict[str, Any]]:
        """获取用户所有话题的对话记录"""
        start_time = None
        if days_limit:
            start_time = datetime.now() - timedelta(days=days_limit)
        
        conversations = self.storage.get_conversations(
            user_id=self.user_id,
            topic_id=None,
            start_time=start_time,
            limit=size
        )
        logger.info(f"📖 读取所有对话: user={self.user_id}, count={len(conversations)}")
        return conversations
    
    def _get_conversations_range(self, start_days_ago: int, end_days_ago: int) -> List[Dict[str, Any]]:
        """获取指定天数范围内的对话"""
        now = datetime.now()
        start_time = now - timedelta(days=end_days_ago)
        end_time = now - timedelta(days=start_days_ago)
        
        return self.storage.get_conversations(
            user_id=self.user_id,
            topic_id=self.topic_id,
            start_time=start_time,
            end_time=end_time
        )
    
    def search_conversations(self, start_days: int, end_days: int) -> List[Dict[str, Any]]:
        """按时间范围检索对话（供外部 LLM 作为 tool 调用）"""
        return self._get_conversations_range(start_days, end_days)

    
    # ========== 画像更新 ==========
    
    def update_profile(self) -> Dict[str, Any]:
        """更新用户画像"""
        user_id = self.user_id
        self._init_profile(user_id)
        
        conversations = self.get_all_conversations()
        if not conversations:
            return {"status": "success", "updated": False, "reason": "no_conversation"}
        
        history_content = self._format_conversations_for_llm(conversations)
        profile_content = self._get_profile(user_id)
        
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
        
        if len(response) > self.max_profile_chars:
            logger.info(f"📦 用户画像超长({len(response)}>{self.max_profile_chars})，触发压缩...")
            response = self._compress_profile(user_id, response)
            logger.info(f"📦 压缩后长度: {len(response)}")
        
        self._save_profile(user_id, response)
        logger.info(f"✓ 画像已更新: {user_id}")
        
        return {"status": "success", "updated": True, "length": len(response)}
    
    def _compress_profile(self, user_id: str, profile_content: str) -> str:
        """压缩用户画像"""
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
        
        return self.llm.generate(messages, response_format="text")
    
    # ========== 上下文获取 ==========
    
    def get_context(self, query: str = "", days_limit: Optional[int] = None) -> Dict[str, Any]:
        """获取记忆上下文"""
        user_id = self.user_id
        profile_content = self._init_profile(user_id)
        
        now = datetime.now()
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        current_time = f"{now.strftime('%Y-%m-%d %H:%M')} {weekdays[now.weekday()]}"
        
        profile_last_updated = "未更新"
        profile_data = self.storage.get_profile(user_id)
        if profile_data:
            profile_last_updated = profile_data.get("updated_at", "未更新")
        
        if days_limit is None:
            days_limit = self.config.memory.context_days_limit
        conversations = self.get_conversations(days_limit=days_limit)
        normal_content = self._format_conversations_for_llm(conversations) if conversations else ""
        
        return {
            "current_time": current_time,
            "user_id": user_id,
            "topic_id": self.topic_id,
            "import_content": profile_content,
            "normal_content": normal_content,
            "conversations_count": len(conversations),
            "profile_last_updated": profile_last_updated
        }
    
    def get_context_progressive(self, query: str, max_days: int = 31, step: int = 7) -> Dict[str, Any]:
        """渐进式检索：每次多查一周，直到 LLM 认为信息足够"""
        user_id = self.user_id
        profile_content = self._init_profile(user_id)
        
        now = datetime.now()
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        current_time = f"{now.strftime('%Y-%m-%d %H:%M')} {weekdays[now.weekday()]}"
        
        profile_last_updated = "未更新"
        profile_data = self.storage.get_profile(user_id)
        if profile_data:
            profile_last_updated = profile_data.get("updated_at", "未更新")
        
        all_conversations = []
        searched_days = 0
        
        for end_day in range(step, max_days + step, step):
            end_day = min(end_day, max_days)
            new_conversations = self._get_conversations_range(searched_days, end_day)
            all_conversations.extend(new_conversations)
            searched_days = end_day
            
            if not all_conversations:
                logger.info(f"📖 渐进检索: 0-{end_day}天 无对话，继续...")
                continue
            
            normal_content = self._format_conversations_for_llm(all_conversations)
            if self._is_context_sufficient(query, profile_content, normal_content, end_day):
                logger.info(f"✓ 渐进检索完成: 0-{end_day}天，{len(all_conversations)}条对话")
                break
            
            logger.info(f"📖 渐进检索: 0-{end_day}天 信息不足，继续...")
        
        normal_content = self._format_conversations_for_llm(all_conversations) if all_conversations else ""
        
        return {
            "current_time": current_time,
            "user_id": user_id,
            "topic_id": self.topic_id,
            "import_content": profile_content,
            "normal_content": normal_content,
            "conversations_count": len(all_conversations),
            "profile_last_updated": profile_last_updated,
            "searched_days": searched_days
        }
    
    def _is_context_sufficient(self, query: str, profile: str, conversations: str, days: int) -> bool:
        """LLM 判断当前上下文是否足够"""
        prompt = CONTEXT_SUFFICIENT_PROMPT.format(
            query=query,
            profile=profile,
            conversations=conversations or "（无对话记录）",
            days=days
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        return "true" in response.strip().lower()

    
    # ========== 图片搜索 ==========
    
    def search_images(self, query: str) -> List[Dict[str, str]]:
        """搜索用户图片"""
        user_id = self.user_id
        images_index = self._load_images_index(user_id)
        if not images_index:
            return []
        
        images_desc = "\n".join([
            f"[{i}] 文件名: {img['original_name']}, 时间: {img['timestamp']}, 描述: {img['description']}"
            for i, img in enumerate(images_index)
        ])
        
        prompt = IMAGE_SEARCH_PROMPT.format(query=query, images_desc=images_desc)
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        
        results = []
        numbers = re.findall(r'\b(\d+)\b', response)
        for num_str in numbers:
            idx = int(num_str)
            if 0 <= idx < len(images_index):
                img = images_index[idx].copy()
                img['abs_path'] = str((self._get_user_images_dir(user_id) / img['filename']).resolve())
                if img not in results:
                    results.append(img)
        
        logger.info(f"🖼️ 图片搜索: query='{query}', 找到 {len(results)} 张")
        return results
    
    # ========== LLM 辅助方法 ==========
    
    def _should_include_history(self, query: str) -> tuple[bool, str]:
        """LLM 判断是否需要加载历史记录"""
        prompt = RECALL_DECISION_PROMPT.format(query=query)
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        response = self.llm.generate(messages, response_format="text")
        response_lower = response.strip().lower()
        need_history = "true" in response_lower or "是" in response_lower or "需要" in response_lower
        
        logger.info(f"🔍 回忆判断: query='{query[:50]}...', need_history={need_history}")
        return need_history, response.strip()
    
    def _summarize_assistant_response(self, content: str) -> str:
        """对超长的助手回复生成摘要"""
        prompt = ASSISTANT_SUMMARY_PROMPT.format(
            content=content,
            max_chars=self.max_assistant_chars
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "请生成摘要"}
        ]
        
        summary = self.llm.generate(messages, response_format="text")
        logger.info(f"📝 助手回复摘要: {len(content)} -> {len(summary)} 字符")
        return summary
    
    def _format_conversations_for_llm(self, conversations: List[Dict[str, Any]]) -> str:
        """格式化对话记录为文本"""
        output = []
        for conv in conversations:
            timestamp = conv.get("timestamp", "未知时间")
            metadata = conv.get("metadata", {})
            
            title = f"### {timestamp}"
            if metadata:
                tags = " ".join([f"[{k}:{v}]" for k, v in metadata.items()])
                title += f" {tags}"
            
            output.append(title)
            output.append("")
            
            for msg in conv.get("messages", []):
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                role_name = "用户" if msg["role"] == "user" else "助手"
                output.append(f"**{role_icon} {role_name}**: {msg['content']}")
                if msg.get("images"):
                    for img_path in msg["images"]:
                        output.append(f"![Image]({img_path})")
                output.append("")
            
            output.append("---")
            output.append("")
        
        return "\n".join(output)
    
    # ========== 用户/话题管理 ==========
    
    def get_user_list(self) -> List[str]:
        """获取所有用户ID列表"""
        return self.storage.get_user_list()
    
    def list_topics(self) -> List[Dict[str, Any]]:
        """列出用户的所有话题"""
        return self.storage.get_topic_list(self.user_id)
    
    def delete_user(self) -> Dict[str, Any]:
        """删除用户所有记忆"""
        user_id = self.user_id
        
        self.storage.delete_conversations(user_id)
        self.storage.delete_user_state(user_id)
        self.storage.delete_profile(user_id)
        
        # 删除本地图片文件
        user_images_dir = self.images_dir / user_id
        if user_images_dir.exists():
            shutil.rmtree(user_images_dir)
        
        logger.info(f"✓ 已删除用户所有数据: {user_id}")
        return {"status": "success", "deleted": user_id}
    
    def delete_topic(self) -> Dict[str, Any]:
        """删除当前话题的对话记录（保留用户画像）"""
        user_id = self.user_id
        topic_id = self.topic_id
        
        self.storage.delete_conversations(user_id, topic_id)
        
        logger.info(f"✓ 已删除话题: user={user_id}, topic={topic_id}")
        return {"status": "success", "deleted_topic": topic_id}
