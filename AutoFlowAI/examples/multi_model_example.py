"""
مثال شامل لاستخدام النماذج المحلية المتعددة
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.autoflowai import AdvancedAutoFlowAI
from utils.config import config

async def multi_model_example():
    """
    يوضح هذا المثال كيفية استخدام الـ agent المحلي الذي تم تحميله.
    """
    print("🚀 مثال استخدام النماذج المحلية المتعددة")
    print("=" * 60)

    # 1. قم بتغيير النموذج النشط في الإعدادات (إذا رغبت في ذلك)
    # على سبيل المثال، لتجربة نموذج GLM:
    # config.set("local_models.active_model", "glm")

    # 2. إنشاء نظام AutoFlowAI (سيقوم تلقائياً بتحميل النموذج المحدد)
    # ملاحظة: قد يستغرق هذا وقتاً طويلاً في المرة الأولى لأنه سيقوم بتحميل النموذج.
    ai_system = AdvancedAutoFlowAI('development')

    # 3. الوصول إلى الـ agent المحلي الذي تم تحميله
    active_model_key = config.local_models.active_model
    local_agent = getattr(ai_system, f"{active_model_key}_agent", None)

    if not local_agent:
        print(f"❌ لم يتم العثور على الـ agent المحلي: {active_model_key}")
        return

    # 4. التفاعل مع الـ agent
    print(f"\n💬 التفاعل مع '{active_model_key}' agent. اكتب 'خروج' للإنهاء.")

    history = []
    while True:
        prompt = input("أنت: ")
        if prompt.lower() == 'خروج':
            break

        print("🤖 Agent يفكر...")
        response = local_agent.generate(prompt, history=history)

        # إزالة المدخلات من الرد لتجنب التكرار
        cleaned_response = response.replace(local_agent.format_prompt(prompt, history), "").strip()

        print(f"Agent: {cleaned_response}")

        # تحديث المحادثة
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": cleaned_response})

    ai_system.shutdown()
    print("\n✅ انتهى المثال.")

if __name__ == "__main__":
    # ملاحظة: يتطلب هذا المثال مكتبات transformers, torch, bitsandbytes, accelerate
    # تأكد من تثبيتها جميعاً.
    # pip install -r requirements.txt
    asyncio.run(multi_model_example())
