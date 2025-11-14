"""
ViFlow - محرك Workflow الأساسي
"""
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json

from .workflow_models import WorkflowContext, NodeExecution, WorkflowStatus, NodeType

@dataclass
class Node:
    id: str
    name: str
    type: str # start, end, ai_agent, condition, data_processing, delay
    position: Tuple[int, int] = field(default_factory=lambda: (0, 0))
    config: Dict[str, Any] = field(default_factory=dict)
    agent_id: Optional[str] = None
    condition: Optional[str] = None # للشروط
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)

@dataclass
class Flow:
    from_node: str
    to_node: str
    condition: Optional[str] = None # true/false أو شرط مخصص

@dataclass
class Workflow:
    id: str
    name: str
    description: str = ""
    nodes: Dict[str, Node] = field(default_factory=dict)
    flows: List[Flow] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_flow(self, flow: Flow):
        self.flows.append(flow)

    def get_next_nodes(self, current_node_id: str, context: Dict[str, Any] = None) -> List[str]:
        context = context or {}
        next_nodes = []
        for flow in self.flows:
            if flow.from_node == current_node_id:
                if flow.condition:
                    if flow.condition in ['true', 'false']:
                        if self._evaluate_condition(flow.condition, context):
                            next_nodes.append(flow.to_node)
                    else:
                        if self._evaluate_custom_condition(flow.condition, context):
                            next_nodes.append(flow.to_node)
                else:
                    next_nodes.append(flow.to_node)
        return next_nodes

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        if condition == 'true':
            return True
        if condition == 'false':
            return False
        try:
            expr = condition
            for key, value in context.items():
                expr = expr.replace(key, f'"{value}"' if isinstance(value, str) else str(value))
            return eval(expr, {"__builtins__": {}})
        except:
            return False

    def _evaluate_custom_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        return self._evaluate_condition(condition, context)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'nodes': {nid: {
                'id': node.id, 'name': node.name, 'type': node.type,
                'position': node.position, 'config': node.config,
                'agent_id': node.agent_id, 'condition': node.condition,
                'inputs': node.inputs, 'outputs': node.outputs
            } for nid, node in self.nodes.items()},
            'flows': [{'from_node': f.from_node, 'to_node': f.to_node, 'condition': f.condition} for f in self.flows],
            'variables': self.variables,
            'version': self.version,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        wf = cls(data['id'], data['name'], data.get('description', ''))
        wf.variables = data.get('variables', {})
        wf.version = data.get('version', '1.0.0')
        wf.tags = data.get('tags', [])
        for nid, ndata in data.get('nodes', {}).items():
            node = Node(
                ndata['id'], ndata['name'], ndata['type'],
                tuple(ndata.get('position', [0, 0])),
                ndata.get('config', {}),
                ndata.get('agent_id'),
                ndata.get('condition'),
                ndata.get('inputs', []),
                ndata.get('outputs', [])
            )
            wf.nodes[nid] = node
        for fdata in data.get('flows', []):
            wf.flows.append(Flow(fdata['from_node'], fdata['to_node'], fdata.get('condition')))
        return wf

    def save(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'Workflow':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
