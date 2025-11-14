"""
نظام الجدولة المتقدم للمهام
"""
import asyncio
import time
import threading
import queue
import uuid
from typing import Dict, List, Any, Callable, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

class TaskType(Enum):
    IMMEDIATE = "immediate" # فوري
    SHORT_TERM = "short_term" # قصير المدى (دقائق)
    MEDIUM_TERM = "medium_term" # متوسط المدى (ساعات)
    LONG_TERM = "long_term" # طويل المدى (أيام)
    PERIODIC = "periodic" # دوري

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class AdvancedTask:
    id: str
    name: str
    description: str
    task_type: TaskType
    priority: TaskPriority = TaskPriority.MEDIUM
    agent_id: str = ""
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable] = None
    created_at: float = field(default_factory=time.time)
    scheduled_at: Optional[float] = None
    estimated_duration: Optional[float] = None
    status: str = "PENDING"
    result: Any = None
    error: Optional[str] = None
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

class TimeBasedTaskScheduler:
    """جدولة مهام بناءً على الفترات الزمنية"""

    def __init__(self):
        self.tasks: Dict[str, AdvancedTask] = {}
        self.task_queues = {
            TaskType.IMMEDIATE: queue.PriorityQueue(),
            TaskType.SHORT_TERM: queue.PriorityQueue(),
            TaskType.MEDIUM_TERM: queue.PriorityQueue(),
            TaskType.LONG_TERM: queue.PriorityQueue(),
            TaskType.PERIODIC: queue.PriorityQueue()
        }
        self.periodic_tasks = {}
        self.running = False
        self.workers = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.task_handlers = {
            TaskType.IMMEDIATE: self._handle_immediate_task,
            TaskType.SHORT_TERM: self._handle_short_term_task,
            TaskType.MEDIUM_TERM: self._handle_medium_term_task,
            TaskType.LONG_TERM: self._handle_long_term_task,
            TaskType.PERIODIC: self._handle_periodic_task
        }

    def add_task(self, task: AdvancedTask):
        """إضافة مهمة جديدة"""
        self.tasks[task.id] = task

        # حساب أولوية المعالجة
        queue_priority = task.priority.value

        # إضافة للطابور
        self.task_queues[task.task_type].put((queue_priority, task.created_at, task.id))

        # جدولة المهمة الدورية إذا كانت من نوع PERIODIC
        if task.task_type == TaskType.PERIODIC:
            self._schedule_periodic_task(task)

        print(f"✅ تم إضافة مهمة: {task.name} ({task.task_type.value})")

    def _schedule_periodic_task(self, task: AdvancedTask):
        """جدولة مهمة دورية"""
        interval = task.parameters.get('interval_seconds', 3600) # افتراضي: ساعة

        def periodic_executor():
            while self.running:
                try:
                    # إعادة إنشاء المهمة الجديدة لكل دورة
                    new_task = AdvancedTask(
                        id=str(uuid.uuid4())[:8],
                        name=task.name,
                        description=task.description,
                        task_type=task.task_type,
                        priority=task.priority,
                        agent_id=task.agent_id,
                        parameters=task.parameters.copy(),
                        callback=task.callback
                    )

                    start_time = time.time()
                    self._execute_task(new_task)
                    execution_time = time.time() - start_time

                    # تسجيل النتائج
                    new_task.execution_log.append({
                        'timestamp': start_time,
                        'status': 'completed',
                        'execution_time': execution_time
                    })

                    # انتظار الفترة التالية
                    time.sleep(interval)

                except Exception as e:
                    print(f"خطأ في تنفيذ المهمة الدورية {task.name}: {e}")
                    time.sleep(interval) # الاستمرار حتى لو فشلت

        # تشغيل في thread منفصل
        thread = threading.Thread(target=periodic_executor, daemon=True)
        thread.start()

    def start_scheduler(self):
        """بدء المجدول"""
        self.running = True

        # بدء workers لكل نوع مهمة
        for task_type in TaskType:
            worker_count = self._get_worker_count(task_type)
            for i in range(worker_count):
                worker_name = f"{task_type.value}_worker_{i}"
                worker = threading.Thread(
                    target=self._worker_loop,
                    args=(task_type, worker_name),
                    daemon=True
                )
                worker.start()
                self.workers[worker_name] = worker

        print(f"🚀 تم بدء المجدول مع {len(self.workers)} workers")

    def stop_scheduler(self):
        """إيقاف المجدول"""
        self.running = False
        # إيقاف جميع Workers
        for worker in self.workers.values():
            if worker.is_alive():
                worker.join(timeout=2)
        print("⏹️ تم إيقاف المجدول")

    def _get_worker_count(self, task_type: TaskType) -> int:
        """تحديد عدد Workers بناءً على نوع المهمة"""
        counts = {
            TaskType.IMMEDIATE: 3, # فوري - 3 workers
            TaskType.SHORT_TERM: 2, # قصير - 2 workers
            TaskType.MEDIUM_TERM: 2, # متوسط - 2 workers
            TaskType.LONG_TERM: 1, # طويل - 1 worker
            TaskType.PERIODIC: 1 # دوري - 1 worker
        }
        return counts.get(task_type, 1)

    def _worker_loop(self, task_type: TaskType, worker_name: str):
        """حلقة عمل الـ Worker"""
        print(f"🔧 بدء Worker: {worker_name}")

        while self.running:
            try:
                # الحصول على مهمة من الطابور
                priority, created_at, task_id = self.task_queues[task_type].get(timeout=1)
                task = self.tasks.get(task_id)

                if task and task.status == "PENDING":
                    # تنفيذ المهمة
                    self._execute_task(task)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ خطأ في {worker_name}: {e}")

    def _execute_task(self, task: AdvancedTask):
        """تنفيذ مهمة"""
        task.status = "RUNNING"
        start_time = time.time()

        try:
            # اختيار معالج المهمة المناسب
            handler = self.task_handlers.get(task.task_type, self._handle_unknown_task)
            result = handler(task)

            task.result = result
            task.status = "COMPLETED"

            # استدعاء callback إذا وُجد
            if task.callback:
                task.callback(task)

        except Exception as e:
            task.error = str(e)
            task.status = "FAILED"
            task.retry_count += 1

            # إعادة المحاولة إذا لم تتجاوز الحد الأقصى
            if task.retry_count < task.max_retries:
                print(f"🔄 إعادة محاولة المهمة {task.name} ({task.retry_count}/{task.max_retries})")
                time.sleep(2 ** task.retry_count) # تأخير متزايد
                task.status = "PENDING"
                # إعادة إضافة للطابور
                self.task_queues[task.task_type].put((task.priority.value, time.time(), task.id))

        finally:
            task.execution_log.append({
                'timestamp': start_time,
                'duration': time.time() - start_time,
                'status': task.status,
                'retry_count': task.retry_count
            })

    def _handle_immediate_task(self, task: AdvancedTask) -> Dict[str, Any]:
        """معالجة مهمة فورية"""
        # محاكاة تنفيذ سريع
        time.sleep(0.1)
        return {
            'task_id': task.id,
            'task_type': task.task_type.value,
            'result': f'تم تنفيذ {task.name} فوراً',
            'execution_time': time.time(),
            'priority': task.priority.value
        }

    def _handle_short_term_task(self, task: AdvancedTask) -> Dict[str, Any]:
        """معالجة مهمة قصيرة المدى"""
        # محاكاة تنفيذ قصير
        time.sleep(0.5)
        return {
            'task_id': task.id,
            'task_type': task.task_type.value,
            'result': f'تم تنفيذ {task.name} في المدى القصير',
            'execution_time': time.time(),
            'estimated_duration': '30 seconds'
        }

    def _handle_medium_term_task(self, task: AdvancedTask) -> Dict[str, Any]:
        """معالجة مهمة متوسطة المدى"""
        # محاكاة تنفيذ متوسط
        time.sleep(2.0)
        return {
            'task_id': task.id,
            'task_type': task.task_type.value,
            'result': f'تم تنفيذ {task.name} في المدى المتوسط',
            'execution_time': time.time(),
            'estimated_duration': '2 minutes'
        }

    def _handle_long_term_task(self, task: AdvancedTask) -> Dict[str, Any]:
        """معالجة مهمة طويلة المدى"""
        # محاكاة تنفيذ طويل
        time.sleep(5.0)
        return {
            'task_id': task.id,
            'task_type': task.task_type.value,
            'result': f'تم تنفيذ {task.name} في المدى الطويل',
            'execution_time': time.time(),
            'estimated_duration': '5 minutes'
        }

    def _handle_periodic_task(self, task: AdvancedTask) -> Dict[str, Any]:
        """معالجة مهمة دورية"""
        return {
            'task_id': task.id,
            'task_type': task.task_type.value,
            'result': f'تم تنفيذ {task.name} بشكل دوري',
            'execution_time': time.time(),
            'is_periodic': True
        }

    def _handle_unknown_task(self, task: AdvancedTask) -> Dict[str, Any]:
        """معالجة مهمة غير معروفة"""
        raise ValueError(f"نوع مهمة غير مدعوم: {task.task_type}")

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """الحصول على حالة مهمة"""
        task = self.tasks.get(task_id)
        if task:
            return {
                'task_id': task_id,
                'name': task.name,
                'status': task.status,
                'type': task.task_type.value,
                'priority': task.priority.value,
                'created_at': task.created_at,
                'retry_count': task.retry_count,
                'execution_log': task.execution_log[-5:] # آخر 5 عمليات
            }
        return {'error': 'Task not found'}

    def get_scheduler_stats(self) -> Dict[str, Any]:
        """إحصائيات المجدول"""
        stats = {}
        for task_type in TaskType:
            try:
                stats[task_type.value] = self.task_queues[task_type].qsize()
            except:
                stats[task_type.value] = 0

        running_tasks = sum(1 for task in self.tasks.values() if task.status == "RUNNING")
        completed_tasks = sum(1 for task in self.tasks.values() if task.status == "COMPLETED")
        failed_tasks = sum(1 for task in self.tasks.values() if task.status == "FAILED")

        return {
            'queue_sizes': stats,
            'total_tasks': len(self.tasks),
            'running_tasks': running_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'active_workers': len([w for w in self.workers.values() if w.is_alive()]),
            'scheduler_running': self.running
        }
