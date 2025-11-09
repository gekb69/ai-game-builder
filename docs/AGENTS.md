# AI Agent Integrations

## Supported Agent Frameworks

### Auto-GPT
```python
# Auto-GPT integration in src/autogpt_manager.py
class AutoGPTManager:
    def __init__(self, config):
        self.config = config
        self.agent = AutoGPT.from_config(config)

    async def execute_task(self, task: str):
        return await self.agent.run(task)

BabyAGI
# BabyAGI integration in src/babyagi_manager.py
class BabyAGIManager:
    def __init__(self, llm, vectorstore):
        self.baby_agi = BabyAGI.from_llm_and_vectorstore(
            llm=llm,
            vectorstore=vectorstore,
            verbose=True
        )

AutoGen
# AutoGen integration in src/autogen_manager.py
class AutoGenManager:
    def __init__(self, config):
        self.config = config
        self.assistant = AssistantAgent(
            name="assistant",
            llm_config={"config_list": [config]}
        )
        self.user_proxy = UserProxyAgent(
            name="user",
            code_execution_config={"work_dir": "coding"}
        )

Kimi K2, MiniMax M2
# Chinese model providers in src/chinese_models.py
class KimiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = Moonshot(api_key=api_key)

    async def generate(self, prompt: str) -> str:
        return await self.client.generate(prompt)

Usage
# Initialize all agents
agents_manager = AgentsManager(config)
await agents_manager.initialize_all()

# Execute with specific agent
result = await agents_manager.execute_with_agent("autogpt", "Research AI consciousness")

Configuration
# Add to config.py
autogpt:
  enabled: true
  api_key: ${AUTOGPT_API_KEY}
  model: "gpt-4"

babyagi:
  enabled: true
  max_iterations: 100

autogen:
  enabled: true
  config_list:
    - model: "gpt-4"
      api_key: ${OPENAI_API_KEY}

Multi-Agent Collaboration
# src/multi_agent_orchestrator.py
class MultiAgentOrchestrator:
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    async def collaborative_solve(self, problem: str):
        # BabyAGI creates tasks
        tasks = await self.agents["babyagi"].create_tasks(problem)

        # Auto-GPT executes tasks
        results = []
        for task in tasks:
            result = await self.agents["autogpt"].execute(task)
            results.append(result)

        # AutoGen reviews results
        review = await self.agents["autogen"].review(results)

        return review
