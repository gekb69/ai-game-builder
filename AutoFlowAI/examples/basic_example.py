"""
مثال أساسي لاستخدام AutoFlowAI
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.autoflowai import AdvancedAutoFlowAI
from core.types import AgentInfo
from agents.advanced_agent import AdvancedReasoningAgent
from workflow.workflow_engine import WorkflowEngine
from workflow.viflow import Workflow, Node, Flow

async def basic_example():
    """مثال أساسي"""
    print("🚀 مثال AutoFlowAI الأساسي")
    print("=" * 50)

    # 1. إنشاء النظام
    ai_system = AdvancedAutoFlowAI('development')
    print("✅ تم إنشاء AutoFlowAI")

    # 2. إضافة وكيل بسيط
    agent_info = AgentInfo(
        id="basic_agent",
        name="وكيل أساسي",
        capabilities=["analysis", "task_execution"]
    )
    ai_system.register_agent(agent_info)
    print(f"✅ تم إضافة الوكيل: {agent_info.name}")

    # 3. إنشاء workflow بسيط
    workflow = Workflow("basic_workflow", "workflow أساسي")
    workflow.add_node(Node("start", "البداية", "start", (100, 100)))
    workflow.add_node(Node("analyze", "تحليل", "ai_agent", (300, 100),
                           agent_id="basic_agent", config={'task_type': 'analysis'}))
    workflow.add_node(Node("end", "النهاية", "end", (500, 100)))

    workflow.add_flow(Flow("start", "analyze"))
    workflow.add_flow(Flow("analyze", "end"))

    engine = WorkflowEngine(ai_system)
    engine.register_workflow(workflow)
    print("✅ تم إنشاء workflow أساسي")

    # 4. تنفيذ workflow
    input_data = {'message': 'مرحباً بالعالم'}
    execution_id = engine.execute_workflow(workflow.id, input_data)
    print(f"⏳ بدء تنفيذ workflow (ID: {execution_id})")

    # انتظار الانتهاء
    while True:
        status = engine.get_execution_status(execution_id)
        if status and status['status'] in ['COMPLETED', 'FAILED']:
            print(f"🎯 انتهى التنفيذ: {status['status']}")
            break
        await asyncio.sleep(1)

    # 5. عرض النتائج
    final_status = engine.get_execution_status(execution_id)
    print(f"📊 النتائج: {final_status}")

    ai_system.shutdown()
    print("✅ انتهى المثال الأساسي")

if __name__ == "__main__":
    asyncio.run(basic_example())
