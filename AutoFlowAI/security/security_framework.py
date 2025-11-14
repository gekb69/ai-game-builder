"""
إطار الأمان المتقدم
"""
import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict, deque

logger = logging.getLogger("SecurityFramework")

class SecurityError(Exception):
    pass

class SecurityViolation(SecurityError):
    pass

class RateLimiter:
    def __init__(self, default_limit: int, window_sec: int):
        self.default_limit = default_limit
        self.window_sec = window_sec
        self.events = defaultdict(deque)

    def allow(self, key: str, limit: Optional[int] = None, window_sec: Optional[int] = None) -> bool:
        limit = limit or self.default_limit
        window_sec = window_sec or self.window_sec
        now = time.time()
        dq = self.events[key]
        # إزالة القديمة
        while dq and dq[0] < now - window_sec:
            dq.popleft()
        if len(dq) >= limit:
            return False
        dq.append(now)
        return True

class ThreatIntelligenceEngine:
    def predict_threat(self, features: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.0
        score += 0.3 if features.get('has_suspicious') else 0.0
        score += min(features.get('suspicious_keywords_count', 0) * 0.1, 0.4)
        score += 0.1 if features.get('param_count', 0) > 20 else 0.0
        score += 0.1 if features.get('user_agent_len', 0) < 5 else 0.0
        score = min(score, 1.0)
        threat_type = 'high_risk_pattern' if score > 0.8 else 'normal'
        return {'threat_probability': score, 'threat_type': threat_type, 'confidence': 1.0 - 0.2 * (1-score)}

class BehavioralAnalytics:
    def __init__(self):
        self.history = defaultdict(deque)

    def get_recent_requests(self, user_id: str, minutes: int = 1) -> list[Dict[str, Any]]:
        cutoff = time.time() - minutes * 60
        dq = self.history[user_id]
        return [x for x in dq if x['time'] >= cutoff]

    def analyze_behavior(self, user_id: str, request: Dict[str, Any]) -> float:
        now = time.time()
        dq = self.history[user_id]
        dq.append({'time': now, 'path': request.get('path'), 'size': len(str(request.get('payload', {})))})
        # إزالة القديمة (> 30 دقيقة)
        while dq and dq[0]['time'] < now - 1800:
            dq.popleft()
        recent = self.get_recent_requests(user_id, minutes=5)
        count = len(recent)
        avg_size = sum(r['size'] for r in recent) / max(count, 1)
        # نقاط سلوك: كثافة الطلبات وحجمها
        base_score = 1.0
        if count > 120: # > 24/sec لمدة 5 دقائق
            base_score -= 0.4
        if avg_size > 5_000:
            base_score -= 0.2
        return max(min(base_score, 1.0), 0.0)

class AdvancedSecurityFramework:
    def __init__(self, security_level='maximum'):
        self.security_level = security_level
        self.threat_intelligence = ThreatIntelligenceEngine()
        self.behavioral_analytics = BehavioralAnalytics()
        self.rate_limiter = RateLimiter(default_limit=100, window_sec=60)

    def multi_layer_security_check(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # طبقة 0: Rate Limiting
        user_id = request.get('user_id', 'anonymous')
        if not self.rate_limiter.allow(user_id):
            raise SecurityViolation("تم تجاوز حد الطلبات المسموح.")

        layers = [
            self._layer_network_security,
            self._layer_behavioral_analysis,
            self._layer_ml_threat_detection,
            self._layer_data_classification,
            self._layer_access_control
        ]

        results = {}
        for i, layer in enumerate(layers, 1):
            try:
                result = layer(request)
                results[f'layer_{i}'] = {'status': 'passed', 'details': result}
            except SecurityViolation as e:
                results[f'layer_{i}'] = {'status': 'failed', 'error': str(e), 'timestamp': time.time()}
                raise SecurityError(f"Security violation at layer {i}: {str(e)}")

        logger.info("اجتاز الطلب جميع طبقات الأمان.")
        return results

    def _layer_network_security(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {'source_ip': request.get('source_ip'), 'validated': True}

    def _layer_behavioral_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        uid = request.get('user_id', 'anonymous')
        score = self.behavioral_analytics.analyze_behavior(uid, request)
        if score < 0.7:
            raise SecurityViolation(f"Suspicious behavior detected: score {score}")
        return {'behavior_score': score}

    def _layer_ml_threat_detection(self, request: Dict[str, Any]) -> Dict[str, Any]:
        features = self._extract_request_features(request)
        threat = self.threat_intelligence.predict_threat(features)
        if threat['threat_probability'] > 0.8:
            raise SecurityViolation(f"High threat probability: {threat['threat_probability']}")
        return threat

    def _layer_data_classification(self, request: Dict[str, Any]) -> Dict[str, Any]:
        sens = request.get('data_classification', 'public')
        return {'data_classification': sens, 'approved': sens in ['public', 'internal', 'confidential']}

    def _layer_access_control(self, request: Dict[str, Any]) -> Dict[str, Any]:
        roles = request.get('roles', [])
        required = request.get('required_roles', [])
        if required and not any(r in roles for r in required):
            raise SecurityViolation("Access denied: insufficient role")
        return {'roles': roles}

    def _extract_request_features(self, request: Dict[str, Any]) -> Dict[str, Any]:
        payload = request.get('payload') or {}
        keywords = ['script', 'DROP', 'SELECT', 'sudo', 'rm -rf', '<script>']
        ua = str(request.get('user_agent', ''))
        has_suspicious = any(k.lower() in str(payload).lower() for k in keywords) or any(k.lower() in ua.lower() for k in keywords)
        return {
            'param_count': len(payload),
            'payload_size': len(str(payload)),
            'user_agent_len': len(ua),
            'suspicious_keywords_count': sum(1 for k in keywords if k.lower() in str(payload).lower()) +
            sum(1 for k in keywords if k.lower() in ua.lower()),
            'has_suspicious': has_suspicious
        }
