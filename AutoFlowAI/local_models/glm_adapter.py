"""
محول لنموذج GLM
"""
from typing import Optional, List
from .base import LocalModelAgentBase

class GLMAgent(LocalModelAgentBase):
    def __init__(self, model_id: str = "THUDM/glm-4-9b-chat", **kwargs):
        super().__init__(model_id=model_id, **kwargs)

    def format_prompt(self, prompt: str, history: Optional[List[dict]] = None) -> str:
        """
        تنسيق المدخلات لتكون متوافقة مع GLM-4.
        """
        messages = history or []
        messages.append({"role": "user", "content": prompt})

        # GLM-4 uses a specific chat template format
        # Using tokenizer.apply_chat_template is the recommended way
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        return formatted_prompt
