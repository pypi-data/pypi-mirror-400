# Core
from .core.scheduler import SkillScheduler
from .core.skill import SkillManager, Skill
from .core.executor import Executor
from .core.matcher import RuleMatcher

# Utils
from .utils.config import Config

# Observability (optional imports)
try:
    from .observability.logging_config import configure_logging
    from .observability.metrics import (
        MetricsCallback,
        MetricsRegistry,
        get_registry,
        register_callback
    )
except ImportError:
    # 如果这些模块有问题，不影响主要功能
    configure_logging = None
    MetricsCallback = None
    MetricsRegistry = None
    get_registry = None
    register_callback = None

# Parsers
try:
    from .parsers.markdown_parser import MarkdownSkillParser, parse_skill_definition
except ImportError:
    MarkdownSkillParser = None
    parse_skill_definition = None

__version__ = "1.0.0"

__all__ = [
    # Core
    "SkillScheduler",
    "SkillManager",
    "Skill",
    "Executor",
    "RuleMatcher",
    "Config",
    # Observability
    "configure_logging",
    "MetricsCallback",
    "MetricsRegistry",
    "get_registry",
    "register_callback",
    # Parsers
    "MarkdownSkillParser",
    "parse_skill_definition",
]
