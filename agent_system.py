"""
Agent System
Features 5, 15, 20: Agent Evolution, Comparison, Cloning
"""

import asyncio
import logging
import random
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

class AIAgent:
    """Individual AI agent"""

    def __init__(self, agent_id: str, agent_type: str, system):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.system = system
        self.state = "initialized"
        self.experiences: List[Dict] = []
        self.success_rate = 0.5
        self.learning_rate = 0.001
        self.generation = 0
        self.parent_agent = None
        self.mutation_history: List[str] = []
        self.consciousness_level = 1.0
        self.logger = logging.getLogger(f"Agent.{self.agent_id}")

        # Behavioral model
        self.behavior_model = self._initialize_behavior_model()

    def _initialize_behavior_model(self) -> Dict[str, Any]:
        """Initialize based on agent type"""
        models = {
            "analytical_mind": {
                "thinking_style": "logical",
                "processing_depth": "deep",
                "creativity_level": 0.3,
                "specialization": "data_analysis",
                "confidence_threshold": 0.85
            },
            "creative_mind": {
                "thinking_style": "intuitive",
                "processing_depth": "variable",
                "creativity_level": 0.9,
                "specialization": "creative_solutions",
                "confidence_threshold": 0.7
            },
            "linguistic_mind": {
                "thinking_style": "semantic",
                "processing_depth": "detailed",
                "creativity_level": 0.6,
                "specialization": "language_processing",
                "confidence_threshold": 0.8
            },
            "sensory_mind": {
                "thinking_style": "perceptual",
                "processing_depth": "real-time",
                "creativity_level": 0.4,
                "specialization": "pattern_recognition",
                "confidence_threshold": 0.75
            },
            "social_mind": {
                "thinking_style": "empathetic",
                "processing_depth": "contextual",
                "creativity_level": 0.7,
                "specialization": "social_interaction",
                "confidence_threshold": 0.8
            },
            "ethical_mind": {
                "thinking_style": "principled",
                "processing_depth": "comprehensive",
                "creativity_level": 0.5,
                "specialization": "ethical_analysis",
                "confidence_threshold": 0.9
            },
            "meta_cognitive_mind": {
                "thinking_style": "reflective",
                "processing_depth": "recursive",
                "creativity_level": 0.6,
                "specialization": "self_awareness",
                "confidence_threshold": 0.85
            },
            "temporal_mind": {
                "thinking_style": "sequential",
                "processing_depth": "historical",
                "creativity_level": 0.4,
                "specialization": "temporal_analysis",
                "confidence_threshold": 0.8
            }
        }

        return models.get(self.agent_type, models["analytical_mind"])

    async def initialize(self):
        """Initialize agent"""
        self.state = "active"
        self.logger.info(f"🤖 Agent initialized: {self.agent_id} ({self.agent_type})")

    async def contribute_to_discussion(self, task: Dict, discussion_history: List, round: int) -> Dict[str, Any]:
        """Contribute to collaborative discussion"""
        try:
            analysis = await self._analyze_task(task)

            response = await self._generate_response(task, analysis, round)

            self.experiences.append({
                "task": task,
                "response": response,
                "round": round,
                "timestamp": datetime.now()
            })

            return response

        except Exception as e:
            self.logger.error(f"Error in discussion: {e}")
            return {
                "agent_id": self.agent_id,
                "answer": "Unable to process",
                "confidence": 0.1,
                "reasoning": "Error occurred"
            }

    async def _analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task based on specialization"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "task_type": task.get("type", "unknown"),
            "complexity": random.uniform(0.3, 0.9),
            "relevance": random.uniform(0.5, 1.0),
            "approach": self.behavior_model["thinking_style"]
        }

    async def _generate_response(self, task: Dict, analysis: Dict, round: int) -> Dict[str, Any]:
        """Generate response"""
        await asyncio.sleep(random.uniform(0.1, 0.5))

        answer = f"{self.agent_type} perspective: Analyzed '{task.get('content', '')}'"

        confidence = random.uniform(
            self.behavior_model["confidence_threshold"] - 0.1,
            1.0
        )

        return {
            "agent_id": self.agent_id,
            "answer": answer,
            "confidence": confidence,
            "reasoning": f"Used {self.behavior_model['thinking_style']} thinking",
            "suggestions": ["Validate with peers", "Consider alternatives"]
        }

    async def update_behavior(self, recent_decisions: List[Dict]):
        """Update behavior based on experiences"""
        if not recent_decisions:
            return

        my_contributions = []
        for decision in recent_decisions:
            for round_data in decision.get("rounds", []):
                for response in round_data.get("responses", []):
                    if response.get("agent_id") == self.agent_id:
                        my_contributions.append(response)

        if not my_contributions:
            return

        avg_confidence = sum(c.get("confidence", 0.5) for c in my_contributions) / len(my_contributions)
        self.success_rate = (self.success_rate * 0.9) + (avg_confidence * 0.1)

        # Adjust behavior
        if avg_confidence > 0.85:
            self.consciousness_level = min(10.0, self.consciousness_level + 0.1)
        elif avg_confidence < 0.5:
            self.consciousness_level = max(1.0, self.consciousness_level - 0.05)

    async def evolve(self):
        """Evolve agent capabilities"""
        self.generation += 1

        # Random mutation
        mutation = random.choice(["enhancement", "specialization"])

        if mutation == "enhancement":
            self.behavior_model["creativity_level"] = min(1.0, self.behavior_model["creativity_level"] + 0.1)

        self.mutation_history.append(f"Gen {self.generation}: {mutation}")

        self.logger.info(f"🧬 Agent evolved: {self.agent_id} -> Gen {self.generation}")

    async def clone(self, new_agent_id: str) -> 'AIAgent':
        """Clone agent (Feature 20)"""
        cloned = AIAgent(new_agent_id, self.agent_type, self.system)
        cloned.behavior_model = self.behavior_model.copy()
        cloned.parent_agent = self.agent_id
        cloned.generation = self.generation + 1

        # Apply mutations
        if random.random() < self.system.config.advanced_features.agent_cloning.mutation_rate:
            cloned.behavior_model["creativity_level"] = min(
                1.0,
                cloned.behavior_model["creativity_level"] + random.uniform(-0.05, 0.05)
            )

        await cloned.initialize()
        return cloned

    async def share_strategies(self, other_agent: 'AIAgent'):
        """Share successful strategies (Feature 70)"""
        if self.success_rate > other_agent.success_rate + 0.2:
            other_agent.learning_rate = min(0.01, other_agent.learning_rate * 1.2)
            self.logger.info(f"📚 Strategy shared: {self.agent_id} -> {other_agent.agent_id}")

    def reduce_activity(self):
        """Reduce activity for sleep/emergency"""
        self.previous_state = self.state
        self.state = "reduced"

    def restore_activity(self):
        """Restore activity"""
        if hasattr(self, 'previous_state'):
            self.state = self.previous_state
        else:
            self.state = "active"

    def get_state(self) -> Dict[str, Any]:
        """Get agent state"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state,
            "generation": self.generation,
            "success_rate": self.success_rate,
            "consciousness_level": self.consciousness_level,
            "behavior_model": self.behavior_model,
            "parent_agent": self.parent_agent
        }

    async def shutdown(self):
        """Shutdown agent"""
        self.state = "shutdown"
        self.logger.info(f"🛑 Agent shutdown: {self.agent_id}")

class AgentManager:
    """Manages agent lifecycle and evolution"""

    def __init__(self, system):
        self.system = system
        self.logger = logging.getLogger("AgentManager")
        self.genealogy: List[Dict] = []

    async def initialize(self):
        """Initialize agent manager"""
        self.logger.info("👥 Initializing Agent Manager...")

    async def create_initial_agents(self) -> List[AIAgent]:
        """Create initial set of agents"""
        agent_types = [
            "analytical_mind", "creative_mind", "linguistic_mind", "sensory_mind",
            "social_mind", "ethical_mind", "meta_cognitive_mind", "temporal_mind"
        ]

        agents = []
        for i, agent_type in enumerate(agent_types):
            agent = AIAgent(f"{agent_type}_{i}", agent_type, self.system)
            await agent.initialize()
            agents.append(agent)

        # Record in genealogy (Feature 5)
        self.genealogy.append({
            "agent_id": agent.agent_id,
            "parent_id": None,
            "generation": 0,
            "created_at": datetime.now().isoformat()
        })

        self.logger.info(f"✅ Created {len(agents)} agents")
        return agents

    def select_agents_for_task(self, task: Dict, agents: List[AIAgent]) -> List[AIAgent]:
        """Intelligent agent selection"""
        task_type = task.get('type', 'general')

        capabilities = {
            'analysis': ['analytical_mind', 'meta_cognitive_mind', 'temporal_mind'],
            'creative': ['creative_mind', 'linguistic_mind'],
            'language': ['linguistic_mind', 'social_mind'],
            'sensory': ['sensory_mind'],
            'social': ['social_mind', 'ethical_mind'],
            'ethical': ['ethical_mind', 'meta_cognitive_mind'],
            'temporal': ['temporal_mind', 'analytical_mind'],
            'general': ['analytical_mind', 'creative_mind', 'social_mind']
        }

        suitable_types = capabilities.get(task_type, capabilities['general'])
        selected = [a for a in agents if a.agent_type in suitable_types and a.state == "active"]

        return selected[:min(len(selected), self.system.config.agents.max_agents)]

    async def orchestrate_discussion(self, agents: List[AIAgent], task: Dict) -> Dict[str, Any]:
        """Orchestrate multi-round discussion (Feature 45)"""
        discussion_id = f"discussion_{uuid.uuid4().hex[:8]}"

        discussion = {
            "id": discussion_id,
            "task": task,
            "participants": [a.agent_id for a in agents],
            "rounds": [],
            "consensus_reached": False
        }

        max_rounds = 3 if task.get('priority', 'medium') != 'high' else 5

        for round_num in range(max_rounds):
            round_responses = await asyncio.gather(*[
                agent.contribute_to_discussion(task, discussion["rounds"], round_num)
                for agent in agents
            ])

            discussion["rounds"].append({
                "round": round_num,
                "responses": list(round_responses)
            })

            if self._check_consensus(round_responses):
                discussion["consensus_reached"] = True
                break

        return await self.system.reasoning_orchestrator.synthesize_decision(discussion, agents)

    def _check_consensus(self, responses: List[Dict]) -> bool:
        """Check if consensus reached"""
        if len(responses) < 2:
            return True

        avg_confidence = sum(r.get("confidence", 0) for r in responses) / len(responses)
        return avg_confidence > self.system.config.reasoning.consensus_threshold

    async def update_agent_genealogy(self):
        """Update agent genealogy (Feature 5)"""
        if not self.system.config.feature_flags.get("agent_genealogy"):
            return

        self.logger.info("📊 Agent genealogy updated")
