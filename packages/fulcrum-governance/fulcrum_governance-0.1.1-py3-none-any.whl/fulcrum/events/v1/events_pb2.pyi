import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[EventType]
    EVENT_TYPE_EXECUTION_STARTED: _ClassVar[EventType]
    EVENT_TYPE_EXECUTION_COMPLETED: _ClassVar[EventType]
    EVENT_TYPE_EXECUTION_FAILED: _ClassVar[EventType]
    EVENT_TYPE_EXECUTION_PAUSED: _ClassVar[EventType]
    EVENT_TYPE_EXECUTION_RESUMED: _ClassVar[EventType]
    EVENT_TYPE_EXECUTION_TERMINATED: _ClassVar[EventType]
    EVENT_TYPE_LLM_CALL_STARTED: _ClassVar[EventType]
    EVENT_TYPE_LLM_CALL_COMPLETED: _ClassVar[EventType]
    EVENT_TYPE_LLM_CALL_FAILED: _ClassVar[EventType]
    EVENT_TYPE_LLM_STREAMING_CHUNK: _ClassVar[EventType]
    EVENT_TYPE_TOOL_INVOKED: _ClassVar[EventType]
    EVENT_TYPE_TOOL_COMPLETED: _ClassVar[EventType]
    EVENT_TYPE_TOOL_FAILED: _ClassVar[EventType]
    EVENT_TYPE_CHECKPOINT_CREATED: _ClassVar[EventType]
    EVENT_TYPE_CHECKPOINT_RESTORED: _ClassVar[EventType]
    EVENT_TYPE_BUDGET_WARNING: _ClassVar[EventType]
    EVENT_TYPE_BUDGET_EXCEEDED: _ClassVar[EventType]
    EVENT_TYPE_BUDGET_RESET: _ClassVar[EventType]
    EVENT_TYPE_POLICY_EVALUATED: _ClassVar[EventType]
    EVENT_TYPE_POLICY_VIOLATION: _ClassVar[EventType]
    EVENT_TYPE_POLICY_WARNING: _ClassVar[EventType]
    EVENT_TYPE_AGENT_HANDOFF: _ClassVar[EventType]
    EVENT_TYPE_AGENT_SPAWN: _ClassVar[EventType]
    EVENT_TYPE_AGENT_JOIN: _ClassVar[EventType]
    EVENT_TYPE_CUSTOM: _ClassVar[EventType]

class EventSeverity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_SEVERITY_UNSPECIFIED: _ClassVar[EventSeverity]
    EVENT_SEVERITY_DEBUG: _ClassVar[EventSeverity]
    EVENT_SEVERITY_INFO: _ClassVar[EventSeverity]
    EVENT_SEVERITY_WARNING: _ClassVar[EventSeverity]
    EVENT_SEVERITY_ERROR: _ClassVar[EventSeverity]
    EVENT_SEVERITY_CRITICAL: _ClassVar[EventSeverity]

