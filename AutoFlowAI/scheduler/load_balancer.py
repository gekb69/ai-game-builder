"""
توزيع الأحمال
"""
import random
import threading
from typing import List, Dict, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass

@dataclass
class LoadMetric:
    timestamp: float
    cpu_usage: float
    memory_usage: float
    response_time: float
    active_connections: int
    error_rate: float

class LoadBalancer:
    """توزيع الأحمال الذكي"""

    def __init__(self):
        self.servers = []
        self.load_metrics = defaultdict(lambda: deque(maxlen=100))
        self.current_weights = {}
        self.lock = threading.Lock()

    def add_server(self, server_id: str, weight: float = 1.0):
        """إضافة خادم"""
        with self.lock:
            self.servers.append(server_id)
            self.current_weights[server_id] = weight
            print(f"✅ تم إضافة خادم {server_id} بوزن {weight}")

    def remove_server(self, server_id: str):
        """إزالة خادم"""
        with self.lock:
            if server_id in self.servers:
                self.servers.remove(server_id)
                self.current_weights.pop(server_id, None)
                print(f"🗑️ تم إزالة خادم {server_id}")

    def select_server(self, algorithm: str = "weighted_round_robin") -> Optional[str]:
        """اختيار خادم بناءً على الخوارزمية"""
        if not self.servers:
            return None

        with self.lock:
            if algorithm == "weighted_round_robin":
                return self._weighted_round_robin()
            elif algorithm == "least_connections":
                return self._least_connections()
            elif algorithm == "response_time":
                return self._best_response_time()
            elif algorithm == "resource_based":
                return self._resource_based_selection()
            else:
                return random.choice(self.servers)

    def _weighted_round_robin(self) -> str:
        """خوارزمية Round Robin الموزونة"""
        # اختيار عشوائي موزون
        weights = [self.current_weights.get(server, 1.0) for server in self.servers]
        total_weight = sum(weights)

        if total_weight == 0:
            return random.choice(self.servers)

        random_weight = random.uniform(0, total_weight)
        current_sum = 0

        for i, server in enumerate(self.servers):
            current_sum += weights[i]
            if random_weight <= current_sum:
                return server

        return self.servers[-1] # fallback

    def _least_connections(self) -> str:
        """اختيار الخادم بأقل اتصالات"""
        min_connections = float('inf')
        selected_server = self.servers[0]

        for server in self.servers:
            metrics = self.get_server_metrics(server)
            connections = metrics.get('active_connections', 0)
            if connections < min_connections:
                min_connections = connections
                selected_server = server

        return selected_server

    def _best_response_time(self) -> str:
        """اختيار الخادم بأفضل وقت استجابة"""
        min_response_time = float('inf')
        selected_server = self.servers[0]

        for server in self.servers:
            metrics = self.get_server_metrics(server)
            response_time = metrics.get('avg_response_time', float('inf'))
            if response_time < min_response_time:
                min_response_time = response_time
                selected_server = server

        return selected_server

    def _resource_based_selection(self) -> str:
        """اختيار الخادم بناءً على الموارد"""
        max_available = -1
        selected_server = self.servers[0]

        for server in self.servers:
            metrics = self.get_server_metrics(server)
            # حساب الموارد المتاحة (أقل استخدام = أكثر تخصص)
            cpu_available = 100 - metrics.get('cpu_usage', 0)
            memory_available = 100 - metrics.get('memory_usage', 0)
            available_score = (cpu_available + memory_available) / 2

            if available_score > max_available:
                max_available = available_score
                selected_server = server

        return selected_server

    def update_server_metrics(self, server_id: str, metrics: Dict[str, Any]):
        """تحديث مقاييس الخادم"""
        load_metric = LoadMetric(
            timestamp=metrics.get('timestamp'),
            cpu_usage=metrics.get('cpu_usage', 0),
            memory_usage=metrics.get('memory_usage', 0),
            response_time=metrics.get('response_time', 0),
            active_connections=metrics.get('active_connections', 0),
            error_rate=metrics.get('error_rate', 0)
        )

        self.load_metrics[server_id].append(load_metric)

    def get_server_metrics(self, server_id: str) -> Dict[str, Any]:
        """الحصول على مقاييس الخادم"""
        metrics_list = list(self.load_metrics[server_id])

        if not metrics_list:
            return {
                'cpu_usage': 0,
                'memory_usage': 0,
                'avg_response_time': 0,
                'active_connections': 0,
                'error_rate': 0
            }

        # حساب المتوسطات من آخر 10 مقاييس
        recent_metrics = metrics_list[-10:]

        return {
            'cpu_usage': sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
            'memory_usage': sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            'avg_response_time': sum(m.response_time for m in recent_metrics) / len(recent_metrics),
            'active_connections': sum(m.active_connections for m in recent_metrics) / len(recent_metrics),
            'error_rate': sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
        }

    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """إحصائيات الموزع"""
        with self.lock:
            server_stats = {}
            for server in self.servers:
                server_stats[server] = self.get_server_metrics(server)

            total_connections = sum(stats.get('active_connections', 0) for stats in server_stats.values())
            avg_response_time = sum(stats.get('avg_response_time', 0) for stats in server_stats.values()) / max(len(server_stats), 1)

            return {
                'total_servers': len(self.servers),
                'server_list': self.servers.copy(),
                'server_weights': self.current_weights.copy(),
                'server_stats': server_stats,
                'total_active_connections': total_connections,
                'average_response_time': avg_response_time,
                'health_status': self._calculate_health_status(server_stats)
            }

    def _calculate_health_status(self, server_stats: Dict[str, Any]) -> str:
        """حساب حالة الصحة العامة"""
        if not server_stats:
            return 'NO_SERVERS'

        unhealthy_servers = 0
        for stats in server_stats.values():
            if stats.get('error_rate', 0) > 0.1 or stats.get('avg_response_time', 0) > 5000:
                unhealthy_servers += 1

        if unhealthy_servers == len(server_stats):
            return 'CRITICAL'
        elif unhealthy_servers > 0:
            return 'WARNING'
        else:
            return 'HEALTHY'
