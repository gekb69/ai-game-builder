"""
اختبارات الأمان
"""
import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.security_framework import AdvancedSecurityFramework, RateLimiter
from security.compliance import ComplianceManager
from security.security_framework import BehavioralAnalytics, ThreatIntelligenceEngine

def test_rate_limiter():
    """اختبار محدد المعدل"""
    limiter = RateLimiter(default_limit=3, window_sec=10)

    # الطلبات الأولى يجب أن تُسمح
    assert limiter.allow("user1") == True
    assert limiter.allow("user1") == True
    assert limiter.allow("user1") == True

    # الطلب الرابع يجب أن يُرفض
    assert limiter.allow("user1") == False

def test_behavioral_analytics():
    """اختبار التحليل السلوكي"""
    analytics = BehavioralAnalytics()

    # طلبات طبيعية
    request1 = {"user_id": "user1", "path": "/api/data", "size": 100}
    request2 = {"user_id": "user1", "path": "/api/other", "size": 200}

    score1 = analytics.analyze_behavior("user1", request1)
    score2 = analytics.analyze_behavior("user1", request2)

    # نقاط طبيعية يجب أن تكون عالية
    assert score1 >= 0.5
    assert score2 >= 0.5

def test_threat_intelligence():
    """اختبار ذكاء التهديدات"""
    threat_engine = ThreatIntelligenceEngine()

    # ميزات عادية
    normal_features = {
        'has_suspicious': False,
        'suspicious_keywords_count': 0,
        'param_count': 5,
        'user_agent_len': 50
    }

    result = threat_engine.predict_threat(normal_features)

    assert 'threat_probability' in result
    assert 'threat_type' in result
    assert 0 <= result['threat_probability'] <= 1

def test_advanced_security_framework():
    """اختبار إطار الأمان المتقدم"""
    security = AdvancedSecurityFramework('high')

    # طلب عادي
    normal_request = {
        'user_id': 'test_user',
        'payload': {'data': 'normal'},
        'roles': ['user'],
        'data_classification': 'internal'
    }

    # يجب أن يجتاز الفحص
    results = security.multi_layer_security_check(normal_request)

    assert 'layer_1' in results
    assert 'layer_5' in results

    # التحقق من اجتياز جميع الطبقات
    for layer in results.values():
        assert layer['status'] == 'passed'

def test_compliance_manager():
    """اختبار مدير الامتثال"""
    compliance = ComplianceManager()

    # بيانات متوافقة
    compliant_data = {
        'consent': True,
        'sensitive': False,
        'retention_days': 30
    }

    # يجب أن يجتاز فحص الامتثال
    try:
        compliance.ensure_compliance('test_operation', compliant_data)
        # إذا وصلنا هنا، فالفحص نجح
        assert True
    except Exception as e:
        pytest.fail(f"فشل فحص الامتثال: {e}")

def test_gdpr_compliance():
    """اختبار امتثال GDPR"""
    from security.compliance import GDPRCompliance

    gdpr = GDPRCompliance()

    # بيانات بموافقة
    data_with_consent = {'consent': True}
    result = gdpr.check_data_processing(data_with_consent)

    assert result['compliant'] == True

    # بيانات بدون موافقة
    data_without_consent = {'consent': False}
    result = gdpr.check_data_processing(data_without_consent)

    assert result['compliant'] == False

if __name__ == "__main__":
    pytest.main([__file__])
