"""
Combined AI agent modules.

This file merges functionalities from the following original files without
duplication:

- ``free_ai_apis.py``: defines free API providers for various LLM services and
  helper functions to call them.
- ``ai_agent_skeleton.py`` and ``ai_agent_skeleton 2.py``: provide the base
  classes for AI models, plugin architecture and agent orchestration.
- ``suna_plugin.py``: a plugin integrating the Suna AI agent.
- ``ai_agent_system.py``: defines a Telegram-based agent system with tasks
  and handlers.

By consolidating these definitions into one module, the system can be
imported as a single package while avoiding repetition.  The combined
module also preserves the original Arabic comments and documentation to
maintain context.
"""

from __future__ import annotations

import os
import logging
import asyncio
import requests
import subprocess
import importlib.util
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Optional imports for Telegram.  These may not be available in all
# environments, so the code handles ImportError gracefully.  When
# unavailable, handlers that rely on Telegram will not function.
try:
    from telegram import Update
    from telegram.ext import (
        ApplicationBuilder, ContextTypes,
        CommandHandler, MessageHandler, filters
    )
except ImportError:
    Update = None  # Telegram library not available
    ApplicationBuilder = None
    ContextTypes = None
    CommandHandler = None
    MessageHandler = None
    filters = None

# Optional import for OpenAI.  The agent can still operate partially
# without this dependency, although some tasks will return placeholder
# messages when OpenAI is not installed.
try:
    import openai
except ImportError:
    openai = None

# Configure logging for the module.  Users of this module can override
# the logging settings as desired in their own applications.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Section: Free AI API providers and helper functions
# ---------------------------------------------------------------------------

#: Dictionary of free API providers with usage limits and metadata.
FREE_API_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "openrouter": {
        "name": "OpenRouter",
        "description": (
            "منصة توفر مجموعة متنوعة من نماذج الذكاء الاصطناعي للمحادثة"
            " وتوليد النصوص، وتسمح بربطها عبر API واحد."
        ),
        # الطبقة المجانية تسمح بما يصل إلى 20 طلباً في الدقيقة و200 طلب في اليوم【986315200663798†L198-L203】.
        "limits": "20 طلب/دقيقة، 200 طلب/يوم【986315200663798†L198-L203】",
        "models": [
            "DeepSeek R1",
            "Llama 3.3 70B Instruct",
            "Mistral 7B Instruct",
        ],
        "documentation": "https://openrouter.ai/docs",
        "notes": (
            "يجب إنشاء مفتاح API من موقع OpenRouter وحفظه في متغير البيئة"
            " OPENROUTER_API_KEY لاستخدام الدوال أدناه."
        ),
    },
    "google_ai_studio": {
        "name": "Google AI Studio",
        "description": (
            "منصة من جوجل توفر إمكانية تجربة نماذج Gemini وغيرها من نماذج"
            " LLM بحدود سخية."
        ),
        # تتيح ما يصل إلى مليون توكن في الدقيقة و1,500 طلب يوميًا في الطبقة المجانية【986315200663798†L281-L284】.
        "limits": "1,000,000 توكن/دقيقة، 1,500 طلب/يوم【986315200663798†L281-L284】",
        "models": [
            "Gemini 2.0 Flash",
            "Gemini 2.5 Pro",
            "Gemini 1.5 Flash",
        ],
        "documentation": "https://ai.google.dev/gemini-api/docs",
        "notes": (
            "تتطلب بعض النماذج التحقق من رقم الهاتف، كما تُستخدم البيانات"
            " لأغراض التدريب خارج مناطق الاتحاد الأوروبي."
        ),
    },
    "mistral": {
        "name": "Mistral (La Plateforme)",
        "description": (
            "تقدم Mistral نماذج عالية الأداء مثل mistral-large-2402 ضمن طبقة"
            " مجانية موجهة للتجربة."
        ),
        # الطبقة المجانية تسمح بطلب واحد في الثانية و500,000 توكن في الدقيقة【986315200663798†L631-L636】.
        "limits": "1 طلب/ثانية، 500,000 توكن/دقيقة【986315200663798†L631-L636】",
        "models": [
            "mistral-large-2402",
            "mistral-8b-latest",
        ],
        "documentation": "https://docs.mistral.ai/getting-started/models/models_overview/",
        "notes": (
            "تتطلب المنصة التحقق من رقم الهاتف وقد تُطبّق شروط بيانات"
            " استخدام معينة."
        ),
    },
    "huggingface_serverless": {
        "name": "HuggingFace Serverless Inference",
        "description": (
            "خدمة استضافة توفر نماذج متنوعة للتوليد والاستكمال، مع قيود"
            " على حجم النموذج."
        ),
        # الخدمة مجانية لبعض النماذج الصغيرة (<10 GB) وتقدم رصيدًا شهريًا وفقاً للمقال【986315200663798†L694-L699】.
        "limits": "نماذج أقل من 10 GB؛ رصيد شهري مجاني محدود【986315200663798†L694-L699】",
        "models": [
            "GPT-2",
            "DistilBERT",
            "Meta-Llama-3-8B-Instruct",
        ],
        "documentation": "https://huggingface.co/docs/inference-providers/en/index",
        "notes": (
            "تحتاج إلى إنشاء رمز دخول (HF_TOKEN) من حسابك على HuggingFace،"
            " كما أن بعض النماذج الكبيرة غير مدعومة في الطبقة المجانية."
        ),
    },
    "cerebras": {
        "name": "Cerebras Cloud",
        "description": (
            "مزود يسمح بالوصول إلى نماذج Llama وغيرها مع حدود عالية للطلبات"
            " والتوكنات في الطبقة المجانية."
        ),
        # الحدود: 30 طلب في الدقيقة و60,000 توكن في الدقيقة【986315200663798†L742-L746】.
        "limits": "30 طلب/دقيقة، 60,000 توكن/دقيقة【986315200663798†L742-L746】",
        "models": [
            "Llama 3.1 8B",
            "Llama 3.3 70B",
        ],
        "documentation": "https://inference-docs.cerebras.ai",
        "notes": (
            "تحتاج إلى الانضمام إلى قائمة الانتظار للحصول على المفتاح، وقد تتغير"
            " الشروط بسرعة."
        ),
    },
}


