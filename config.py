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

@dataclass
class AdvancedFeaturesConfig:
    spontaneous_evolution: SpontaneousEvolutionConfig = field(default_factory=SpontaneousEvolutionConfig)
    multi_objective_evolution: MultiObjectiveEvolutionConfig = field(default_factory=MultiObjectiveEvolutionConfig)
    agent_cloning: AgentCloningConfig = field(default_factory=AgentCloningConfig)
    security: SecurityFeatureConfig = field(default_factory=SecurityFeatureConfig)
    fault_prediction: FaultPredictionConfig = field(default_factory=FaultPredictionConfig)

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
