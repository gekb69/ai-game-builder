"""
إدارة الأدوات المتخصصة
"""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .tools.web_search import WebSearchTool
from .tools.data_analysis import DataAnalysisTool
from .tools.market_data import MarketDataTool
from .tools.task_management import TaskManagementTool
from .base import Tool


class ToolManager:
    """إدارة الأدوات المتاحة للـ Agents"""

    def __init__(self):
        self.tools = self._initialize_default_tools()

    def _initialize_default_tools(self) -> Dict[str, Tool]:
        """تهيئة الأدوات الافتراضية"""
        return {
            'web_search': WebSearchTool(),
            'data_analysis': DataAnalysisTool(),
            'market_data': MarketDataTool(),
            'task_management': TaskManagementTool()
        }

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """تنفيذ أداة معينة"""
        if tool_name not in self.tools:
            raise ValueError(f"أداة غير مدعومة: {tool_name}")

        tool = self.tools[tool_name]
        start_time = time.time()

        try:
            result = await tool.execute(parameters)
            execution_time = time.time() - start_time

            return {
                'tool_name': tool_name,
                'status': 'success',
                'result': result,
                'execution_time': execution_time,
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'tool_name': tool_name,
                'status': 'failed',
                'error': str(e),
                'execution_time': time.time() - start_time,
                'timestamp': time.time()
            }

    def get_available_tools(self) -> List[str]:
        """الحصول على قائمة الأدوات المتاحة"""
        return list(self.tools.keys())

    def add_tool(self, tool: Tool):
        """إضافة أداة جديدة"""
        self.tools[tool.name] = tool

    def get_tool_info(self, tool_name: str) -> Dict[str, str]:
        """الحصول على معلومات الأداة"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            return {
                'name': tool.name,
                'description': tool.description
            }
        return {}
