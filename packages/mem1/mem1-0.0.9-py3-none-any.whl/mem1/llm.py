"""LLM 客户端"""
from typing import List, Dict, Optional
from openai import OpenAI
from mem1.config import LLMConfig, VLConfig


class LLMClient:
    """LLM 客户端（基于 OpenAI 兼容 API）"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        response_format: str = "text"
    ) -> str:
        """
        生成响应
        
        Args:
            messages: [{"role": "system", "content": "..."}, ...]
            response_format: "text" 或 "json"
        
        Returns:
            响应文本
        """
        kwargs = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
        }
        
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        
        return response.choices[0].message.content


class VLClient:
    """视觉语言模型客户端（支持 qwen/doubao）"""
    
    def __init__(self, config: VLConfig):
        self.config = config
        self.provider = config.provider.lower()
        
        if self.provider == "qwen":
            import dashscope
            dashscope.api_key = config.api_key
        elif self.provider == "doubao":
            self.client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
    
    def understand_image(
        self,
        image_path: str,
        user_description: str = ""
    ) -> str:
        """理解图片内容（OCR + 图片理解）
        
        Args:
            image_path: 图片本地路径
            user_description: 用户对图片的描述（可选）
        
        Returns:
            图片理解结果（包含 OCR 文字和内容描述）
        """
        prompt = "请分析这张图片，完成以下任务：\n1. OCR识别：提取图片中的所有文字\n2. 内容理解：描述图片的主要内容和关键信息\n\n请用简洁的中文回答，格式如下：\n【文字内容】...\n【图片描述】..."
        
        if user_description:
            prompt += f"\n\n用户补充说明：{user_description}"
        
        if self.provider == "qwen":
            return self._call_qwen(image_path, prompt)
        elif self.provider == "doubao":
            return self._call_doubao(image_path, prompt)
        else:
            raise ValueError(f"不支持的 VL provider: {self.provider}")
    
    def _call_qwen(self, image_path: str, prompt: str) -> str:
        """调用 Qwen-VL（dashscope SDK）"""
        import dashscope
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": image_path},
                    {"text": prompt}
                ]
            }
        ]
        
        response = dashscope.MultiModalConversation.call(
            model=self.config.model,
            messages=messages
        )
        
        return response.output.choices[0].message.content[0]["text"]
    
    def _call_doubao(self, image_path: str, prompt: str) -> str:
        """调用豆包视觉模型（OpenAI 兼容接口）"""
        import base64
        
        # 读取图片并转为 base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 获取图片格式
        ext = image_path.lower().split(".")[-1]
        mime_type = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/png")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_data}"}
                    },
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages
        )
        
        return response.choices[0].message.content
