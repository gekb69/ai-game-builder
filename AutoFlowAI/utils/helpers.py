"""
دوال مساعدة
"""
import json
import uuid
import hashlib
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from functools import wraps

def generate_id(prefix: str = "") -> str:
    """توليد معرف فريد"""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}" if prefix else unique_id

def hash_data(data: Any) -> str:
    """تشفير البيانات"""
    data_str = json.dumps(data, sort_keys=True) if not isinstance(data, str) else data
    return hashlib.sha256(data_str.encode()).hexdigest()

def format_timestamp(timestamp: float) -> str:
    """تنسيق الطابع الزمني"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def parse_duration(duration_str: str) -> float:
    """تحويل مدة نصية إلى ثواني"""
    if not duration_str:
        return 0.0

    duration_str = duration_str.lower().strip()

    if 'h' in duration_str:
        hours = float(duration_str.replace('h', ''))
        return hours * 3600
    elif 'm' in duration_str:
        minutes = float(duration_str.replace('m', ''))
        return minutes * 60
    elif 's' in duration_str:
        return float(duration_str.replace('s', ''))
    else:
        # افتراض ثواني
        try:
            return float(duration_str)
        except:
            return 0.0

def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
    """مزخرف إعادة المحاولة"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    time.sleep(delay * (2 ** attempt)) # تأخير متزايد
            return None
        return wrapper
    return decorator

def measure_time(func):
    """مزخرف قياس الوقت"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"⏱️ {func.__name__} استغرق {execution_time:.3f} ثانية")
        return result
    return wrapper

def validate_json(data: str) -> bool:
    """التحقق من صحة JSON"""
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """الحصول الآمن على قيمة من قاموس"""
    try:
        return data.get(key, default)
    except (KeyError, TypeError):
        return default

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """تقسيم قائمة إلى قطع"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """تسطيح القاموس المتعدد المستويات"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def class_name(obj: Any) -> str:
    """الحصول على اسم الكلاس"""
    return obj.__class__.__name__

def is_debug_mode() -> bool:
    """فحص وضع التطوير"""
    import os
    return os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']
