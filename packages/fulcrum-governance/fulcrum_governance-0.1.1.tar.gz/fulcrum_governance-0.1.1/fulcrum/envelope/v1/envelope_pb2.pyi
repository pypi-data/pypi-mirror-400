import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from fulcrum.events.v1 import events_pb2 as _events_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FrameworkType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FRAMEWORK_TYPE_UNSPECIFIED: _ClassVar[FrameworkType]
    FRAMEWORK_TYPE_LANGGRAPH: _ClassVar[FrameworkType]
    FRAMEWORK_TYPE_MICROSOFT: _ClassVar[FrameworkType]
    FRAMEWORK_TYPE_CREWAI: _ClassVar[FrameworkType]
    FRAMEWORK_TYPE_AUTOGEN: _ClassVar[FrameworkType]
    FRAMEWORK_TYPE_A2A_PROXY: _ClassVar[FrameworkType]
    FRAMEWORK_TYPE_CUSTOM: _ClassVar[FrameworkType]

class EnvelopeStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENVELOPE_STATUS_UNSPECIFIED: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_PENDING: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_AUTHORIZED: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_RUNNING: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_PAUSED: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_COMPLETED: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_FAILED: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_TERMINATED: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_BUDGET_EXCEEDED: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_POLICY_VIOLATION: _ClassVar[EnvelopeStatus]
    ENVELOPE_STATUS_TIMEOUT: _ClassVar[EnvelopeStatus]
FRAMEWORK_TYPE_UNSPECIFIED: FrameworkType
FRAMEWORK_TYPE_LANGGRAPH: FrameworkType
FRAMEWORK_TYPE_MICROSOFT: FrameworkType
FRAMEWORK_TYPE_CREWAI: FrameworkType
FRAMEWORK_TYPE_AUTOGEN: FrameworkType
FRAMEWORK_TYPE_A2A_PROXY: FrameworkType
FRAMEWORK_TYPE_CUSTOM: FrameworkType
ENVELOPE_STATUS_UNSPECIFIED: EnvelopeStatus
ENVELOPE_STATUS_PENDING: EnvelopeStatus
ENVELOPE_STATUS_AUTHORIZED: EnvelopeStatus
ENVELOPE_STATUS_RUNNING: EnvelopeStatus
ENVELOPE_STATUS_PAUSED: EnvelopeStatus
ENVELOPE_STATUS_COMPLETED: EnvelopeStatus
ENVELOPE_STATUS_FAILED: EnvelopeStatus
ENVELOPE_STATUS_TERMINATED: EnvelopeStatus
ENVELOPE_STATUS_BUDGET_EXCEEDED: EnvelopeStatus
ENVELOPE_STATUS_POLICY_VIOLATION: EnvelopeStatus
ENVELOPE_STATUS_TIMEOUT: EnvelopeStatus

