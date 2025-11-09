"""
BabyAGI Manager
"""
import logging
from babyagi import BabyAGI

class BabyAGIManager:
    def __init__(self, config, llm, vectorstore):
        self.config = config
        self.logger = logging.getLogger("BabyAGIManager")
        self.baby_agi = BabyAGI.from_llm_and_vectorstore(
            llm=llm,
            vectorstore=vectorstore,
            verbose=True
        )

    async def create_tasks(self, objective: str):
        """Create tasks with BabyAGI"""
        return self.baby_agi.run(objective)
