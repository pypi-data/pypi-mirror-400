import json
from dataclasses import dataclass, asdict
from enum import Enum, IntEnum
from typing import List, Optional
from uuid import uuid4

from construct import (
    Struct,
    Float64l,
    PascalString,
    Int8ul,
    Bytes,
)


# ============================================================================
# CONTROL (JSON) MESSAGES
# ============================================================================


class MessageType(str, Enum):
    TOPIC_REQUEST = "topic_request"
    TOPIC_RESPONSE = "topic_response"
    SIGNAL_REQUEST = "signal_request"
    SIGNAL_RESPONSE = "signal_response"
    HELLO_MESSAGE = "hello_message"


def _normalize_topic(topic: str) -> str:
    return topic if topic.startswith("/") else f"/{topic}"


def _generate_msg_id() -> str:
    return uuid4().hex


@dataclass(slots=True)
class HelloMessage:
    msg_id:str
    peer_id: str
    owner: str
    connection:list

    def to_json(self) -> str:
        return json.dumps(
            {
                "id": self.msg_id,
                "type": MessageType.HELLO_MESSAGE.value,
                "peer_id": self.peer_id,
                "owner":self.owner,
                "connection":self.connection
            }
        )

@dataclass(slots=True)
class TopicRequest:
    topic_name: str
    msg_id: Optional[str] = None
    maxhop: int = 1

    def __post_init__(self) -> None:
        self.topic_name = _normalize_topic(self.topic_name)
        self.msg_id = self.msg_id or _generate_msg_id()

    def to_json(self, node_id: str) -> str:
        return json.dumps(
            {
                "id": self.msg_id,
                "type": MessageType.TOPIC_REQUEST.value,
                "node": node_id,
                "maxhop": self.maxhop,
                "detail": {"topic_name": self.topic_name},
            }
        )


@dataclass(slots=True)
class TopicResponse:
    topic_name: str
    status: bool
    signals: Optional[List[str]] = None
    msg_id: Optional[str] = None
    maxhop: int = 0

    def __post_init__(self) -> None:
        self.topic_name = _normalize_topic(self.topic_name)
        self.msg_id = self.msg_id or _generate_msg_id()

    def to_json(self, node_id: str) -> str:
        detail = {
            "topic_name": self.topic_name,
            "status": self.status,
        }
        if self.signals is not None:
            detail["signals"] = self.signals

        return json.dumps(
            {
                "id": self.msg_id,
                "type": MessageType.TOPIC_RESPONSE.value,
                "node": node_id,
                "maxhop": self.maxhop,
                "detail": detail,
            }
        )


@dataclass(slots=True)
class SignalRequest:
    topic: str
    signal: str
    msg_id: Optional[str] = None
    maxhop: int = 1

    def __post_init__(self) -> None:
        self.topic = _normalize_topic(self.topic)
        self.msg_id = self.msg_id or _generate_msg_id()

    def to_json(self, node_id: str) -> str:
        return json.dumps(
            {
                "id": self.msg_id,
                "type": MessageType.SIGNAL_REQUEST.value,
                "node": node_id,
                "maxhop": self.maxhop,
                "detail": {
                    "topic": self.topic,
                    "signal": self.signal,
                },
            }
        )


@dataclass(slots=True)
class SignalResponse:
    topic: str
    signal: str
    status: bool
    msg_id: Optional[str] = None
    maxhop: int = 0

    def __post_init__(self) -> None:
        self.topic = _normalize_topic(self.topic)
        self.msg_id = self.msg_id or _generate_msg_id()

    def to_json(self, node_id: str) -> str:
        return json.dumps(
            {
                "id": self.msg_id,
                "type": MessageType.SIGNAL_RESPONSE.value,
                "node": node_id,
                "maxhop": self.maxhop,
                "detail": {
                    "topic": self.topic,
                    "signal": self.signal,
                    "status": self.status,
                },
            }
        )


def parse_message(data: bytes) -> Optional[dict]:
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


# ============================================================================
# STREAM (BINARY) MESSAGES
# ============================================================================


class StreamType(IntEnum):
    SIGNAL_DATA = 0x01
    FILE_BATCH = 0x02


SignalDataStruct = Struct(
    "type" / Int8ul,
    "key" / PascalString(Int8ul, "utf8"),
    "value" / Float64l,
    "time" / Float64l,
)

FileBatchStruct = Struct(
    "type" / Int8ul,
    "batch_id" / PascalString(Int8ul, "utf8"),
    "chunk_index" / Int8ul,
    "total_chunks" / Int8ul,
    "data_length" / Int8ul,
    "data" / Bytes(lambda ctx: ctx.data_length),
)


@dataclass(slots=True)
class SignalData:
    key: str
    value: float
    time: float

    def to_bytes(self) -> bytes:
        return SignalDataStruct.build(
            {
                "type": StreamType.SIGNAL_DATA,
                "key": self.key,
                "value": self.value,
                "time": self.time,
            }
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "SignalData":
        parsed = SignalDataStruct.parse(data)
        return cls(parsed.key, parsed.value, parsed.time)

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> "SignalData":
        return cls(**json.loads(data))


@dataclass(slots=True)
class FileBatch:
    batch_id: str
    chunk_index: int
    total_chunks: int
    data: bytes

    def to_bytes(self) -> bytes:
        return FileBatchStruct.build(
            {
                "type": StreamType.FILE_BATCH,
                "batch_id": self.batch_id,
                "chunk_index": self.chunk_index,
                "total_chunks": self.total_chunks,
                "data_length": len(self.data),
                "data": self.data,
            }
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "FileBatch":
        parsed = FileBatchStruct.parse(data)
        return cls(
            parsed.batch_id,
            parsed.chunk_index,
            parsed.total_chunks,
            bytes(parsed.data),
        )


def parse_stream_data(data: bytes) -> Optional[object]:
    if not data:
        return None

    try:
        stream_type = StreamType(data[0])
    except ValueError:
        return None

    try:
        if stream_type is StreamType.SIGNAL_DATA:
            return SignalData.from_bytes(data)
        if stream_type is StreamType.FILE_BATCH:
            return FileBatch.from_bytes(data)
    except Exception:
        return None

    return None
