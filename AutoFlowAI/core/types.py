"""
تعريفات الأنواع الأساسية لـ AutoFlowAI
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import time

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class TaskStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class Task:
    id: str
    type: str
    payload: Dict[str, Any]
    created_at: float = field(default_factory=time.time)
    priority: int = 5 # 1 أعلى
    scheduled_at: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent_id: Optional[str] = None
    estimated_duration: Optional[float] = None
    actual_duration: Optional[float] = None

@dataclass
class AgentInfo:
    id: str
    name: str
    capabilities: List[str]
    status: str = "IDLE"
    tasks_completed: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_activity: float = field(default_factory=time.time)
