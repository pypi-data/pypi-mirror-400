"""
Core types for App4 Plugin SDK.

This module defines all the data structures used throughout the SDK,
including plugin manifests, action metadata, and analyzer rules.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


class UIComponent(str, Enum):
    """UI component types for action parameters."""
    TEXT_INPUT = "TextInput"
    TEXT_AREA = "TextArea"
    NUMBER_INPUT = "NumberInput"
    SELECT = "Select"
    MULTI_SELECT = "MultiSelect"
    CHECKBOX = "Checkbox"
    SWITCH = "Switch"
    DATE_PICKER = "DatePicker"
    TIME_PICKER = "TimePicker"
    COLOR_PICKER = "ColorPicker"
    FILE_UPLOAD = "FileUpload"
    CODE_EDITOR = "CodeEditor"
    JSON_EDITOR = "JsonEditor"
    SCHEMA_REF = "SchemaRef"
    PIPELINE_REF = "PipelineRef"
    PROVIDER_REF = "ProviderRef"


@dataclass
class ParamOption:
    """Option for select-type parameters."""
    label: str
    value: Any
    description: str = ""


@dataclass
class ParamSchema:
    """
    Parameter schema for action inputs and outputs.

    Describes the type, requirements, and UI representation
    of an action parameter.
    """
    name: str
    type: str  # "string", "number", "boolean", "array", "object"
    required: bool = False
    description: str = ""
    default: Any = None
    ui_component: Optional[str] = None
    options: list[ParamOption] = field(default_factory=list)
    items_type: Optional[str] = None  # For arrays: type of items
    properties: dict[str, "ParamSchema"] = field(default_factory=dict)  # For objects

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "description": self.description,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.ui_component:
            result["uiComponent"] = self.ui_component
        if self.options:
            result["options"] = [
                {"label": o.label, "value": o.value, "description": o.description}
                for o in self.options
            ]
        if self.items_type:
            result["itemsType"] = self.items_type
        if self.properties:
            result["properties"] = {k: v.to_dict() for k, v in self.properties.items()}
        return result


@dataclass
class ActionExample:
    """
    Example usage for an action.

    Provides sample input/output for documentation and testing.
    """
    name: str
    description: str = ""
    input: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "input": self.input,
            "config": self.config,
            "output": self.output,
        }


@dataclass
class ActionMeta:
    """
    Metadata for a plugin action.

    Describes what the action does, its inputs, outputs, and examples.
    This metadata is used by Studio UI for action configuration.
    """
    name: str
    category: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    inputs: dict[str, ParamSchema] = field(default_factory=dict)
    outputs: dict[str, ParamSchema] = field(default_factory=dict)
    examples: list[ActionExample] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "tags": self.tags,
            "inputs": {k: v.to_dict() for k, v in self.inputs.items()},
            "outputs": {k: v.to_dict() for k, v in self.outputs.items()},
            "examples": [e.to_dict() for e in self.examples],
        }


@dataclass
class Manifest:
    """
    Plugin manifest describing identity and capabilities.

    Every plugin must provide a manifest that identifies it
    and declares what it can do.
    """
    name: str
    version: str
    description: str = ""
    author: str = ""
    homepage: str = ""
    license: str = ""
    capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "homepage": self.homepage,
            "license": self.license,
            "capabilities": self.capabilities,
        }


@dataclass
class PatternSuggestion:
    """
    Common pattern suggestion for the analyzer.

    Describes a common usage pattern that the analyzer can suggest
    when similar sequences of actions are detected.
    """
    name: str
    actions: list[str]
    description: str = ""
    benefit: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "actions": self.actions,
            "description": self.description,
            "benefit": self.benefit,
        }


@dataclass
class AnalyzerRules:
    """
    Rules for the meta-model analyzer.

    Defines validation rules, action categorizations, and pattern
    suggestions for the plugin's actions.
    """
    plugin_name: str
    plugin_version: str = ""
    action_prefix: str = ""
    provider_type: str = ""
    write_actions: list[str] = field(default_factory=list)
    read_actions: list[str] = field(default_factory=list)
    transaction_action: str = ""
    collection_actions: list[str] = field(default_factory=list)
    collection_field: str = "collection"
    require_schema_prefix: bool = False
    schema_prefix: str = "$schema:"
    failable_actions: list[str] = field(default_factory=list)
    pattern_suggestions: list[PatternSuggestion] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "pluginName": self.plugin_name,
            "pluginVersion": self.plugin_version,
            "actionPrefix": self.action_prefix,
            "providerType": self.provider_type,
            "writeActions": self.write_actions,
            "readActions": self.read_actions,
            "transactionAction": self.transaction_action,
            "collectionActions": self.collection_actions,
            "collectionField": self.collection_field,
            "requireSchemaPrefix": self.require_schema_prefix,
            "schemaPrefix": self.schema_prefix,
            "failableActions": self.failable_actions,
            "patternSuggestions": [p.to_dict() for p in self.pattern_suggestions],
        }


# Resource and stats types for plugin status

@dataclass
class PluginResource:
    """Resource tracked by a plugin (provider, connection, etc.)."""
    type: str  # "provider", "connection", "cache", "queue"
    name: str
    status: str  # "connected", "disconnected", "error", "idle"
    info: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "name": self.name,
            "status": self.status,
            "info": self.info,
        }


@dataclass
class PluginStats:
    """Execution statistics for a plugin."""
    total_executions: int = 0
    successful: int = 0
    failed: int = 0
    avg_latency_ms: float = 0.0
    action_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "totalExecutions": self.total_executions,
            "successful": self.successful,
            "failed": self.failed,
            "avgLatencyMs": self.avg_latency_ms,
            "actionCounts": self.action_counts,
        }


@dataclass
class PluginStatus:
    """Detailed status of a plugin."""
    manifest: Manifest
    uptime_seconds: int
    resources: list[PluginResource] = field(default_factory=list)
    stats: Optional[PluginStats] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "manifest": self.manifest.to_dict(),
            "uptimeSeconds": self.uptime_seconds,
            "resources": [r.to_dict() for r in self.resources],
            "stats": self.stats.to_dict() if self.stats else None,
        }
