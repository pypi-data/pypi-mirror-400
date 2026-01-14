
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("promptops.renderer")

try:
    from jinja2 import Template, TemplateError
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

def render_template(template: str, inputs: dict, engine: str = "auto", safe: bool = True, defaults: Optional[dict] = None) -> str:
    """
    Render a template with the given inputs.
    Supports 'jinja2' (if installed) or 'format' (default).
    If safe=True, missing keys are replaced with blanks.
    """
    data = dict(defaults or {})
    data.update(inputs or {})
    try:
        # Auto-detect: if template has {{ or {% it's Jinja2, otherwise format
        if engine == "jinja2" or (engine == "auto" and JINJA2_AVAILABLE and ("{{" in template or "{%" in template)):
            return Template(template).render(**data)
        elif engine == "format" or engine == "auto":
            if safe:
                return _safe_format(template, data)
            return template.format(**data)
        else:
            raise ValueError(f"Unknown template engine: {engine}")
    except Exception as e:
        logger.error(f"Template render failed: {e}")
        raise

def _safe_format(template: str, data: dict) -> str:
    """Format with blanks for missing keys."""
    class SafeDict(dict):
        def __missing__(self, key):
            return ""
    return template.format_map(SafeDict(data))

def validate_template(template: str, engine: str = "auto") -> bool:
    """Validate template syntax for the given engine."""
    try:
        if engine == "jinja2" or (engine == "auto" and JINJA2_AVAILABLE and "{{" in template):
            Template(template)
        elif engine == "format" or engine == "auto":
            # Validate format string syntax by parsing it
            import string
            list(string.Formatter().parse(template))
        else:
            raise ValueError(f"Unknown template engine: {engine}")
        return True
    except Exception as e:
        logger.error(f"Template validation failed: {e}")
        return False

def preview_template(template: str, sample_inputs: dict, engine: str = "auto") -> str:
    """Render a template with sample inputs for preview."""
    return render_template(template, sample_inputs, engine=engine)
