"""
محرك تنفيذ Workflow
"""
import threading
import time
import logging
from typing import Dict, List, Any, Optional
import uuid

from .viflow import Workflow, Node, Flow
from .workflow_models import WorkflowContext, NodeExecution, WorkflowStatus
from core.types import Task

logger = logging.getLogger("WorkflowEngine")

class WorkflowEngine:
    def __init__(self, autoflowai=None):
        self.workflows: Dict[str, Workflow] = {}
        self.running_executions: Dict[str, WorkflowContext] = {}
        self.autoflowai = autoflowai
        self.node_handlers = {
            'start': self._handle_start_node,
            'end': self._handle_end_node,
            'ai_agent': self._handle_ai_agent_node,
            'condition': self._handle_condition_node,
            'data_processing': self._handle_data_processing_node,
            'delay': self._handle_delay_node
        }

    def register_workflow(self, workflow: Workflow):
        self.workflows[workflow.id] = workflow
        logger.info(f"تم تسجيل workflow: {workflow.name}")

    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None, execution_id: str = None) -> str:
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow غير موجود: {workflow_id}")

        execution_id = execution_id or str(uuid.uuid4())[:8]
        input_data = input_data or {}

        context = WorkflowContext(
            execution_id=execution_id,
            workflow_id=workflow_id,
            input_data=input_data,
            variables={},
            status=WorkflowStatus.RUNNING
        )

        self.running_executions[execution_id] = context
        logger.info(f"بدء تنفيذ workflow: {workflow_id} (execution_id: {execution_id})")

        # تشغيل في thread منفصل
        thread = threading.Thread(target=self._execute_workflow_thread, args=(workflow_id, execution_id), daemon=True)
        thread.start()

        return execution_id

    def _execute_workflow_thread(self, workflow_id: str, execution_id: str):
        try:
            workflow = self.workflows[workflow_id]
            context = self.running_executions[execution_id]

            # العثور على عقدة البداية
            start_nodes = [n for n in workflow.nodes.values() if n.type == 'start']
            if not start_nodes:
                raise ValueError("لا توجد عقدة بداية")

            current_node = start_nodes[0]
            context.current_node = current_node.id
            context.variables.update(workflow.variables)
            context.variables.update(context.input_data)

            # تنفيذ الخطوات
            while current_node and context.status == WorkflowStatus.RUNNING:
                self._execute_node(workflow, current_node, context)

                # التحقق من انتهاء التنفيذ
                if current_node.type == 'end':
                    context.status = WorkflowStatus.COMPLETED
                    context.completed_at = time.time()
                    break

                # الانتقال للعقد التالية
                next_nodes = workflow.get_next_nodes(current_node.id, context.variables)
                if not next_nodes:
                    logger.warning(f"لا توجد عقدة تالية من {current_node.id}")
                    context.status = WorkflowStatus.COMPLETED
                    context.completed_at = time.time()
                    break

                next_node_id = next_nodes[0]
                current_node = workflow.nodes.get(next_node_id)
                context.current_node = current_node.id if current_node else None

            logger.info(f"انتهاء تنفيذ workflow: {execution_id} - الحالة: {context.status}")

        except Exception as e:
            context.status = WorkflowStatus.FAILED
            context.error = str(e)
            context.completed_at = time.time()
            logger.error(f"خطأ في تنفيذ workflow {execution_id}: {e}")

    def _execute_node(self, workflow: Workflow, node: Node, context: WorkflowContext):
        logger.info(f"تنفيذ عقدة: {node.name} ({node.type})")

        step_start = time.time()
        node_execution = NodeExecution(
            node_id=node.id,
            node_name=node.name,
            node_type=node.type,
            status="running"
        )
        context.history.append(node_execution.__dict__)

        try:
            handler = self.node_handlers.get(node.type, self._handle_unknown_node)
            result = handler(workflow, node, context)

            node_execution.status = "completed"
            node_execution.completed_at = time.time()
            node_execution.duration = node_execution.completed_at - step_start
            node_execution.result = result

            context.results[node.id] = result
            if isinstance(result, dict):
                context.variables.update(result)

        except Exception as e:
            node_execution.status = "failed"
            node_execution.completed_at = time.time()
            node_execution.duration = node_execution.completed_at - step_start
            node_execution.error = str(e)
            raise

    def _handle_start_node(self, workflow: Workflow, node: Node, context: WorkflowContext) -> Dict[str, Any]:
        return {'message': 'بداية التنفيذ'}

    def _handle_end_node(self, workflow: Workflow, node: Node, context: WorkflowContext) -> Dict[str, Any]:
        return {'message': 'انتهاء التنفيذ', 'final_results': context.results}

    def _handle_ai_agent_node(self, workflow: Workflow, node: Node, context: WorkflowContext) -> Dict[str, Any]:
        if not self.autoflowai or not node.agent_id:
            return {'note': 'لا يوجد autoflowai أو agent_id', 'mock': True}

        # تنفيذ المهمة عبر الـ Agent
        task_data = {
            'type': 'workflow_task',
            'data': context.variables.copy(),
            'node_config': node.config,
            'workflow_context': context.__dict__
        }

        task = Task(
            id=str(uuid.uuid4())[:8],
            type=task_data['type'],
            payload=task_data,
            priority=node.config.get('priority', 5)
        )

        try:
            result = self.autoflowai.core.execute_task(node.agent_id, task)
            return {
                'agent_id': node.agent_id,
                'task_result': result,
                'executed_at': time.time()
            }
        except Exception as e:
            return {
                'agent_id': node.agent_id,
                'error': str(e),
                'executed_at': time.time()
            }

    def _handle_condition_node(self, workflow: Workflow, node: Node, context: WorkflowContext) -> Dict[str, Any]:
        condition = node.condition or node.config.get('condition', 'true')
        result = self._evaluate_condition(condition, context.variables)
        return {'condition_result': result, 'condition': condition}

    def _handle_data_processing_node(self, workflow: Workflow, node: Node, context: WorkflowContext) -> Dict[str, Any]:
        operation = node.config.get('operation', 'copy')
        input_key = node.config.get('input_key')
        output_key = node.config.get('output_key', input_key)

        if operation == 'copy' and input_key:
            return {output_key: context.variables.get(input_key)}
        elif operation == 'calculate':
            formula = node.config.get('formula')
            result = self._evaluate_condition(formula, context.variables)
            return {output_key: result}
        else:
            return {'note': f'عملية غير مدعومة: {operation}'}

    def _handle_delay_node(self, workflow: Workflow, node: Node, context: WorkflowContext) -> Dict[str, Any]:
        delay_seconds = node.config.get('seconds', 1)
        time.sleep(delay_seconds)
        return {'delayed_seconds': delay_seconds}

    def _handle_unknown_node(self, workflow: Workflow, node: Node, context: WorkflowContext) -> Dict[str, Any]:
        return {'note': f'نوع عقدة غير مدعوم: {node.type}'}

    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        try:
            expr = condition
            for key, value in variables.items():
                if isinstance(value, str):
                    expr = expr.replace(key, f'"{value}"')
                else:
                    expr = expr.replace(key, str(value))
            return eval(expr, {"__builtins__": {}})
        except Exception as e:
            logger.warning(f"خطأ في تقييم الشرط: {condition} - {e}")
            return False

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        context = self.running_executions.get(execution_id)
        if context:
            return {
                'execution_id': execution_id,
                'workflow_id': context.workflow_id,
                'status': context.status.value,
                'current_node': context.current_node,
                'started_at': context.started_at,
                'completed_at': context.completed_at,
                'error': context.error,
                'results_count': len(context.results),
                'history_count': len(context.history)
            }
        return None

    def get_workflow_executions(self, workflow_id: str) -> List[Dict[str, Any]]:
        return [ctx.__dict__ for ctx in self.running_executions.values() if ctx.workflow_id == workflow_id]
