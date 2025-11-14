"""
AutoFlowAI - نقطة الدخول الرئيسية
"""
import asyncio
import sys
import click
from pathlib import Path
from typing import Optional
import json
import time

from core.autoflowai import AdvancedAutoFlowAI
from core.types import AgentInfo
from agents.advanced_agent import AdvancedReasoningAgent
from workflow.workflow_engine import WorkflowEngine
from workflow.viflow import Workflow, Node, Flow
from trading.intelligent_trading import IntelligentTradingSystem
from utils.logger import setup_logger
from utils.config import Config

# إعداد السجلات
logger = setup_logger("AutoFlowAI", level="INFO")

@click.group()
@click.option('--config', '-c', type=click.Path(), help='ملف الإعدادات')
@click.option('--debug', is_flag=True, help='وضع التطوير')
@click.pass_context
def cli(ctx, config, debug):
    """AutoFlowAI - نظام ذكي متقدم لإدارة العمليات والمهام"""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    ctx.obj['debug'] = debug

    if debug:
        logger.setLevel('DEBUG')

@cli.command()
@click.option('--mode', default='development', type=click.Choice(['development', 'production', 'enterprise']), help='وضع التشغيل')
def start(mode):
    """بدء تشغيل AutoFlowAI"""
    logger.info(f"🚀 بدء تشغيل AutoFlowAI في وضع {mode}")

    # إنشاء النظام
    ai_system = AdvancedAutoFlowAI(mode)

    # عرض معلومات النظام
    click.echo(f"✅ AutoFlowAI v{ai_system.version} - {mode}")
    click.echo(f"📊 مكونات النظام:")
    click.echo(f" - الوكلاء: {len(ai_system.core.agents) if hasattr(ai_system.core, 'agents') else 0}")
    click.echo(f" - المراقبة: {'مفعل' if ai_system.monitoring else 'غير مفعل'}")
    click.echo(f" - التعلم: {'مفعل' if ai_system.learning else 'غير مفعل'}")

    # إبقاء النظام يعمل
    try:
        while True:
            click.echo("\n💡 أوامر متاحة:")
            click.echo(" 1. إضافة وكيل")
            click.echo(" 2. تشغيل workflow")
            click.echo(" 3. بدء التداول الذكي")
            click.echo(" 4. عرض حالة النظام")
            click.echo(" 5. إيقاف النظام")

            choice = click.prompt("اختر أمر", type=int, default=5, show_default=False)

            if choice == 1:
                _add_agent_interactive(ai_system)
            elif choice == 2:
                _run_workflow_interactive(ai_system)
            elif choice == 3:
                _start_trading_interactive()
            elif choice == 4:
                _show_system_status(ai_system)
            elif choice == 5:
                break
            else:
                click.echo("❌ اختيار غير صحيح")

    except KeyboardInterrupt:
        click.echo("\n⏹️ إيقاف النظام...")
    finally:
        ai_system.shutdown()
        click.echo("✅ تم إيقاف النظام بنجاح")

@cli.command()
@click.argument('workflow_file', type=click.Path(exists=True))
@click.option('--input-data', help='بيانات الإدخال (JSON)')
@click.option('--output', '-o', type=click.Path(), help='ملف الإخراج')
def execute_workflow(workflow_file, input_data, output):
    """تنفيذ workflow من ملف"""
    logger.info(f"📋 تنفيذ workflow: {workflow_file}")

    # تحميل workflow
    workflow = Workflow.load(workflow_file)
    engine = WorkflowEngine()
    engine.register_workflow(workflow)

    # تحضير بيانات الإدخال
    input_dict = {}
    if input_data:
        try:
            input_dict = json.loads(input_data)
        except json.JSONDecodeError as e:
            click.echo(f"❌ خطأ في JSON: {e}")
            return

    # تنفيذ workflow
    execution_id = engine.execute_workflow(workflow.id, input_dict)

    # انتظار الانتهاء
    click.echo(f"⏳ تنفيذ Workflow (ID: {execution_id})...")

    while True:
        status = engine.get_execution_status(execution_id)
        if not status:
            click.echo("❌ تنفيذ غير موجود")
            break

        click.echo(f"📊 الحالة: {status['status']}")

        if status['status'] in ['COMPLETED', 'FAILED']:
            click.echo(f"🎯 النتيجة النهائية: {status['status']}")
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(status, f, indent=2, ensure_ascii=False)
                click.echo(f"💾 تم حفظ النتائج في: {output}")
            break

        time.sleep(2)

@cli.command()
@click.option('--initial-balance', default=100000, help='الرصيد الابتدائي')
@click.option('--risk-tolerance', default='medium', type=click.Choice(['low', 'medium', 'high']), help='تحمل المخاطر')
def start_trading(initial_balance, risk_tolerance):
    """بدء نظام التداول الذكي"""
    logger.info(f"💰 بدء نظام التداول الذكي")

    trading_system = IntelligentTradingSystem(initial_balance, risk_tolerance)

    click.echo(f"✅ نظام التداول مُهيأ")
    click.echo(f"💵 الرصيد: ${initial_balance:,.2f}")
    click.echo(f"⚖️ تحمّل المخاطر: {risk_tolerance}")

    # محاكاة بيانات السوق
    market_data = {
        'BTC_USD': {'price': 45000, 'volume': 1000000, 'rsi': 65.2},
        'ETH_USD': {'price': 3200, 'volume': 800000, 'rsi': 58.7}
    }

    investment_params = {
        'asset': 'BTC_USD',
        'amount': 5000,
        'risk_tolerance': risk_tolerance
    }

    # تشغيل التداول الذكي
    async def run_trading():
        result = await trading_system.intelligent_trading_workflow(
            ['BTC_USD', 'ETH_USD'], market_data, investment_params
        )

        click.echo("\n🎯 نتائج التداول:")
        click.echo(f"📊 الحالة: {result.get('status')}")
        if result.get('status') == 'SUCCESS':
            portfolio = result.get('portfolio_summary', {})
            click.echo(f"💰 قيمة المحفظة: ${portfolio.get('total_value', 0):,.2f}")
            click.echo(f"📈 العائد الإجمالي: {portfolio.get('performance_metrics', {}).get('total_return', 0):.2%}")

    asyncio.run(run_trading())

