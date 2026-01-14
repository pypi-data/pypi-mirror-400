"""可插拔存储层抽象

设计目标：
- 将存储操作从 Mem1Memory 中解耦
- 支持 ES/SQLite/MySQL 等多种后端
- 保持接口简洁，只抽象必要操作

使用方式：
    from mem1.storage import ESStorage
    storage = ESStorage(config.es)
    
    # 或未来实现
    from mem1.storage import SQLiteStorage
    storage = SQLiteStorage(db_path="mem1.db")
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional


class StorageBackend(ABC):
    """存储后端抽象基类
    
    所有存储实现需要实现以下方法：
    - 对话记录：save_conversation, get_conversations, delete_conversations
    - 用户画像：get_profile, save_profile, delete_profile
    - 用户状态：get_user_state, save_user_state, delete_user_state
    - 聚合查询：get_user_list, get_topic_list
    """
    
    # ========== 对话记录 ==========
    
    @abstractmethod
    def save_conversation(self, conversation: Dict[str, Any]) -> str:
        """保存对话记录
        
        Args:
            conversation: {
                "user_id": str,
                "topic_id": str,
                "timestamp": str,  # 格式: '%Y-%m-%d %H:%M:%S'
                "messages": List[Dict],
                "metadata": Dict,
                "images": List[Dict] (可选)
            }
        
        Returns:
            记录ID
        """
        pass
    
    @abstractmethod
    def get_conversations(
        self,
        user_id: str,
        topic_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """查询对话记录
        
        Args:
            user_id: 用户ID
            topic_id: 话题ID，None 表示所有话题
            start_time: 起始时间
            end_time: 结束时间
            metadata_filter: 元数据过滤
            limit: 最大返回数量
        
        Returns:
            对话记录列表，按时间升序
        """
        pass
    
    @abstractmethod
    def delete_conversations(
        self,
        user_id: str,
        topic_id: Optional[str] = None
    ) -> int:
        """删除对话记录
        
        Args:
            user_id: 用户ID
            topic_id: 话题ID，None 表示删除所有话题
        
        Returns:
            删除的记录数
        """
        pass
    
    # ========== 用户画像 ==========
    
    @abstractmethod
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户画像
        
        Returns:
            {"content": str, "updated_at": str} 或 None
        """
        pass
    
    @abstractmethod
    def save_profile(self, user_id: str, content: str) -> None:
        """保存用户画像"""
        pass
    
    @abstractmethod
    def delete_profile(self, user_id: str) -> bool:
        """删除用户画像"""
        pass
    
    # ========== 用户状态 ==========
    
    @abstractmethod
    def get_user_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户状态
        
        Returns:
            {"rounds": int, "last_update": str} 或 None
        """
        pass
    
    @abstractmethod
    def save_user_state(self, user_id: str, rounds: int, last_update: Optional[str] = None) -> None:
        """保存用户状态"""
        pass
    
    @abstractmethod
    def delete_user_state(self, user_id: str) -> bool:
        """删除用户状态"""
        pass
    
    # ========== 聚合查询 ==========
    
    @abstractmethod
    def get_user_list(self) -> List[str]:
        """获取所有用户ID列表"""
        pass
    
    @abstractmethod
    def get_topic_list(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户的话题列表
        
        Returns:
            [{"topic_id": str, "conversation_count": int, "last_active": str}, ...]
        """
        pass
    
    # ========== 初始化 ==========
    
    @abstractmethod
    def ensure_schema(self) -> None:
        """确保存储结构存在（索引/表）"""
        pass



