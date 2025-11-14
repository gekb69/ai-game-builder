"""
نظام الذاكرة الذكي المتقدم
"""
import threading
import time
from typing import Dict, List, Any

class AdvancedMemorySystem:
    def __init__(self):
        self.episodic_memory = [] # ذاكرة الأحداث
        self.semantic_memory = {} # ذاكرة المعاني
        self.working_memory = {} # ذاكرة العمل
        self.memory_lock = threading.Lock()

    def store_episode(self, episode: Dict[str, Any]):
        with self.memory_lock:
            self.episodic_memory.append({
                'timestamp': time.time(),
                'episode': episode
            })
            # الاحتفاظ بآخر 1000 حدث فقط
            if len(self.episodic_memory) > 1000:
                self.episodic_memory = self.episodic_memory[-1000:]

    def store_semantic(self, concept: str, knowledge: Dict[str, Any]):
        with self.memory_lock:
            self.semantic_memory[concept] = knowledge

    def get_relevant_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        with self.memory_lock:
            relevant = []
            for episode in reversed(self.episodic_memory[-100:]):
                if any(keyword in str(episode['episode']).lower() for keyword in query.lower().split()):
                    relevant.append(episode)
                if len(relevant) >= limit:
                    break
            return relevant

    def get_memory_stats(self) -> Dict[str, int]:
        with self.memory_lock:
            return {
                'episodic_memories': len(self.episodic_memory),
                'semantic_concepts': len(self.semantic_memory),
                'working_memory_items': len(self.working_memory)
            }
