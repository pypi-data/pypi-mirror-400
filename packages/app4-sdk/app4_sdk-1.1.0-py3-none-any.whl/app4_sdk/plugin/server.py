"""
gRPC server for App4 plugins.

This module provides functions to serve a plugin over gRPC:
- serve(): Simple server without registry
- serve_with_registry(): Server with registry integration
- serve_with_auto_registry(): Auto-configure registry from environment
"""

import json
import logging
import os
import signal
import sys
import time
from concurrent import futures
from typing import Optional

import grpc

from app4_sdk.plugin.plugin import Plugin
from app4_sdk.plugin.context import BaseContext
from app4_sdk.plugin.registry import RegistryClient, RegistryConfig

# Import generated proto modules
try:
    from app4_sdk.proto import plugin_pb2
    from app4_sdk.proto import plugin_pb2_grpc
except ImportError:
    # Proto modules not generated yet - provide stubs
    plugin_pb2 = None
    plugin_pb2_grpc = None


logger = logging.getLogger("app4.plugin.server")


class PluginServicer:
    """gRPC servicer implementation for Plugin interface."""

    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.start_time = time.time()
        self._shutdown_requested = False

    def GetManifest(self, request, context):
        """Return plugin manifest."""
        manifest = self.plugin.manifest()
        rules = self.plugin.analyzer_rules()

        response = plugin_pb2.Manifest(
            name=manifest.name,
            version=manifest.version,
            description=manifest.description,
            author=manifest.author,
            homepage=manifest.homepage,
            license=manifest.license,
            capabilities=manifest.capabilities,
        )

        if rules:
            response.analyzer_rules_json = json.dumps(rules.to_dict()).encode()

        return response

    def ListActions(self, request, context):
        """Return list of all actions."""
        actions = self.plugin.list_actions()

        action_list = plugin_pb2.ActionList()
        for action in actions:
            action_meta = plugin_pb2.ActionMeta(
                name=action.name,
                category=action.category,
                description=action.description,
                tags=action.tags,
                inputs_json=json.dumps({k: v.to_dict() for k, v in action.inputs.items()}).encode(),
                outputs_json=json.dumps({k: v.to_dict() for k, v in action.outputs.items()}).encode(),
                examples_json=json.dumps([e.to_dict() for e in action.examples]).encode(),
            )
            action_list.actions.append(action_meta)

        return action_list

    def ExecuteAction(self, request, context):
        """Execute an action."""
        try:
            # Parse input data
            data = json.loads(request.data_json) if request.data_json else {}
            config = json.loads(request.config_json) if request.config_json else {}
            ctx_data = json.loads(request.context_json) if request.context_json else {}

            # Create context
            ctx = BaseContext(
                trace_id=request.trace_id,
                args=ctx_data.get("args", {}),
                ctx=ctx_data.get("ctx", {}),
            )

            # Execute action
            result = self.plugin.execute_action(ctx, request.action_name, data, config)

            return plugin_pb2.ActionResponse(
                success=True,
                result_json=json.dumps(result).encode(),
            )

        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            error_code = type(e).__name__
            return plugin_pb2.ActionResponse(
                success=False,
                error=str(e),
                error_code=error_code,
            )

    def InitProvider(self, request, context):
        """Initialize a provider instance."""
        try:
            config = json.loads(request.config_json) if request.config_json else {}
            self.plugin.init_provider(request.name, config)
            return plugin_pb2.ProviderResponse(success=True)
        except Exception as e:
            logger.error(f"Provider init failed: {e}")
            return plugin_pb2.ProviderResponse(success=False, error=str(e))

    def CloseProvider(self, request, context):
        """Close a provider instance."""
        try:
            self.plugin.close_provider(request.name)
            return plugin_pb2.ProviderResponse(success=True)
        except Exception as e:
            logger.error(f"Provider close failed: {e}")
            return plugin_pb2.ProviderResponse(success=False, error=str(e))

    def Health(self, request, context):
        """Health check."""
        healthy, message, details = self.plugin.health_check()
        return plugin_pb2.HealthResponse(
            healthy=healthy,
            message=message,
            details=details,
        )

    def Shutdown(self, request, context):
        """Graceful shutdown."""
        self._shutdown_requested = True
        self.plugin.shutdown()
        return plugin_pb2.Empty()

    def GetStatus(self, request, context):
        """Get detailed plugin status."""
        status = self.plugin.get_status()

        # Build manifest proto
        manifest = plugin_pb2.Manifest(
            name=status.manifest.name,
            version=status.manifest.version,
            description=status.manifest.description,
            author=status.manifest.author,
            homepage=status.manifest.homepage,
            license=status.manifest.license,
            capabilities=status.manifest.capabilities,
        )

        # Build resources
        resources = []
        for r in status.resources:
            resources.append(plugin_pb2.PluginResource(
                type=r.type,
                name=r.name,
                status=r.status,
                info=r.info,
            ))

        # Build stats
        stats = None
        if status.stats:
            stats = plugin_pb2.PluginStats(
                total_executions=status.stats.total_executions,
                successful=status.stats.successful,
                failed=status.stats.failed,
                avg_latency_ms=status.stats.avg_latency_ms,
                action_counts=status.stats.action_counts,
            )

        # Calculate actual uptime
        uptime = int(time.time() - self.start_time)

        return plugin_pb2.PluginStatus(
            manifest=manifest,
            uptime_seconds=uptime,
            resources=resources,
            stats=stats,
        )


