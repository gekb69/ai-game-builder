"""
Agents Manager
"""
import logging
from src.agents.metagpt_manager import MetaGPTManager
from src.agents.autogpt_manager import AutoGPTManager
from src.agents.babyagi_manager import BabyAGIManager
from src.agents.autogen_manager import AutoGenManager

class AgentsManager:
    def __init__(self, config, llm, vectorstore):
        self.config = config
        self.logger = logging.getLogger("AgentsManager")
        self.agents = {
            "metagpt": MetaGPTManager(config),
            "autogpt": AutoGPTManager(config),
            "babyagi": BabyAGIManager(config, llm, vectorstore),
            "autogen": AutoGenManager(config),
        }

    async def initialize_all(self):
        """Initialize all agents"""
        for agent in self.agents.values():
            if hasattr(agent, "initialize"):
                await agent.initialize()

    async def execute_with_agent(self, agent_name: str, task: str):
        """Execute a task with a specific agent"""
        if agent_name in self.agents:
            return await self.agents[agent_name].execute_task(task)
        else:
            raise ValueError(f"Agent {agent_name} not found.")
