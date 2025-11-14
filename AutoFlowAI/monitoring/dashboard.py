"""
لوحة التحكم
"""
import json
from typing import Dict, Any, List
from .real_time_monitor import RealTimeMonitor
from .performance_tracker import PerformanceTracker

class SystemDashboard:
    def __init__(self, autoflowai):
        self.system = autoflowai
        self.real_time_data = RealTimeMonitor()
        self.performance_tracker = PerformanceTracker()

    def get_live_dashboard(self) -> Dict[str, Any]:
        return {
            'system_status': self._get_system_status(),
            'active_agents': self._get_active_agents(),
            'performance_metrics': self._get_performance_metrics(),
            'resource_usage': self._get_resource_usage(),
            'active_workflows': self._get_active_workflows(),
            'security_alerts': self._get_security_alerts()
        }

    def generate_system_report(self, timeframe='24h') -> Dict[str, Any]:
        return {
            'summary': self._generate_executive_summary(),
            'performance': self._analyze_performance(timeframe),
            'security': self._security_report(timeframe),
            'agents': self._agents_report(timeframe),
            'recommendations': self._generate_recommendations()
        }

    def _get_system_status(self) -> str:
        metrics = self.real_time_data.get_current_metrics()
        return self.real_time_data._determine_system_status(metrics)

    def _get_active_agents(self) -> int:
        return len(self.system.core.agents) if hasattr(self.system.core, 'agents') else 0

    def _get_performance_metrics(self) -> Dict[str, Any]:
        return self.performance_tracker.get_performance_summary()

    def _get_resource_usage(self) -> Dict[str, Any]:
        return self.real_time_data.get_current_metrics()

    def _get_active_workflows(self) -> int:
        #计数活跃工作流
        if hasattr(self.system, 'workflow_engine') and self.system.workflow_engine:
            return len(self.system.workflow_engine.running_executions)
        return 0

    def _get_security_alerts(self) -> int:
        return len(self.real_time_data.alerts)

    def _generate_executive_summary(self) -> str:
        status = self._get_system_status()
        agents = self._get_active_agents()
        workflows = self._get_active_workflows()

        return f"النظام {status} مع {agents} agents نشطة و {workflows} workflows قيد التنفيذ"

    def _analyze_performance(self, timeframe: str) -> Dict[str, Any]:
        return self.performance_tracker.get_performance_summary()

    def _security_report(self, timeframe: str) -> Dict[str, Any]:
        return {
            'alerts_count': len(self.real_time_data.alerts),
            'recent_alerts': self.real_time_data.alerts[-10:],
            'security_level': 'HIGH'
        }

    def _agents_report(self, timeframe: str) -> Dict[str, Any]:
        if hasattr(self.system.core, 'agents'):
            return self.system.core.agent_health()
        return {}

    def _generate_recommendations(self) -> List[str]:
        recommendations = []

        # تحليل استخدام الموارد
        metrics = self.real_time_data.get_current_metrics()
        if metrics.get('cpu_percent', 0) > 80:
            recommendations.append("استخدم المزيد من الموارد أو قم بتحسين الأداء")

        if metrics.get('memory_percent', 0) > 80:
            recommendations.append("فكر في زيادة الذاكرة أو تحسين إدارة الذاكرة")

        # تحليل الأداء
        perf_summary = self.performance_tracker.get_performance_summary()
        if perf_summary.get('overall_success_rate', 1.0) < 0.95:
            recommendations.append("معدل النجاح منخفض، راجع الأخطاء")

        if not recommendations:
            recommendations.append("النظام يعمل بشكل ممتاز")

        return recommendations
