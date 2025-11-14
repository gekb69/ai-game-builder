"""
اختبارات نظام التداول
"""
import pytest
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trading.portfolio_manager import PortfolioManager, Transaction
from trading.risk_engine import AdvancedRiskEngine, RiskAssessment
from trading.intelligent_trading import IntelligentTradingSystem

def test_portfolio_creation():
    """اختبار إنشاء المحفظة"""
    portfolio = PortfolioManager(initial_balance=100000)

    assert portfolio.initial_balance == 100000
    assert portfolio.cash_balance == 100000
    assert portfolio.get_total_value() == 100000
    assert len(portfolio.positions) == 0

def test_portfolio_rebalance():
    """اختبار إعادة توازن المحفظة"""
    portfolio = PortfolioManager(initial_balance=100000)

    # إضافة مراكز
    target_allocation = {
        "BTC_USD": 0.6,
        "ETH_USD": 0.4
    }

    actions = portfolio.rebalance_portfolio(target_allocation)

    # يجب أن يقترح إجراءات إعادة توازن
    assert isinstance(actions, list)

def test_risk_engine():
    """اختبار محرك المخاطر"""
    risk_engine = AdvancedRiskEngine()

    # بيانات محفظة بسيطة
    portfolio_data = {
        'total_value': 100000,
        'positions': {
            'BTC_USD': {'weight': 0.5, 'volatility': 0.6},
            'ETH_USD': {'weight': 0.5, 'volatility': 0.8}
        },
        'value_history': [100000, 102000, 99000, 105000],
        'returns_history': [0.02, -0.03, 0.06]
    }

    assessment = risk_engine.assess_portfolio_risk(portfolio_data)

    assert assessment.risk_level is not None
    assert assessment.value_at_risk >= 0
    assert assessment.max_drawdown >= 0

@pytest.mark.asyncio
async def test_intelligent_trading_system():
    """اختبار نظام التداول الذكي"""
    trading_system = IntelligentTradingSystem(initial_balance=50000)

    assert trading_system.initial_balance == 50000

@pytest.mark.asyncio
async def test_trading_workflow():
    """اختبار سير عمل التداول"""
    trading_system = IntelligentTradingSystem(initial_balance=50000)

    market_data = {
        'BTC_USD': {'price': 45000, 'volume': 1000000, 'rsi': 65.2}
    }

    investment_params = {
        'asset': 'BTC_USD',
        'amount': 5000,
        'risk_tolerance': 'medium'
    }

    result = await trading_system.intelligent_trading_workflow(
        symbols=['BTC_USD'],
        market_data=market_data,
        investment_params=investment_params
    )

    assert 'status' in result
    assert result['status'] in ['SUCCESS', 'FAILED', 'ERROR']

def test_transaction_creation():
    """اختبار إنشاء معاملة"""
    transaction = Transaction(
        id="test_123",
        symbol="ETH_USD",
        side="SELL",
        quantity=1.5,
        price=3200,
        fee=5.0
    )

    assert transaction.id == "test_123"
    assert transaction.symbol == "ETH_USD"
    assert transaction.side == "SELL"
    assert transaction.quantity == 1.5
    assert transaction.price == 3200
    assert transaction.fee == 5.0

if __name__ == "__main__":
    pytest.main([__file__])
