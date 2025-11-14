"""
إدارة الامتثال والحوكمة
"""
import logging
import time
from typing import Dict, Any

logger = logging.getLogger("Compliance")

class ComplianceError(Exception):
    pass

class AuditTrail:
    def log_operation(self, operation: str, data: Dict[str, Any]):
        logger.info(f"AUDIT [{operation}] ts={time.time()}")

class ComplianceManager:
    def __init__(self):
        self.gdpr = GDPRCompliance()
        self.sox = SOXCompliance()
        self.audit_trail = AuditTrail()

    def ensure_compliance(self, operation: str, data: Dict[str, Any]):
        # فحص GDPR
        gdpr_ok = self.gdpr.check_data_processing(data)
        if not gdpr_ok['compliant']:
            raise ComplianceError(f"GDPR: {gdpr_ok['issue']}")
        # تدقيق
        self.audit_trail.log_operation(operation, data)
        # احتفاظ بالبيانات
        retention_ok = self._check_data_retention(data)
        if not retention_ok['compliant']:
            raise ComplianceError(f"Retention: {retention_ok['issue']}")

    def _check_data_retention(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = data.get('sensitive', False)
        retention_days = data.get('retention_days', 365)
        if sensitive and retention_days > 90:
            return {'compliant': False, 'issue': 'Sensitive data retention too long'}
        return {'compliant': True}

class GDPRCompliance:
    def check_data_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # فحص_consent
        consent = data.get('consent')
        if not consent:
            return {'compliant': False, 'issue': 'Missing consent'}
        return {'compliant': True}

class SOXCompliance:
    def validate_controls(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'compliant': True}
