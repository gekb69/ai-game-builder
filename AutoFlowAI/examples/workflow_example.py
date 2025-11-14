"""
مثال workflow متقدم
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
from workflow.visual_editor import VisualFlowEditor

async def workflow_example():
    """مثال workflow متقدم"""
    print("🎨 مثال Workflow المرئي")
    print("=" * 50)

    # 1. إنشاء نظام متقدم
    ai_system = AdvancedAutoFlowAI('production')

    # 2. إضافة وكلاء متخصصة
    agents = [
        AgentInfo('data_collector', 'جامع البيانات', ['web_scraping', 'api_integration']),
        AgentInfo('market_analyst', 'محلل السوق', ['technical_analysis', 'sentiment_analysis']),
        AgentInfo('strategy_agent', 'وكيل الاستراتيجية', ['strategy_optimization', 'backtesting']),
        AgentInfo('risk_agent', 'وكيل المخاطر', ['risk_modeling', 'portfolio_management']),
    ]

    for agent in agents:
        ai_system.register_agent(agent)

    print("✅ تم إضافة الوكلاء المتخصصة")

    # 3. إنشاء workflow تداول ذكي
    trading_workflow = Workflow(
        id="intelligent_trading_workflow",
        name="نظام تداول ذكي",
        description="workflow شامل للتداول مع تقييم المخاطر والاستراتيجيات"
    )

    # إضافة العقد
    nodes = [
        Node("start", "بداية", "start", (100, 100)),
        Node("collect_data", "جمع البيانات", "ai_agent", (300, 100),
             agent_id="data_collector", config={'task_type': 'data_collection'}),
        Node("analyze_market", "تحليل السوق", "ai_agent", (500, 100),
             agent_id="market_analyst", config={'task_type': 'market_analysis'}),
        Node("risk_assess", "تقييم المخاطر", "ai_agent", (700, 100),
             agent_id="risk_agent", config={'task_type': 'risk_assessment'}),
        Node("strategy_dev", "تطوير الاستراتيجية", "ai_agent", (900, 100),
             agent_id="strategy_agent", config={'task_type': 'strategy_development'}),
        Node("decision", "قرار", "condition", (1100, 100),
             condition="risk_level != 'HIGH'"),
        Node("execute_trade", "تنفيذ الصفقة", "ai_agent", (1300, 100),
             agent_id="strategy_agent", config={'task_type': 'trade_execution'}),
        Node("log_results", "تسجيل النتائج", "data_processing", (1500, 100),
             config={'operation': 'copy', 'input_key': 'trade_result', 'output_key': 'final_log'}),
        Node("end", "نهاية", "end", (1700, 100))
    ]

    for node in nodes:
        trading_workflow.add_node(node)

    # إضافة الروابط
    flows = [
        Flow("start", "collect_data"),
        Flow("collect_data", "analyze_market"),
        Flow("analyze_market", "risk_assess"),
        Flow("risk_assess", "strategy_dev"),
        Flow("strategy_dev", "decision"),
        Flow("decision", "execute_trade", "true"),
        Flow("execute_trade", "log_results"),
        Flow("log_results", "end"),
        Flow("decision", "end", "false")
    ]

    for flow in flows:
        trading_workflow.add_flow(flow)

    print("✅ تم إنشاء workflow التداول الذكي")

    # 4. حفظ workflow بصري
    editor = VisualFlowEditor(trading_workflow)
    editor.save_html("trading_workflow.html")
    print("💾 تم حفظ المحرر المرئي في: trading_workflow.html")

    # 5. تنفيذ workflow
    engine = WorkflowEngine(ai_system)
    engine.register_workflow(trading_workflow)

    input_data = {
        'symbol': 'BTC_USD',
        'amount': 10000,
        'risk_tolerance': 'medium',
        'investment_horizon': 'short_term'
    }

    execution_id = engine.execute_workflow(trading_workflow.id, input_data)
    print(f"⏳ بدء تنفيذ workflow التداول (ID: {execution_id})")

    # 6. مراقبة التنفيذ
    print("📊 مراقبة التنفيذ:")
    while True:
        status = engine.get_execution_status(execution_id)
        if status:
            print(f" الحالة: {status['status']} | العقدة: {status.get('current_node', 'N/A')}")
            if status['status'] in ['COMPLETED', 'FAILED']:
                break
        await asyncio.sleep(2)

    final_status = engine.get_execution_status(execution_id)
    print(f"\n🎯 النتيجة النهائية:")
    print(f"الحالة: {final_status['status']}")
    print(f"عدد النتائج: {final_status.get('results_count', 0)}")

    # حفظ workflow
    trading_workflow.save("trading_workflow.json")
    print("💾 تم حفظ workflow في: trading_workflow.json")

    ai_system.shutdown()
    print("✅ انتهى مثال workflow المتقدم")

if __name__ == "__main__":
    asyncio.run(workflow_example())
