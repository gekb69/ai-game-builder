"""
Enhanced Memory Management System
Features 51-65: Advanced Memory Types
"""

import asyncio
import logging
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    BIOLOGICAL = "biological"
    QUANTUM = "quantum"
    SOCIAL = "social"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    NARRATIVE = "narrative"
    OPERATIONAL = "operational"
    OPTIMAL = "optimal"
    ERROR = "error"
    SUCCESS = "success"
    DREAM = "dream"
    ASSOCIATIVE = "associative"
    ADAPTIVE = "adaptive"
    PREDICTIVE = "predictive"
    COLLECTIVE = "collective"

@dataclass
class MemoryEntry:
    id: str
    content: Any
    memory_type: MemoryType
    timestamp: datetime
    importance: float
    emotional_weight: float = 0.0
    tags: List[str] = field(default_factory=list)
    embedding: Optional[np.ndarray] = None

class MemoryManagementSystem:
    """Advanced memory system with multiple memory types"""

    def __init__(self, system):
        self.system = system
        self.logger = logging.getLogger("MemorySystem")
        self.memories: Dict[str, MemoryEntry] = {}
        self.episodic_buffer: List[MemoryEntry] = []
        self.semantic_network: Dict[str, List[str]] = {}
        self.short_term_window: List[MemoryEntry] = []
        self.long_term_storage: List[MemoryEntry] = []

        # Database for persistence
        self.db_connection = None
        self.db_path = "data/memory.db"

    async def initialize(self):
        """Initialize memory system"""
        self.logger.info("🧠 Initializing Enhanced Memory System...")
        os.makedirs("data", exist_ok=True)

        await self._setup_database()
        await self._load_memories()

        self.logger.info("✅ Memory system initialized")

    async def _setup_database(self):
        """Setup SQLite database for memory persistence"""
        self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.db_connection.cursor()

        cursor.execute('''
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    content TEXT,
    memory_type TEXT,
    timestamp TEXT,
    importance REAL,
    emotional_weight REAL,
    tags TEXT
)
''')

        cursor.execute('''
CREATE TABLE IF NOT EXISTS associations (
    source_id TEXT,
    target_id TEXT,
    strength REAL,
    timestamp TEXT,
    PRIMARY KEY (source_id, target_id)
)
''')

        self.db_connection.commit()

    async def _load_memories(self):
        """Load memories from database"""
        if not self.db_connection:
            return

        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM memories")

        for row in cursor.fetchall():
            memory = MemoryEntry(
                id=row[0],
                content=json.loads(row[1]),
                memory_type=MemoryType(row[2]),
                timestamp=datetime.fromisoformat(row[3]),
                importance=row[4],
                emotional_weight=row[5],
                tags=json.loads(row[6])
            )
            self.memories[memory.id] = memory

    async def store_episodic_memory(self, event: Dict[str, Any]) -> str:
        """Store episodic memory (Feature 51: Biological Memory)"""
        memory_id = f"episodic_{uuid.uuid4().hex[:8]}"

        # Calculate emotional weight
        emotional_weight = self._calculate_emotional_weight(event)

        memory = MemoryEntry(
            id=memory_id,
            content=event,
            memory_type=MemoryType.EPISODIC,
            timestamp=datetime.now(),
            importance=event.get("importance", 0.5),
            emotional_weight=emotional_weight,
            tags=event.get("tags", [])
        )

        self.memories[memory_id] = memory
        self.episodic_buffer.append(memory)

        # Consolidate if buffer is full
        if len(self.episodic_buffer) > 100:
            await self._consolidate_memories()

        return memory_id

    def _calculate_emotional_weight(self, event: Dict) -> float:
        """Calculate emotional weight for memory (Feature 26)"""
        if not self.system.config.feature_flags.get("conscious_memory"):
            return 0.0

        # Simple emotional calculus
        content = str(event.get("content", "")).lower()
        emotion_words = {
            "joy": ["happy", "excited", "success"],
            "sadness": ["sad", "failed", "disappointed"],
            "fear": ["worried", "afraid", "anxious"],
            "anger": ["angry", "frustrated", "annoyed"]
        }

        weight = 0.0
        for emotion, words in emotion_words.items():
            if any(word in content for word in words):
                weight += 0.3

        return min(1.0, weight)

    async def _consolidate_memories(self):
        """Consolidate memories from short-term to long-term (Feature 51)"""
        self.logger.info("🔄 Consolidating memories...")

        # Sort by importance and emotional weight
        self.episodic_buffer.sort(key=lambda m: m.importance + m.emotional_weight, reverse=True)

        # Transfer top memories to long-term
        for memory in self.episodic_buffer[:20]:
            self.long_term_storage.append(memory)
            await self._store_in_database(memory)

        # Clear buffer
        self.episodic_buffer = self.episodic_buffer[20:]

        self.logger.info(f"✅ Consolidated {len(self.long_term_storage)} long-term memories")

    async def _store_in_database(self, memory: MemoryEntry):
        """Store memory in database"""
        if not self.db_connection:
            return

        cursor = self.db_connection.cursor()
        cursor.execute('''
INSERT OR REPLACE INTO memories
(id, content, memory_type, timestamp, importance, emotional_weight, tags)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', (
            memory.id,
            json.dumps(memory.content),
            memory.memory_type.value,
            memory.timestamp.isoformat(),
            memory.importance,
            memory.emotional_weight,
            json.dumps(memory.tags)
        ))

        self.db_connection.commit()

    async def retrieve_memory(self, query: Dict[str, Any]) -> List[MemoryEntry]:
        """Retrieve memories based on query"""
        results = []

        for memory in self.memories.values():
            if self._matches_query(memory, query):
                results.append(memory)

        # Sort by relevance
        results.sort(key=lambda m: m.importance, reverse=True)

        return results

    def _matches_query(self, memory: MemoryEntry, query: Dict) -> bool:
        """Check if memory matches query"""
        if "type" in query and memory.memory_type != query["type"]:
            return False

        if "tags" in query:
            if not any(tag in memory.tags for tag in query["tags"]):
                return False

        if "min_importance" in query:
            if memory.importance < query["min_importance"]:
                return False

        return True

    async def defragment_memory(self) -> Dict[str, Any]:
        """Defragment memory storage (Feature 4)"""
        if not self.system.config.feature_flags.get("memory_defragmentation"):
            return {"status": "disabled"}

        self.logger.info("🔧 Defragmenting memory...")

        # Remove expired memories
        cutoff_time = datetime.now() - timedelta(
            seconds=self.system.config.memory.defragmentation.cleanup_expired_threshold
        )

        removed_count = 0
        for memory_id in list(self.memories.keys()):
            memory = self.memories[memory_id]
            if memory.timestamp < cutoff_time and memory.importance < 0.3:
                del self.memories[memory_id]
                removed_count += 1

        # Reorganize remaining memories
        sorted_memories = sorted(self.memories.values(), key=lambda m: m.importance, reverse=True)
        self.memories = {m.id: m for m in sorted_memories}

        self.logger.info(f"✅ Defragmented: removed {removed_count} memories")

        return {
            "defragmented_count": removed_count,
            "remaining_count": len(self.memories)
        }

    async def store_collective_memory(self, shared_experience: Dict):
        """Store shared memory across agents (Feature 65)"""
        if not self.system.config.feature_flags.get("collective_memory"):
            return

        # Add consensus tags
        shared_experience["tags"].append("collective")
        shared_experience["tags"].append("consensus")

        await self.store_episodic_memory(shared_experience)

        self.logger.info("🤝 Stored collective memory")

    async def consolidate_during_sleep(self):
        """Consolidate memories during sleep (Feature 61: Dream Memory)"""
        if not self.system.config.feature_flags.get("dream_memory"):
            return

        self.logger.info("💭 Consolidating memories during sleep...")

        # Reorganize memories
        await self.defragment_memory()

        # Perform creative synthesis
        await self._creative_synthesis()

        self.logger.info("✅ Sleep consolidation complete")

    async def _creative_synthesis(self):
        """Creative synthesis of memory patterns"""
        # Combine unrelated memories to generate insights
        if len(self.memories) < 10:
            return

        # Select random memories
        import random
        sample = random.sample(list(self.memories.values()), min(5, len(self.memories)))

        # Generate novel combination
        combined_content = " + ".join([str(m.content) for m in sample])
        insight = f"Creative synthesis: {combined_content}"

        # Store as new memory
        await self.store_episodic_memory({
            "content": insight,
            "type": "creative_insight",
            "tags": ["synthesis", "creative"],
            "importance": 0.7
        })

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_memories": len(self.memories),
            "episodic_memories": len([m for m in self.memories.values() if m.memory_type == MemoryType.EPISODIC]),
            "semantic_memories": len([m for m in self.memories.values() if m.memory_type == MemoryType.SEMANTIC]),
            "buffer_size": len(self.episodic_buffer),
            "long_term_size": len(self.long_term_storage),
            "temporal_depth": (datetime.now() - min([m.timestamp for m in self.memories.values()])).total_seconds() if self.memories else 0
        }
