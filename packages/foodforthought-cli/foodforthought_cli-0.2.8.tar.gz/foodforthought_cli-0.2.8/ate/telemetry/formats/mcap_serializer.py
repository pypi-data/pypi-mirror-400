"""
MCAP Serializer for Telemetry Data

Serializes trajectory recordings to MCAP format, which is the standard
for ROS2 bag files and is compatible with Foxglove visualization.

MCAP spec: https://mcap.dev/spec
"""

import io
import json
import struct
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..types import TrajectoryRecording, TrajectoryFrame

# MCAP constants
MCAP_MAGIC = b"\x89MCAP0\r\n"
MCAP_FOOTER_MAGIC = b"\x89MCAP0\r\n"

# Op codes
OP_HEADER = 0x01
OP_FOOTER = 0x02
OP_SCHEMA = 0x03
OP_CHANNEL = 0x04
OP_MESSAGE = 0x05
OP_CHUNK = 0x06
OP_MESSAGE_INDEX = 0x07
OP_CHUNK_INDEX = 0x08
OP_ATTACHMENT = 0x09
OP_ATTACHMENT_INDEX = 0x0A
OP_STATISTICS = 0x0B
OP_METADATA = 0x0C
OP_METADATA_INDEX = 0x0D
OP_SUMMARY_OFFSET = 0x0E
OP_DATA_END = 0x0F


def _write_record(buf: io.BytesIO, op: int, data: bytes) -> None:
    """Write a record to the buffer."""
    buf.write(struct.pack("<B", op))
    buf.write(struct.pack("<Q", len(data)))
    buf.write(data)


def _write_header(buf: io.BytesIO, profile: str = "", library: str = "ate-telemetry") -> None:
    """Write MCAP header."""
    profile_bytes = profile.encode("utf-8")
    library_bytes = library.encode("utf-8")

    data = io.BytesIO()
    data.write(struct.pack("<I", len(profile_bytes)))
    data.write(profile_bytes)
    data.write(struct.pack("<I", len(library_bytes)))
    data.write(library_bytes)

    _write_record(buf, OP_HEADER, data.getvalue())


def _write_schema(
    buf: io.BytesIO,
    schema_id: int,
    name: str,
    encoding: str,
    data: bytes,
) -> None:
    """Write a schema record."""
    name_bytes = name.encode("utf-8")
    encoding_bytes = encoding.encode("utf-8")

    record = io.BytesIO()
    record.write(struct.pack("<H", schema_id))
    record.write(struct.pack("<I", len(name_bytes)))
    record.write(name_bytes)
    record.write(struct.pack("<I", len(encoding_bytes)))
    record.write(encoding_bytes)
    record.write(struct.pack("<I", len(data)))
    record.write(data)

    _write_record(buf, OP_SCHEMA, record.getvalue())


def _write_channel(
    buf: io.BytesIO,
    channel_id: int,
    schema_id: int,
    topic: str,
    message_encoding: str,
    metadata: Dict[str, str] = None,
) -> None:
    """Write a channel record."""
    topic_bytes = topic.encode("utf-8")
    encoding_bytes = message_encoding.encode("utf-8")
    metadata = metadata or {}

    record = io.BytesIO()
    record.write(struct.pack("<H", channel_id))
    record.write(struct.pack("<H", schema_id))
    record.write(struct.pack("<I", len(topic_bytes)))
    record.write(topic_bytes)
    record.write(struct.pack("<I", len(encoding_bytes)))
    record.write(encoding_bytes)

    # Metadata map
    record.write(struct.pack("<I", len(metadata)))
    for key, value in metadata.items():
        key_bytes = key.encode("utf-8")
        value_bytes = value.encode("utf-8")
        record.write(struct.pack("<I", len(key_bytes)))
        record.write(key_bytes)
        record.write(struct.pack("<I", len(value_bytes)))
        record.write(value_bytes)

    _write_record(buf, OP_CHANNEL, record.getvalue())


def _write_message(
    buf: io.BytesIO,
    channel_id: int,
    sequence: int,
    log_time: int,
    publish_time: int,
    data: bytes,
) -> None:
    """Write a message record."""
    record = io.BytesIO()
    record.write(struct.pack("<H", channel_id))
    record.write(struct.pack("<I", sequence))
    record.write(struct.pack("<Q", log_time))
    record.write(struct.pack("<Q", publish_time))
    record.write(data)

    _write_record(buf, OP_MESSAGE, record.getvalue())


def _write_metadata(buf: io.BytesIO, name: str, metadata: Dict[str, str]) -> None:
    """Write a metadata record."""
    name_bytes = name.encode("utf-8")

    record = io.BytesIO()
    record.write(struct.pack("<I", len(name_bytes)))
    record.write(name_bytes)

    record.write(struct.pack("<I", len(metadata)))
    for key, value in metadata.items():
        key_bytes = key.encode("utf-8")
        value_bytes = str(value).encode("utf-8")
        record.write(struct.pack("<I", len(key_bytes)))
        record.write(key_bytes)
        record.write(struct.pack("<I", len(value_bytes)))
        record.write(value_bytes)

    _write_record(buf, OP_METADATA, record.getvalue())


