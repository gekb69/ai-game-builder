"""
System Configuration - All 100 Features
إعدادات وتكوين النظام الممتد
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import json
import os

# --- Enums ---
class SystemMode(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"
    EMERGENCY = "emergency"
    SLEEP = "sleep"

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# --- Nested Config Dataclasses ---

@dataclass
class ExistentialConfig:
    self_recognition_threshold: float = 0.8

@dataclass
class AmbiguityConfig:
    uncertainty_toleration: float = 0.6

@dataclass
class ConsciousnessConfig:
    existential: ExistentialConfig = field(default_factory=ExistentialConfig)
    ambiguity: AmbiguityConfig = field(default_factory=AmbiguityConfig)

@dataclass
class DefragmentationConfig:
    cleanup_expired_threshold: int = 2592000  # 30 days in seconds

@dataclass
class MemoryConfig:
    defragmentation: DefragmentationConfig = field(default_factory=DefragmentationConfig)

@dataclass
class SpontaneousEvolutionConfig:
    idea_generation_rate: int = 5
    creativity_threshold: float = 0.8

@dataclass
class MultiObjectiveEvolutionConfig:
    objectives: List[str] = field(default_factory=lambda: ["efficiency", "robustness", "creativity"])

@dataclass
class AgentCloningConfig:
    mutation_rate: float = 0.1

@dataclass
class SelfAuditConfig:
    self_repair_enabled: bool = True

@dataclass
class EthicalAnalysisConfig:
    stop_on_violation: bool = True

@dataclass
class SecurityFeatureConfig:
    self_audit: SelfAuditConfig = field(default_factory=SelfAuditConfig)
    ethical_analysis: EthicalAnalysisConfig = field(default_factory=EthicalAnalysisConfig)

@dataclass
class FaultPredictionConfig:
    early_warning_threshold: float = 0.75

# --- New AI Tool Configurations ---

@dataclass
class LangChainConfig:
    """Configuration for LangChain integration"""
    enabled: bool = True
    model_provider: str = "openai"
    default_model: str = "gpt-4"
    max_tokens: int = 4096
    temperature: float = 0.7
    vector_store: str = "weaviate"

@dataclass
class LlamaIndexConfig:
    """Configuration for LlamaIndex"""
    enabled: bool = True
    index_type: str = "vector"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 512

@dataclass
class WeaviateNestedConfig:
    enabled: bool = True
    url: str = "http://weaviate:8080"
    api_key: str = ""

@dataclass
class QdrantNestedConfig:
    enabled: bool = True
    url: str = "http://qdrant:6333"
    api_key: str = ""

@dataclass
class FaissNestedConfig:
    enabled: bool = True
    index_path: str = "data/faiss_index.bin"

@dataclass
class VectorDBConfig:
    """Vector database configurations"""
    weaviate: WeaviateNestedConfig = field(default_factory=WeaviateNestedConfig)
    qdrant: QdrantNestedConfig = field(default_factory=QdrantNestedConfig)
    faiss: FaissNestedConfig = field(default_factory=FaissNestedConfig)

@dataclass
class OpenAINestedConfig:
    enabled: bool = True
    api_key: str = ""
    model: str = "gpt-4"

@dataclass
class AnthropicNestedConfig:
    enabled: bool = True
    api_key: str = ""
    model: str = "claude-3-sonnet-20240229"

@dataclass
class GoogleNestedConfig:
    enabled: bool = True
    api_key: str = ""
    model: str = "gemini-pro"

@dataclass
class HuggingFaceNestedConfig:
    enabled: bool = True
    api_key: str = ""
    model: str = "meta-llama/Llama-2-7b-chat-hf"

@dataclass
class OllamaNestedConfig:
    enabled: bool = True
    url: str = "http://localhost:11434"
    model: str = "llama2"

@dataclass
class KimiNestedConfig:
    enabled: bool = False
    api_key: str = ""

@dataclass
class MiniMaxNestedConfig:
    enabled: bool = False
    api_key: str = ""
    group_id: str = ""

@dataclass
class LLMProvidersConfig:
    """Multi-LLM provider configurations"""
    openai: OpenAINestedConfig = field(default_factory=OpenAINestedConfig)
    anthropic: AnthropicNestedConfig = field(default_factory=AnthropicNestedConfig)
    google: GoogleNestedConfig = field(default_factory=GoogleNestedConfig)
    huggingface: HuggingFaceNestedConfig = field(default_factory=HuggingFaceNestedConfig)
    ollama: OllamaNestedConfig = field(default_factory=OllamaNestedConfig)
    kimi: KimiNestedConfig = field(default_factory=KimiNestedConfig)
    minimax: MiniMaxNestedConfig = field(default_factory=MiniMaxNestedConfig)

@dataclass
class PrometheusNestedConfig:
    enabled: bool = True
    url: str = "http://prometheus:9090"

@dataclass
class GrafanaNestedConfig:
    enabled: bool = True
    url: str = "http://localhost:3000"
    admin_user: str = "admin"
    admin_password: str = "admin"

@dataclass
class SentryNestedConfig:
    enabled: bool = True
    dsn: str = ""
    traces_sample_rate: float = 1.0

@dataclass
class OpenTelemetryNestedConfig:
    enabled: bool = True
    service_name: str = "SelfAwareAI-v100"
    exporter_endpoint: str = "http://prometheus:9090"

@dataclass
class MonitoringToolsConfig:
    """Monitoring tools configuration"""
    prometheus: PrometheusNestedConfig = field(default_factory=PrometheusNestedConfig)
    grafana: GrafanaNestedConfig = field(default_factory=GrafanaNestedConfig)
    sentry: SentryNestedConfig = field(default_factory=SentryNestedConfig)
    open_telemetry: OpenTelemetryNestedConfig = field(default_factory=OpenTelemetryNestedConfig)

@dataclass
class CeleryNestedConfig:
    enabled: bool = True
    broker_url: str = "redis://redis:6379"
    backend_url: str = "redis://redis:6379"
    task_timeout: int = 300

@dataclass
class PrefectNestedConfig:
    enabled: bool = True
    api_url: str = "http://localhost:4200"

@dataclass
class DagsterNestedConfig:
    enabled: bool = True
    api_url: str = "http://localhost:3000"

@dataclass
class OrchestrationConfig:
    """Workflow orchestration"""
    celery: CeleryNestedConfig = field(default_factory=CeleryNestedConfig)
    prefect: PrefectNestedConfig = field(default_factory=PrefectNestedConfig)
    dagster: DagsterNestedConfig = field(default_factory=DagsterNestedConfig)

@dataclass
class AdvancedFeaturesConfig:
    """Master configuration for all integrations"""
    # [Previous features remain...]
    spontaneous_evolution: SpontaneousEvolutionConfig = field(default_factory=SpontaneousEvolutionConfig)
    multi_objective_evolution: MultiObjectiveEvolutionConfig = field(default_factory=MultiObjectiveEvolutionConfig)
    agent_cloning: AgentCloningConfig = field(default_factory=AgentCloningConfig)
    security: SecurityFeatureConfig = field(default_factory=SecurityFeatureConfig)
    fault_prediction: FaultPredictionConfig = field(default_factory=FaultPredictionConfig)

    # New AI Tool Configurations
    langchain: LangChainConfig = field(default_factory=LangChainConfig)
    llama_index: LlamaIndexConfig = field(default_factory=LlamaIndexConfig)
    vector_db: VectorDBConfig = field(default_factory=VectorDBConfig)
    llm_providers: LLMProvidersConfig = field(default_factory=LLMProvidersConfig)
    monitoring_tools: MonitoringToolsConfig = field(default_factory=MonitoringToolsConfig)
    orchestration: OrchestrationConfig = field(default_factory=OrchestrationConfig)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spontaneous_evolution": self.spontaneous_evolution.__dict__,
            "multi_objective_evolution": self.multi_objective_evolution.__dict__,
            "agent_cloning": self.agent_cloning.__dict__,
            "security": self.security.__dict__,
            "fault_prediction": self.fault_prediction.__dict__,
            "langchain": self.langchain.__dict__,
            "llama_index": self.llama_index.__dict__,
            "vector_db": self.vector_db.__dict__,
            "llm_providers": self.llm_providers.__dict__,
            "monitoring_tools": self.monitoring_tools.__dict__,
            "orchestration": self.orchestration.__dict__,
        }

@dataclass
class PerformanceConfig:
    cpu_threshold: int = 80
    memory_threshold: int = 80
    metrics_collection_interval: int = 5

@dataclass
class InteractionConfig:
    rest_port: int = 8080

@dataclass
class SecurityConfig:
    enable_encryption: bool = True
    access_control_enabled: bool = True

@dataclass
class ReasoningConfig:
    consensus_threshold: float = 0.8

@dataclass
class AgentsConfig:
    max_agents: int = 5

@dataclass
class EmergencyConfig:
    recovery_timeout: int = 10

# --- Main System Config ---

@dataclass
class SystemConfig:
    mode: SystemMode = SystemMode.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO

    # Nested Configurations
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    interaction: InteractionConfig = field(default_factory=InteractionConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    reasoning: ReasoningConfig = field(default_factory=ReasoningConfig)
    agents: AgentsConfig = field(default_factory=AgentsConfig)
    emergency: EmergencyConfig = field(default_factory=EmergencyConfig)
    consciousness: ConsciousnessConfig = field(default_factory=ConsciousnessConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    advanced_features: AdvancedFeaturesConfig = field(default_factory=AdvancedFeaturesConfig)

    # Feature Flags
    feature_flags: Dict[str, bool] = field(default_factory=lambda: {
        "temporal_awareness": True,
        "existential_awareness": True,
        "meta_reflection": True,
        "cognitive_error_detection": True,
        "ambiguity_awareness": True,
        "predictive_consciousness": True,
        "memory_defragmentation": True,
        "collective_memory": True,
        "dream_memory": True,
        "architectural_evolution": True,
        "spontaneous_evolution": True,
        "multi_objective_evolution": True,
        "recursive_evolution": True,
        "monitoring_dashboard_3d": True,
        "fault_prediction": True,
        "response_time_analysis": True,
        "energy_cost_tracking": True,
        "information_aging_detection": True,
        "self_security_audit": True,
        "ethical_decision_analysis": True,
        "conscious_backup_system": True,
        "failure_simulation": True,
        "agent_genealogy": True,
        "conscious_memory": True
    })

    @classmethod
    def load_config_from_file(cls, path: str) -> "SystemConfig":
        # A more robust loader can be implemented here
        with open(path, 'r') as f:
            data = json.load(f)
        # This is a simplified loader; a real one would need to handle nested structures
        return cls()

def get_config(path: Optional[str] = None) -> SystemConfig:
    if path and os.path.exists(path):
        return SystemConfig.load_config_from_file(path)
    return SystemConfig()