class PolicyDecision(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    POLICY_DECISION_UNSPECIFIED: _ClassVar[PolicyDecision]
    POLICY_DECISION_ALLOW: _ClassVar[PolicyDecision]
    POLICY_DECISION_DENY: _ClassVar[PolicyDecision]
    POLICY_DECISION_WARN: _ClassVar[PolicyDecision]
EVENT_TYPE_UNSPECIFIED: EventType
EVENT_TYPE_EXECUTION_STARTED: EventType
EVENT_TYPE_EXECUTION_COMPLETED: EventType
EVENT_TYPE_EXECUTION_FAILED: EventType
EVENT_TYPE_EXECUTION_PAUSED: EventType
EVENT_TYPE_EXECUTION_RESUMED: EventType
EVENT_TYPE_EXECUTION_TERMINATED: EventType
EVENT_TYPE_LLM_CALL_STARTED: EventType
EVENT_TYPE_LLM_CALL_COMPLETED: EventType
EVENT_TYPE_LLM_CALL_FAILED: EventType
EVENT_TYPE_LLM_STREAMING_CHUNK: EventType
EVENT_TYPE_TOOL_INVOKED: EventType
EVENT_TYPE_TOOL_COMPLETED: EventType
EVENT_TYPE_TOOL_FAILED: EventType
EVENT_TYPE_CHECKPOINT_CREATED: EventType
EVENT_TYPE_CHECKPOINT_RESTORED: EventType
EVENT_TYPE_BUDGET_WARNING: EventType
EVENT_TYPE_BUDGET_EXCEEDED: EventType
EVENT_TYPE_BUDGET_RESET: EventType
EVENT_TYPE_POLICY_EVALUATED: EventType
EVENT_TYPE_POLICY_VIOLATION: EventType
EVENT_TYPE_POLICY_WARNING: EventType
EVENT_TYPE_AGENT_HANDOFF: EventType
EVENT_TYPE_AGENT_SPAWN: EventType
EVENT_TYPE_AGENT_JOIN: EventType
EVENT_TYPE_CUSTOM: EventType
EVENT_SEVERITY_UNSPECIFIED: EventSeverity
EVENT_SEVERITY_DEBUG: EventSeverity
EVENT_SEVERITY_INFO: EventSeverity
EVENT_SEVERITY_WARNING: EventSeverity
EVENT_SEVERITY_ERROR: EventSeverity
EVENT_SEVERITY_CRITICAL: EventSeverity
POLICY_DECISION_UNSPECIFIED: PolicyDecision
POLICY_DECISION_ALLOW: PolicyDecision
POLICY_DECISION_DENY: PolicyDecision
POLICY_DECISION_WARN: PolicyDecision

class FulcrumEvent(_message.Message):
    __slots__ = ("event_id", "envelope_id", "tenant_id", "workflow_id", "timestamp", "event_type", "severity", "tokens", "checkpoint", "error", "tool", "policy", "budget", "native_payload", "trace")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVELOPE_ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TOOL_FIELD_NUMBER: _ClassVar[int]
    POLICY_FIELD_NUMBER: _ClassVar[int]
    BUDGET_FIELD_NUMBER: _ClassVar[int]
    NATIVE_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    envelope_id: str
    tenant_id: str
    workflow_id: str
    timestamp: _timestamp_pb2.Timestamp
    event_type: EventType
    severity: EventSeverity
    tokens: TokenInfo
    checkpoint: CheckpointRef
    error: ErrorInfo
    tool: ToolInfo
    policy: PolicyResult
    budget: BudgetStatusEvent
    native_payload: _struct_pb2.Struct
    trace: TraceContext
    def __init__(self, event_id: _Optional[str] = ..., envelope_id: _Optional[str] = ..., tenant_id: _Optional[str] = ..., workflow_id: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., event_type: _Optional[_Union[EventType, str]] = ..., severity: _Optional[_Union[EventSeverity, str]] = ..., tokens: _Optional[_Union[TokenInfo, _Mapping]] = ..., checkpoint: _Optional[_Union[CheckpointRef, _Mapping]] = ..., error: _Optional[_Union[ErrorInfo, _Mapping]] = ..., tool: _Optional[_Union[ToolInfo, _Mapping]] = ..., policy: _Optional[_Union[PolicyResult, _Mapping]] = ..., budget: _Optional[_Union[BudgetStatusEvent, _Mapping]] = ..., native_payload: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., trace: _Optional[_Union[TraceContext, _Mapping]] = ...) -> None: ...

class TokenInfo(_message.Message):
    __slots__ = ("model_id", "input_tokens", "output_tokens", "cost_usd", "time_to_first_token_ms", "total_latency_ms", "is_streaming", "chunk_index")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    COST_USD_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_FIRST_TOKEN_MS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
    IS_STREAMING_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    time_to_first_token_ms: int
    total_latency_ms: int
    is_streaming: bool
    chunk_index: int
    def __init__(self, model_id: _Optional[str] = ..., input_tokens: _Optional[int] = ..., output_tokens: _Optional[int] = ..., cost_usd: _Optional[float] = ..., time_to_first_token_ms: _Optional[int] = ..., total_latency_ms: _Optional[int] = ..., is_streaming: bool = ..., chunk_index: _Optional[int] = ...) -> None: ...

class CheckpointRef(_message.Message):
    __slots__ = ("checkpoint_id", "state_hash", "size_bytes")
    CHECKPOINT_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_HASH_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    checkpoint_id: str
    state_hash: str
    size_bytes: int
    def __init__(self, checkpoint_id: _Optional[str] = ..., state_hash: _Optional[str] = ..., size_bytes: _Optional[int] = ...) -> None: ...

class ErrorInfo(_message.Message):
    __slots__ = ("code", "message", "recoverable", "stack_trace", "retry_count", "will_retry")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECOVERABLE_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    RETRY_COUNT_FIELD_NUMBER: _ClassVar[int]
    WILL_RETRY_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    recoverable: bool
    stack_trace: str
    retry_count: int
    will_retry: bool
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ..., recoverable: bool = ..., stack_trace: _Optional[str] = ..., retry_count: _Optional[int] = ..., will_retry: bool = ...) -> None: ...