def _write_data_end(buf: io.BytesIO) -> None:
    """Write data end record."""
    data = struct.pack("<I", 0)  # data_section_crc (0 = not computed)
    _write_record(buf, OP_DATA_END, data)


def _write_footer(buf: io.BytesIO) -> None:
    """Write MCAP footer."""
    data = io.BytesIO()
    data.write(struct.pack("<Q", 0))  # summary_start
    data.write(struct.pack("<Q", 0))  # summary_offset_start
    data.write(struct.pack("<I", 0))  # summary_crc

    _write_record(buf, OP_FOOTER, data.getvalue())


def serialize_to_mcap(recording: TrajectoryRecording) -> bytes:
    """
    Serialize trajectory recording to MCAP format.

    Creates an MCAP file with:
    - /joint_states topic: Joint positions, velocities, torques
    - /end_effector_pose topic: End effector pose (if available)
    - /events topic: Execution events

    Args:
        recording: The trajectory recording to serialize

    Returns:
        MCAP file as bytes
    """
    buf = io.BytesIO()

    # Write magic
    buf.write(MCAP_MAGIC)

    # Write header
    _write_header(buf, profile="ros2", library="ate-telemetry/1.0")

    # Define schemas
    joint_state_schema = json.dumps({
        "type": "object",
        "title": "JointState",
        "properties": {
            "timestamp": {"type": "number"},
            "positions": {"type": "object", "additionalProperties": {"type": "number"}},
            "velocities": {"type": "object", "additionalProperties": {"type": "number"}},
            "torques": {"type": "object", "additionalProperties": {"type": "number"}},
            "accelerations": {"type": "object", "additionalProperties": {"type": "number"}},
        },
    }).encode("utf-8")

    pose_schema = json.dumps({
        "type": "object",
        "title": "Pose",
        "properties": {
            "timestamp": {"type": "number"},
            "position": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "z": {"type": "number"},
                },
            },
            "orientation": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "z": {"type": "number"},
                    "w": {"type": "number"},
                },
            },
        },
    }).encode("utf-8")

    event_schema = json.dumps({
        "type": "object",
        "title": "ExecutionEvent",
        "properties": {
            "timestamp": {"type": "number"},
            "eventType": {"type": "string"},
            "data": {"type": "object"},
        },
    }).encode("utf-8")

    # Write schemas
    _write_schema(buf, 1, "JointState", "jsonschema", joint_state_schema)
    _write_schema(buf, 2, "Pose", "jsonschema", pose_schema)
    _write_schema(buf, 3, "ExecutionEvent", "jsonschema", event_schema)

    # Write channels
    _write_channel(buf, 1, 1, "/joint_states", "json", {
        "robot_id": recording.robot_id,
        "skill_id": recording.skill_id or "",
    })
    _write_channel(buf, 2, 2, "/end_effector_pose", "json")
    _write_channel(buf, 3, 3, "/events", "json")

    # Calculate base timestamp
    if recording.start_time:
        base_time_ns = int(recording.start_time.timestamp() * 1e9)
    else:
        base_time_ns = int(datetime.utcnow().timestamp() * 1e9)

    # Write frames as messages
    sequence = 0
    for frame in recording.frames:
        timestamp_ns = base_time_ns + int(frame.timestamp * 1e9)

        # Joint state message
        joint_data = json.dumps({
            "timestamp": frame.timestamp,
            "positions": frame.joint_positions,
            "velocities": frame.joint_velocities,
            "torques": frame.joint_torques,
            "accelerations": frame.joint_accelerations,
        }).encode("utf-8")

        _write_message(buf, 1, sequence, timestamp_ns, timestamp_ns, joint_data)
        sequence += 1

        # End effector pose message (if available)
        if frame.end_effector_pose:
            pose_data = json.dumps({
                "timestamp": frame.timestamp,
                "position": frame.end_effector_pose.position.to_dict(),
                "orientation": frame.end_effector_pose.orientation.to_dict(),
            }).encode("utf-8")

            _write_message(buf, 2, sequence, timestamp_ns, timestamp_ns, pose_data)
            sequence += 1

    # Write events as messages
    for event in recording.events:
        timestamp_ns = base_time_ns + int(event.timestamp * 1e9)

        event_data = json.dumps({
            "timestamp": event.timestamp,
            "eventType": event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
            "data": event.data,
        }).encode("utf-8")

        _write_message(buf, 3, sequence, timestamp_ns, timestamp_ns, event_data)
        sequence += 1

    # Write metadata
    _write_metadata(buf, "recording_info", {
        "recording_id": recording.id,
        "robot_id": recording.robot_id,
        "skill_id": recording.skill_id or "",
        "source": recording.source.value if hasattr(recording.source, "value") else str(recording.source),
        "success": str(recording.success),
        "duration": str(recording.metadata.duration),
        "frame_count": str(recording.metadata.total_frames),
        "frame_rate": str(recording.metadata.frame_rate),
    })

    # Write data end and footer
    _write_data_end(buf)
    _write_footer(buf)
    buf.write(MCAP_FOOTER_MAGIC)

    return buf.getvalue()


