"""
محول لنموذج Kimi
"""
from typing import Optional, List
from .base import LocalModelAgentBase

class KimiAgent(LocalModelAgentBase):
    def __init__(self, model_id: str = "moonshotai/Kimi-K2-Instruct", **kwargs):
        super().__init__(model_id=model_id, **kwargs)

    def format_prompt(self, prompt: str, history: Optional[List[dict]] = None) -> str:
        """
        تنسيق المدخلات لتكون متوافقة مع Kimi K2.
        """
        messages = [
            {"role": "system", "content": "You are Kimi, an AI assistant created by Moonshot AI."}
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        # Kimi uses a specific format with <|im_start|>, <|im_middle|>, <|im_end|> tokens
        # The tokenizer's chat template should handle this automatically.
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        return formatted_prompt
