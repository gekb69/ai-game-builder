"""
اختبارات الأدوات
"""
import pytest
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.tools.web_search import WebSearchTool
from agents.tools.data_analysis import DataAnalysisTool
from agents.tools.market_data import MarketDataTool
from agents.tools.task_management import TaskManagementTool
from agents.tool_manager import ToolManager

@pytest.mark.asyncio
async def test_web_search_tool():
    """اختبار أداة البحث"""
    tool = WebSearchTool()

    result = await tool.execute({'query': 'test search'})

    assert tool.name == 'web_search'
    assert 'query' in result
    assert 'results' in result
    assert result['query'] == 'test search'
    assert len(result['results']) > 0

@pytest.mark.asyncio
async def test_data_analysis_tool():
    """اختبار أداة تحليل البيانات"""
    tool = DataAnalysisTool()

    # تحليل وصفي
    data = [1, 2, 3, 4, 5]
    result = await tool.execute({
        'data': data,
        'analysis_type': 'descriptive'
    })

    assert tool.name == 'data_analysis'
    assert result['analysis_type'] == 'descriptive'
    assert result['count'] == 5
    assert result['mean'] == 3.0
    assert result['min'] == 1
    assert result['max'] == 5

@pytest.mark.asyncio
async def test_market_data_tool():
    """اختبار أداة بيانات السوق"""
    tool = MarketDataTool()

    result = await tool.execute({'symbol': 'BTC_USD'})

    assert tool.name == 'market_data'
    assert 'symbol' in result
    assert 'current_price' in result
    assert 'volume' in result
    assert 'indicators' in result
    assert result['symbol'] == 'BTC_USD'
    assert result['current_price'] > 0

@pytest.mark.asyncio
async def test_task_management_tool():
    """اختبار أداة إدارة المهام"""
    tool = TaskManagementTool()
    result = await tool.execute({'action': 'status'})
    assert result['active_tasks'] == 1

def test_tool_manager():
    """اختبار مدير الأدوات"""
    manager = ToolManager()

    # التحقق من الأدوات الافتراضية
    tools = manager.get_available_tools()

    assert 'web_search' in tools
    assert 'data_analysis' in tools
    assert 'market_data' in tools
    assert 'task_management' in tools
    assert len(tools) >= 4

@pytest.mark.asyncio
async def test_tool_manager_execution():
    """اختبار تنفيذ الأدوات"""
    manager = ToolManager()

    # تنفيذ أداة البحث
    result = await manager.execute_tool('web_search', {'query': 'test'})

    assert result['status'] == 'success'
    assert result['tool_name'] == 'web_search'
    assert 'result' in result
    assert 'execution_time' in result

@pytest.mark.asyncio
async def test_tool_error_handling():
    """اختبار معالجة أخطاء الأدوات"""
    manager = ToolManager()

    # محاولة تنفيذ أداة غير موجودة
    with pytest.raises(ValueError):
        await manager.execute_tool('nonexistent_tool', {})

@pytest.mark.asyncio
async def test_data_analysis_correlation():
    """اختبار تحليل الارتباط"""
    tool = DataAnalysisTool()

    result = await tool.execute({
        'analysis_type': 'correlation'
    })

    assert result['analysis_type'] == 'correlation'
    assert 'correlation_matrix' in result
    assert 'significant_pairs' in result

def test_tool_info():
    """اختبار معلومات الأداة"""
    manager = ToolManager()

    info = manager.get_tool_info('web_search')

    assert info['name'] == 'web_search'
    assert 'description' in info

if __name__ == "__main__":
    pytest.main([__file__])
