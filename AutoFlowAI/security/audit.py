"""
نظام التدقيق والمراجعة
"""
import time
import hashlib
import json
from typing import Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class AuditRecord:
    timestamp: float
    operation: str
    user_id: str
    resource: str
    action: str
    result: str
    details: Dict[str, Any] = field(default_factory=dict)
    hash_id: str = ""

    def __post_init__(self):
        content = f"{self.timestamp}_{self.operation}_{self.user_id}_{self.resource}_{self.action}"
        self.hash_id = hashlib.sha256(content.encode()).hexdigest()[:16]

class AuditTrail:
    def __init__(self):
        self.records: List[AuditRecord] = []
        self.retention_days = 2555 # 7 سنوات

    def log(self, operation: str, user_id: str, resource: str,
            action: str, result: str, details: Dict[str, Any] = None):
        record = AuditRecord(
            timestamp=time.time(),
            operation=operation,
            user_id=user_id,
            resource=resource,
            action=action,
            result=result,
            details=details or {}
        )
        self.records.append(record)
        # تنظيف السجلات القديمة
        self._cleanup_old_records()

    def _cleanup_old_records(self):
        cutoff = time.time() - (self.retention_days * 24 * 3600)
        self.records = [r for r in self.records if r.timestamp >= cutoff]

    def get_records(self, user_id: str = None, operation: str = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        filtered = self.records

        if user_id:
            filtered = [r for r in filtered if r.user_id == user_id]
        if operation:
            filtered = [r for r in filtered if r.operation == operation]

        return [record.__dict__ for record in filtered[-limit:]]