def deserialize_from_mcap(data: bytes) -> TrajectoryRecording:
    """
    Deserialize MCAP data to TrajectoryRecording.

    Args:
        data: MCAP file as bytes

    Returns:
        Parsed TrajectoryRecording
    """
    from ..types import (
        TrajectoryRecording,
        TrajectoryFrame,
        TrajectoryMetadata,
        ExecutionEvent,
        EventType,
        TelemetrySource,
        Pose,
        Vector3,
        Quaternion,
    )

    buf = io.BytesIO(data)

    # Verify magic
    magic = buf.read(8)
    if magic != MCAP_MAGIC:
        raise ValueError("Invalid MCAP file: bad magic")

    frames: List[TrajectoryFrame] = []
    events: List[ExecutionEvent] = []
    metadata: Dict[str, str] = {}
    channels: Dict[int, str] = {}

    while True:
        op_byte = buf.read(1)
        if not op_byte:
            break

        op = struct.unpack("<B", op_byte)[0]
        length = struct.unpack("<Q", buf.read(8))[0]
        record_data = buf.read(length)

        if op == OP_FOOTER:
            break

        if op == OP_CHANNEL:
            record_buf = io.BytesIO(record_data)
            channel_id = struct.unpack("<H", record_buf.read(2))[0]
            record_buf.read(2)  # schema_id
            topic_len = struct.unpack("<I", record_buf.read(4))[0]
            topic = record_buf.read(topic_len).decode("utf-8")
            channels[channel_id] = topic

        elif op == OP_MESSAGE:
            record_buf = io.BytesIO(record_data)
            channel_id = struct.unpack("<H", record_buf.read(2))[0]
            record_buf.read(4)  # sequence
            record_buf.read(8)  # log_time
            record_buf.read(8)  # publish_time
            msg_data = record_buf.read()

            topic = channels.get(channel_id, "")

            try:
                msg = json.loads(msg_data.decode("utf-8"))

                if topic == "/joint_states":
                    frame = TrajectoryFrame(
                        timestamp=msg.get("timestamp", 0),
                        joint_positions=msg.get("positions", {}),
                        joint_velocities=msg.get("velocities", {}),
                        joint_torques=msg.get("torques", {}),
                        joint_accelerations=msg.get("accelerations", {}),
                    )
                    frames.append(frame)

                elif topic == "/events":
                    event_type_str = msg.get("eventType", "")
                    try:
                        event_type = EventType(event_type_str)
                    except ValueError:
                        event_type = event_type_str

                    event = ExecutionEvent(
                        timestamp=msg.get("timestamp", 0),
                        event_type=event_type,
                        data=msg.get("data", {}),
                    )
                    events.append(event)

            except json.JSONDecodeError:
                pass

        elif op == OP_METADATA:
            record_buf = io.BytesIO(record_data)
            name_len = struct.unpack("<I", record_buf.read(4))[0]
            name = record_buf.read(name_len).decode("utf-8")

            if name == "recording_info":
                map_len = struct.unpack("<I", record_buf.read(4))[0]
                for _ in range(map_len):
                    key_len = struct.unpack("<I", record_buf.read(4))[0]
                    key = record_buf.read(key_len).decode("utf-8")
                    val_len = struct.unpack("<I", record_buf.read(4))[0]
                    val = record_buf.read(val_len).decode("utf-8")
                    metadata[key] = val

    # Sort frames by timestamp
    frames.sort(key=lambda f: f.timestamp)

    # Build recording
    source_str = metadata.get("source", "hardware")
    try:
        source = TelemetrySource(source_str)
    except ValueError:
        source = TelemetrySource.HARDWARE

    recording = TrajectoryRecording(
        id=metadata.get("recording_id", ""),
        robot_id=metadata.get("robot_id", ""),
        skill_id=metadata.get("skill_id") or None,
        source=source,
        success=metadata.get("success", "True").lower() == "true",
        frames=frames,
        events=events,
        metadata=TrajectoryMetadata(
            duration=float(metadata.get("duration", 0)),
            total_frames=int(metadata.get("frame_count", len(frames))),
            frame_rate=float(metadata.get("frame_rate", 0)),
        ),
    )

    return recording
