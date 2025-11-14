"""
اختبارات workflow
"""
import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from workflow.viflow import Workflow, Node, Flow
from workflow.workflow_engine import WorkflowEngine
from workflow.visual_editor import VisualFlowEditor

def test_workflow_creation():
    """اختبار إنشاء workflow"""
    workflow = Workflow(
        id="test_workflow",
        name="workflow اختبار",
        description="workflow للاختبار"
    )

    assert workflow.id == "test_workflow"
    assert workflow.name == "workflow اختبار"
    assert len(workflow.nodes) == 0
    assert len(workflow.flows) == 0

def test_workflow_nodes():
    """اختبار إضافة العقد"""
    workflow = Workflow("test_nodes", "اختبار العقد")

    start_node = Node("start", "البداية", "start")
    end_node = Node("end", "النهاية", "end")

    workflow.add_node(start_node)
    workflow.add_node(end_node)

    assert len(workflow.nodes) == 2
    assert "start" in workflow.nodes
    assert "end" in workflow.nodes

def test_workflow_flows():
    """اختبار الروابط"""
    workflow = Workflow("test_flows", "اختبار الروابط")

    workflow.add_node(Node("start", "البداية", "start"))
    workflow.add_node(Node("process", "معالجة", "data_processing"))
    workflow.add_node(Node("end", "النهاية", "end"))

    workflow.add_flow(Flow("start", "process"))
    workflow.add_flow(Flow("process", "end"))

    assert len(workflow.flows) == 2
    assert workflow.flows[0].from_node == "start"
    assert workflow.flows[0].to_node == "process"

def test_workflow_conditions():
    """اختبار الشروط"""
    workflow = Workflow("test_conditions", "اختبار الشروط")

    workflow.add_node(Node("start", "البداية", "start"))
    workflow.add_node(Node("condition", "شرط", "condition", condition="True"))
    workflow.add_node(Node("end", "النهاية", "end"))

    workflow.add_flow(Flow("start", "condition"))
    workflow.add_flow(Flow("condition", "end", "true"))

    # اختبار تقييم الشرط
    context = {"variable": "test"}
    next_nodes = workflow.get_next_nodes("condition", context)

    assert "end" in next_nodes

def test_workflow_serialization():
    """اختبار حفظ وتحميل workflow"""
    original_workflow = Workflow("serialization_test", "اختبار التسلسل")

    # إضافة عقد
    original_workflow.add_node(Node("start", "البداية", "start", (100, 100)))
    original_workflow.add_node(Node("process", "معالجة", "data_processing", (300, 100),
                                    config={'operation': 'copy'}))
    original_workflow.add_node(Node("end", "النهاية", "end", (500, 100)))

    # إضافة روابط
    original_workflow.add_flow(Flow("start", "process"))
    original_workflow.add_flow(Flow("process", "end"))

    # حفظ في ملف مؤقت
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name

    try:
        original_workflow.save(temp_file)

        # تحميل من الملف
        loaded_workflow = Workflow.load(temp_file)

        # المقارنة
        assert loaded_workflow.id == original_workflow.id
        assert loaded_workflow.name == original_workflow.name
        assert len(loaded_workflow.nodes) == len(original_workflow.nodes)
        assert len(loaded_workflow.flows) == len(original_workflow.flows)

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_visual_editor():
    """اختبار المحرر المرئي"""
    workflow = Workflow("editor_test", "اختبار المحرر")

    workflow.add_node(Node("start", "البداية", "start"))
    workflow.add_node(Node("end", "النهاية", "end"))

    editor = VisualFlowEditor(workflow)

    # التحقق من وجود القالب
    assert editor.html_template is not None
    assert "{{WORKFLOW_DATA}}" in editor.html_template

def test_workflow_engine():
    """اختبار محرك workflow"""
    # إعداد بسيط
    workflow = Workflow("engine_test", "اختبار المحرك")
    workflow.add_node(Node("start", "البداية", "start"))
    workflow.add_node(Node("end", "النهاية", "end"))
    workflow.add_flow(Flow("start", "end"))

    engine = WorkflowEngine()
    engine.register_workflow(workflow)

    # تنفيذ workflow
    execution_id = engine.execute_workflow(workflow.id, {})

    assert execution_id is not None
    assert execution_id in engine.running_executions

if __name__ == "__main__":
    pytest.main([__file__])
