"""
AutoFlowAI - النظام الأساسي المتقدم
"""
import logging
import time
from typing import Dict, List, Any, Optional
from .types import Task, AgentInfo

logger = logging.getLogger("AutoFlowAI")

class CoreAIController:
    def __init__(self, autoflow):
        self.autoflow = autoflow
        self.agents: Dict[str, AgentInfo] = {}
        self.performance_tracker = PerformanceTracker()

    def register_agent(self, agent: AgentInfo):
        self.agents[agent.id] = agent
        logger.info(f"تم تسجيل Agent: {agent.id}")

    def execute_task(self, agent_id: str, task: Task) -> Dict[str, Any]:
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent غير موجود: {agent_id}")
        agent.status = "RUNNING"
        start = time.time()
        try:
            # محاكاة عمل
            time.sleep(min(0.3, task.estimated_duration or 0.3))
            result = {'agent_id': agent_id, 'task_id': task.id, 'status': 'SUCCESS', 'timestamp': time.time()}
            agent.tasks_completed += 1
            agent.success_count += 1
            agent.status = "IDLE"
            agent.last_activity = time.time()
            self.performance_tracker.record_success(agent_id, time.time() - start)
            return result
        except Exception as e:
            agent.failure_count += 1
            agent.status = "IDLE"
            agent.last_activity = time.time()
            self.performance_tracker.record_failure(agent_id, time.time() - start)
            raise e

    def agent_health(self) -> Dict[str, Any]:
        out = {}
        for k, v in self.agents.items():
            success_rate = v.success_count / max(v.success_count + v.failure_count, 1)
            out[k] = {
                'status': v.status,
                'tasks_completed': v.tasks_completed,
                'success_rate': success_rate,
                'last_activity': v.last_activity
            }
        return out

class PerformanceTracker:
    def __init__(self):
        self.stats = {}

    def record_success(self, agent_id: str, duration: float):
        if agent_id not in self.stats:
            self.stats[agent_id] = {'success': 0, 'failure': 0, 'times': []}
        self.stats[agent_id]['success'] += 1
        self.stats[agent_id]['times'].append(duration)

    def record_failure(self, agent_id: str, duration: float):
        if agent_id not in self.stats:
            self.stats[agent_id] = {'success': 0, 'failure': 0, 'times': []}
        self.stats[agent_id]['failure'] += 1
        self.stats[agent_id]['times'].append(duration)

class RealTimeMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.events = []

    def record_event(self, name: str, payload: Dict[str, Any]):
        self.events.append({'ts': time.time(), 'name': name, 'payload': payload})

    def get_dashboard(self) -> Dict[str, Any]:
        return {
            'uptime_sec': time.time() - self.start_time,
            'system_status': 'OK',
            'security_level': 'HIGH',
            'recent_events': len(self.events)
        }

class AdaptiveLearningEngine:
    def __init__(self):
        self.learned = {}

    def ingest_feedback(self, feature_key: str, feedback: float):
        if feature_key not in self.learned:
            self.learned[feature_key] = 0.5
        self.learned[feature_key] = 0.9 * self.learned[feature_key] + 0.1 * feedback

    def recommend(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'preferred_strategy': 'balanced',
            'confidence': self.learned.get('strategy_confidence', 0.5),
            'notes': 'تعلم تكيفي مفعّل'
        }

class AdvancedCommunicationLayer:
    def __init__(self):
        self.handlers = {}

    def register_handler(self, channel: str, handler):
        self.handlers[channel] = handler

    def send(self, channel: str, message: Dict[str, Any]):
        handler = self.handlers.get(channel)
        if handler:
            handler(message)
        else:
            logger.info(f"Comunicating [{channel}]: {message}")

class PerformanceOptimizer:
    def __init__(self):
        self.metrics = {}

    def optimize(self, context: Dict[str, Any]):
        self.metrics['optimizations'] = self.metrics.get('optimizations', 0) + 1
        return {'optimization_id': 'opt_' + str(int(time.time())), 'applied': True}

class MultiModalAIEngine:
    def __init__(self):
        self.models = {}

    def register_model(self, name: str, model: Any):
        self.models[name] = model

    def infer(self, modality: str, data: Any) -> Dict[str, Any]:
        return {'modality': modality, 'inference': 'ok', 'ts': time.time()}

class IntelligentDecisionMaker:
    def __init__(self, autoflow):
        self.autoflow = autoflow

    def decide(self, options: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        best = max(options, key=lambda o: o.get('score', 0) - o.get('risk', 0))
        best['decision'] = 'APPROVE' if best.get('score', 0) > 0.6 else 'REJECT'
        return best

class ResourceManager:
    def allocate(self, requested_cpu: float, requested_mem: float) -> bool:
        return requested_cpu <= 80.0 and requested_mem <= 80.0

class AdvancedAutoFlowAI:
    """
    AutoFlowAI المتقدم - نسخة إنتاج
    """
    def __init__(self, config='production'):
        self.version = "2.0.0"
        self.mode = config

        # المكونات الأساسية
        self.core = CoreAIController(self)
        self.monitoring = RealTimeMonitor()
        self.learning = AdaptiveLearningEngine()

        # أدوات متقدمة
        self.communication = AdvancedCommunicationLayer()
        self.performance = PerformanceOptimizer()

        # محرك الذكاء الاصطناعي
        self.ai_engine = MultiModalAIEngine()
        self.decision_engine = IntelligentDecisionMaker(self)

        # إدارة الموارد
        self.resource_manager = ResourceManager()

        logger.info(f"🧠 AutoFlowAI v{self.version} ({self.mode}) - Ready!")

        # تحميل الـ agent المحلي
        self._load_local_agent()

    def register_agent(self, agent: AgentInfo):
        self.core.register_agent(agent)

    def shutdown(self):
        logger.info("AutoFlowAI shutdown completed.")

    def _load_local_agent(self):
        """
        تحميل الـ agent المحلي المحدد في الإعدادات.
        """
        from utils.config import config
        from local_models.deepseek_adapter import DeepSeekAgent
        from local_models.glm_adapter import GLMAgent
        from local_models.kimi_adapter import KimiAgent
        from local_models.minimax_adapter import MinimaxAgent

        model_map = {
            "deepseek": DeepSeekAgent,
            "glm": GLMAgent,
            "kimi": KimiAgent,
            "minimax": MinimaxAgent,
        }

        active_model_key = config.local_models.active_model
        if active_model_key in model_map:
            model_config = config.local_models.models[active_model_key]
            agent_class = model_map[active_model_key]

            agent = agent_class(
                model_id=model_config["model_id"],
                quantization_config=model_config.get("quantization")
            )

            # Register the local agent
            agent_info = AgentInfo(
                id=active_model_key,
                name=f"Local Agent: {active_model_key}",
                capabilities=["local_inference", "text_generation"]
            )
            self.register_agent(agent_info)

            # Make the agent instance accessible
            setattr(self, f"{active_model_key}_agent", agent)
            print(f"✅ تم تحميل وتسجيل الـ agent المحلي: {active_model_key}")