class ESStorage(StorageBackend):
    """Elasticsearch 存储后端"""
    
    # 索引名常量
    USER_STATE_INDEX = "mem1_user_state"
    USER_PROFILE_INDEX = "mem1_user_profile"
    
    def __init__(self, hosts: List[str], index_name: str):
        """
        Args:
            hosts: ES 地址列表
            index_name: 对话记录索引名
        """
        from elasticsearch import Elasticsearch
        self.es = Elasticsearch(hosts)
        self.index_name = index_name
        self.ensure_schema()
    
    def ensure_schema(self) -> None:
        """确保所有索引存在"""
        # 对话记录索引
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(
                index=self.index_name,
                body={
                    "mappings": {
                        "properties": {
                            "user_id": {"type": "keyword"},
                            "topic_id": {"type": "keyword"},
                            "timestamp": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||epoch_millis"},
                            "messages": {"type": "nested"},
                            "metadata": {"type": "object"},
                            "images": {"type": "nested"}
                        }
                    }
                }
            )
        
        # 用户状态索引
        if not self.es.indices.exists(index=self.USER_STATE_INDEX):
            self.es.indices.create(
                index=self.USER_STATE_INDEX,
                body={
                    "mappings": {
                        "properties": {
                            "user_id": {"type": "keyword"},
                            "rounds": {"type": "integer"},
                            "last_update": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||epoch_millis"}
                        }
                    }
                }
            )
        
        # 用户画像索引
        if not self.es.indices.exists(index=self.USER_PROFILE_INDEX):
            self.es.indices.create(
                index=self.USER_PROFILE_INDEX,
                body={
                    "mappings": {
                        "properties": {
                            "user_id": {"type": "keyword"},
                            "content": {"type": "text"},
                            "updated_at": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||epoch_millis"}
                        }
                    }
                }
            )
    
    # ========== 对话记录 ==========
    
    def save_conversation(self, conversation: Dict[str, Any]) -> str:
        response = self.es.index(
            index=self.index_name,
            document=conversation,
            refresh=True
        )
        return response["_id"]
    
    def get_conversations(
        self,
        user_id: str,
        topic_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        query = {"bool": {"must": [{"term": {"user_id": user_id}}]}}
        
        if topic_id:
            query["bool"]["must"].append({"term": {"topic_id": topic_id}})
        
        if start_time or end_time:
            range_query = {}
            if start_time:
                range_query["gte"] = start_time.strftime('%Y-%m-%d %H:%M:%S')
            if end_time:
                range_query["lt"] = end_time.strftime('%Y-%m-%d %H:%M:%S')
            query["bool"]["must"].append({"range": {"timestamp": range_query}})
        
        if metadata_filter:
            for k, v in metadata_filter.items():
                query["bool"]["must"].append({"term": {f"metadata.{k}": v}})
        
        response = self.es.search(
            index=self.index_name,
            query=query,
            size=limit,
            sort=[{"timestamp": {"order": "asc"}}]
        )
        
        return [hit["_source"] for hit in response["hits"]["hits"]]
    
    def delete_conversations(self, user_id: str, topic_id: Optional[str] = None) -> int:
        query = {"bool": {"must": [{"term": {"user_id": user_id}}]}}
        if topic_id:
            query["bool"]["must"].append({"term": {"topic_id": topic_id}})
        
        try:
            response = self.es.delete_by_query(
                index=self.index_name,
                query=query,
                refresh=True
            )
            return response.get("deleted", 0)
        except Exception:
            return 0
    
    # ========== 用户画像 ==========
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.es.get(index=self.USER_PROFILE_INDEX, id=user_id)
            return response["_source"]
        except Exception:
            return None
    
    def save_profile(self, user_id: str, content: str) -> None:
        self.es.index(
            index=self.USER_PROFILE_INDEX,
            id=user_id,
            document={
                "user_id": user_id,
                "content": content,
                "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            refresh=True
        )
    
    def delete_profile(self, user_id: str) -> bool:
        try:
            self.es.delete(index=self.USER_PROFILE_INDEX, id=user_id, refresh=True)
            return True
        except Exception:
            return False
    
    # ========== 用户状态 ==========
    
    def get_user_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.es.get(index=self.USER_STATE_INDEX, id=user_id)
            return response["_source"]
        except Exception:
            return None
    
    def save_user_state(self, user_id: str, rounds: int, last_update: Optional[str] = None) -> None:
        doc = {"user_id": user_id, "rounds": rounds}
        if last_update:
            doc["last_update"] = last_update
        
        self.es.index(
            index=self.USER_STATE_INDEX,
            id=user_id,
            document=doc,
            refresh=True
        )
    
    def delete_user_state(self, user_id: str) -> bool:
        try:
            self.es.delete(index=self.USER_STATE_INDEX, id=user_id, refresh=True)
            return True
        except Exception:
            return False
    
    # ========== 聚合查询 ==========
    
    def get_user_list(self) -> List[str]:
        response = self.es.search(
            index=self.index_name,
            body={
                "size": 0,
                "aggs": {"users": {"terms": {"field": "user_id", "size": 10000}}}
            }
        )
        return [bucket["key"] for bucket in response["aggregations"]["users"]["buckets"]]
    
    def get_topic_list(self, user_id: str) -> List[Dict[str, Any]]:
        response = self.es.search(
            index=self.index_name,
            body={
                "size": 0,
                "query": {"term": {"user_id": user_id}},
                "aggs": {
                    "topics": {
                        "terms": {"field": "topic_id", "size": 1000},
                        "aggs": {
                            "latest": {"max": {"field": "timestamp"}},
                            "count": {"value_count": {"field": "timestamp"}}
                        }
                    }
                }
            }
        )
        
        topics = []
        for bucket in response["aggregations"]["topics"]["buckets"]:
            topics.append({
                "topic_id": bucket["key"],
                "conversation_count": bucket["doc_count"],
                "last_active": bucket["latest"]["value_as_string"] if bucket["latest"]["value"] else None
            })
        return topics
    
    def get_conversations_with_images(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户所有带图片的对话（用于图片索引）"""
        response = self.es.search(
            index=self.index_name,
            query={
                "bool": {
                    "must": [
                        {"term": {"user_id": user_id}},
                        {"exists": {"field": "images"}}
                    ]
                }
            },
            size=1000,
            sort=[{"timestamp": {"order": "asc"}}]
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]
