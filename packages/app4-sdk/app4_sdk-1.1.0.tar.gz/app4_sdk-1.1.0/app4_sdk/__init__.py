"""
App4 Plugin SDK for Python

A Python SDK for building App4 plugins that can integrate with the App4 platform
via gRPC protocol.

Example:
    from app4_sdk import Plugin, Manifest, ActionMeta, serve

    class MyPlugin(Plugin):
        def manifest(self) -> Manifest:
            return Manifest(name="my-plugin", version="1.0.0")

        def list_actions(self) -> list[ActionMeta]:
            return [...]

        def execute_action(self, ctx, action_name, data, config) -> dict:
            ...

    if __name__ == "__main__":
        serve(MyPlugin())
"""

from app4_sdk.plugin.types import (
    Manifest,
    ActionMeta,
    ParamSchema,
    ParamOption,
    ActionExample,
    AnalyzerRules,
    PatternSuggestion,
)
from app4_sdk.plugin.plugin import Plugin
from app4_sdk.plugin.context import Context, BaseContext
from app4_sdk.plugin.server import serve, serve_with_registry, serve_with_auto_registry
from app4_sdk.plugin.registry import RegistryClient, RegistryConfig
from app4_sdk.plugin.helpers import (
    get_config_string,
    get_config_bool,
    get_config_int,
    get_config_float,
    get_config_value,
    get_config_list,
    get_config_dict,
    require_config,
    get_nested_value,
    set_nested_value,
    is_namespaced_path,
    parse_action_name,
    copy_dict,
    merge_dicts,
)

__version__ = "1.0.0"
__all__ = [
    # Types
    "Manifest",
    "ActionMeta",
    "ParamSchema",
    "ParamOption",
    "ActionExample",
    "AnalyzerRules",
    "PatternSuggestion",
    # Plugin
    "Plugin",
    "Context",
    "BaseContext",
    # Server
    "serve",
    "serve_with_registry",
    "serve_with_auto_registry",
    # Registry
    "RegistryClient",
    "RegistryConfig",
    # Helpers
    "get_config_string",
    "get_config_bool",
    "get_config_int",
    "get_config_float",
    "get_config_value",
    "get_config_list",
    "get_config_dict",
    "require_config",
    "get_nested_value",
    "set_nested_value",
    "is_namespaced_path",
    "parse_action_name",
    "copy_dict",
    "merge_dicts",
]