def call_openrouter(prompt: str,
                    model: str = "cognitivecomputations/dolphin3.0-r1-mistral-24b:free"
                   ) -> Dict[str, Any]:
    """Send a chat request to a model hosted on OpenRouter.

    The ``prompt`` parameter is the user text, and ``model`` is the model
    identifier on the OpenRouter platform. You must set the
    ``OPENROUTER_API_KEY`` environment variable before calling this function.
    The function sends a POST request and returns the full JSON response.

    Args:
        prompt: User input text.
        model: Model identifier on OpenRouter (default: a free Dolphin Mistral model).

    Returns:
        A dictionary containing the server response.

    Raises:
        RuntimeError: If the API key is not set.
        requests.HTTPError: If the HTTP request fails.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("يرجى تعيين متغير البيئة OPENROUTER_API_KEY أولاً.")
    base_url = "https://openrouter.ai/api/v1"
    endpoint = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }
    response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def call_huggingface(model: str,
                     prompt: str,
                     max_tokens: int = 256
                    ) -> Dict[str, Any]:
    """Send a completion request to a HuggingFace model via the serverless API.

    The ``HF_TOKEN`` environment variable must be set before calling this
    function. The free tier may impose limits on model size and request
    volume.

    Args:
        model: Model identifier (e.g., 'meta-llama/Meta-Llama-3-8B-Instruct').
        prompt: User input text.
        max_tokens: Maximum number of output tokens.

    Returns:
        The JSON response from the service.

    Raises:
        RuntimeError: If the API token is not configured.
        requests.HTTPError: If the HTTP request fails.
    """
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("يرجى تعيين متغير البيئة HF_TOKEN أولاً.")
    endpoint = "https://api.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
    }
    response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

# ---------------------------------------------------------------------------
# Section: Core AI models and agent framework
# ---------------------------------------------------------------------------


class BaseAIModel:
    """Abstract base class for AI models.

    Subclass this and implement the ``generate`` method to connect to
    different AI providers.  For example, you could create a class
    ``OpenAIModel`` that wraps calls to OpenAI's APIs, or ``LocalModel``
    that runs a local inference engine.
    """

    def generate(self, prompt: str) -> str:
        raise NotImplementedError("AI models must implement generate()")


class DummyModel(BaseAIModel):
    """A dummy AI model used as a placeholder.

    This dummy simply echoes the prompt and notes that a real model
    integration is required.  You can replace this class with a
    concrete implementation when you integrate a real LLM.
    """

    def generate(self, prompt: str) -> str:
        return f"[Dummy response to: {prompt}]"


class BasePlugin:
    """Base class for plugins that extend an :class:`Agent`.

    Plugins provide a way to add new capabilities to an existing agent at
    runtime without modifying the core agent class.  To create a plugin,
    subclass :class:`BasePlugin` and implement a :meth:`register` method
    that takes an :class:`Agent` instance and uses :meth:`Agent.add_feature`
    to attach new methods.  Plugins can live in a ``plugins`` directory or
    any other folder you specify when calling :meth:`Agent.load_plugins`.
    """

    def register(self, agent: "Agent") -> None:
        """Register plugin functionality with an agent.

        Subclasses must override this method to attach new features to the
        provided agent.  A typical implementation will call
        ``agent.add_feature(<feature_name>, <callable>)`` for each new
        capability.

        :param agent: The agent instance to extend.
        """
        raise NotImplementedError("Plugins must implement register()")


class PluginLoader:
    """Utility class to discover and instantiate plugins from a directory.

    The loader looks for Python files in the specified directory, imports
    them dynamically using :mod:`importlib`, and creates instances of any
    classes that inherit from :class:`BasePlugin` (excluding
    :class:`BasePlugin` itself).  These instances can then be used to
    extend an :class:`Agent` by calling their :meth:`register` methods.
    """

    def __init__(self, plugins_dir: str = "plugins") -> None:
        self.plugins_dir = plugins_dir

    def discover(self) -> List[BasePlugin]:
        """Discover and instantiate plugin classes in ``self.plugins_dir``.

        :return: A list of instantiated plugins.
        """
        plugins: List[BasePlugin] = []
        if not os.path.isdir(self.plugins_dir):
            return plugins
        for fname in os.listdir(self.plugins_dir):
            # Only load *.py files that are not private (don't start with _)
            if fname.startswith("_") or not fname.endswith(".py"):
                continue
            path = os.path.join(self.plugins_dir, fname)
            module_name = os.path.splitext(fname)[0]
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)  # type: ignore[misc]
                except Exception as e:
                    # Ignore faulty plugins but continue loading others
                    logger.warning("Error loading plugin %s: %s", fname, e)
                    continue
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr is not BasePlugin
                    ):
                        try:
                            plugins.append(attr())  # type: ignore[misc]
                        except Exception as e:
                            logger.warning("Error instantiating plugin %s: %s", attr_name, e)
        return plugins


@dataclass
class Agent:
    """Core agent class that manages tasks and multiple models.

    :param primary_model: The main model used for tasks such as code
        generation.  Typically this will be a powerful LLM like GPT‑4 or
        similar.
    :param secondary_model: A secondary model that can be used to verify or
        critique the primary model's output.  This encourages
        collaborative reasoning between models.
    """
    primary_model: BaseAIModel
    secondary_model: BaseAIModel
    aggregator: Optional[Callable[[str, str], str]] = None

    def __post_init__(self) -> None:
        # Internal registry of dynamically added features.  A feature is a bound
        # method exposed by plugins or by manual extension.  Keeping a registry
        # allows the agent to list and invoke features by name.
        self._features: Dict[str, Callable[..., Any]] = {}

        if self.aggregator is None:
            # Default aggregator simply concatenates both responses.
            self.aggregator = lambda a, b: f"Primary: {a}\nSecondary: {b}"

        # Automatically load any plugins located in a "plugins" directory
        # relative to the current working directory.  Users can opt out by
        # passing ``plugins_dir=None`` when calling ``load_plugins`` directly.
        try:
            self.load_plugins()
        except Exception as e:
            # Plugin loading errors should not prevent the agent from working.
            logger.warning("Could not load plugins: %s", e)

    def generate_code(self, instruction: str) -> str:
        """Generate code using the primary model.

        :param instruction: Natural language description of the code to produce.
        :return: Source code as produced by the model.
        """
        return self.primary_model.generate(instruction)

    def critique_code(self, code: str) -> str:
        """Use the secondary model to review or critique code.

        :param code: Code generated by the primary model.
        :return: Feedback or improvements suggested by the secondary model.
        """
        prompt = f"Please review the following code and suggest improvements:\n{code}"
        return self.secondary_model.generate(prompt)

    def collaborate(self, instruction: str) -> str:
        """Generate and critique code, returning an aggregated result.

        :param instruction: The user’s instruction describing what code
            should be generated.
        :return: Aggregated output combining the primary and secondary models.
        """
        code = self.generate_code(instruction)
        critique = self.critique_code(code)
        return self.aggregator(code, critique)

    def add_feature(self, name: str, func: Callable[..., Any]) -> None:
        """Dynamically add a new capability to the agent.

        This method allows you to attach additional functions (features)
        without modifying the core class.  For example, you could define
        ``login_to_service`` and attach it later when you decide to add
        account‑authentication functionality.

        :param name: Name of the feature/method.
        :param func: Callable implementing the feature.  It should accept
            ``self`` as its first argument if it needs access to the agent.
        """
        bound = func.__get__(self, self.__class__)
        setattr(self, name, bound)
        self._features[name] = bound

    def list_features(self) -> List[str]:
        """Return the names of all registered features.

        Features can be added either via plugins or by calling :meth:`add_feature`
        directly.  Knowing which features are available is helpful when building
        higher‑level orchestration on top of the agent.
        """
        return sorted(self._features.keys())

    def call_feature(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Invoke a registered feature by name.

        :param name: The feature name to invoke.
        :param args: Positional arguments forwarded to the feature.
        :param kwargs: Keyword arguments forwarded to the feature.
        :raises AttributeError: If the requested feature does not exist.
        :return: Whatever the feature returns.
        """
        feature = self._features.get(name)
        if feature is None:
            raise AttributeError(f"No such feature registered: {name}")
        return feature(*args, **kwargs)

    def set_aggregator(self, aggregator: Callable[[str, str], str]) -> None:
        """Replace the current aggregator with a new function.

        Aggregators combine outputs from the primary and secondary models into
        a single response.  Use this method to implement voting, scoring or
        other custom aggregation strategies.

        :param aggregator: A callable that takes two strings (code and
            critique) and returns a combined string.
        """
        self.aggregator = aggregator

    def load_plugins(self, plugins_dir: Optional[str] = "plugins") -> None:
        """Load and register plugins from a directory.

        This method searches for Python files in ``plugins_dir`` and
        instantiates any subclasses of :class:`BasePlugin`.  Each plugin's
        :meth:`register` method is then called with this agent instance,
        enabling the plugin to add new features via :meth:`add_feature`.

        :param plugins_dir: Directory containing plugin modules.  If
            ``None``, plugin loading is skipped.
        """
        if not plugins_dir:
            return
        loader = PluginLoader(plugins_dir)
        for plugin in loader.discover():
            try:
                plugin.register(self)
            except Exception as e:
                logger.error("Error registering plugin %s: %s", plugin, e)

    def install_plugins_from_git(
        self,
        repo_url: str,
        dest_dir: str = "plugins",
        branch: str = "main",
        update: bool = True,
        version: Optional[str] = None,
    ) -> None:
        """Install or update plugins from a remote Git repository.

        This method uses the ``git`` command-line tool to clone a repository
        containing plugin files into ``dest_dir``.  If the directory
        already exists and ``update`` is True, a ``git pull`` is executed
        instead of cloning.  After cloning or updating, :meth:`load_plugins`
        is called to register any new plugins.

        :param repo_url: URL of the Git repository containing plugin code.
        :param dest_dir: Local directory where plugins will be stored.
        :param branch: Branch name to checkout when cloning.
        :param update: Whether to update an existing clone via ``git pull``.
        :param version: Optional tag, commit or branch to checkout after
            cloning or updating.
        """
        dest_path = Path(dest_dir)
        if dest_path.is_dir():
            if update:
                try:
                    subprocess.run(
                        ["git", "-C", str(dest_path), "pull"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                except subprocess.CalledProcessError as e:
                    logger.error("Failed to pull plugins: %s", e.stderr.decode().strip())
            else:
                logger.info(
                    "Directory %s already exists. Set update=True to pull latest changes or remove it first.",
                    dest_dir,
                )
                return
        else:
            try:
                subprocess.run(
                    ["git", "clone", "--branch", branch, repo_url, dest_dir],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except subprocess.CalledProcessError as e:
                logger.error("Failed to clone plugins: %s", e.stderr.decode().strip())
                return
        # Optionally checkout a specific version
        if version:
            try:
                subprocess.run(
                    ["git", "-C", str(dest_path), "checkout", version],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except subprocess.CalledProcessError as e:
                logger.error(
                    "Failed to checkout version %s: %s",
                    version,
                    e.stderr.decode().strip(),
                )
        # Load newly installed or updated plugins
        self.load_plugins(dest_dir)

    def collaborate_concurrent(self, instruction: str) -> str:
        """Generate and critique code concurrently before aggregating.

        This method leverages a thread pool to call the primary and secondary
        models in parallel, which can reduce latency when model invocations
        involve network or IO.  It falls back to the standard aggregator to
        combine results.

        :param instruction: A natural language description of the code to
            generate.
        :return: Aggregated output combining the primary and secondary models.
        """
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_code = executor.submit(self.generate_code, instruction)
            code = future_code.result()
            future_critique = executor.submit(self.critique_code, code)
            critique = future_critique.result()
        return self.aggregator(code, critique)

# ---------------------------------------------------------------------------
# Section: Suna plugin
# ---------------------------------------------------------------------------


class SunaPlugin(BasePlugin):
    """A plugin that bridges the agent skeleton with the Suna AI agent.

    This class exposes two features when registered:

    * ``install_suna_agent`` – Clone or update the Suna repository locally.
    * ``run_suna_query`` – Run a query through the Suna agent if it is installed.

    The plugin expects Suna to be placed in a directory (default ``suna_agent``)
    relative to the working directory.  If you wish to use a different
    directory or repository URL, override the attributes ``repo_url`` and
    ``local_dir`` when instantiating the plugin.
    """

    def __init__(self, repo_url: str | None = None, local_dir: str | None = None) -> None:
        # Default repository URL for the Suna project
        self.repo_url = repo_url or "https://github.com/Sangha-code/suna.git"
        # Directory where the Suna repository will be cloned
        self.local_dir = local_dir or "suna_agent"

    def register(self, agent: Agent) -> None:
        """Register Suna integration features with the provided agent."""
        agent.add_feature("install_suna_agent", self.install_suna_agent)
        agent.add_feature("run_suna_query", self.run_suna_query)

    def install_suna_agent(self, update: bool = True, version: Optional[str] = None) -> None:
        """Clone or update the Suna repository.

        Uses ``git`` via subprocess to clone the Suna repository into
        ``self.local_dir``.  If the directory already exists and ``update``
        is True, a ``git pull`` is executed instead of cloning. Optionally,
        a specific tag, branch or commit can be checked out via the
        ``version`` argument.  Because this environment restricts network
        access, cloning may fail unless external connectivity is available.
        """
        dest_path = Path(self.local_dir)
        if dest_path.is_dir():
            if update:
                try:
                    subprocess.run(
                        ["git", "-C", str(dest_path), "pull"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                except subprocess.CalledProcessError as e:
                    print(f"Failed to pull Suna repository: {e.stderr.decode().strip()}")
                    return
            else:
                print(
                    f"Directory {self.local_dir} already exists. Set update=True to pull latest changes or remove it first."
                )
                return
        else:
            try:
                subprocess.run(
                    ["git", "clone", self.repo_url, self.local_dir],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except subprocess.CalledProcessError as e:
                print(f"Failed to clone Suna repository: {e.stderr.decode().strip()}")
                return

        # Checkout a specific version if requested
        if version:
            try:
                subprocess.run(
                    ["git", "-C", str(dest_path), "checkout", version],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except subprocess.CalledProcessError as e:
                print(f"Failed to checkout version {version}: {e.stderr.decode().strip()}")
                return

        print("Suna repository is ready at", dest_path)

    def run_suna_query(self, query: str) -> str:
        """Run a natural‑language query through the Suna agent.

        Executes the Suna entry point script (``suna.py``) as a subprocess and
        sends the query via standard input.  Captures the output and returns it
        as a string.  If Suna is not installed, or dependencies are missing,
        returns an informative message.
        """
        dest_path = Path(self.local_dir)
        suna_entry = dest_path / "suna.py"
        if not suna_entry.is_file():
            return (
                f"Suna agent not found at {suna_entry}. Please run install_suna_agent() "
                "and ensure dependencies are installed."
            )
        try:
            result = subprocess.run(
                ["python", str(suna_entry)],
                input=query.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError as e:
            return f"Error running Suna: {e.stderr.decode().strip()}"

# ---------------------------------------------------------------------------
# Section: Telegram-based agent system and tasks
# ---------------------------------------------------------------------------


def get_env(var_name: str, default: str | None = None) -> str:
    """Helper to fetch environment variables.

    Raises:
        EnvironmentError: If the variable is not set and no default is provided.

    Args:
        var_name: Name of the environment variable.
        default: Default value if variable is absent.

    Returns:
        str: Value of the environment variable.
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise EnvironmentError(f"Environment variable {var_name} is not set.")
    return value


@dataclass
class AgentTask:
    """Represents a discrete task the agent can perform.

    Each task has a name used as the Telegram command, a human readable
    description, a handler function to perform the work, and an optional
    permission requirement. The handler receives the query string and a
    context dictionary and returns a string response.
    """
    name: str
    description: str
    handler: Callable[[str, Dict[str, Any]], str]
    required_permission: str | None = None

    async def execute(self, query: str, context: Dict[str, Any]) -> str:
        """Execute the task asynchronously.

        To avoid blocking the event loop, the handler is invoked in a thread.
        """
        return await asyncio.to_thread(self.handler, query, context)


@dataclass
class AIAgentSystem:
    """Core class managing tasks and user permissions.

    Attributes:
        tasks: Registered tasks keyed by name.
        user_permissions: Map of user ID to list of permissions.
        operation_log_file: Path to the log file recording operations.
    """
    tasks: Dict[str, AgentTask] = field(default_factory=dict)
    user_permissions: Dict[int, List[str]] = field(default_factory=dict)
    operation_log_file: str = 'operations.log'

    def register_task(self, task: AgentTask) -> None:
        """Register a new task with the system."""
        self.tasks[task.name] = task

    def set_user_permissions(self, user_id: int, permissions: List[str]) -> None:
        """Assign a list of permissions to a user."""
        self.user_permissions[user_id] = permissions

    def has_permission(self, user_id: int, permission: str | None) -> bool:
        """Check whether a user has the specified permission."""
        if permission is None:
            return True
        return permission in self.user_permissions.get(user_id, [])

    async def handle_message(self, user_id: int, text: str) -> str:
        """Process an incoming message from a user.

        Messages that do not start with a slash are ignored. Commands are
        extracted and routed to the appropriate task handler.
        """
        if not text.startswith('/'):
            return "الرجاء بدء الأمر بإشارة '/'."
        parts = text[1:].split(' ', 1)
        task_name = parts[0]
        query = parts[1] if len(parts) > 1 else ''
        task = self.tasks.get(task_name)
        if not task:
            return f"المهمة '{task_name}' غير معروفة."
        if not self.has_permission(user_id, task.required_permission):
            return "ليس لديك صلاحية لتنفيذ هذه المهمة."
        context: Dict[str, Any] = {'log_file': self.operation_log_file}
        try:
            response = await task.execute(query, context)
            self.log_operation(user_id, task.name, query)
            return response
        except Exception as exc:
            logger.exception("Task execution failed", exc_info=exc)
            return f"حدث خطأ أثناء تنفيذ المهمة: {exc}"

    def log_operation(self, user_id: int, task_name: str, query: str) -> None:
        """Append an entry to the operation log."""
        try:
            with open(self.operation_log_file, 'a', encoding='utf-8') as f:
                f.write(f"user_id={user_id}; task={task_name}; query={query}\n")
        except Exception:
            logger.exception("Failed to write operation log")


# Task handlers

def code_task_handler(query: str, context: Dict[str, Any]) -> str:
    """Generate code based on a text description using OpenAI.

    If the OpenAI library is unavailable, a placeholder message is returned.
    """
    prompt = (
        "أنت مساعد برمجي. اكتب الكود المطلوب بناءً على الوصف التالي.\n\n"
        f"الطلب: {query}\n\n"
        "الكود:\n"
    )
    if openai is None:
        return "[نموذج الذكاء الاصطناعي غير متوفر حالياً]"
    api_key = get_env('OPENAI_API_KEY')
    openai.api_key = api_key
    completion = openai.ChatCompletion.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message['content']


def news_task_handler(query: str, context: Dict[str, Any]) -> str:
    """Fetch news using an external API key."""
    news_api_key = os.getenv('NEWS_API_KEY')
    if not news_api_key:
        return "يجب إعداد NEWS_API_KEY في ملف البيئة."
    # Placeholder for actual API integration.
    return "[سيتم هنا عرض موجز الأخبار بعد تنفيذ الطلب إلى News API]"


def github_search_handler(query: str, context: Dict[str, Any]) -> str:
    """Search GitHub for repositories or issues matching the query."""
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        return "يجب إعداد GITHUB_TOKEN في ملف البيئة."
    # Placeholder for actual GitHub API call.
    return f"[بحث GitHub عن '{query}' سيُرجع نتائج هنا]"


SAFE_DIR = os.getenv('SAFE_DIR', '/tmp')


def file_task_handler(query: str, context: Dict[str, Any]) -> str:
    """Read or write files within a safe directory.

    The query should be of the form "read <filename>" or "write <filename> <content>".
    Only files within SAFE_DIR are accessible. Attempts to access other paths
    are rejected.
    """
    parts = query.split(' ', 2)
    if len(parts) < 2:
        return "الاستخدام: read <file> أو write <file> <content>"
    action, filename = parts[0], parts[1]
    safe_path = os.path.abspath(os.path.join(SAFE_DIR, filename))
    if not safe_path.startswith(os.path.abspath(SAFE_DIR)):
        return "اسم الملف غير صالح."
    if action == 'read':
        try:
            with open(safe_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"محتوى {filename}:\n{content}"
        except FileNotFoundError:
            return "الملف غير موجود."
        except Exception as exc:
            return f"خطأ في قراءة الملف: {exc}"
    elif action == 'write':
        if len(parts) < 3:
            return "يرجى تحديد المحتوى بعد اسم الملف عند الكتابة."
        content = parts[2]
        try:
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"تمت كتابة المحتوى إلى {filename}."
        except Exception as exc:
            return f"خطأ في كتابة الملف: {exc}"
    else:
        return "العملية غير معروفة، استخدم read أو write."


def log_task_handler(query: str, context: Dict[str, Any]) -> str:
    """Return the contents of the operation log file."""
    log_file = context.get('log_file', 'operations.log')
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"سجل العمليات:\n{content}"
    except FileNotFoundError:
        return "سجل العمليات غير موجود بعد."
    except Exception as exc:
        return f"حدث خطأ أثناء قراءة السجل: {exc}"


def research_task_handler(query: str, context: Dict[str, Any]) -> str:
    """Provide a general research summary for the given topic."""
    prompt = (
        "أنت مساعد بحث. قم بإجراء بحث موجز وقدم ملخصاً واضحاً حول الموضوع التالي:\n\n"
        f"الموضوع: {query}\n\n"
        "الملخص:\n"
    )
    if openai is None:
        return "[ميزة البحث غير متوفرة حالياً – لم يتم تثبيت openai]"
    api_key = get_env('OPENAI_API_KEY')
    openai.api_key = api_key
    completion = openai.ChatCompletion.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message['content']


def video_task_handler(query: str, context: Dict[str, Any]) -> str:
    """Generate a video plan or script based on a text description."""
    prompt = (
        "أنت منتج فيديو. بناءً على الوصف التالي، قم بإعداد مخطط فيديو مفصل يتضمن سيناريو مختصر، "
        "واللقطات الأساسية، والتعليمات اللازمة لإنتاج الفيديو.\n\n"
        f"الوصف: {query}\n\n"
        "المخطط:\n"
    )
    if openai is None:
        return "[ميزة صناعة الفيديو غير متوفرة حالياً – لم يتم تثبيت openai]"
    api_key = get_env('OPENAI_API_KEY')
    openai.api_key = api_key
    completion = openai.ChatCompletion.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message['content']


def app_task_handler(query: str, context: Dict[str, Any]) -> str:
    """Draft an application or website concept based on a description."""
    prompt = (
        "أنت مطور تطبيقات ومواقع. باستخدام الوصف التالي، قم بإعداد مخطط لتطبيق أو موقع يتضمن "
        "الوظائف الرئيسية، الهيكلية، والتقنيات المحتملة المستخدمة في البناء.\n\n"
        f"الوصف: {query}\n\n"
        "المخطط:\n"
    )
    if openai is None:
        return "[ميزة تطوير التطبيقات غير متوفرة حالياً – لم يتم تثبيت openai]"
    api_key = get_env('OPENAI_API_KEY')
    openai.api_key = api_key
    completion = openai.ChatCompletion.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message['content']


def multi_task_handler(query: str, context: Dict[str, Any]) -> str:
    """
    Execute a coordinated workflow using both the code and research agents.

    This handler demonstrates how two agents—one that writes code and another
    that performs research/audit—can work together in a synchronized manner.
    """
    # Step 1: Generate code using the existing code task handler
    code_output = code_task_handler(query, context)
    # If code generation failed due to missing OpenAI, propagate the message
    if code_output.startswith('[') and 'غير متوفر' in code_output:
        return code_output
    # Step 2: Write the generated code to a file in the SAFE_DIR
    code_filename = 'generated_code.py'
    code_path = os.path.abspath(os.path.join(SAFE_DIR, code_filename))
    try:
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(code_output)
    except Exception as exc:
        logger.exception("Failed to write generated code file", exc_info=exc)
        return f"تعذر حفظ الكود المولد في ملف: {exc}"
    # Step 3: Perform research/audit on the generated code
    if openai is None:
        return ("تم إنشاء الكود وحفظه في الملف: " +
                f"{code_filename}، لكن خدمة التدقيق غير متوفرة حالياً.")
    audit_prompt = (
        "أنت باحث ومدقق برمجيات. لديك الكود التالي. قم بتحليل الكود وتقديم مراجعة "
        "أو تحسينات وإيضاحات عند الحاجة:\n\n"
        f"{code_output}\n\n"
        "المراجعة أو التحسينات:\n"
    )
    try:
        api_key = get_env('OPENAI_API_KEY')
        openai.api_key = api_key
        audit_completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": audit_prompt}]
        )
        audit_response = audit_completion.choices[0].message['content']
    except Exception as exc:
        logger.exception("Audit step failed", exc_info=exc)
        return ("تم إنشاء الكود وحفظه في الملف: " +
                f"{code_filename}، ولكن حدث خطأ أثناء تنفيذ التدقيق: {exc}")
    # Step 4: Save the audit to a separate file
    audit_filename = 'code_audit.txt'
    audit_path = os.path.abspath(os.path.join(SAFE_DIR, audit_filename))
    try:
        with open(audit_path, 'w', encoding='utf-8') as f:
            f.write(audit_response)
    except Exception as exc:
        logger.exception("Failed to write audit file", exc_info=exc)
        return ("تم إنشاء الكود وحفظه في الملف: " +
                f"{code_filename}، وتم تنفيذ التدقيق بنجاح، ولكن حدث خطأ أثناء حفظ المراجعة: {exc}\n\n"
                f"المراجعة:\n{audit_response}")
    # Step 5: Construct a user-friendly summary
    summary_intro = (
        "تم تنفيذ المهمة المتزامنة بنجاح. تم إنشاء الكود وحفظه في الملف "
        f"{code_filename} وحفظ مراجعة الكود في الملف {audit_filename}. "
        "يمكنك قراءة الملفات باستخدام أمر /file.\n\n"
    )
    snippet_length = 500
    code_snippet = code_output[:snippet_length] + ("..." if len(code_output) > snippet_length else "")
    audit_snippet = audit_response[:snippet_length] + ("..." if len(audit_response) > snippet_length else "")
    summary_body = (
        f"مقتطف من الكود:\n{code_snippet}\n\n"
        f"مقتطف من المراجعة:\n{audit_snippet}"
    )
    return summary_intro + summary_body

# Telegram bot handlers

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greet the user when they start the bot."""
    user = update.effective_user
    await update.message.reply_text(
        f"مرحباً {user.first_name}! استخدم الأمر /help لعرض قائمة المهام."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message listing available tasks."""
    system: AIAgentSystem = context.bot_data['agent_system']
    help_lines = ["المهام المتاحة:"]
    for task in system.tasks.values():
        help_lines.append(f"/{task.name} – {task.description}")
    await update.message.reply_text("\n".join(help_lines))


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle arbitrary text messages and route commands to tasks."""
    user_id = update.effective_user.id
    text = update.message.text or ''
    system: AIAgentSystem = context.bot_data['agent_system']
    response = await system.handle_message(user_id, text)
    await update.message.reply_text(response)

# System initialization


def initialize_agent_system() -> AIAgentSystem:
    """Create and initialize the agent system with all tasks registered."""
    system = AIAgentSystem()
    # Register base tasks
    system.register_task(AgentTask(
        name='code',
        description='كتابة كود برمجي اعتماداً على وصف نصي',
        handler=code_task_handler,
        required_permission='write_code'
    ))
    system.register_task(AgentTask(
        name='news',
        description='جلب موجز للأخبار الحالية',
        handler=news_task_handler,
        required_permission='general'
    ))
    system.register_task(AgentTask(
        name='ghsearch',
        description='البحث في GitHub عن مستودعات أو قضايا',
        handler=github_search_handler,
        required_permission='github_read'
    ))
    system.register_task(AgentTask(
        name='file',
        description='قراءة أو كتابة ملفات داخل دليل آمن',
        handler=file_task_handler,
        required_permission='file_access'
    ))
    system.register_task(AgentTask(
        name='log',
        description='عرض سجل العمليات للنظام (للمسؤول فقط)',
        handler=log_task_handler,
        required_permission='view_logs'
    ))
    # Register newly added tasks
    system.register_task(AgentTask(
        name='research',
        description='إجراء بحث عام وتقديم ملخص للموضوع',
        handler=research_task_handler,
        required_permission='general'
    ))
    system.register_task(AgentTask(
        name='video',
        description='إعداد مخطط لصناعة فيديو بناءً على وصف نصي',
        handler=video_task_handler,
        required_permission='create_video'
    ))
    system.register_task(AgentTask(
        name='app',
        description='تخطيط وإنشاء مفهوم لتطبيق أو موقع',
        handler=app_task_handler,
        required_permission='create_app'
    ))
    system.register_task(AgentTask(
        name='multi',
        description='تنفيذ مهام كتابة الكود والبحث المتزامن',
        handler=multi_task_handler,
        required_permission='multi_agent'
    ))
    # Assign full permissions to admin if present
    admin_id = int(os.getenv('ADMIN_TELEGRAM_ID', '0'))
    if admin_id:
        system.set_user_permissions(admin_id, [
            'write_code', 'general', 'github_read', 'file_access',
            'view_logs', 'create_video', 'create_app', 'multi_agent'
        ])
    return system


def run_telegram_bot() -> None:
    """Initialize the agent system and start the Telegram bot.

    This function builds the Telegram application, registers handlers and starts polling.
    """
    if ApplicationBuilder is None:
        raise RuntimeError("telegram library is not available")
    system = initialize_agent_system()
    telegram_token = get_env('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(telegram_token).build()
    application.bot_data['agent_system'] = system
    application.add_handler(CommandHandler('start', cmd_start))
    application.add_handler(CommandHandler('help', cmd_help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    logger.info("Starting AI Agent Telegram bot...")
    application.run_polling()

# Stand-alone execution entry point

if __name__ == '__main__':
    # If this file is run directly, start the Telegram bot.
    run_telegram_bot()