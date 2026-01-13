# App4 Plugin SDK for Python

Python SDK for building App4 plugins that integrate with the App4 platform via gRPC.

## Installation

```bash
pip install app4-sdk
```

For development:

```bash
pip install app4-sdk[dev]
```

## Quick Start

### 1. Create a Plugin

```python
from app4_sdk import (
    Plugin,
    Manifest,
    ActionMeta,
    ParamSchema,
    Context,
    serve,
)

class MyPlugin(Plugin):
    def manifest(self) -> Manifest:
        return Manifest(
            name="my-plugin",
            version="1.0.0",
            description="My awesome plugin",
            capabilities=["actions"],
        )

    def list_actions(self) -> list[ActionMeta]:
        return [
            ActionMeta(
                name="my-plugin:greet",
                description="Say hello",
                inputs={
                    "name": ParamSchema(
                        name="name",
                        type="string",
                        required=True,
                        description="Name to greet",
                    ),
                },
                outputs={
                    "message": ParamSchema(
                        name="message",
                        type="string",
                        description="Greeting message",
                    ),
                },
            ),
        ]

    def execute_action(
        self,
        ctx: Context,
        action_name: str,
        data: dict,
        config: dict,
    ) -> dict:
        if action_name == "my-plugin:greet":
            name = data.get("name", "World")
            ctx.info(f"Greeting {name}")
            return {"message": f"Hello, {name}!"}

        raise ValueError(f"Unknown action: {action_name}")

if __name__ == "__main__":
    serve(MyPlugin(), ":50051")
```

### 2. Run the Plugin

```bash
python my_plugin.py
```

### 3. With Registry Integration

```python
from app4_sdk import serve_with_registry, RegistryConfig

config = RegistryConfig(
    address="localhost:50100",
    heartbeat_seconds=10,
)

serve_with_registry(MyPlugin(), ":50051", config)
```

Or use environment variables:

```bash
export PLUGIN_REGISTRY_ADDRESS=localhost:50100
python my_plugin.py --registry
```

## Features

### Action Metadata

Define rich metadata for your actions:

```python
ActionMeta(
    name="mongo:find",
    category="database",
    description="Find documents in a collection",
    tags=["mongodb", "query", "read"],
    inputs={
        "collection": ParamSchema(
            name="collection",
            type="string",
            required=True,
            ui_component="TextInput",
        ),
        "filter": ParamSchema(
            name="filter",
            type="object",
            required=False,
            default={},
            ui_component="JsonEditor",
        ),
    },
    outputs={
        "documents": ParamSchema(
            name="documents",
            type="array",
            description="Found documents",
        ),
    },
    examples=[
        ActionExample(
            name="Find all users",
            input={"collection": "users", "filter": {}},
            output={"documents": [{"_id": "1", "name": "Alice"}]},
        ),
    ],
)
```

### Provider Management

Initialize and manage provider connections:

```python
class MyPlugin(Plugin):
    def __init__(self):
        self._connections: dict[str, Any] = {}

    def init_provider(self, name: str, config: dict) -> None:
        # Create connection
        uri = config.get("uri", "localhost:27017")
        self._connections[name] = create_connection(uri)

    def close_provider(self, name: str) -> None:
        # Close connection
        if name in self._connections:
            self._connections[name].close()
            del self._connections[name]
```

### Context and Logging

Use the context for logging and variable access:

```python
def execute_action(self, ctx: Context, action_name: str, data: dict, config: dict):
    ctx.debug("Processing request")
    ctx.info(f"Action: {action_name}")

    # Access input arguments
    user_id = ctx.arg("userId")

    # Access/set context variables
    session = ctx.ctx("session")
    ctx.set_ctx("lastAction", action_name)

    # Set return values
    ctx.set_return("success", True)

    return {"result": "done"}
```

### Health Checks

Implement custom health checking:

```python
def health_check(self) -> tuple[bool, str, dict[str, str]]:
    # Check all connections
    all_healthy = all(
        conn.is_connected() for conn in self._connections.values()
    )

    return (
        all_healthy,
        "OK" if all_healthy else "Some connections unhealthy",
        {
            "connections": str(len(self._connections)),
            "healthy": str(sum(1 for c in self._connections.values() if c.is_connected())),
        },
    )
```

### Export Metadata

Export plugin metadata for documentation:

```bash
# Export action metadata as JSON
python my_plugin.py --export-meta

# Export analyzer rules as JSON
python my_plugin.py --export-rules

# Export as Markdown documentation
python my_plugin.py --export-md
```

## Helper Functions

The SDK provides utility functions for config extraction:

```python
from app4_sdk import (
    get_config_string,
    get_config_bool,
    get_config_int,
    get_config_float,
    get_config_list,
    get_config_dict,
    require_config,
    get_nested_value,
    set_nested_value,
)

# Type-safe config extraction
uri = get_config_string(config, "uri", "localhost:27017")
timeout = get_config_int(config, "timeout", 30)
ssl = get_config_bool(config, "ssl", False)

# Require specific keys
require_config(config, "uri", "database")  # Raises ValueError if missing

# Nested value access
name = get_nested_value(data, "user.profile.name")
set_nested_value(result, "response.status", "ok")
```

## Analyzer Rules

Define validation rules for the meta-model analyzer:

```python
def analyzer_rules(self) -> AnalyzerRules:
    return AnalyzerRules(
        plugin_name="mongo",
        plugin_version="1.0.0",
        action_prefix="mongo:",
        provider_type="mongo",
        write_actions=["mongo:insert", "mongo:update", "mongo:delete"],
        read_actions=["mongo:find", "mongo:findOne", "mongo:count"],
        transaction_action="mongo:transaction",
        collection_actions=["mongo:find", "mongo:insert", "mongo:update"],
        collection_field="collection",
    )
```

## Development

### Generate Proto Files

```bash
make proto
```

### Run Tests

```bash
make test
```

### Format Code

```bash
make format
```

## API Reference

### Types

- `Manifest` - Plugin identity and capabilities
- `ActionMeta` - Action metadata with inputs/outputs
- `ParamSchema` - Parameter schema for inputs/outputs
- `ParamOption` - Option for select-type parameters
- `ActionExample` - Example usage for an action
- `AnalyzerRules` - Validation rules for analyzer
- `PluginStatus` - Detailed plugin status
- `PluginResource` - Resource tracked by plugin
- `PluginStats` - Execution statistics

### Interfaces

- `Plugin` - Abstract base class for plugins
- `Context` - Execution context interface

### Functions

- `serve(plugin, address)` - Start gRPC server
- `serve_with_registry(plugin, address, config)` - Serve with registry
- `serve_with_auto_registry(plugin, address)` - Auto-configure registry

### Registry

- `RegistryClient` - Client for plugin registry
- `RegistryConfig` - Registry configuration
- `ConfigClient` - Provider config management

## License

MIT License - see LICENSE file for details.
