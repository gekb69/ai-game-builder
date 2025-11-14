"""
AI Agent متطور مع reasoning وأدوات
"""
import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import threading
import time

from .reasoning_engine import ReasoningEngine, ReasoningChain
from .memory_system import AdvancedMemorySystem
from .tool_manager import ToolManager

class AdvancedReasoningAgent:
    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.id = agent_id
        self.name = name
        self.capabilities = capabilities

        # المكونات الأساسية
        self.reasoning_engine = ReasoningEngine()
        self.memory = AdvancedMemorySystem()
        self.tool_manager = ToolManager()

        # حالة التشغيل
        self.status = "IDLE"
        self.current_task = None
        self.performance_metrics = {
            'tasks_completed': 0,
            'reasoning_chains': 0,
            'tools_used': 0,
            'average_task_time': 0.0
        }

    async def think_and_act(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """التفكير واتخاذ إجراء - الوظيفة الرئيسية"""
        self.status = "THINKING"
        context = context or {}

        try:
            # الخطوة 1: التفكير والاستدلال
            reasoning_chain = await self.reasoning_engine.think(problem, context)

            # الخطوة 2: اختيار الأدوات المناسبة
            selected_tools = await self._select_tools(problem, reasoning_chain, context)

            # الخطوة 3: تنفيذ الأدوات
            tool_results = {}
            for tool_name in selected_tools:
                tool_result = await self.tool_manager.execute_tool(tool_name, context)
                tool_results[tool_name] = tool_result

            # الخطوة 4: تحليل النتائج واتخاذ القرار النهائي
            final_decision = await self._analyze_and_decide(
                problem, reasoning_chain, tool_results, context
            )

            # تحديث الأداء
            self.performance_metrics['reasoning_chains'] += 1
            self.performance_metrics['tools_used'] += len(selected_tools)

            # حفظ في الذاكرة
            self.memory.store_episode({
                'reasoning_chain': reasoning_chain.__dict__,
                'problem': problem,
                'context': context,
                'final_decision': final_decision
            })

            self.status = "IDLE"

            return {
                'agent_id': self.id,
                'reasoning_chain': {
                    'id': reasoning_chain.id,
                    'steps': reasoning_chain.steps,
                    'confidence': reasoning_chain.confidence
                },
                'selected_tools': selected_tools,
                'tool_results': tool_results,
                'final_decision': final_decision,
                'status': 'SUCCESS',
                'timestamp': time.time()
            }

        except Exception as e:
            self.status = "ERROR"
            return {
                'agent_id': self.id,
                'status': 'FAILED',
                'error': str(e),
                'timestamp': time.time()
            }

    async def _select_tools(self, problem: str, reasoning_chain: ReasoningChain, context: Dict[str, Any]) -> List[str]:
        """اختيار الأدوات المناسبة بناءً على التفكير"""
        tools_needed = []
        problem_lower = problem.lower()

        if 'بحث' in problem_lower or 'search' in problem_lower:
            tools_needed.append('web_search')

        if 'تحليل' in problem_lower or 'analysis' in problem_lower or 'بيانات' in problem_lower:
            tools_needed.append('data_analysis')

        if 'سوق' in problem_lower or 'market' in problem_lower or 'تداول' in problem_lower:
            tools_needed.append('market_data')

        return tools_needed

    async def _analyze_and_decide(self, problem: str, reasoning_chain: ReasoningChain,
                                  tool_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل النتائج واتخاذ القرار النهائي"""
        summary = {
            'problem': problem,
            'reasoning_confidence': reasoning_chain.confidence,
            'tools_used': list(tool_results.keys()),
            'successful_tools': len([t for t in tool_results.values() if t.get('status') == 'success']),
            'failed_tools': len([t for t in tool_results.values() if t.get('status') == 'failed'])
        }

        if summary['successful_tools'] > summary['failed_tools']:
            decision = "RECOMMENDED"
            confidence = min(summary['reasoning_confidence'] + 0.1, 1.0)
        else:
            decision = "REVIEW_REQUIRED"
            confidence = max(summary['reasoning_confidence'] - 0.2, 0.1)

        return {
            'decision': decision,
            'confidence': confidence,
            'summary': summary,
            'action_items': self._generate_action_items(tool_results, context)
        }

    def _generate_action_items(self, tool_results: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """توليد عناصر العمل المطلوبة"""
        actions = []

        if 'web_search' in tool_results and tool_results['web_search'].get('status') == 'success':
            actions.append("مراجعة نتائج البحث لاتخاذ قرار مدروس")

        if 'market_data' in tool_results and tool_results['market_data'].get('status') == 'success':
            actions.append("تطبيق الاستراتيجية بناءً على بيانات السوق الحالية")

        return actions

    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الـ Agent"""
        return {
            'agent_id': self.id,
            'name': self.name,
            'status': self.status,
            'capabilities': self.capabilities,
            'performance_metrics': self.performance_metrics,
            'available_tools': self.tool_manager.get_available_tools(),
            'memory_stats': self.memory.get_memory_stats(),
            'timestamp': time.time()
        }
