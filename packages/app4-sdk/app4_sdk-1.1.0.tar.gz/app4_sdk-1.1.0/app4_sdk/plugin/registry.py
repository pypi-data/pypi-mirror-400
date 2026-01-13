"""
Registry client for App4 plugins.

This module provides the RegistryClient class for interacting with
the plugin registry service.
"""

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import grpc

# Import generated proto modules
try:
    from app4_sdk.proto import plugin_pb2
    from app4_sdk.proto import registry_pb2
    from app4_sdk.proto import registry_pb2_grpc
except ImportError:
    plugin_pb2 = None
    registry_pb2 = None
    registry_pb2_grpc = None


logger = logging.getLogger("app4.plugin.registry")


@dataclass
class RegistryConfig:
    """Configuration for registry client."""
    address: str
    heartbeat_seconds: int = 10
    instance_id: Optional[str] = None
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class ConfigEvent:
    """Event for provider config changes."""
    type: str  # "created", "updated", "deleted"
    app_id: str
    plugin_name: str
    provider_name: str
    version: int
    timestamp: int


class RegistryClient:
    """
    Client for interacting with the plugin registry.

    Handles:
    - Plugin registration and unregistration
    - Periodic heartbeats
    - App connection tracking
    - Provider config management
    """

    def __init__(
        self,
        config: RegistryConfig,
        plugin_name: str,
        version: str,
        address: str,
    ):
        """
        Create a new registry client.

        Args:
            config: Registry configuration
            plugin_name: Name of the plugin
            version: Version of the plugin
            address: gRPC address this plugin is listening on
        """
        self.config = config
        self.plugin_name = plugin_name
        self.version = version
        self.address = address
        self.instance_id = config.instance_id or str(uuid.uuid4())

        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[Any] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._running = False
        self._registered = False

    def start(self) -> None:
        """
        Start the registry client.

        Connects to the registry, registers the plugin, and starts
        the heartbeat thread.
        """
        if registry_pb2 is None:
            raise RuntimeError("gRPC proto modules not generated")

        # Connect to registry
        self._channel = grpc.insecure_channel(self.config.address)
        self._stub = registry_pb2_grpc.PluginRegistryServiceStub(self._channel)

        # Register
        try:
            request = registry_pb2.RegisterRequest(
                plugin_name=self.plugin_name,
                version=self.version,
                address=self.address,
                instance_id=self.instance_id,
                labels=self.config.labels,
            )
            response = self._stub.Register(request)

            if response.success:
                self._registered = True
                if response.assigned_id:
                    self.instance_id = response.assigned_id
                logger.info(f"Registered with registry: {self.instance_id}")
            else:
                raise RuntimeError(f"Registration failed: {response.error}")

        except grpc.RpcError as e:
            logger.error(f"Failed to register: {e}")
            raise

        # Start heartbeat thread
        self._running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def stop(self) -> None:
        """
        Stop the registry client.

        Stops the heartbeat thread and unregisters from the registry.
        """
        self._running = False

        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2)

        if self._registered and self._stub:
            try:
                request = registry_pb2.UnregisterRequest(
                    plugin_name=self.plugin_name,
                    version=self.version,
                    instance_id=self.instance_id,
                )
                self._stub.Unregister(request)
                logger.info("Unregistered from registry")
            except grpc.RpcError as e:
                logger.warning(f"Failed to unregister: {e}")

        if self._channel:
            self._channel.close()

    def _heartbeat_loop(self) -> None:
        """Background thread for sending heartbeats."""
        while self._running:
            try:
                self._send_heartbeat()
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")

            # Sleep in small increments to allow quick shutdown
            for _ in range(self.config.heartbeat_seconds * 10):
                if not self._running:
                    break
                time.sleep(0.1)

    def _send_heartbeat(self) -> None:
        """Send a heartbeat to the registry."""
        if not self._stub:
            return

        request = registry_pb2.HeartbeatRequest(
            plugin_name=self.plugin_name,
            version=self.version,
            instance_id=self.instance_id,
            healthy=True,
        )

        try:
            response = self._stub.Heartbeat(request)

            if response.should_shutdown:
                logger.warning("Registry requested shutdown")
                self._running = False

            if response.deprecated:
                logger.warning(
                    f"This version is deprecated: {response.deprecation_message}. "
                    f"Recommended version: {response.recommended_version}"
                )

        except grpc.RpcError as e:
            logger.warning(f"Heartbeat RPC failed: {e}")

    def notify_connect(self, app_id: str, app_name: str = "") -> None:
        """
        Notify the registry that an app has connected.

        Args:
            app_id: Application ID
            app_name: Application name (optional)
        """
        if not self._stub:
            return

        try:
            request = registry_pb2.ConnectionEvent(
                plugin_instance_id=self.instance_id,
                plugin_name=self.plugin_name,
                plugin_version=self.version,
                app_id=app_id,
                app_name=app_name,
                timestamp=int(time.time()),
            )
            self._stub.NotifyConnect(request)
            logger.debug(f"Notified connect: {app_id}")

        except grpc.RpcError as e:
            logger.warning(f"Failed to notify connect: {e}")

    def notify_disconnect(self, app_id: str) -> None:
        """
        Notify the registry that an app has disconnected.

        Args:
            app_id: Application ID
        """
        if not self._stub:
            return

        try:
            request = registry_pb2.ConnectionEvent(
                plugin_instance_id=self.instance_id,
                plugin_name=self.plugin_name,
                plugin_version=self.version,
                app_id=app_id,
                timestamp=int(time.time()),
            )
            self._stub.NotifyDisconnect(request)
            logger.debug(f"Notified disconnect: {app_id}")

        except grpc.RpcError as e:
            logger.warning(f"Failed to notify disconnect: {e}")