class ExecutionEnvelope(_message.Message):
    __slots__ = ("envelope_id", "tenant_id", "workflow_id", "execution_id", "governance", "framework", "status", "events", "cost", "created_at", "updated_at", "completed_at", "parent_envelope_id", "metadata", "trace_context")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class TraceContextEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ENVELOPE_ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_ID_FIELD_NUMBER: _ClassVar[int]
    GOVERNANCE_FIELD_NUMBER: _ClassVar[int]
    FRAMEWORK_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    PARENT_ENVELOPE_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TRACE_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    envelope_id: str
    tenant_id: str
    workflow_id: str
    execution_id: str
    governance: GovernanceContext
    framework: FrameworkContext
    status: EnvelopeStatus
    events: _containers.RepeatedCompositeFieldContainer[_events_pb2.FulcrumEvent]
    cost: CostSummary
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    parent_envelope_id: str
    metadata: _containers.ScalarMap[str, str]
    trace_context: _containers.ScalarMap[str, str]
    def __init__(self, envelope_id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., workflow_id: _Optional[str] = ..., execution_id: _Optional[str] = ..., governance: _Optional[_Union[GovernanceContext, _Mapping]] = ..., framework: _Optional[_Union[FrameworkContext, _Mapping]] = ..., status: _Optional[_Union[EnvelopeStatus, str]] = ..., events: _Optional[_Iterable[_Union[_events_pb2.FulcrumEvent, _Mapping]]] = ..., cost: _Optional[_Union[CostSummary, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., completed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., parent_envelope_id: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ..., trace_context: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GovernanceContext(_message.Message):
    __slots__ = ("budget_id", "token_budget", "cost_limit_usd", "timeout_seconds", "policy_set_id", "allowed_models", "allowed_tools", "max_llm_calls", "max_tool_calls", "compliance_tags")
    BUDGET_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_BUDGET_FIELD_NUMBER: _ClassVar[int]
    COST_LIMIT_USD_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    POLICY_SET_ID_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_MODELS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_TOOLS_FIELD_NUMBER: _ClassVar[int]
    MAX_LLM_CALLS_FIELD_NUMBER: _ClassVar[int]
    MAX_TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    COMPLIANCE_TAGS_FIELD_NUMBER: _ClassVar[int]
    budget_id: str
    token_budget: int
    cost_limit_usd: float
    timeout_seconds: int
    policy_set_id: str
    allowed_models: _containers.RepeatedScalarFieldContainer[str]
    allowed_tools: _containers.RepeatedScalarFieldContainer[str]
    max_llm_calls: int
    max_tool_calls: int
    compliance_tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, budget_id: _Optional[str] = ..., token_budget: _Optional[int] = ..., cost_limit_usd: _Optional[float] = ..., timeout_seconds: _Optional[int] = ..., policy_set_id: _Optional[str] = ..., allowed_models: _Optional[_Iterable[str]] = ..., allowed_tools: _Optional[_Iterable[str]] = ..., max_llm_calls: _Optional[int] = ..., max_tool_calls: _Optional[int] = ..., compliance_tags: _Optional[_Iterable[str]] = ...) -> None: ...

class FrameworkContext(_message.Message):
    __slots__ = ("framework_type", "native_execution_ref", "checkpoint_id", "thread_id", "native_config")
    FRAMEWORK_TYPE_FIELD_NUMBER: _ClassVar[int]
    NATIVE_EXECUTION_REF_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    NATIVE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    framework_type: FrameworkType
    native_execution_ref: str
    checkpoint_id: str
    thread_id: str
    native_config: _struct_pb2.Struct
    def __init__(self, framework_type: _Optional[_Union[FrameworkType, str]] = ..., native_execution_ref: _Optional[str] = ..., checkpoint_id: _Optional[str] = ..., thread_id: _Optional[str] = ..., native_config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CostSummary(_message.Message):
    __slots__ = ("total_input_tokens", "total_output_tokens", "total_cost_usd", "llm_call_count", "tool_call_count", "model_costs")
    TOTAL_INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COST_USD_FIELD_NUMBER: _ClassVar[int]
    LLM_CALL_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_COUNT_FIELD_NUMBER: _ClassVar[int]
    MODEL_COSTS_FIELD_NUMBER: _ClassVar[int]
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    llm_call_count: int
    tool_call_count: int
    model_costs: _containers.RepeatedCompositeFieldContainer[ModelCost]
    def __init__(self, total_input_tokens: _Optional[int] = ..., total_output_tokens: _Optional[int] = ..., total_cost_usd: _Optional[float] = ..., llm_call_count: _Optional[int] = ..., tool_call_count: _Optional[int] = ..., model_costs: _Optional[_Iterable[_Union[ModelCost, _Mapping]]] = ...) -> None: ...

class ModelCost(_message.Message):
    __slots__ = ("model_id", "input_tokens", "output_tokens", "cost_usd", "call_count")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    COST_USD_FIELD_NUMBER: _ClassVar[int]
    CALL_COUNT_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    call_count: int
    def __init__(self, model_id: _Optional[str] = ..., input_tokens: _Optional[int] = ..., output_tokens: _Optional[int] = ..., cost_usd: _Optional[float] = ..., call_count: _Optional[int] = ...) -> None: ...

class Checkpoint(_message.Message):
    __slots__ = ("checkpoint_id", "envelope_id", "created_at", "state_hash", "state_data", "state_size_bytes", "node_id", "iteration", "cost_snapshot")
    CHECKPOINT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVELOPE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATE_HASH_FIELD_NUMBER: _ClassVar[int]
    STATE_DATA_FIELD_NUMBER: _ClassVar[int]
    STATE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    ITERATION_FIELD_NUMBER: _ClassVar[int]
    COST_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    checkpoint_id: str
    envelope_id: str
    created_at: _timestamp_pb2.Timestamp
    state_hash: str
    state_data: bytes
    state_size_bytes: int
    node_id: str
    iteration: int
    cost_snapshot: CostSummary
    def __init__(self, checkpoint_id: _Optional[str] = ..., envelope_id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., state_hash: _Optional[str] = ..., state_data: _Optional[bytes] = ..., state_size_bytes: _Optional[int] = ..., node_id: _Optional[str] = ..., iteration: _Optional[int] = ..., cost_snapshot: _Optional[_Union[CostSummary, _Mapping]] = ...) -> None: ...
