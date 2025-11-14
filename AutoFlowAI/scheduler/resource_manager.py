"""
إدارة الموارد
"""
import threading
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ResourceAllocation:
    allocation_id: str
    resource_type: str # cpu, memory, disk, network
    requested_amount: float
    allocated_amount: float
    allocated_at: float
    released_at: Optional[float] = None
    status: str = "allocated" # allocated, released

class ResourceManager:
    """إدارة موارد النظام"""

    def __init__(self):
        self.total_cpu = 100.0 # 100% CPU متاح
        self.total_memory = 100.0 # 100% ذاكرة متاحة
        self.total_disk = 100.0 # 100% قرص متاح
        self.total_network = 1000.0 # 1000 Mbps متاح

        self.used_resources = {
            'cpu': 0.0,
            'memory': 0.0,
            'disk': 0.0,
            'network': 0.0
        }

        self.allocations: Dict[str, ResourceAllocation] = {}
        self.lock = threading.Lock()

    def allocate_resources(self, requested_resources: Dict[str, float],
                             allocation_id: str = None) -> Dict[str, Any]:
        """تخصيص الموارد"""
        if allocation_id is None:
            allocation_id = f"alloc_{int(time.time())}_{threading.current_thread().ident}"

        with self.lock:
            # التحقق من توفر الموارد
            if not self._check_resource_availability(requested_resources):
                return {
                    'success': False,
                    'error': 'موارد غير كافية',
                    'available_resources': self.used_resources.copy()
                }

            # تخصيص الموارد
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                resource_type='mixed',
                requested_amount=sum(requested_resources.values()),
                allocated_amount=sum(requested_resources.values()),
                allocated_at=time.time()
            )

            # تحديث الموارد المستخدمة
            for resource_type, amount in requested_resources.items():
                if resource_type in self.used_resources:
                    self.used_resources[resource_type] += amount

            self.allocations[allocation_id] = allocation

            return {
                'success': True,
                'allocation_id': allocation_id,
                'allocated_resources': requested_resources,
                'remaining_resources': {
                    'cpu': self.total_cpu - self.used_resources['cpu'],
                    'memory': self.total_memory - self.used_resources['memory'],
                    'disk': self.total_disk - self.used_resources['disk'],
                    'network': self.total_network - self.used_resources['network']
                }
            }

    def release_resources(self, allocation_id: str) -> Dict[str, Any]:
        """تحرير الموارد"""
        with self.lock:
            allocation = self.allocations.get(allocation_id)
            if not allocation:
                return {'success': False, 'error': 'allocation غير موجود'}

            if allocation.status == 'released':
                return {'success': False, 'error': 'تم تحرير الموارد مسبقاً'}

            # تقدير الموارد التي تم تخصيصها (محاكاة)
            estimated_resources = {
                'cpu': allocation.allocated_amount * 0.3,
                'memory': allocation.allocated_amount * 0.4,
                'disk': allocation.allocated_amount * 0.2,
                'network': allocation.allocated_amount * 0.1
            }

            # تحرير الموارد
            for resource_type, amount in estimated_resources.items():
                if resource_type in self.used_resources:
                    self.used_resources[resource_type] = max(0,
                                                               self.used_resources[resource_type] - amount)

            allocation.status = 'released'
            allocation.released_at = time.time()

            return {
                'success': True,
                'released_resources': estimated_resources,
                'remaining_resources': self.used_resources.copy()
            }

    def _check_resource_availability(self, requested: Dict[str, float]) -> bool:
        """التحقق من توفر الموارد"""
        limits = {
            'cpu': self.total_cpu,
            'memory': self.total_memory,
            'disk': self.total_disk,
            'network': self.total_network
        }

        for resource_type, amount in requested.items():
            if resource_type in limits:
                if amount > (limits[resource_type] - self.used_resources[resource_type]):
                    return False
        return True

    def get_resource_status(self) -> Dict[str, Any]:
        """الحصول على حالة الموارد"""
        with self.lock:
            return {
                'total_resources': {
                    'cpu': self.total_cpu,
                    'memory': self.total_memory,
                    'disk': self.total_disk,
                    'network': self.total_network
                },
                'used_resources': self.used_resources.copy(),
                'available_resources': {
                    'cpu': self.total_cpu - self.used_resources['cpu'],
                    'memory': self.total_memory - self.used_resources['memory'],
                    'disk': self.total_disk - self.used_resources['disk'],
                    'network': self.total_network - self.used_resources['network']
                },
                'usage_percentages': {
                    'cpu': (self.used_resources['cpu'] / self.total_cpu) * 100,
                    'memory': (self.used_resources['memory'] / self.total_memory) * 100,
                    'disk': (self.used_resources['disk'] / self.total_disk) * 100,
                    'network': (self.used_resources['network'] / self.total_network) * 100
                },
                'active_allocations': len([a for a in self.allocations.values() if a.status == 'allocated'])
            }
