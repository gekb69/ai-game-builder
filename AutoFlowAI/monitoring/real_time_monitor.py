"""
المراقبة المباشرة
"""
import time
import psutil
from typing import Dict, Any, List
from collections import deque
from dataclasses import dataclass

@dataclass
class SystemMetric:
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int

class RealTimeMonitor:
    def __init__(self, max_history: int = 1000):
        self.start_time = time.time()
        self.events = deque(maxlen=max_history)
        self.metrics_history = deque(maxlen=max_history)
        self.alerts = []

    def record_event(self, name: str, payload: Dict[str, Any]):
        self.events.append({
            'ts': time.time(),
            'name': name,
            'payload': payload
        })

    def collect_metrics(self) -> SystemMetric:
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            network = psutil.net_io_counters()
            process_count = len(psutil.pids())

            metric = SystemMetric(
                timestamp=time.time(),
                cpu_percent=cpu,
                memory_percent=memory,
                disk_percent=disk,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                process_count=process_count
            )

            self.metrics_history.append(metric)
            return metric

        except Exception as e:
            # في حالة عدم توفر psutil
            return SystemMetric(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_io={'bytes_sent': 0, 'bytes_recv': 0},
                process_count=0
            )

    def get_current_metrics(self) -> Dict[str, Any]:
        metric = self.collect_metrics()
        return {
            'uptime_sec': time.time() - self.start_time,
            'cpu_percent': metric.cpu_percent,
            'memory_percent': metric.memory_percent,
            'disk_percent': metric.disk_percent,
            'process_count': metric.process_count,
            'network_io': metric.network_io,
            'recent_events': len(self.events),
            'metrics_history_count': len(self.metrics_history)
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        current = self.get_current_metrics()
        # حساب المتوسطات من آخر 10 مقاييس
        recent_metrics = list(self.metrics_history)[-10:]

        if recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = avg_memory = 0.0

        return {
            **current,
            'average_cpu_10min': avg_cpu,
            'average_memory_10min': avg_memory,
            'system_status': self._determine_system_status(current),
            'recent_alerts': self.alerts[-5:] # آخر 5 تنبيهات
        }

    def _determine_system_status(self, metrics: Dict[str, Any]) -> str:
        cpu = metrics.get('cpu_percent', 0)
        memory = metrics.get('memory_percent', 0)

        if cpu > 90 or memory > 90:
            return 'CRITICAL'
        elif cpu > 70 or memory > 70:
            return 'WARNING'
        else:
            return 'HEALTHY'

    def add_alert(self, level: str, message: str):
        alert = {
            'timestamp': time.time(),
            'level': level,
            'message': message
        }
        self.alerts.append(alert)
        self.record_event('alert', alert)
