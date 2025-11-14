"""
مثال متقدم شامل
"""
import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.autoflowai import AdvancedAutoFlowAI
from core.types import AgentInfo, Task
from agents.advanced_agent import AdvancedReasoningAgent
from agents.tool_manager import ToolManager
from workflow.workflow_engine import WorkflowEngine
from workflow.viflow import Workflow, Node, Flow
from workflow.visual_editor import VisualFlowEditor
from trading.intelligent_trading import IntelligentTradingSystem
from scheduler.task_scheduler import TimeBasedTaskScheduler, AdvancedTask, TaskType, TaskPriority
from security.security_framework import AdvancedSecurityFramework
from monitoring.real_time_monitor import RealTimeMonitor

async def advanced_example():
    """مثال متقدم شامل"""
    print("🚀 AutoFlowAI - مثال متقدم شامل")
    print("=" * 60)

    # 1. إنشاء النظام الأساسي
    ai_system = AdvancedAutoFlowAI('production')
    print("✅ AutoFlowAI - جاهز")

    # 2. إنشاء وكلاء متخصصة
    specialized_agents = [
        AdvancedReasoningAgent('research_agent', 'وكيل البحث', ['research', 'analysis']),
        AdvancedReasoningAgent('strategy_agent', 'وكيل الاستراتيجية', ['strategy', 'optimization']),
        AdvancedReasoningAgent('risk_agent', 'وكيل المخاطر', ['risk_management', 'assessment']),
        AdvancedReasoningAgent('execution_agent', 'وكيل التنفيذ', ['execution', 'automation'])
    ]

    for agent in specialized_agents:
        ai_system.register_agent(AgentInfo(agent.id, agent.name, agent.capabilities))

    print(f"✅ تم إضافة {len(specialized_agents)} وكلاء متخصصة")

    # 3. نظام الأمان المتقدم
    security = AdvancedSecurityFramework('maximum')
    print("🛡️ نظام الأمان - مُفعّل")

    # 4. المراقبة المباشرة
    monitor = RealTimeMonitor()
    monitor.record_event('system_start', {'component': 'advanced_example'})
    print("📊 نظام المراقبة - نشط")

    # 5. نظام الجدولة المتقدم
    scheduler = TimeBasedTaskScheduler()
    scheduler.start_scheduler()

    # جدولة مهام متنوعة
    tasks = [
        AdvancedTask('market_scan', 'فحص السوق', 'فحص دوري للأسعار', TaskType.PERIODIC,
                     priority=TaskPriority.HIGH, parameters={'interval_seconds': 30}),
        AdvancedTask('risk_check', 'فحص المخاطر', 'تقييم دوري للمخاطر', TaskType.MEDIUM_TERM,
                     priority=TaskPriority.MEDIUM, estimated_duration=60),
        AdvancedTask('portfolio_update', 'تحديث المحفظة', 'تحديث قيم المحفظة', TaskType.SHORT_TERM,
                     priority=TaskPriority.LOW, estimated_duration=30)
    ]

    for task in tasks:
        scheduler.add_task(task)

    print(f"📅 تم جدولة {len(tasks)} مهام متنوعة")

    # 6. إنشاء workflow معقد
    complex_workflow = Workflow(
        id="advanced_trading_workflow",
        name="نظام التداول المتقدم",
        description="workflow شامل للتداول مع إدارة متقدمة للمخاطر"
    )

    # العقد المتقدمة
    workflow_nodes = [
        # مرحلة التحضير
        Node("init", "تهيئة النظام", "start", (100, 100)),
        Node("security_check", "فحص الأمان", "ai_agent", (300, 100), agent_id='execution_agent'),
        Node("data_collection", "جمع البيانات", "ai_agent", (500, 100), agent_id='research_agent'),

        # مرحلة التحليل
        Node("market_analysis", "تحليل السوق", "ai_agent", (700, 100), agent_id='research_agent'),
        Node("risk_modeling", "نمذجة المخاطر", "ai_agent", (900, 100), agent_id='risk_agent'),
        Node("risk_threshold", "فحص حدود المخاطر", "condition", (1100, 100), condition="risk_score <= 0.7"),

        # مرحلة القرار
        Node("strategy_generation", "توليد الاستراتيجيات", "ai_agent", (1300, 100), agent_id='strategy_agent'),
        Node("backtesting", "اختبار الاستراتيجيات", "ai_agent", (1500, 100), agent_id='strategy_agent'),
        Node("final_decision", "القرار النهائي", "condition", (1700, 100), condition="strategy_score > 0.8"),

        # مرحلة التنفيذ
        Node("trade_execution", "تنفيذ التداول", "ai_agent", (1900, 100), agent_id='execution_agent'),
        Node("post_trade_analysis", "تحليل ما بعد التداول", "ai_agent", (2100, 100), agent_id='research_agent'),
        Node("logging", "تسجيل العمليات", "data_processing", (2300, 100),
             config={'operation': 'copy', 'input_key': 'execution_result', 'output_key': 'audit_log'}),
        Node("complete", "انتهاء ناجح", "end", (2500, 100)),

        # مسار الإنهاء
        Node("terminate", "إنهاء للإدارة", "end", (1300, 400))
    ]

    for node in workflow_nodes:
        complex_workflow.add_node(node)

    # الروابط المتقدمة
    workflow_flows = [
        # التدفق الرئيسي
        Flow("init", "security_check"),
        Flow("security_check", "data_collection"),
        Flow("data_collection", "market_analysis"),
        Flow("market_analysis", "risk_modeling"),
        Flow("risk_modeling", "risk_threshold"),

        # مسار المخاطر
        Flow("risk_threshold", "strategy_generation", "true"),
        Flow("risk_threshold", "terminate", "false"),

        # مسار الاستراتيجيات
        Flow("strategy_generation", "backtesting"),
        Flow("backtesting", "final_decision"),
        Flow("final_decision", "trade_execution", "true"),
        Flow("final_decision", "terminate", "false"),

        # مسار التنفيذ
        Flow("trade_execution", "post_trade_analysis"),
        Flow("post_trade_analysis", "logging"),
        Flow("logging", "complete")
    ]

    for flow in workflow_flows:
        complex_workflow.add_flow(flow)

    print("🔗 تم إنشاء workflow معقد")

    # 7. تنفيذ workflow مع مراقبة شاملة
    engine = WorkflowEngine(ai_system)
    engine.register_workflow(complex_workflow)

    # تحضير بيانات شاملة
    comprehensive_input = {
        'symbols': ['BTC_USD', 'ETH_USD', 'AAPL', 'TSLA'],
        'investment_budget': 50000,
        'risk_tolerance': 'medium',
        'time_horizon': 'medium_term',
        'strategy_preference': 'momentum',
        'compliance_required': True,
        'security_level': 'maximum'
    }

    # فحص الأمان
    security_request = {
        'user_id': 'system_admin',
        'payload': comprehensive_input,
        'roles': ['admin', 'trader'],
        'data_classification': 'confidential'
    }

    try:
        security_results = security.multi_layer_security_check(security_request)
        print("🔒 فحص الأمان - مُجتاز")
    except Exception as e:
        print(f"🛡️ فشل فحص الأمان: {e}")
        return

    # بدء التنفيذ
    execution_id = engine.execute_workflow(complex_workflow.id, comprehensive_input)
    print(f"⏳ بدء التنفيذ المتقدم (ID: {execution_id})")

    # 8. إنشاء نظام التداول المتكامل
    trading_system = IntelligentTradingSystem(initial_balance=100000, risk_tolerance='medium')

    # محاكاة بيانات السوق المتقدمة
    advanced_market_data = {
        'BTC_USD': {'price': 45000, 'volume': 2000000, 'volatility': 0.6, 'trend': 'bullish'},
        'ETH_USD': {'price': 3200, 'volume': 1500000, 'volatility': 0.8, 'trend': 'neutral'},
        'AAPL': {'price': 175.50, 'volume': 80000000, 'volatility': 0.4, 'trend': 'bullish'},
        'TSLA': {'price': 220.75, 'volume': 30000000, 'volatility': 0.9, 'trend': 'bearish'}
    }

    # تشغيل التداول المتكامل
    trading_result = await trading_system.intelligent_trading_workflow(
        symbols=['BTC_USD', 'ETH_USD', 'AAPL'],
        market_data=advanced_market_data,
        investment_params={
            'asset': 'BTC_USD',
            'amount': 20000,
            'risk_tolerance': 'medium'
        }
    )

    print("💰 نظام التداول المتكامل - مُنجز")

    # 9. مراقبة الأداء في الوقت الفعلي
    print("\n📈 مراقبة الأداء في الوقت الفعلي:")

    performance_metrics = []
    for i in range(5): # مراقبة 5 ثوان
        current_metrics = monitor.get_current_metrics()
        performance_metrics.append(current_metrics)

        # عرض المقاييس كل ثانية
        print(f" {i+1}s: CPU {current_metrics['cpu_percent']:.1f}% | "
              f"Memory {current_metrics['memory_percent']:.1f}% | "
              f"Disk {current_metrics['disk_percent']:.1f}%")

        await asyncio.sleep(1)

    # 10. تحليل الأداء الشامل
    print(f"\n📊 تحليل الأداء الشامل:")

    # حساب المتوسطات
    if performance_metrics:
        avg_cpu = sum(m['cpu_percent'] for m in performance_metrics) / len(performance_metrics)
        avg_memory = sum(m['memory_percent'] for m in performance_metrics) / len(performance_metrics)

        print(f"متوسط استخدام المعالج: {avg_cpu:.1f}%")
        print(f"متوسط استخدام الذاكرة: {avg_memory:.1f}%")

    # حالة المهام
    scheduler_stats = scheduler.get_scheduler_stats()
    print(f"المهام النشطة: {scheduler_stats['running_tasks']}")
    print(f"المهام المكتملة: {scheduler_stats['completed_tasks']}")

    # حالة الأمان
    print(f"فحوصات الأمان: {len(security_results)} طبقات")

    # النتائج النهائية
    final_workflow_status = engine.get_execution_status(execution_id)
    final_portfolio_status = trading_system.get_portfolio_status()

    print(f"\n🎯 النتائج النهائية:")
    if final_workflow_status:
        print(f"Workflow: {final_workflow_status.get('status', 'UNKNOWN')}")
    print(f"قيمة المحفظة: ${final_portfolio_status['portfolio']['total_value']:,.2f}")
    print(f"العائد: {final_portfolio_status['portfolio']['performance_metrics']['total_return']:.2%}")

    # حفظ جميع النتائج
    comprehensive_results = {
        'workflow_execution': final_workflow_status,
        'trading_results': trading_result,
        'portfolio_status': final_portfolio_status,
        'security_results': security_results,
        'performance_metrics': performance_metrics[-5:], # آخر 5 مقاييس
        'scheduler_stats': scheduler_stats,
        'execution_timestamp': asyncio.get_event_loop().time()
    }

    with open('advanced_example_results.json', 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 تم حفظ النتائج الشاملة في: advanced_example_results.json")

    # إنشاء المحرر المرئي
    editor = VisualFlowEditor(complex_workflow)
    editor.save_html("advanced_workflow.html")
    print(f"🎨 تم حفظ المحرر المرئي في: advanced_workflow.html")

    # إيقاف جميع الأنظمة
    scheduler.stop_scheduler()
    trading_system.stop_trading()
    ai_system.shutdown()

    print(f"\n✅ انتهى المثال المتقدم الشامل!")
    print(f"📋 الملخص:")
    print(f" • {len(specialized_agents)} وكلاء متخصصة")
    print(f" • {len(workflow_nodes)} عقدة في workflow")
    print(f" • {len(tasks)} مهام مجدولة")
    print(f" • نظام أمان متعدد الطبقات")
    print(f" • مراقبة في الوقت الفعلي")

if __name__ == "__main__":
    asyncio.run(advanced_example())