class ConfigClient:
    """
    Client for managing provider configurations via the registry.

    Provides caching and change notification for provider configs.
    """

    def __init__(self, registry_address: str):
        """
        Create a config client.

        Args:
            registry_address: Registry gRPC address
        """
        self.registry_address = registry_address
        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[Any] = None
        self._cache: dict[str, dict[str, Any]] = {}  # key -> {config, version, cached_at}
        self._event_handlers: list[Callable[[ConfigEvent], None]] = []
        self._subscription_thread: Optional[threading.Thread] = None
        self._running = False

    def connect(self) -> None:
        """Connect to the registry."""
        if registry_pb2 is None:
            raise RuntimeError("gRPC proto modules not generated")

        self._channel = grpc.insecure_channel(self.registry_address)
        self._stub = registry_pb2_grpc.PluginRegistryServiceStub(self._channel)

    def close(self) -> None:
        """Close the connection."""
        self._running = False
        if self._subscription_thread:
            self._subscription_thread.join(timeout=2)
        if self._channel:
            self._channel.close()

    def _cache_key(self, app_id: str, plugin_name: str, provider_name: str) -> str:
        """Generate cache key."""
        return f"{app_id}:{plugin_name}:{provider_name}"

    def get_config(
        self,
        app_id: str,
        plugin_name: str,
        provider_name: str,
    ) -> Optional[dict[str, Any]]:
        """
        Get provider configuration.

        Returns cached config if available, otherwise fetches from registry.

        Args:
            app_id: Application ID
            plugin_name: Plugin name
            provider_name: Provider instance name

        Returns:
            Config dictionary or None if not found
        """
        if not self._stub:
            self.connect()

        key = self._cache_key(app_id, plugin_name, provider_name)

        # Check cache
        if key in self._cache:
            return self._cache[key]["config"]

        # Fetch from registry
        try:
            request = registry_pb2.GetProviderConfigRequest(
                app_id=app_id,
                plugin_name=plugin_name,
                provider_name=provider_name,
            )
            response = self._stub.GetProviderConfig(request)

            if response.found:
                import json
                config = json.loads(response.config.config_json)
                self._cache[key] = {
                    "config": config,
                    "version": response.config.version,
                    "cached_at": time.time(),
                }
                return config

        except grpc.RpcError as e:
            logger.warning(f"Failed to get config: {e}")

        return None

    def store_config(
        self,
        app_id: str,
        plugin_name: str,
        provider_name: str,
        config: dict[str, Any],
        created_by: str = "",
    ) -> bool:
        """
        Store provider configuration.

        Args:
            app_id: Application ID
            plugin_name: Plugin name
            provider_name: Provider instance name
            config: Configuration dictionary
            created_by: Identifier of the creator

        Returns:
            True if successful
        """
        if not self._stub:
            self.connect()

        try:
            import json
            request = registry_pb2.StoreProviderConfigRequest(
                app_id=app_id,
                plugin_name=plugin_name,
                provider_name=provider_name,
                config_json=json.dumps(config).encode(),
                created_by=created_by,
            )
            response = self._stub.StoreProviderConfig(request)

            if response.success:
                # Update cache
                key = self._cache_key(app_id, plugin_name, provider_name)
                self._cache[key] = {
                    "config": config,
                    "version": response.version,
                    "cached_at": time.time(),
                }
                return True
            else:
                logger.warning(f"Failed to store config: {response.error}")
                return False

        except grpc.RpcError as e:
            logger.warning(f"Failed to store config: {e}")
            return False

    def subscribe(
        self,
        handler: Callable[[ConfigEvent], None],
        app_id: str = "",
        plugin_name: str = "",
    ) -> None:
        """
        Subscribe to config changes.

        Args:
            handler: Callback function for config events
            app_id: Filter by app ID (empty for all)
            plugin_name: Filter by plugin name (empty for all)
        """
        if not self._stub:
            self.connect()

        self._event_handlers.append(handler)

        if not self._subscription_thread:
            self._running = True
            self._subscription_thread = threading.Thread(
                target=self._subscription_loop,
                args=(app_id, plugin_name),
                daemon=True,
            )
            self._subscription_thread.start()

    def _subscription_loop(self, app_id: str, plugin_name: str) -> None:
        """Background thread for subscription."""
        while self._running:
            try:
                request = registry_pb2.SubscribeProviderConfigsRequest(
                    app_id=app_id,
                    plugin_name=plugin_name,
                )

                for event in self._stub.SubscribeProviderConfigs(request):
                    if not self._running:
                        break

                    config_event = ConfigEvent(
                        type=["created", "updated", "deleted"][event.type],
                        app_id=event.app_id,
                        plugin_name=event.plugin_name,
                        provider_name=event.provider_name,
                        version=event.version,
                        timestamp=event.timestamp,
                    )

                    # Invalidate cache
                    key = self._cache_key(
                        event.app_id, event.plugin_name, event.provider_name
                    )
                    if key in self._cache:
                        del self._cache[key]

                    # Notify handlers
                    for handler in self._event_handlers:
                        try:
                            handler(config_event)
                        except Exception as e:
                            logger.warning(f"Handler error: {e}")

            except grpc.RpcError as e:
                if self._running:
                    logger.warning(f"Subscription error: {e}, reconnecting...")
                    time.sleep(5)
