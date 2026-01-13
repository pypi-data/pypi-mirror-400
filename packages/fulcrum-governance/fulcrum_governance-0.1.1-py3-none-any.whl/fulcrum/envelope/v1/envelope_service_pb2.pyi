from fulcrum.envelope.v1 import envelope_pb2 as _envelope_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateEnvelopeRequest(_message.Message):
    __slots__ = ("tenant_id", "budget_id", "adapter_type", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    BUDGET_ID_FIELD_NUMBER: _ClassVar[int]
    ADAPTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    tenant_id: str
    budget_id: str
    adapter_type: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, tenant_id: _Optional[str] = ..., budget_id: _Optional[str] = ..., adapter_type: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CreateEnvelopeResponse(_message.Message):
    __slots__ = ("envelope",)
    ENVELOPE_FIELD_NUMBER: _ClassVar[int]
    envelope: _envelope_pb2.ExecutionEnvelope
    def __init__(self, envelope: _Optional[_Union[_envelope_pb2.ExecutionEnvelope, _Mapping]] = ...) -> None: ...

class GetEnvelopeRequest(_message.Message):
    __slots__ = ("envelope_id",)
    ENVELOPE_ID_FIELD_NUMBER: _ClassVar[int]
    envelope_id: str
    def __init__(self, envelope_id: _Optional[str] = ...) -> None: ...

class GetEnvelopeResponse(_message.Message):
    __slots__ = ("envelope",)
    ENVELOPE_FIELD_NUMBER: _ClassVar[int]
    envelope: _envelope_pb2.ExecutionEnvelope
    def __init__(self, envelope: _Optional[_Union[_envelope_pb2.ExecutionEnvelope, _Mapping]] = ...) -> None: ...

class UpdateEnvelopeStatusRequest(_message.Message):
    __slots__ = ("envelope_id", "status", "reason")
    ENVELOPE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    envelope_id: str
    status: _envelope_pb2.EnvelopeStatus
    reason: str
    def __init__(self, envelope_id: _Optional[str] = ..., status: _Optional[_Union[_envelope_pb2.EnvelopeStatus, str]] = ..., reason: _Optional[str] = ...) -> None: ...

class UpdateEnvelopeStatusResponse(_message.Message):
    __slots__ = ("envelope",)
    ENVELOPE_FIELD_NUMBER: _ClassVar[int]
    envelope: _envelope_pb2.ExecutionEnvelope
    def __init__(self, envelope: _Optional[_Union[_envelope_pb2.ExecutionEnvelope, _Mapping]] = ...) -> None: ...
