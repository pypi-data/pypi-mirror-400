from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Manifest(_message.Message):
    __slots__ = ("name", "version", "description", "author", "homepage", "license", "capabilities", "analyzer_rules_json")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    HOMEPAGE_FIELD_NUMBER: _ClassVar[int]
    LICENSE_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_RULES_JSON_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    description: str
    author: str
    homepage: str
    license: str
    capabilities: _containers.RepeatedScalarFieldContainer[str]
    analyzer_rules_json: bytes
    def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ..., description: _Optional[str] = ..., author: _Optional[str] = ..., homepage: _Optional[str] = ..., license: _Optional[str] = ..., capabilities: _Optional[_Iterable[str]] = ..., analyzer_rules_json: _Optional[bytes] = ...) -> None: ...

class ActionRequest(_message.Message):
    __slots__ = ("action_name", "trace_id", "data_json", "config_json", "context_json", "app_id", "app_name")
    ACTION_NAME_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_JSON_FIELD_NUMBER: _ClassVar[int]
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_JSON_FIELD_NUMBER: _ClassVar[int]
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    action_name: str
    trace_id: str
    data_json: bytes
    config_json: bytes
    context_json: bytes
    app_id: str
    app_name: str
    def __init__(self, action_name: _Optional[str] = ..., trace_id: _Optional[str] = ..., data_json: _Optional[bytes] = ..., config_json: _Optional[bytes] = ..., context_json: _Optional[bytes] = ..., app_id: _Optional[str] = ..., app_name: _Optional[str] = ...) -> None: ...

class ActionResponse(_message.Message):
    __slots__ = ("success", "result_json", "error", "error_code")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_JSON_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    result_json: bytes
    error: str
    error_code: str
    def __init__(self, success: bool = ..., result_json: _Optional[bytes] = ..., error: _Optional[str] = ..., error_code: _Optional[str] = ...) -> None: ...

class ActionMeta(_message.Message):
    __slots__ = ("name", "category", "description", "tags", "inputs_json", "outputs_json", "examples_json")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_JSON_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_JSON_FIELD_NUMBER: _ClassVar[int]
    EXAMPLES_JSON_FIELD_NUMBER: _ClassVar[int]
    name: str
    category: str
    description: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    inputs_json: bytes
    outputs_json: bytes
    examples_json: bytes
    def __init__(self, name: _Optional[str] = ..., category: _Optional[str] = ..., description: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., inputs_json: _Optional[bytes] = ..., outputs_json: _Optional[bytes] = ..., examples_json: _Optional[bytes] = ...) -> None: ...

class ActionList(_message.Message):
    __slots__ = ("actions",)
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    actions: _containers.RepeatedCompositeFieldContainer[ActionMeta]
    def __init__(self, actions: _Optional[_Iterable[_Union[ActionMeta, _Mapping]]] = ...) -> None: ...

class ProviderConfig(_message.Message):
    __slots__ = ("name", "config_json")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    name: str
    config_json: bytes
    def __init__(self, name: _Optional[str] = ..., config_json: _Optional[bytes] = ...) -> None: ...

class ProviderName(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ProviderResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...

class HealthResponse(_message.Message):
    __slots__ = ("healthy", "message", "details")
    class DetailsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    healthy: bool
    message: str
    details: _containers.ScalarMap[str, str]
    def __init__(self, healthy: bool = ..., message: _Optional[str] = ..., details: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PluginStatus(_message.Message):
    __slots__ = ("manifest", "uptime_seconds", "resources", "stats")
    MANIFEST_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    manifest: Manifest
    uptime_seconds: int
    resources: _containers.RepeatedCompositeFieldContainer[PluginResource]
    stats: PluginStats
    def __init__(self, manifest: _Optional[_Union[Manifest, _Mapping]] = ..., uptime_seconds: _Optional[int] = ..., resources: _Optional[_Iterable[_Union[PluginResource, _Mapping]]] = ..., stats: _Optional[_Union[PluginStats, _Mapping]] = ...) -> None: ...

class PluginResource(_message.Message):
    __slots__ = ("type", "name", "status", "info")
    class InfoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    type: str
    name: str
    status: str
    info: _containers.ScalarMap[str, str]
    def __init__(self, type: _Optional[str] = ..., name: _Optional[str] = ..., status: _Optional[str] = ..., info: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PluginStats(_message.Message):
    __slots__ = ("total_executions", "successful", "failed", "avg_latency_ms", "action_counts")
    class ActionCountsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    TOTAL_EXECUTIONS_FIELD_NUMBER: _ClassVar[int]
    SUCCESSFUL_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    AVG_LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
    ACTION_COUNTS_FIELD_NUMBER: _ClassVar[int]
    total_executions: int
    successful: int
    failed: int
    avg_latency_ms: float
    action_counts: _containers.ScalarMap[str, int]
    def __init__(self, total_executions: _Optional[int] = ..., successful: _Optional[int] = ..., failed: _Optional[int] = ..., avg_latency_ms: _Optional[float] = ..., action_counts: _Optional[_Mapping[str, int]] = ...) -> None: ...