@cli.command()
def demo():
    """تشغيل عرض توضيحي شامل"""
    click.echo("🎬 بدء العرض التوضيحي الشامل")

    # 1. إنشاء نظام AutoFlowAI
    ai_system = AdvancedAutoFlowAI('development')
    click.echo("✅ تم إنشاء AutoFlowAI")

    # 2. إضافة وكيل متقدم
    agent = AdvancedReasoningAgent(
        agent_id="demo_agent",
        name="وكيل تجريبي متقدم",
        capabilities=["analysis", "research", "decision_making"]
    )
    click.echo(f"✅ تم إنشاء وكيل: {agent.name}")

    # 3. تشغيل التفكير والإجراء
    async def demo_agent():
        problem = "تحليل أداء السوق واتخاذ قرار تداول"
        context = {'symbol': 'BTC_USD', 'amount': 10000}
        result = await agent.think_and_act(problem, context)

        click.echo("\n🧠 نتيجة التفكير:")
        click.echo(f"القرار: {result['final_decision']['decision']}")
        click.echo(f"الثقة: {result['final_decision']['confidence']:.2%}")

    asyncio.run(demo_agent())

    # 4. إنشاء workflow بسيط
    workflow = Workflow("demo_workflow", "workflow تجريبي")
    workflow.add_node(Node("start", "البداية", "start", (100, 100)))
    workflow.add_node(Node("process", "معالجة", "data_processing", (300, 100),
                           config={'operation': 'copy', 'input_key': 'data', 'output_key': 'processed_data'}))
    workflow.add_node(Node("end", "النهاية", "end", (500, 100)))
    workflow.add_flow(Flow("start", "process"))
    workflow.add_flow(Flow("process", "end"))
    click.echo("✅ تم إنشاء workflow تجريبي")

    # 5. نظام التداول
    trading_system = IntelligentTradingSystem(50000)
    click.echo("💰 تم إنشاء نظام التداول")

    click.echo("\n🎉 انتهى العرض التوضيحي!")

@cli.command()
@click.option('--agent-id', prompt='معرف الوكيل', help='معرف الوكيل الجديد')
@click.option('--name', prompt='اسم الوكيل', help='اسم الوكيل')
@click.option('--capabilities', prompt='القدرات (مفصولة بفاصلة)', help='قدرات الوكيل')
def add_agent(agent_id, name, capabilities):
    """إضافة وكيل جديد"""
    agent_info = AgentInfo(
        id=agent_id,
        name=name,
        capabilities=[cap.strip() for cap in capabilities.split(',')]
    )

    ai_system = AdvancedAutoFlowAI()
    ai_system.register_agent(agent_info)

    click.echo(f"✅ تم إضافة الوكيل: {name} ({agent_id})")
    click.echo(f"القدرات: {', '.join(agent_info.capabilities)}")

def _add_agent_interactive(ai_system):
    """إضافة وكيل تفاعلياً"""
    agent_id = click.prompt("معرف الوكيل")
    name = click.prompt("اسم الوكيل")
    capabilities = click.prompt("القدرات (مفصولة بفاصلة)")

    agent_info = AgentInfo(
        id=agent_id,
        name=name,
        capabilities=[cap.strip() for cap in capabilities.split(',')]
    )

    ai_system.register_agent(agent_info)
    click.echo(f"✅ تم إضافة الوكيل: {name}")

def _run_workflow_interactive(ai_system):
    """تشغيل workflow تفاعلياً"""
    workflow_name = click.prompt("اسم workflow")

    # إنشاء workflow بسيط
    workflow = Workflow(f"workflow_{workflow_name}", f"workflow {workflow_name}")
    workflow.add_node(Node("start", "البداية", "start", (100, 100)))
    workflow.add_node(Node("process", "معالجة", "data_processing", (300, 100)))
    workflow.add_node(Node("end", "النهاية", "end", (500, 100)))

    workflow.add_flow(Flow("start", "process"))
    workflow.add_flow(Flow("process", "end"))

    engine = WorkflowEngine(ai_system)
    engine.register_workflow(workflow)

    execution_id = engine.execute_workflow(workflow.id)
    click.echo(f"✅ تم بدء تنفيذ workflow (ID: {execution_id})")

def _start_trading_interactive():
    """بدء التداول تفاعلياً"""
    initial_balance = click.prompt("الرصيد الابتدائي", type=float, default=100000)
    risk_tolerance = click.prompt("تحمل المخاطر", type=click.Choice(['low', 'medium', 'high']), default='medium')

    trading_system = IntelligentTradingSystem(initial_balance, risk_tolerance)
    click.echo(f"✅ تم إنشاء نظام التداول برصيد ${initial_balance:,.2f}")

def _show_system_status(ai_system):
    """عرض حالة النظام"""
    dashboard = ai_system.monitoring.get_dashboard()
    click.echo("\n📊 حالة النظام:")
    click.echo(f"مدة التشغيل: {dashboard.get('uptime_sec', 0):.0f} ثانية")
    click.echo(f"الأحداث الحديثة: {dashboard.get('recent_events', 0)}")
    click.echo(f"مستوى الأمان: {dashboard.get('security_level', 'UNKNOWN')}")

if __name__ == '__main__':
    cli()
