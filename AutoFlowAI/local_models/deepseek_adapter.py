"""
محول لنموذج DeepSeek
"""
from typing import Optional, List
from .base import LocalModelAgentBase

class DeepSeekAgent(LocalModelAgentBase):
    def __init__(self, model_id: str = "deepseek-ai/deepseek-coder-v2-lite-instruct", **kwargs):
        super().__init__(model_id=model_id, **kwargs)

    def format_prompt(self, prompt: str, history: Optional[List[dict]] = None) -> str:
        """
        تنسيق المدخلات لتكون متوافقة مع DeepSeek Coder V2.
        """
        messages = history or []
        messages.append({"role": "user", "content": prompt})

        # This is a simplified version of the official chat template
        # In a real-world scenario, you might want to use the tokenizer's apply_chat_template method
        formatted_prompt = ""
        for message in messages:
            formatted_prompt += f"### {message['role']}\n{message['content']}\n"
        formatted_prompt += "### assistant\n"

        return formatted_prompt
