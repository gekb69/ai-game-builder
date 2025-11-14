"""
نظام السجلات
"""
import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import json
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "AutoFlowAI", level: str = "INFO",
                 log_file: Optional[str] = None,
                 max_bytes: int = 10*1024*1024, backup_count: int = 5) -> logging.Logger:
    """
    إعداد نظام السجلات
    """
    # إنشاء Logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # إزالة المعالجات الموجودة
    logger.handlers.clear()

    # تنسيق الرسائل
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # معالج وحدة التحكم
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # معالج الملف إذا طُلب
    if log_file:
        try:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"لم يتم إنشاء ملف السجل: {e}")

    return logger

def log_function_call(logger: logging.Logger):
    """مزخرف تسجيل استدعاء الدوال"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"استدعاء {func.__name__}")
            result = func(*args, **kwargs)
            logger.info(f"انتهاء {func.__name__}")
            return result
        return wrapper
    return decorator

def log_performance(logger: logging.Logger):
    """مزخرف تسجيل الأداء"""
    def decorator(func):
        import time
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"{func.__name__} استغرق {duration:.3f} ثانية")
            return result
        return wrapper
    return decorator

class PerformanceLogger:
    """مسجل الأداء المتقدم"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = {}

    def start_timer(self, operation: str):
        """بدء مؤقت العملية"""
        import time
        self.metrics[operation] = {'start_time': time.time()}

    def end_timer(self, operation: str, metadata: Dict[str, Any] = None):
        """إنهاء مؤقت العملية"""
        import time
        if operation not in self.metrics:
            self.logger.warning(f"لم يتم بدء مؤقت العملية: {operation}")
            return

        start_time = self.metrics[operation]['start_time']
        end_time = time.time()
        duration = end_time - start_time

        log_data = {
            'operation': operation,
            'duration': duration,
            'timestamp': end_time
        }

        if metadata:
            log_data.update(metadata)

        self.logger.info(f"أداء العملية: {json.dumps(log_data, ensure_ascii=False)}")

        # تنظيف
        del self.metrics[operation]
