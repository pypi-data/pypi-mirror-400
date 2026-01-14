"""Module for loading prompt definitions from various sources with caching and validation."""


import yaml
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from .exceptions import ConfigurationError
try:
    import requests
except ImportError:
    requests = None
try:
    import importlib.resources as pkg_resources
except ImportError:
    pkg_resources = None

logger = logging.getLogger("promptops.loader")

_prompt_cache: Dict[str, Any] = {}

def load_prompt(
    name: str,
    version: str,
    source: str = "local",
    validate: bool = True,
    reload: bool = False,
    schema: Optional[dict] = None,
    env_interpolate: bool = True
) -> dict:
    """
    Load a prompt definition by name and version from the given source.
    Supports local, remote, or package sources. Caches by default.
    Raises ConfigurationError on failure.
    """
    cache_key = f"{source}:{name}:{version}"
    if not reload and cache_key in _prompt_cache:
        logger.debug(f"Loaded prompt {name} v{version} from cache.")
        data = _prompt_cache[cache_key]
        # Re-validate even cached prompts if validation is requested
        if validate:
            _validate_prompt(data, name, version)
            if schema:
                _validate_schema(data, schema)
        return data
    try:
        if source == "local":
            path = Path(f"prompts/{name}/{version}.yaml")
            if not path.exists():
                raise ConfigurationError(f"Prompt file not found: {path}", config_key="prompt_path")
            raw = path.read_text()
        elif source == "package":
            if not pkg_resources:
                raise ConfigurationError("importlib.resources not available", config_key="package")
            try:
                raw = pkg_resources.files("prompts").joinpath(f"{name}/{version}.yaml").read_text()
            except Exception as e:
                raise ConfigurationError(f"Prompt not found in package: {name}/{version}", cause=e)
        elif source == "remote":
            if not requests:
                raise ConfigurationError("requests not installed", config_key="remote")
            url = f"{name}/{version}.yaml" if name.startswith("http") else f"https://{name}/{version}.yaml"
            resp = requests.get(url)
            if resp.status_code != 200:
                raise ConfigurationError(f"Remote prompt not found: {url}", config_key="remote_url")
            raw = resp.text
        else:
            raise ConfigurationError(f"Unknown prompt source: {source}", config_key="source")
        if env_interpolate:
            raw = _interpolate_env(raw)
        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            raise ConfigurationError("Prompt YAML must be a dict", config_key="prompt_yaml")
        if validate:
            _validate_prompt(data, name, version)
            if schema:
                _validate_schema(data, schema)
        _prompt_cache[cache_key] = data
        logger.info(f"Loaded prompt {name} v{version} from {source}.")
        return data
    except Exception as e:
        logger.error(f"Failed to load prompt {name} v{version}: {e}")
        if isinstance(e, ConfigurationError):
            raise
        raise ConfigurationError(f"Failed to load prompt: {e}", cause=e)

def _validate_prompt(data: dict, name: str, version: str):
    if "name" in data and data["name"] != name:
        raise ConfigurationError(f"Prompt name mismatch: {data['name']} != {name}", config_key="name")
    if "version" in data and str(data["version"]) != str(version):
        raise ConfigurationError(f"Prompt version mismatch: {data['version']} != {version}", config_key="version")
    # Add more schema checks as needed

def _validate_schema(data: dict, schema: dict):
    """Validate prompt data against a schema (very basic)."""
    for key, required_type in schema.items():
        if key not in data:
            raise ConfigurationError(f"Missing required key: {key}", config_key=key)
        if not isinstance(data[key], required_type):
            raise ConfigurationError(f"Key {key} must be {required_type}, got {type(data[key])}", config_key=key)

def _interpolate_env(raw: str) -> str:
    """Replace ${VAR} in YAML with environment variables."""
    import re
    def repl(match):
        var = match.group(1)
        return os.environ.get(var, match.group(0))
    return re.sub(r'\$\{([A-Za-z0-9_]+)\}', repl, raw)

def clear_prompt_cache():
    """Clear the prompt cache."""
    _prompt_cache.clear()
    logger.info("Prompt cache cleared.")

def get_prompt_cache_keys() -> List[str]:
    """Return a list of cache keys for loaded prompts."""
    return list(_prompt_cache.keys())

def list_prompt_versions(name: str, source: str = "local") -> List[str]:
    """List available versions for a prompt name from the given source."""
    if source == "local":
        prompt_dir = Path(f"prompts/{name}")
        if not prompt_dir.exists() or not prompt_dir.is_dir():
            return []
        return [p.stem for p in prompt_dir.glob("*.yaml")]
    # Could add remote/package support here
    return []