def serve(
    plugin: Plugin,
    address: str = ":50051",
    max_workers: int = 10,
) -> None:
    """
    Start a gRPC server for the plugin.

    This is the simplest way to serve a plugin without registry integration.

    Args:
        plugin: Plugin instance to serve
        address: gRPC address to listen on (default: ":50051")
        max_workers: Maximum thread pool workers (default: 10)

    Example:
        if __name__ == "__main__":
            plugin = MyPlugin()
            serve(plugin, ":50051")
    """
    if plugin_pb2 is None:
        raise RuntimeError(
            "gRPC proto modules not generated. Run: "
            "python -m grpc_tools.protoc -I./app4_sdk/proto "
            "--python_out=./app4_sdk/proto --grpc_python_out=./app4_sdk/proto "
            "./app4_sdk/proto/plugin.proto"
        )

    # Parse address
    if address.startswith(":"):
        address = f"0.0.0.0{address}"

    # Create server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    servicer = PluginServicer(plugin)
    plugin_pb2_grpc.add_PluginServiceServicer_to_server(servicer, server)

    server.add_insecure_port(address)

    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info("Shutdown signal received, stopping server...")
        server.stop(grace=5)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start server
    manifest = plugin.manifest()
    logger.info(f"Starting plugin {manifest.name} v{manifest.version} on {address}")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Interrupted, stopping server...")
        server.stop(grace=5)


def serve_with_registry(
    plugin: Plugin,
    address: str = ":50051",
    registry_config: Optional[RegistryConfig] = None,
    max_workers: int = 10,
) -> None:
    """
    Start a gRPC server with registry integration.

    The plugin will register with the registry on startup and send
    periodic heartbeats. On shutdown, it will unregister.

    Args:
        plugin: Plugin instance to serve
        address: gRPC address to listen on (default: ":50051")
        registry_config: Registry configuration
        max_workers: Maximum thread pool workers (default: 10)

    Example:
        if __name__ == "__main__":
            plugin = MyPlugin()
            config = RegistryConfig(address="localhost:50100")
            serve_with_registry(plugin, ":50051", config)
    """
    if plugin_pb2 is None:
        raise RuntimeError("gRPC proto modules not generated")

    # Parse address
    if address.startswith(":"):
        listen_address = f"0.0.0.0{address}"
    else:
        listen_address = address

    # Create server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    servicer = PluginServicer(plugin)
    plugin_pb2_grpc.add_PluginServiceServicer_to_server(servicer, server)

    server.add_insecure_port(listen_address)

    # Create registry client if configured
    registry_client = None
    if registry_config:
        manifest = plugin.manifest()
        registry_client = RegistryClient(
            config=registry_config,
            plugin_name=manifest.name,
            version=manifest.version,
            address=address,
        )

    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info("Shutdown signal received, stopping server...")
        if registry_client:
            registry_client.stop()
        server.stop(grace=5)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start server
    manifest = plugin.manifest()
    logger.info(f"Starting plugin {manifest.name} v{manifest.version} on {listen_address}")
    server.start()

    # Register with registry
    if registry_client:
        try:
            registry_client.start()
        except Exception as e:
            logger.error(f"Failed to register with registry: {e}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Interrupted, stopping server...")
        if registry_client:
            registry_client.stop()
        server.stop(grace=5)


def serve_with_auto_registry(
    plugin: Plugin,
    address: str = ":50051",
    max_workers: int = 10,
) -> None:
    """
    Start a gRPC server with auto-configured registry.

    Registry configuration is read from environment variables:
    - PLUGIN_REGISTRY_ADDRESS: Registry gRPC address
    - PLUGIN_REGISTRY_HEARTBEAT: Heartbeat interval in seconds (default: 10)
    - PLUGIN_INSTANCE_ID: Custom instance ID (optional)

    If PLUGIN_REGISTRY_ADDRESS is not set, serves without registry.

    Args:
        plugin: Plugin instance to serve
        address: gRPC address to listen on (default: ":50051")
        max_workers: Maximum thread pool workers (default: 10)

    Example:
        if __name__ == "__main__":
            plugin = MyPlugin()
            # Set PLUGIN_REGISTRY_ADDRESS=localhost:50100
            serve_with_auto_registry(plugin, ":50051")
    """
    registry_address = os.environ.get("PLUGIN_REGISTRY_ADDRESS", "")

    if not registry_address:
        logger.info("No registry address configured, serving without registry")
        serve(plugin, address, max_workers)
        return

    heartbeat = int(os.environ.get("PLUGIN_REGISTRY_HEARTBEAT", "10"))
    instance_id = os.environ.get("PLUGIN_INSTANCE_ID", "")
    labels_str = os.environ.get("PLUGIN_LABELS", "")

    labels = {}
    if labels_str:
        for pair in labels_str.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                labels[key.strip()] = value.strip()

    config = RegistryConfig(
        address=registry_address,
        heartbeat_seconds=heartbeat,
        instance_id=instance_id if instance_id else None,
        labels=labels,
    )

    serve_with_registry(plugin, address, config, max_workers)


def check_export_flags() -> bool:
    """
    Check for export flags and handle them.

    Supports:
    - --export-meta: Export action metadata as JSON
    - --export-rules: Export analyzer rules as JSON
    - --export-all: Export both
    - --export-md: Export as Markdown documentation

    Returns:
        True if an export flag was handled, False otherwise
    """
    if len(sys.argv) < 2:
        return False

    flag = sys.argv[1]

    if flag not in ("--export-meta", "--export-rules", "--export-all", "--export-md"):
        return False

    # Import here to avoid circular imports
    from app4_sdk.plugin.export import export_metadata, export_rules, export_all, export_markdown

    if flag == "--export-meta":
        export_metadata()
    elif flag == "--export-rules":
        export_rules()
    elif flag == "--export-all":
        export_all()
    elif flag == "--export-md":
        export_markdown()

    return True
