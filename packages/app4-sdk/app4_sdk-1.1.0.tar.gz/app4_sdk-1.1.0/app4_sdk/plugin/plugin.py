"""
Plugin interface for App4 SDK.

This module defines the base Plugin class that all plugins must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from app4_sdk.plugin.types import (
    Manifest,
    ActionMeta,
    AnalyzerRules,
    PluginStatus,
    PluginResource,
    PluginStats,
)
from app4_sdk.plugin.context import Context


class Plugin(ABC):
    """
    Abstract base class for App4 plugins.

    All plugins must implement this interface to be compatible
    with the App4 platform.

    Example:
        class MyPlugin(Plugin):
            def manifest(self) -> Manifest:
                return Manifest(
                    name="my-plugin",
                    version="1.0.0",
                    description="My awesome plugin",
                    capabilities=["actions", "provider"],
                )

            def list_actions(self) -> list[ActionMeta]:
                return [
                    ActionMeta(
                        name="my-plugin:greet",
                        description="Say hello",
                        inputs={"name": ParamSchema(name="name", type="string")},
                        outputs={"message": ParamSchema(name="message", type="string")},
                    ),
                ]

            def execute_action(
                self, ctx: Context, action_name: str, data: dict, config: dict
            ) -> dict:
                if action_name == "my-plugin:greet":
                    name = data.get("name", "World")
                    return {"message": f"Hello, {name}!"}
                raise ValueError(f"Unknown action: {action_name}")

            def init_provider(self, name: str, config: dict) -> None:
                # Initialize provider connection
                pass

            def close_provider(self, name: str) -> None:
                # Close provider connection
                pass
    """

    @abstractmethod
    def manifest(self) -> Manifest:
        """
        Return the plugin manifest.

        The manifest describes the plugin's identity and capabilities.
        """
        pass

    @abstractmethod
    def list_actions(self) -> list[ActionMeta]:
        """
        Return a list of all actions provided by this plugin.

        Each action should have complete metadata including inputs,
        outputs, and examples.
        """
        pass

    @abstractmethod
    def execute_action(
        self,
        ctx: Context,
        action_name: str,
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute an action.

        Args:
            ctx: Execution context with logging and variable access
            action_name: Name of the action to execute (e.g., "mongo:find")
            data: Input data for the action
            config: Configuration for the action

        Returns:
            Result dictionary

        Raises:
            ValueError: If action is unknown
            Exception: If action execution fails
        """
        pass

    def init_provider(self, name: str, config: dict[str, Any]) -> None:
        """
        Initialize a provider instance.

        Override this method to set up connections or resources
        for a named provider instance.

        Args:
            name: Provider instance name (e.g., "default", "analytics")
            config: Provider configuration
        """
        pass

    def close_provider(self, name: str) -> None:
        """
        Close a provider instance.

        Override this method to clean up connections or resources
        for a named provider instance.

        Args:
            name: Provider instance name
        """
        pass

    def health_check(self) -> tuple[bool, str, dict[str, str]]:
        """
        Check plugin health.

        Override this method to provide custom health checking.

        Returns:
            Tuple of (healthy, message, details)
        """
        return True, "OK", {}

    def get_status(self) -> PluginStatus:
        """
        Get detailed plugin status.

        Override this method to provide custom status information
        including resources and statistics.

        Returns:
            PluginStatus with manifest, uptime, resources, and stats
        """
        return PluginStatus(
            manifest=self.manifest(),
            uptime_seconds=0,
            resources=[],
            stats=PluginStats(),
        )

    def analyzer_rules(self) -> Optional[AnalyzerRules]:
        """
        Return analyzer rules for this plugin.

        Override this method to provide validation rules for the
        meta-model analyzer.

        Returns:
            AnalyzerRules or None if no special rules
        """
        return None

    def shutdown(self) -> None:
        """
        Gracefully shutdown the plugin.

        Override this method to clean up all resources before shutdown.
        """
        pass
