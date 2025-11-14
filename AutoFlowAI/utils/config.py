"""
إعدادات النظام
"""
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "autoflowai"
    user: str = "autoflowai"
    password: str = ""
    pool_size: int = 10

@dataclass
class SecurityConfig:
    secret_key: str = "your-secret-key-here"
    jwt_expiration: int = 3600
    rate_limit_per_hour: int = 1000
    encryption_enabled: bool = True

@dataclass
class AgentConfig:
    max_concurrent_tasks: int = 10
    task_timeout: int = 300
    retry_attempts: int = 3
    reasoning_timeout: int = 60

@dataclass
class WorkflowConfig:
    max_execution_time: int = 3600
    max_nodes_per_workflow: int = 100
    parallel_execution: bool = True
    save_state_enabled: bool = True

@dataclass
class TradingConfig:
    risk_tolerance: str = "medium"
    max_position_size: float = 0.1
    stop_loss_percentage: float = 0.05
    take_profit_percentage: float = 0.1
    paper_trading: bool = True

class Config:
    """إعدادات النظام الرئيسية"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.environment = os.getenv('ENVIRONMENT', 'development')

        # إعدادات فرعية
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.agent = AgentConfig()
        self.workflow = WorkflowConfig()
        self.trading = TradingConfig()

        # تحميل الإعدادات من الملف
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)

        # تحميل متغيرات البيئة
        self.load_from_env()

    def load_from_file(self, config_file: str):
        """تحميل الإعدادات من ملف"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # تحديث الإعدادات
            for section, values in config_data.items():
                if hasattr(self, section):
                    section_obj = getattr(self, section)
                    for key, value in values.items():
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, value)

        except Exception as e:
            print(f"خطأ في تحميل إعدادات الملف: {e}")

    def load_from_env(self):
        """تحميل الإعدادات من متغيرات البيئة"""
        # قاعدة البيانات
        self.database.host = os.getenv('DB_HOST', self.database.host)
        self.database.port = int(os.getenv('DB_PORT', self.database.port))
        self.database.name = os.getenv('DB_NAME', self.database.name)
        self.database.user = os.getenv('DB_USER', self.database.user)
        self.database.password = os.getenv('DB_PASSWORD', self.database.password)

        # الأمان
        self.security.secret_key = os.getenv('SECRET_KEY', self.security.secret_key)
        self.security.jwt_expiration = int(os.getenv('JWT_EXPIRATION', self.security.jwt_expiration))

        # الوكلاء
        self.agent.max_concurrent_tasks = int(os.getenv('MAX_CONCURRENT_TASKS', self.agent.max_concurrent_tasks))
        self.agent.task_timeout = int(os.getenv('TASK_TIMEOUT', self.agent.task_timeout))

        # العمليات
        self.workflow.max_execution_time = int(os.getenv('WORKFLOW_TIMEOUT', self.workflow.max_execution_time))

        # التداول
        self.trading.risk_tolerance = os.getenv('RISK_TOLERANCE', self.trading.risk_tolerance)
        self.trading.paper_trading = os.getenv('PAPER_TRADING', 'true').lower() == 'true'

    def save_to_file(self, config_file: str):
        """حفظ الإعدادات في ملف"""
        config_data = {
            'debug': self.debug,
            'environment': self.environment,
            'database': self.database.__dict__,
            'security': self.security.__dict__,
            'agent': self.agent.__dict__,
            'workflow': self.workflow.__dict__,
            'trading': self.trading.__dict__
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """الحصول على قيمة إعداد"""
        keys = key.split('.')
        obj = self

        for k in keys:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                return default

        return obj

    def set(self, key: str, value: Any):
        """تعيين قيمة إعداد"""
        keys = key.split('.')
        obj = self

        for k in keys[:-1]:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                raise ValueError(f"الطريق غير موجود: {key}")

        setattr(obj, keys[-1], value)

    def is_production(self) -> bool:
        """فحص بيئة الإنتاج"""
        return self.environment.lower() in ['production', 'prod']

    def is_development(self) -> bool:
        """فحص بيئة التطوير"""
        return self.environment.lower() in ['development', 'dev']

    def get_database_url(self) -> str:
        """الحصول على رابط قاعدة البيانات"""
        return f"postgresql://{self.database.user}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.name}"

    def __repr__(self) -> str:
        return f"Config(environment={self.environment}, debug={self.debug})"

# إنشاء إعداد افتراضي
config = Config()
