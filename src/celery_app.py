"""
Celery Worker for Distributed Task Processing
"""
from celery import Celery
from celery.signals import worker_process_init
import os
import asyncio
from src.config import get_config

system = None

@worker_process_init.connect
def init_worker(**kwargs):
    """Initialize the SelfAwareAISystem once per worker process."""
    global system
    from src.main import SelfAwareAISystem
    print("Initializing SelfAwareAISystem for Celery worker...")
    system = SelfAwareAISystem()
    asyncio.run(system.initialize_system())
    print("SelfAwareAISystem initialized.")


config = get_config()

# Initialize Celery app
celery_app = Celery(
    "selfaware_ai",
    broker=config.orchestration.celery.broker_url,
    backend=config.orchestration.celery.backend_url
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=config.orchestration.celery.task_timeout,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Tasks
@celery_app.task(bind=True, name="process_ai_task")
def process_ai_task(self, task_data: dict):
    """Process AI task asynchronously"""
    if system is None:
        raise RuntimeError("System not initialized")

    task_id = task_data.get("id", "unknown_task")
    agent_name = task_data.get("agent", "autogpt")
    prompt = task_data.get("prompt")

    if not prompt:
        return {"status": "error", "message": "No prompt provided"}

    result = asyncio.run(system.agents_manager.execute_with_agent(agent_name, prompt))

    return {"status": "processed", "task_id": task_id, "result": result}

@celery_app.task(name="run_consciousness_benchmark")
def run_consciousness_benchmark():
    """Run consciousness benchmark"""
    if system is None:
        raise RuntimeError("System not initialized")

    result = asyncio.run(system.benchmark_consciousness())
    return result

@celery_app.task(name="backup_system_state")
def backup_system_state():
    """Backup system state"""
    if system is None:
        raise RuntimeError("System not initialized")

    result = asyncio.run(system.security_system.backup_critical_data())

    return {"status": "backup_complete", "result": result}