class ToolInfo(_message.Message):
    __slots__ = ("tool_name", "tool_id", "input", "output", "latency_ms", "success")
    TOOL_NAME_FIELD_NUMBER: _ClassVar[int]
    TOOL_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    tool_name: str
    tool_id: str
    input: _struct_pb2.Struct
    output: _struct_pb2.Struct
    latency_ms: int
    success: bool
    def __init__(self, tool_name: _Optional[str] = ..., tool_id: _Optional[str] = ..., input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., output: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., latency_ms: _Optional[int] = ..., success: bool = ...) -> None: ...

class PolicyResult(_message.Message):
    __slots__ = ("policy_id", "rule_id", "decision", "reason", "trigger")
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    RULE_ID_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    rule_id: str
    decision: PolicyDecision
    reason: str
    trigger: str
    def __init__(self, policy_id: _Optional[str] = ..., rule_id: _Optional[str] = ..., decision: _Optional[_Union[PolicyDecision, str]] = ..., reason: _Optional[str] = ..., trigger: _Optional[str] = ...) -> None: ...

class BudgetStatusEvent(_message.Message):
    __slots__ = ("budget_id", "tokens_used", "tokens_remaining", "cost_used_usd", "cost_remaining_usd", "percentage_used", "threshold_percentage")
    BUDGET_ID_FIELD_NUMBER: _ClassVar[int]
    TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    TOKENS_REMAINING_FIELD_NUMBER: _ClassVar[int]
    COST_USED_USD_FIELD_NUMBER: _ClassVar[int]
    COST_REMAINING_USD_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_USED_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    budget_id: str
    tokens_used: int
    tokens_remaining: int
    cost_used_usd: float
    cost_remaining_usd: float
    percentage_used: float
    threshold_percentage: float
    def __init__(self, budget_id: _Optional[str] = ..., tokens_used: _Optional[int] = ..., tokens_remaining: _Optional[int] = ..., cost_used_usd: _Optional[float] = ..., cost_remaining_usd: _Optional[float] = ..., percentage_used: _Optional[float] = ..., threshold_percentage: _Optional[float] = ...) -> None: ...

class TraceContext(_message.Message):
    __slots__ = ("trace_id", "span_id", "parent_span_id", "baggage")
    class BaggageEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    BAGGAGE_FIELD_NUMBER: _ClassVar[int]
    trace_id: str
    span_id: str
    parent_span_id: str
    baggage: _containers.ScalarMap[str, str]
    def __init__(self, trace_id: _Optional[str] = ..., span_id: _Optional[str] = ..., parent_span_id: _Optional[str] = ..., baggage: _Optional[_Mapping[str, str]] = ...) -> None: ...
