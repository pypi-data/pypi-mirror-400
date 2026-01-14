"""Module for managing policies in PromptOps."""


import yaml
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from .exceptions import ConfigurationError

POLICY_FILE = Path("promptops.yaml")
logger = logging.getLogger("promptops.policies")

class PolicyManager:
    """
    Manages loading, validating, querying, and evaluating policies.
    Supports dynamic reload and extensible policy types.
    """
    def __init__(self, policy_file: Path = POLICY_FILE, reload_interval: Optional[int] = None):
        self.policy_file = policy_file
        self._lock = threading.RLock()
        self._policies: Dict[str, Any] = {}
        self._last_loaded = 0.0
        self._reload_interval = reload_interval
        self._watch_thread = None
        self._callbacks: list = []
        self.load()
        if reload_interval:
            self._start_watcher()

    def load(self):
        with self._lock:
            if not self.policy_file.exists():
                logger.warning(f"Policy file not found: {self.policy_file}")
                self._policies = {}
                return
            try:
                data = yaml.safe_load(self.policy_file.read_text())
                self._policies = data.get("policies", {}) if data else {}
                self._last_loaded = time.time()
                logger.info(f"Loaded policies from {self.policy_file}")
            except Exception as e:
                logger.error(f"Failed to load policies: {e}")
                raise ConfigurationError(f"Failed to load policies: {e}", cause=e)

    def get(self, policy_type: str, name: Optional[str] = None) -> Any:
        with self._lock:
            if name:
                return self._policies.get(policy_type, {}).get(name)
            return self._policies.get(policy_type, {})

    def set(self, policy_type: str, name: str, value: Any):
        with self._lock:
            if policy_type not in self._policies:
                self._policies[policy_type] = {}
            self._policies[policy_type][name] = value
            self._save()
            self._notify(policy_type, name, value)

    def evaluate(self, policy_type: str, name: str, context: dict) -> bool:
        """Evaluate a policy with the given context. Returns True if allowed."""
        policy = self.get(policy_type, name)
        if not policy:
            logger.warning(f"Policy not found: {policy_type}.{name}")
            return True  # Default allow if not found
        # Example: support for simple allow/deny policies
        if isinstance(policy, dict) and "rule" in policy:
            rule = policy["rule"]
            try:
                return eval(rule, {}, context)
            except Exception as e:
                logger.error(f"Policy rule eval failed: {e}")
                return False
        return bool(policy)

    def _save(self):
        try:
            data = {"policies": self._policies}
            self.policy_file.write_text(yaml.safe_dump(data))
            logger.info(f"Saved policies to {self.policy_file}")
        except Exception as e:
            logger.error(f"Failed to save policies: {e}")

    def _start_watcher(self):
        def watch():
            last_mtime = self.policy_file.stat().st_mtime if self.policy_file.exists() else 0
            while True:
                time.sleep(self._reload_interval)
                if not self.policy_file.exists():
                    continue
                mtime = self.policy_file.stat().st_mtime
                if mtime > last_mtime:
                    logger.info("Policy file changed, reloading...")
                    self.load()
                    last_mtime = mtime
        self._watch_thread = threading.Thread(target=watch, daemon=True)
        self._watch_thread.start()

    def add_callback(self, callback: Callable[[str, str, Any], None]):
        self._callbacks.append(callback)

    def _notify(self, policy_type: str, name: str, value: Any):
        for cb in self._callbacks:
            try:
                cb(policy_type, name, value)
            except Exception as e:
                logger.error(f"Policy callback failed: {e}")

def load_policies() -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    if POLICY_FILE.exists():
        return yaml.safe_load(POLICY_FILE.read_text()).get("policies", {})
    return {}
