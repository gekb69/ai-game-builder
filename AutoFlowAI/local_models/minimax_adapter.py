"""
محول لنموذج Minimax
"""
from typing import Optional, List
from .base import LocalModelAgentBase

class MinimaxAgent(LocalModelAgentBase):
    def __init__(self, model_id: str = "MiniMaxAI/MiniMax-M2", **kwargs):
        super().__init__(model_id=model_id, **kwargs)

    def format_prompt(self, prompt: str, history: Optional[List[dict]] = None) -> str:
        """
        تنسيق المدخلات لتكون متوافقة مع Minimax-M2.
        """
        messages = history or []
        messages.append({"role": "user", "content": prompt})

        # Minimax models might have their own specific chat format.
        # Using the tokenizer's apply_chat_template is generally the safest approach.
        try:
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        except Exception:
            # Fallback for models that might not have a pre-defined chat template
            formatted_prompt = ""
            for message in messages:
                formatted_prompt += f"<|{message['role']}|>\n{message['content']}\n"
            formatted_prompt += "<|assistant|>\n"

        return formatted_prompt
