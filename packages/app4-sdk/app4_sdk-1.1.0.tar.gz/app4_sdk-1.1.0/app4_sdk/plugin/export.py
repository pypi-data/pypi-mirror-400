"""
Export utilities for App4 plugins.

This module provides functions to export plugin metadata and
analyzer rules in various formats.
"""

import json
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app4_sdk.plugin.plugin import Plugin


def _format_value(v: Any) -> str:
    """Format a value for YAML output."""
    if isinstance(v, str):
        # Check if it's a reference (starts with $ or ~)
        if v.startswith("$") or v.startswith("~"):
            return v
        return f'"{v}"'
    elif isinstance(v, dict):
        return json.dumps(v)
    elif isinstance(v, list):
        return json.dumps(v)
    else:
        return str(v)


def export_metadata(plugin: "Plugin") -> None:
    """
    Export action metadata as JSON to stdout.

    Args:
        plugin: Plugin instance
    """
    actions = plugin.list_actions()
    manifest = plugin.manifest()

    output = {
        "plugin": manifest.to_dict(),
        "actions": [a.to_dict() for a in actions],
    }

    print(json.dumps(output, indent=2))


def export_rules(plugin: "Plugin") -> None:
    """
    Export analyzer rules as JSON to stdout.

    Args:
        plugin: Plugin instance
    """
    rules = plugin.analyzer_rules()

    if rules:
        print(json.dumps(rules.to_dict(), indent=2))
    else:
        print("{}")


def export_all(plugin: "Plugin") -> None:
    """
    Export both metadata and rules as JSON to stdout.

    Args:
        plugin: Plugin instance
    """
    actions = plugin.list_actions()
    manifest = plugin.manifest()
    rules = plugin.analyzer_rules()

    output = {
        "plugin": manifest.to_dict(),
        "actions": [a.to_dict() for a in actions],
        "analyzerRules": rules.to_dict() if rules else None,
    }

    print(json.dumps(output, indent=2))


