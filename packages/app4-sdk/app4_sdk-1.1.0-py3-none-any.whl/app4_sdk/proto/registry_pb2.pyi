import plugin_pb2 as _plugin_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RegisterRequest(_message.Message):
    __slots__ = ("plugin_name", "version", "address", "instance_id", "labels")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    version: str
    address: str
    instance_id: str
    labels: _containers.ScalarMap[str, str]
    def __init__(self, plugin_name: _Optional[str] = ..., version: _Optional[str] = ..., address: _Optional[str] = ..., instance_id: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RegisterResponse(_message.Message):
    __slots__ = ("success", "error", "assigned_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    assigned_id: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., assigned_id: _Optional[str] = ...) -> None: ...

class UnregisterRequest(_message.Message):
    __slots__ = ("plugin_name", "version", "instance_id")
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    version: str
    instance_id: str
    def __init__(self, plugin_name: _Optional[str] = ..., version: _Optional[str] = ..., instance_id: _Optional[str] = ...) -> None: ...

class HeartbeatRequest(_message.Message):
    __slots__ = ("plugin_name", "version", "instance_id", "healthy", "metrics")
    class MetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    version: str
    instance_id: str
    healthy: bool
    metrics: _containers.ScalarMap[str, str]
    def __init__(self, plugin_name: _Optional[str] = ..., version: _Optional[str] = ..., instance_id: _Optional[str] = ..., healthy: bool = ..., metrics: _Optional[_Mapping[str, str]] = ...) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ("acknowledged", "should_shutdown", "deprecated", "deprecation_message", "recommended_version")
    ACKNOWLEDGED_FIELD_NUMBER: _ClassVar[int]
    SHOULD_SHUTDOWN_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    DEPRECATION_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDED_VERSION_FIELD_NUMBER: _ClassVar[int]
    acknowledged: bool
    should_shutdown: bool
    deprecated: bool
    deprecation_message: str
    recommended_version: str
    def __init__(self, acknowledged: bool = ..., should_shutdown: bool = ..., deprecated: bool = ..., deprecation_message: _Optional[str] = ..., recommended_version: _Optional[str] = ...) -> None: ...

class ResolveRequest(_message.Message):
    __slots__ = ("plugin_name", "version_constraint", "prefer_labels")
    class PreferLabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_CONSTRAINT_FIELD_NUMBER: _ClassVar[int]
    PREFER_LABELS_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    version_constraint: str
    prefer_labels: _containers.ScalarMap[str, str]
    def __init__(self, plugin_name: _Optional[str] = ..., version_constraint: _Optional[str] = ..., prefer_labels: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ResolveResponse(_message.Message):
    __slots__ = ("found", "resolved_version", "address", "instance_id", "error")
    FOUND_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_VERSION_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    found: bool
    resolved_version: str
    address: str
    instance_id: str
    error: str
    def __init__(self, found: bool = ..., resolved_version: _Optional[str] = ..., address: _Optional[str] = ..., instance_id: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class ListVersionsRequest(_message.Message):
    __slots__ = ("plugin_name", "include_unhealthy")
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_UNHEALTHY_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    include_unhealthy: bool
    def __init__(self, plugin_name: _Optional[str] = ..., include_unhealthy: bool = ...) -> None: ...

class ListVersionsResponse(_message.Message):
    __slots__ = ("versions",)
    VERSIONS_FIELD_NUMBER: _ClassVar[int]
    versions: _containers.RepeatedCompositeFieldContainer[PluginVersion]
    def __init__(self, versions: _Optional[_Iterable[_Union[PluginVersion, _Mapping]]] = ...) -> None: ...

class PluginVersion(_message.Message):
    __slots__ = ("version", "instances", "deprecated", "deprecation_message", "recommended_version", "deprecated_at")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTANCES_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    DEPRECATION_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDED_VERSION_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_AT_FIELD_NUMBER: _ClassVar[int]
    version: str
    instances: _containers.RepeatedCompositeFieldContainer[PluginInstance]
    deprecated: bool
    deprecation_message: str
    recommended_version: str
    deprecated_at: int
    def __init__(self, version: _Optional[str] = ..., instances: _Optional[_Iterable[_Union[PluginInstance, _Mapping]]] = ..., deprecated: bool = ..., deprecation_message: _Optional[str] = ..., recommended_version: _Optional[str] = ..., deprecated_at: _Optional[int] = ...) -> None: ...

class PluginInstance(_message.Message):
    __slots__ = ("instance_id", "address", "healthy", "last_heartbeat", "labels", "metrics")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class MetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    LAST_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    instance_id: str
    address: str
    healthy: bool
    last_heartbeat: int
    labels: _containers.ScalarMap[str, str]
    metrics: _containers.ScalarMap[str, str]
    def __init__(self, instance_id: _Optional[str] = ..., address: _Optional[str] = ..., healthy: bool = ..., last_heartbeat: _Optional[int] = ..., labels: _Optional[_Mapping[str, str]] = ..., metrics: _Optional[_Mapping[str, str]] = ...) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = ("plugin_names",)
    PLUGIN_NAMES_FIELD_NUMBER: _ClassVar[int]
    plugin_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, plugin_names: _Optional[_Iterable[str]] = ...) -> None: ...

class RegistryEvent(_message.Message):
    __slots__ = ("type", "plugin_name", "version", "instance_id", "address", "timestamp")
    class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PLUGIN_REGISTERED: _ClassVar[RegistryEvent.EventType]
        PLUGIN_UNREGISTERED: _ClassVar[RegistryEvent.EventType]
        PLUGIN_HEALTHY: _ClassVar[RegistryEvent.EventType]
        PLUGIN_UNHEALTHY: _ClassVar[RegistryEvent.EventType]
        VERSION_DEPRECATED: _ClassVar[RegistryEvent.EventType]
    PLUGIN_REGISTERED: RegistryEvent.EventType
    PLUGIN_UNREGISTERED: RegistryEvent.EventType
    PLUGIN_HEALTHY: RegistryEvent.EventType
    PLUGIN_UNHEALTHY: RegistryEvent.EventType
    VERSION_DEPRECATED: RegistryEvent.EventType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    type: RegistryEvent.EventType
    plugin_name: str
    version: str
    instance_id: str
    address: str
    timestamp: int
    def __init__(self, type: _Optional[_Union[RegistryEvent.EventType, str]] = ..., plugin_name: _Optional[str] = ..., version: _Optional[str] = ..., instance_id: _Optional[str] = ..., address: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...

class RegistryHealthResponse(_message.Message):
    __slots__ = ("healthy", "total_plugins", "healthy_plugins", "total_instances", "healthy_instances")
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PLUGINS_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_PLUGINS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    healthy: bool
    total_plugins: int
    healthy_plugins: int
    total_instances: int
    healthy_instances: int
    def __init__(self, healthy: bool = ..., total_plugins: _Optional[int] = ..., healthy_plugins: _Optional[int] = ..., total_instances: _Optional[int] = ..., healthy_instances: _Optional[int] = ...) -> None: ...

class PluginList(_message.Message):
    __slots__ = ("plugins",)
    PLUGINS_FIELD_NUMBER: _ClassVar[int]
    plugins: _containers.RepeatedCompositeFieldContainer[PluginInfo]
    def __init__(self, plugins: _Optional[_Iterable[_Union[PluginInfo, _Mapping]]] = ...) -> None: ...

class PluginInfo(_message.Message):
    __slots__ = ("name", "available_versions", "total_instances", "healthy_instances")
    NAME_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    name: str
    available_versions: _containers.RepeatedScalarFieldContainer[str]
    total_instances: int
    healthy_instances: int
    def __init__(self, name: _Optional[str] = ..., available_versions: _Optional[_Iterable[str]] = ..., total_instances: _Optional[int] = ..., healthy_instances: _Optional[int] = ...) -> None: ...

class DeprecateVersionRequest(_message.Message):
    __slots__ = ("plugin_name", "version", "message", "recommended_version")
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDED_VERSION_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    version: str
    message: str
    recommended_version: str
    def __init__(self, plugin_name: _Optional[str] = ..., version: _Optional[str] = ..., message: _Optional[str] = ..., recommended_version: _Optional[str] = ...) -> None: ...

class DeprecateVersionResponse(_message.Message):
    __slots__ = ("success", "error", "affected_instances")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    AFFECTED_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    affected_instances: int
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., affected_instances: _Optional[int] = ...) -> None: ...

class RemoveVersionRequest(_message.Message):
    __slots__ = ("plugin_name", "version", "force")
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    version: str
    force: bool
    def __init__(self, plugin_name: _Optional[str] = ..., version: _Optional[str] = ..., force: bool = ...) -> None: ...

class RemoveVersionResponse(_message.Message):
    __slots__ = ("success", "error", "removed_instances")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    REMOVED_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    removed_instances: int
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., removed_instances: _Optional[int] = ...) -> None: ...

class RegistryProviderConfig(_message.Message):
    __slots__ = ("app_id", "plugin_name", "provider_name", "config_json", "version", "created_by", "created_at", "updated_at")
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    app_id: str
    plugin_name: str
    provider_name: str
    config_json: bytes
    version: int
    created_by: str
    created_at: int
    updated_at: int
    def __init__(self, app_id: _Optional[str] = ..., plugin_name: _Optional[str] = ..., provider_name: _Optional[str] = ..., config_json: _Optional[bytes] = ..., version: _Optional[int] = ..., created_by: _Optional[str] = ..., created_at: _Optional[int] = ..., updated_at: _Optional[int] = ...) -> None: ...

class StoreProviderConfigRequest(_message.Message):
    __slots__ = ("app_id", "plugin_name", "provider_name", "config_json", "created_by")
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    app_id: str
    plugin_name: str
    provider_name: str
    config_json: bytes
    created_by: str
    def __init__(self, app_id: _Optional[str] = ..., plugin_name: _Optional[str] = ..., provider_name: _Optional[str] = ..., config_json: _Optional[bytes] = ..., created_by: _Optional[str] = ...) -> None: ...

class StoreProviderConfigResponse(_message.Message):
    __slots__ = ("success", "error", "version")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    version: int
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class GetProviderConfigRequest(_message.Message):
    __slots__ = ("app_id", "plugin_name", "provider_name")
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    app_id: str
    plugin_name: str
    provider_name: str
    def __init__(self, app_id: _Optional[str] = ..., plugin_name: _Optional[str] = ..., provider_name: _Optional[str] = ...) -> None: ...

class GetProviderConfigResponse(_message.Message):
    __slots__ = ("found", "config", "error")
    FOUND_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    found: bool
    config: RegistryProviderConfig
    error: str
    def __init__(self, found: bool = ..., config: _Optional[_Union[RegistryProviderConfig, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class DeleteProviderConfigRequest(_message.Message):
    __slots__ = ("app_id", "plugin_name", "provider_name")
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    app_id: str
    plugin_name: str
    provider_name: str
    def __init__(self, app_id: _Optional[str] = ..., plugin_name: _Optional[str] = ..., provider_name: _Optional[str] = ...) -> None: ...

class ListProviderConfigsRequest(_message.Message):
    __slots__ = ("app_id", "plugin_name")
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    app_id: str
    plugin_name: str
    def __init__(self, app_id: _Optional[str] = ..., plugin_name: _Optional[str] = ...) -> None: ...

class ListProviderConfigsResponse(_message.Message):
    __slots__ = ("configs",)
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    configs: _containers.RepeatedCompositeFieldContainer[RegistryProviderConfig]
    def __init__(self, configs: _Optional[_Iterable[_Union[RegistryProviderConfig, _Mapping]]] = ...) -> None: ...

class SubscribeProviderConfigsRequest(_message.Message):
    __slots__ = ("app_id", "plugin_name")
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    app_id: str
    plugin_name: str
    def __init__(self, app_id: _Optional[str] = ..., plugin_name: _Optional[str] = ...) -> None: ...

class ProviderConfigEvent(_message.Message):
    __slots__ = ("type", "app_id", "plugin_name", "provider_name", "version", "timestamp")
    class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CONFIG_CREATED: _ClassVar[ProviderConfigEvent.EventType]
        CONFIG_UPDATED: _ClassVar[ProviderConfigEvent.EventType]
        CONFIG_DELETED: _ClassVar[ProviderConfigEvent.EventType]
    CONFIG_CREATED: ProviderConfigEvent.EventType
    CONFIG_UPDATED: ProviderConfigEvent.EventType
    CONFIG_DELETED: ProviderConfigEvent.EventType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    type: ProviderConfigEvent.EventType
    app_id: str
    plugin_name: str
    provider_name: str
    version: int
    timestamp: int
    def __init__(self, type: _Optional[_Union[ProviderConfigEvent.EventType, str]] = ..., app_id: _Optional[str] = ..., plugin_name: _Optional[str] = ..., provider_name: _Optional[str] = ..., version: _Optional[int] = ..., timestamp: _Optional[int] = ...) -> None: ...

class ConnectionEvent(_message.Message):
    __slots__ = ("plugin_instance_id", "plugin_name", "plugin_version", "app_id", "app_name", "timestamp")
    PLUGIN_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_VERSION_FIELD_NUMBER: _ClassVar[int]
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    plugin_instance_id: str
    plugin_name: str
    plugin_version: str
    app_id: str
    app_name: str
    timestamp: int
    def __init__(self, plugin_instance_id: _Optional[str] = ..., plugin_name: _Optional[str] = ..., plugin_version: _Optional[str] = ..., app_id: _Optional[str] = ..., app_name: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...

class ListConnectionsRequest(_message.Message):
    __slots__ = ("plugin_name", "app_id", "include_history")
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HISTORY_FIELD_NUMBER: _ClassVar[int]
    plugin_name: str
    app_id: str
    include_history: bool
    def __init__(self, plugin_name: _Optional[str] = ..., app_id: _Optional[str] = ..., include_history: bool = ...) -> None: ...

class ListConnectionsResponse(_message.Message):
    __slots__ = ("connections",)
    CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
    connections: _containers.RepeatedCompositeFieldContainer[AppConnection]
    def __init__(self, connections: _Optional[_Iterable[_Union[AppConnection, _Mapping]]] = ...) -> None: ...

class AppConnection(_message.Message):
    __slots__ = ("app_id", "app_name", "plugin_name", "plugin_version", "plugin_instance_id", "plugin_address", "connected_at", "last_activity", "active")
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_VERSION_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    app_id: str
    app_name: str
    plugin_name: str
    plugin_version: str
    plugin_instance_id: str
    plugin_address: str
    connected_at: int
    last_activity: int
    active: bool
    def __init__(self, app_id: _Optional[str] = ..., app_name: _Optional[str] = ..., plugin_name: _Optional[str] = ..., plugin_version: _Optional[str] = ..., plugin_instance_id: _Optional[str] = ..., plugin_address: _Optional[str] = ..., connected_at: _Optional[int] = ..., last_activity: _Optional[int] = ..., active: bool = ...) -> None: ...
