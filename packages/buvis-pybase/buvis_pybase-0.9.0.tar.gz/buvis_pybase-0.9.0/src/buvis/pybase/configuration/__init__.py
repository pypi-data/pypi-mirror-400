"""Configuration management with precedence: CLI > ENV > YAML > Defaults.

Usage::

    from buvis.pybase.configuration import get_settings, buvis_options

    @click.command()
    @buvis_options
    @click.pass_context
    def main(ctx):
        settings = get_settings(ctx)
        if settings.debug:
            ...

Precedence (highest to lowest):
    1. CLI arguments (--debug, --log-level, etc.)
    2. Environment variables (BUVIS_* prefix)
    3. YAML config file (~/.config/buvis/config.yaml)
    4. Model defaults
"""

from .exceptions import (
    ConfigurationError,
    ConfigurationKeyNotFoundError,
    MissingEnvVarError,
)
from .loader import ConfigurationLoader
from .click_integration import buvis_options, get_settings
from .resolver import ConfigResolver
from .source import ConfigSource
from .settings import GlobalSettings, ToolSettings
from .validators import (
    MAX_JSON_ENV_SIZE,
    MAX_NESTING_DEPTH,
    SafeLoggingMixin,
    SecureSettingsMixin,
    get_model_depth,
    is_sensitive_field,
    validate_json_env_size,
    validate_nesting_depth,
)

__all__ = [
    "ConfigurationKeyNotFoundError",
    "ConfigurationError",
    "MissingEnvVarError",
    "ConfigurationLoader",
    "ConfigResolver",
    "ConfigSource",
    "buvis_options",
    "get_settings",
    "MAX_NESTING_DEPTH",
    "MAX_JSON_ENV_SIZE",
    "SafeLoggingMixin",
    "SecureSettingsMixin",
    "get_model_depth",
    "is_sensitive_field",
    "validate_json_env_size",
    "validate_nesting_depth",
    "ToolSettings",
    "GlobalSettings",
]