def export_markdown(plugin: "Plugin") -> None:
    """
    Export plugin documentation as AI-friendly Markdown to stdout.

    Args:
        plugin: Plugin instance
    """
    manifest = plugin.manifest()
    actions = plugin.list_actions()
    rules = plugin.analyzer_rules()

    # Build write actions set from rules
    write_actions_set = set()
    if rules and rules.write_actions:
        for action in rules.write_actions:
            write_actions_set.add(f"{manifest.name}:{action}")

    # Categorize actions
    write_actions = []
    read_actions = []
    for action in actions:
        if action.name in write_actions_set:
            write_actions.append(action)
        else:
            read_actions.append(action)

    lines = [
        f"# {manifest.name} Plugin",
        "",
        "<!-- AI-FRIENDLY: This document describes a plugin for the App4 meta-model system -->",
        "",
        "## Overview",
        "",
        manifest.description if manifest.description else "",
        "",
        "| Property | Value |",
        "|----------|-------|",
        f"| Name | `{manifest.name}` |",
        f"| Version | `{manifest.version}` |",
    ]

    # Add provider type if available from rules
    provider_type = manifest.name  # Default to plugin name
    if rules and hasattr(rules, 'provider_type') and rules.provider_type:
        provider_type = rules.provider_type
    lines.append(f"| Provider | `$provider:{provider_type}:<name>` |")
    lines.append("")

    # Actions summary by category
    lines.append("## Actions")
    lines.append("")

    if write_actions:
        lines.extend([
            "### Write Actions",
            "",
            "| Action | Description |",
            "|--------|-------------|",
        ])
        for action in write_actions:
            desc = action.description if action.description else ""
            lines.append(f"| `{action.name}` | {desc} |")
        lines.append("")

    if read_actions:
        lines.extend([
            "### Read Actions",
            "",
            "| Action | Description |",
            "|--------|-------------|",
        ])
        for action in read_actions:
            desc = action.description if action.description else ""
            lines.append(f"| `{action.name}` | {desc} |")
        lines.append("")

    # Detailed action reference
    lines.extend([
        "## Action Reference",
        "",
    ])

    for action in actions:
        lines.extend([
            f"### `{action.name}`",
            "",
            action.description if action.description else "",
            "",
        ])

        if action.tags:
            tags_str = ", ".join([f"`{t}`" for t in action.tags])
            lines.append(f"**Tags:** {tags_str}")
            lines.append("")

        if action.inputs:
            lines.extend([
                "**Configuration:**",
                "",
                "| Parameter | Type | Required | Default | Description |",
                "|-----------|------|----------|---------|-------------|",
            ])
            for name, param in action.inputs.items():
                required = "**Yes**" if param.required else "No"
                default = getattr(param, 'default', None)
                default_str = str(default) if default is not None else "-"
                desc = param.description.replace("|", "\\|") if param.description else ""
                lines.append(f"| `{name}` | {param.type} | {required} | {default_str} | {desc} |")
            lines.append("")

        # Examples section
        if hasattr(action, 'examples') and action.examples:
            lines.append("**Examples:**")
            lines.append("")
            for ex in action.examples:
                ex_title = getattr(ex, 'title', 'Example')
                ex_desc = getattr(ex, 'description', '')
                lines.append(f"#### {ex_title}")
                lines.append("")
                if ex_desc:
                    lines.append(ex_desc)
                    lines.append("")

                # JSON config example
                if hasattr(ex, 'config') and ex.config:
                    lines.append("**JSON Config:**")
                    lines.append("```yaml")
                    lines.append(f"- action: {action.name}")
                    lines.append("  config:")
                    for k, v in ex.config.items():
                        lines.append(f"    {k}: {_format_value(v)}")
                    lines.append("```")
                    lines.append("")

                # DSL examples
                if hasattr(ex, 'dsl_examples') and ex.dsl_examples:
                    lines.append("**DSL Format:**")
                    lines.append("```app4")
                    for dsl in ex.dsl_examples:
                        lines.append(dsl)
                    lines.append("```")
                    lines.append("")
        else:
            # Fallback: generate basic example from inputs
            lines.extend([
                "**Example:**",
                "",
                "```yaml",
                f"- action: {action.name}",
                "  config:",
                f"    provider: $provider:{provider_type}:default",
            ])
            # Add required inputs as example
            if action.inputs:
                for name, param in action.inputs.items():
                    if name == "provider" or name == "target":
                        continue
                    if param.required:
                        if param.type == "string":
                            lines.append(f'    {name}: "value"')
                        elif param.type == "object":
                            lines.append(f"    {name}: {{}}")
                        elif param.type == "array":
                            lines.append(f"    {name}: []")
                        else:
                            lines.append(f"    {name}: # {param.type}")
            lines.append("```")
            lines.append("")

        lines.extend([
            "---",
            "",
        ])

    # Footer
    lines.extend([
        "---",
        "",
        "*Generated by App4 Plugin SDK*",
    ])

    print("\n".join(lines))


def handle_export_flags(plugin: "Plugin") -> bool:
    """
    Check for and handle export flags.

    Call this in your main() before serve() to support:
    - --export-meta: Export action metadata as JSON
    - --export-rules: Export analyzer rules as JSON
    - --export-all: Export both
    - --export-md: Export as Markdown documentation

    Args:
        plugin: Plugin instance

    Returns:
        True if an export flag was handled (should exit)
        False if no export flag present (continue to serve)

    Example:
        if __name__ == "__main__":
            plugin = MyPlugin()
            if handle_export_flags(plugin):
                sys.exit(0)
            serve(plugin)
    """
    if len(sys.argv) < 2:
        return False

    flag = sys.argv[1]

    if flag == "--export-meta":
        export_metadata(plugin)
        return True
    elif flag == "--export-rules":
        export_rules(plugin)
        return True
    elif flag == "--export-all":
        export_all(plugin)
        return True
    elif flag == "--export-md":
        export_markdown(plugin)
        return True

    return False
