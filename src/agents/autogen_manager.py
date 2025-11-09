"""
AutoGen Manager
"""
import logging
from autogen import AssistantAgent, UserProxyAgent

class AutoGenManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("AutoGenManager")
        self.assistant = AssistantAgent(
            name="assistant",
            llm_config={"config_list": [{"model": "gpt-4", "api_key": self.config.llm_providers.openai.api_key}]}
        )
        self.user_proxy = UserProxyAgent(
            name="user",
            code_execution_config={"work_dir": "coding"}
        )

    async def review(self, results: list):
        """Review results with AutoGen"""
        message = f"Please review the following results: {results}"
        self.user_proxy.initiate_chat(self.assistant, message=message)
        return self.user_proxy.last_message()["content"]
