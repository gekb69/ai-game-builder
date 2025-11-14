"""
تتبع الأداء
"""
import time
from typing import Dict, Any, List
from collections import defaultdict, deque
from dataclasses import dataclass, field

@dataclass
class PerformanceMetric:
    timestamp: float
    component: str
    operation: str
    duration: float
    status: str # success, failed
    metadata: Dict[str, Any] = field(default_factory=dict)

class PerformanceTracker:
    def __init__(self, max_history: int = 10000):
        self.metrics = deque(maxlen=max_history)
        self.component_stats = defaultdict(lambda: {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_duration': 0.0,
            'avg_duration': 0.0
        })

    def record_operation(self, component: str, operation: str, duration: float,
                         status: str, metadata: Dict[str, Any] = None):
        metric = PerformanceMetric(
            timestamp=time.time(),
            component=component,
            operation=operation,
            duration=duration,
            status=status,
            metadata=metadata or {}
        )

        self.metrics.append(metric)
        self._update_component_stats(component, operation, duration, status)

    def _update_component_stats(self, component: str, operation: str, duration: float, status: str):
        stats = self.component_stats[component]
        stats['total_operations'] += 1
        stats['total_duration'] += duration

        if status == 'success':
            stats['successful_operations'] += 1
        else:
            stats['failed_operations'] += 1

        stats['avg_duration'] = stats['total_duration'] / stats['total_operations']

    def get_component_performance(self, component: str) -> Dict[str, Any]:
        stats = self.component_stats[component]
        total = stats['total_operations']
        success_rate = stats['successful_operations'] / max(total, 1)

        return {
            'component': component,
            'total_operations': total,
            'successful_operations': stats['successful_operations'],
            'failed_operations': stats['failed_operations'],
            'success_rate': success_rate,
            'total_duration': stats['total_duration'],
            'average_duration': stats['avg_duration']
        }

    def get_all_components_performance(self) -> Dict[str, Any]:
        return {comp: self.get_component_performance(comp)
                for comp in self.component_stats.keys()}

    def get_recent_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [metric.__dict__ for metric in list(self.metrics)[-limit:]]

    def get_performance_summary(self) -> Dict[str, Any]:
        all_stats = self.get_all_components_performance()
        total_ops = sum(stats['total_operations'] for stats in all_stats.values())
        total_success = sum(stats['successful_operations'] for stats in all_stats.values())
        overall_success_rate = total_success / max(total_ops, 1)

        return {
            'total_operations': total_ops,
            'overall_success_rate': overall_success_rate,
            'components_count': len(all_stats),
            'components': all_stats
        }
