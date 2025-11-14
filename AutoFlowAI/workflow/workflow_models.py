"""
نماذج البيانات للـ Workflow
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import time

class WorkflowStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class NodeType(Enum):
    START = "start"
    END = "end"
    AI_AGENT = "ai_agent"
    CONDITION = "condition"
    DATA_PROCESSING = "data_processing"
    DELAY = "delay"
    PARALLEL = "parallel"

@dataclass
class WorkflowContext:
    """سياق تنفيذ الـ Workflow"""
    execution_id: str
    workflow_id: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    current_node: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.CREATED
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    error: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class NodeExecution:
    """تنفيذ عقدة واحدة"""
    node_id: str
    node_name: str
    node_type: NodeType
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    retry_count: int = 0
