"""
الفئة الأساسية للنماذج المحلية
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

class LocalModelAgentBase(ABC):
    def __init__(self, model_id: str, quantization_config: Optional[Dict[str, Any]] = None):
        self.model_id = model_id
        self.quantization_config = self._create_bnb_config(quantization_config)
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _create_bnb_config(self, config: Optional[Dict[str, Any]]) -> Optional[BitsAndBytesConfig]:
        if not config:
            return None

        return BitsAndBytesConfig(
            load_in_4bit=config.get('load_in_4bit', False),
            load_in_8bit=config.get('load_in_8bit', False),
            bnb_4bit_use_double_quant=config.get('bnb_4bit_use_double_quant', True),
            bnb_4bit_quant_type=config.get('bnb_4bit_quant_type', "nf4"),
            bnb_4bit_compute_dtype=torch.bfloat16
        )

    def _load_model(self):
        """
        تحميل النموذج والمحول من Hugging Face Hub.
        """
        print(f"🔄 جاري تحميل النموذج: {self.model_id}...")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=self.quantization_config,
            device_map="auto",
            trust_remote_code=True
        )

        print("✅ تم تحميل النموذج بنجاح!")

    @abstractmethod
    def format_prompt(self, prompt: str, history: Optional[list] = None) -> str:
        """
        تنسيق المدخلات (prompt) لتكون متوافقة مع النموذج المحدد.
        """
        pass

    def generate(self, prompt: str, history: Optional[list] = None, max_new_tokens: int = 256, temperature: float = 0.7) -> str:
        """
        توليد رد من النموذج.
        """
        formatted_prompt = self.format_prompt(prompt, history)

        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

    def __call__(self, prompt: str, **kwargs) -> str:
        return self.generate(prompt, **kwargs)
