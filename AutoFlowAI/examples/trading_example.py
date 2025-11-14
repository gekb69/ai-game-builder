"""
مثال نظام التداول الذكي
"""
import asyncio
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trading.intelligent_trading import IntelligentTradingSystem
from trading.portfolio_manager import PortfolioManager
from trading.risk_engine import AdvancedRiskEngine

async def trading_example():
    """مثال التداول الذكي"""
    print("💰 مثال نظام التداول الذكي")
    print("=" * 50)

    # 1. إنشاء نظام التداول
    trading_system = IntelligentTradingSystem(initial_balance=100000, risk_tolerance='medium')
    print(f"✅ تم إنشاء نظام التداول برصيد ${100000:,.2f}")

    # 2. محاكاة بيانات السوق
    market_data = {
        'BTC_USD': {
            'price': 45000,
            'volume': 1000000,
            'rsi': 65.2,
            'macd': 1200,
            'bb_upper': 48000,
            'bb_lower': 42000
        },
        'ETH_USD': {
            'price': 3200,
            'volume': 800000,
            'rsi': 58.7,
            'macd': 85,
            'bb_upper': 3400,
            'bb_lower': 3000
        },
        'AAPL': {
            'price': 175.50,
            'volume': 50000000,
            'rsi': 52.1,
            'pe_ratio': 28.5,
            'dividend_yield': 0.006
        }
    }

    investment_params = {
        'asset': 'BTC_USD',
        'amount': 25000, # $25,000
        'risk_tolerance': 'medium',
        'time_horizon': 'short_term',
        'strategy_type': 'momentum'
    }

    print("📊 بيانات السوق:")
    for symbol, data in market_data.items():
        print(f" {symbol}: ${data['price']}")

    # 3. تشغيل سير العمل الذكي
    result = await trading_system.intelligent_trading_workflow(
        symbols=['BTC_USD', 'ETH_USD', 'AAPL'],
        market_data=market_data,
        investment_params=investment_params
    )

    # 4. عرض النتائج
    print(f"\n🎯 نتائج التداول الذكي:")
    print(f"الحالة: {result['status']}")

    if result['status'] == 'SUCCESS':
        portfolio = result['portfolio_summary']
        risk = result['final_risk_assessment']

        print(f"\n📊 ملخص المحفظة:")
        print(f"💰 القيمة الإجمالية: ${portfolio['total_value']:,.2f}")
        print(f"💵 الرصيد النقدي: ${portfolio['cash_balance']:,.2f}")
        print(f"📈 المراكز: {portfolio['positions_count']}")
        print(f"🔄 العائد الإجمالي: {portfolio['performance_metrics']['total_return']:.2%}")
        print(f"📊 Sharpe Ratio: {portfolio['performance_metrics']['sharpe_ratio']:.2f}")
        print(f"📉 أقصى انخفاض: {portfolio['performance_metrics']['max_drawdown']:.2%}")

        print(f"\n⚠️ تقييم المخاطر:")
        print(f"🎯 مستوى المخاطر: {risk['current_risk_level']}")
        print(f"📊 نقاط المخاطر: {risk['risk_score']:.2f}")
        print(f"💰 Value at Risk: ${risk['var']:,.2f}")

        if risk['recommendations']:
            print(f"\n💡 التوصيات:")
            for rec in risk['recommendations']:
                print(f" • {rec}")

    # 5. عرض تفاصيل التداولات
    if 'executed_trades' in result:
        print(f"\n💹 التداولات المنفذة:")
        for trade in result['executed_trades']:
            print(f" {trade['trade']['symbol']}: {trade['trade']['side']} "
                  f"{trade['trade']['quantity']:.4f} @ ${trade['trade']['price']:,.2f}")

    # 6. عرض حالة المحفظة التفصيلية
    portfolio_status = trading_system.get_portfolio_status()
    print(f"\n📋 حالة المحفظة التفصيلية:")

    if portfolio_status['active_trades'] > 0:
        active_trades = trading_system.get_active_trades()
        print(f"🔄 التداولات النشطة: {portfolio_status['active_trades']}")
        for trade in active_trades[:3]: # أول 3
            print(f" {trade['symbol']}: {trade['side']} {trade['quantity']:.4f}")

    # 7. اختبار إدارة المخاطر
    print(f"\n🛡️ اختبار إدارة المخاطر:")
    risk_engine = AdvancedRiskEngine()

    # إنشاء بيانات محفظة للاختبار
    test_portfolio = {
        'total_value': 100000,
        'positions': {
            'BTC_USD': {'weight': 0.4, 'volatility': 0.6},
            'ETH_USD': {'weight': 0.3, 'volatility': 0.8},
            'AAPL': {'weight': 0.3, 'volatility': 0.4}
        },
        'value_history': [100000, 102000, 99000, 105000, 103000, 107000],
        'returns_history': [0.02, -0.03, 0.06, -0.02, 0.04]
    }

    risk_assessment = risk_engine.assess_portfolio_risk(test_portfolio)

    print(f"🎯 مستوى المخاطر: {risk_assessment.risk_level.value}")
    print(f"📊 نقاط المخاطر: {risk_assessment.risk_score:.2f}")
    print(f"💰 Value at Risk: ${risk_assessment.value_at_risk:,.2f}")
    print(f"📉 أقصى انخفاض: {risk_assessment.max_drawdown:.2%}")
    print(f"📈 Sharpe Ratio: {risk_assessment.sharpe_ratio:.2f}")

    # 8. اختبار إعادة التوازن
    print(f"\n⚖️ اختبار إعادة التوازن:")
    portfolio_manager = PortfolioManager(100000)

    target_allocation = {
        'BTC_USD': 0.4,
        'ETH_USD': 0.3,
        'AAPL': 0.3
    }

    rebalance_actions = portfolio_manager.rebalance_portfolio(target_allocation)
    if rebalance_actions:
        print("إجراءات إعادة التوازن المقترحة:")
        for action in rebalance_actions:
            print(f" {action['action']} {action['asset']}: ${action['amount']:,.2f}")
    else:
        print("✅ المحفظة متوازنة بالفعل")

    # حفظ النتائج
    with open('trading_results.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n💾 تم حفظ النتائج في: trading_results.json")

    print(f"\n✅ انتهى مثال التداول الذكي")

if __name__ == "__main__":
    asyncio.run(trading_example())
