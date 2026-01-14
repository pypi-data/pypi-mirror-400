
import logging
from .loader import load_prompt
from .renderer import render_template
from .approval import enforce_approval
from .guard import enforce_safety, Guard
from .providers.openai_provider import OpenAIProvider
from .rollback.engine import maybe_rollback
from .rollback.store import record
from .policies import load_policies
from .env import get_env
from .cost.budget import BudgetPool
from .testing.runner import run_tests
from .exceptions import TestFailureError


logger = logging.getLogger("promptops.prompt")

class Prompt:
    """
    Represents a prompt with config, provider, policies, hooks, and execution logic.
    Supports multi-provider, hooks, cost tracking, and robust error handling.
    """
    def __init__(self, name, version, config):
        self.name = name
        self.version = version
        self.config = config
        self.env = get_env()
        self.policies = load_policies()
        self.provider = self._init_provider()
        self.guard = Guard()
        self.budget_pool = BudgetPool()
        self._pre_hooks = []
        self._post_hooks = []

    def _init_provider(self):
        # Support for multiple providers in config
        provider_type = self.config.get("provider", "openai").lower()
        if provider_type == "openai":
            return OpenAIProvider()
        # Add more providers here as needed
        raise ValueError(f"Unknown provider: {provider_type}")

    @classmethod
    def load(cls, name, version):
        return cls(name, version, load_prompt(name, version))

    def add_pre_hook(self, hook):
        self._pre_hooks.append(hook)

    def add_post_hook(self, hook):
        self._post_hooks.append(hook)

    def render(self, inputs):
        return render_template(self.config["template"], inputs)

    def run(self, inputs, track_cost: bool = True, run_tests_flag: bool = False):
        try:
            for hook in self._pre_hooks:
                hook(self, inputs)
            enforce_approval(self.config, self.env)
            text = self.render(inputs)
            self.guard.enforce(text, self.env, {"prompt": self})
            if track_cost:
                self._track_cost(text)
            result = self.provider.run(text)
            for hook in self._post_hooks:
                hook(self, inputs, result)
            if run_tests_flag:
                self._run_tests(result)
            return result
        except Exception as e:
            logger.error(f"Prompt run failed: {e}")
            record(self.name)
            if "rollback" in self.policies:
                maybe_rollback(self, self.policies["rollback"])
            raise

    def _track_cost(self, text):
        # Example: estimate and record cost
        if hasattr(self.provider, "estimate_cost"):
            cost = self.provider.estimate_cost(text)
            self.budget_pool.record(self.name, cost)
            logger.info(f"Cost for {self.name}: ${cost:.4f}")

    def _run_tests(self, result):
        tests = self.config.get("tests", [])
        if tests:
            report = run_tests(self, self.provider, tests, result=result)
            if not report.passed:
                logger.error(f"Prompt test failed: {report.summary()}")
                raise TestFailureError("Prompt test failed", test_name=self.name)

    @classmethod
    def load(cls, name, version):
        return cls(name, version, load_prompt(name, version))

    def render(self, inputs):
        return render_template(self.config["template"], inputs)

    def run(self, inputs):
        try:
            enforce_approval(self.config, self.env)
            text = self.render(inputs)
            enforce_safety(text, self.env)
            return self.provider.run(text)

        except Exception:
            record(self.name)
            if "rollback" in self.policies:
                maybe_rollback(self, self.policies["rollback"])
            raise
