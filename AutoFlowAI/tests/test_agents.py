"""
اختبارات وكلاء AutoFlowAI
"""
import pytest
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.advanced_agent import AdvancedReasoningAgent

@pytest.mark.asyncio
async def test_agent_creation():
    """اختبار إنشاء وكيل"""
    agent = AdvancedReasoningAgent(
        agent_id="test_agent",
        name="وكيل اختبار",
        capabilities=["test", "validation"]
    )

    assert agent.id == "test_agent"
    assert agent.name == "وكيل اختبار"
    assert agent.status == "IDLE"
    assert len(agent.capabilities) == 2

@pytest.mark.asyncio
async def test_think_and_act():
    """اختبار التفكير والإجراء"""
    agent = AdvancedReasoningAgent(
        agent_id="test_agent",
        name="وكيل اختبار",
        capabilities=["analysis", "decision_making"]
    )

    problem = "اختبار تحليل بسيط"
    context = {"test_data": "sample"}

    result = await agent.think_and_act(problem, context)

    assert result['status'] == 'SUCCESS'
    assert result['agent_id'] == agent.id
    assert 'reasoning_chain' in result
    assert 'final_decision' in result

@pytest.mark.asyncio
async def test_agent_memory():
    """اختبار ذاكرة الوكيل"""
    agent = AdvancedReasoningAgent(
        agent_id="memory_agent",
        name="وكيل الذاكرة",
        capabilities=["memory_test"]
    )

    # حفظ ذكريات
    agent.memory.store_episode({"event": "test_event"})
    agent.memory.store_semantic("concept", {"definition": "test_definition"})

    # استرجاع الذكريات
    memories = agent.memory.get_relevant_memories("test")

    assert len(memories) > 0
    assert agent.memory.get_memory_stats()['episodic_memories'] >= 1

def test_agent_status():
    """اختبار حالة الوكيل"""
    agent = AdvancedReasoningAgent(
        agent_id="status_agent",
        name="وكيل الحالة",
        capabilities=["status_check"]
    )

    status = agent.get_status()

    assert status['agent_id'] == agent.id
    assert status['name'] == agent.name
    assert 'performance_metrics' in status
    assert 'available_tools' in status

if __name__ == "__main__":
    pytest.main([__file__])
