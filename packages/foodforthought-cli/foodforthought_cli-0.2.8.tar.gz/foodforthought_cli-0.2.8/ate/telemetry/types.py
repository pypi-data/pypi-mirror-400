"""
Telemetry data types for FoodforThought

Defines the core data structures for trajectory recording, sensor data,
and execution events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class TelemetrySource(str, Enum):
    """Source of telemetry data"""
    SIMULATION = "simulation"
    HARDWARE = "hardware"
    FLEET = "fleet"


class EventType(str, Enum):
    """Types of execution events"""
    SKILL_START = "skill_start"
    SKILL_END = "skill_end"
    CONTACT = "contact"
    ERROR = "error"
    RECOVERY = "recovery"
    USER_INTERVENTION = "user_intervention"
    WAYPOINT_REACHED = "waypoint_reached"
    GRASP = "grasp"
    RELEASE = "release"


class SensorType(str, Enum):
    """Types of sensor readings"""
    FORCE = "force"
    TORQUE = "torque"
    IMU = "imu"
    CAMERA = "camera"
    LIDAR = "lidar"
    PROXIMITY = "proximity"
    TEMPERATURE = "temperature"
    CURRENT = "current"


@dataclass
class Vector3:
    """3D vector for positions and forces"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]

    @classmethod
    def from_list(cls, data: List[float]) -> "Vector3":
        return cls(x=data[0], y=data[1], z=data[2] if len(data) > 2 else 0.0)


@dataclass
class Quaternion:
    """Quaternion for orientations (w, x, y, z)"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z, "w": self.w}

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z, self.w]

    @classmethod
    def from_list(cls, data: List[float]) -> "Quaternion":
        return cls(x=data[0], y=data[1], z=data[2], w=data[3])


@dataclass
class Pose:
    """6-DOF pose with position and orientation"""
    position: Vector3 = field(default_factory=Vector3)
    orientation: Quaternion = field(default_factory=Quaternion)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position.to_dict(),
            "orientation": self.orientation.to_dict(),
        }

    def to_flat_list(self) -> List[float]:
        """Returns [x, y, z, qx, qy, qz, qw]"""
        return self.position.to_list() + self.orientation.to_list()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pose":
        pos = data.get("position", {})
        ori = data.get("orientation", {})
        return cls(
            position=Vector3(
                x=pos.get("x", 0),
                y=pos.get("y", 0),
                z=pos.get("z", 0)
            ),
            orientation=Quaternion(
                x=ori.get("x", 0),
                y=ori.get("y", 0),
                z=ori.get("z", 0),
                w=ori.get("w", 1)
            ),
        )


@dataclass
class Contact:
    """Contact information between robot and environment"""
    body1: str  # Name of first body in contact
    body2: str  # Name of second body in contact
    position: Vector3 = field(default_factory=Vector3)
    normal: Vector3 = field(default_factory=Vector3)
    force: float = 0.0  # Contact force magnitude
    penetration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body1": self.body1,
            "body2": self.body2,
            "position": self.position.to_dict(),
            "normal": self.normal.to_dict(),
            "force": self.force,
            "penetration": self.penetration,
        }


@dataclass
class SensorReading:
    """Individual sensor reading"""
    timestamp: float  # Seconds from recording start
    sensor_id: str
    sensor_type: SensorType
    data: Union[List[float], bytes]  # Raw sensor data or numeric values

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "sensorId": self.sensor_id,
            "sensorType": self.sensor_type.value if isinstance(self.sensor_type, SensorType) else self.sensor_type,
            "data": list(self.data) if isinstance(self.data, (list, tuple)) else None,
        }


@dataclass
class TrajectoryFrame:
    """Single frame of trajectory data"""
    timestamp: float  # Seconds from recording start
    joint_positions: Dict[str, float] = field(default_factory=dict)
    joint_velocities: Dict[str, float] = field(default_factory=dict)
    joint_torques: Dict[str, float] = field(default_factory=dict)
    joint_accelerations: Dict[str, float] = field(default_factory=dict)
    end_effector_pose: Optional[Pose] = None
    contacts: List[Contact] = field(default_factory=list)
    sensor_readings: Dict[str, float] = field(default_factory=dict)
    control_inputs: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "jointPositions": self.joint_positions,
            "jointVelocities": self.joint_velocities,
            "jointTorques": self.joint_torques,
            "jointAccelerations": self.joint_accelerations,
            "endEffectorPose": self.end_effector_pose.to_dict() if self.end_effector_pose else None,
            "contacts": [c.to_dict() for c in self.contacts],
            "sensorReadings": self.sensor_readings,
            "controlInputs": self.control_inputs,
        }


@dataclass
class DomainRandomizationConfig:
    """Configuration for domain randomization applied during recording"""
    friction_range: Optional[tuple] = None
    mass_range: Optional[tuple] = None
    damping_range: Optional[tuple] = None
    noise_scale: float = 0.0
    visual_variations: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frictionRange": list(self.friction_range) if self.friction_range else None,
            "massRange": list(self.mass_range) if self.mass_range else None,
            "dampingRange": list(self.damping_range) if self.damping_range else None,
            "noiseScale": self.noise_scale,
            "visualVariations": self.visual_variations,
        }


@dataclass
class TrajectoryMetadata:
    """Metadata about a trajectory recording"""
    duration: float = 0.0  # Total duration in seconds
    frame_rate: float = 0.0  # Frames per second
    total_frames: int = 0
    skill_params: Optional[Dict[str, Any]] = None
    environment_id: Optional[str] = None
    domain_randomization: Optional[DomainRandomizationConfig] = None
    robot_version: Optional[str] = None
    urdf_hash: Optional[str] = None  # Hash of URDF for reproducibility
    joint_names: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "duration": self.duration,
            "frameRate": self.frame_rate,
            "totalFrames": self.total_frames,
            "skillParams": self.skill_params,
            "environmentId": self.environment_id,
            "domainRandomization": self.domain_randomization.to_dict() if self.domain_randomization else None,
            "robotVersion": self.robot_version,
            "urdfHash": self.urdf_hash,
            "jointNames": self.joint_names,
            "tags": self.tags,
        }


@dataclass
class TrajectoryRecording:
    """Complete trajectory recording with frames and metadata"""
    id: str
    robot_id: str
    skill_id: Optional[str] = None
    source: TelemetrySource = TelemetrySource.HARDWARE
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    success: bool = True
    frames: List[TrajectoryFrame] = field(default_factory=list)
    metadata: TrajectoryMetadata = field(default_factory=TrajectoryMetadata)
    events: List["ExecutionEvent"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "robotId": self.robot_id,
            "skillId": self.skill_id,
            "source": self.source.value if isinstance(self.source, TelemetrySource) else self.source,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "success": self.success,
            "metadata": self.metadata.to_dict(),
            "frameCount": len(self.frames),
            "eventCount": len(self.events),
        }


@dataclass
class ExecutionEvent:
    """Event that occurred during skill execution"""
    timestamp: float  # Seconds from recording start
    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "eventType": self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            "data": self.data,
        }


@dataclass
class TelemetryBuffer:
    """Ring buffer for efficient telemetry storage"""
    max_size: int = 36000  # 10 minutes at 60Hz
    _frames: List[TrajectoryFrame] = field(default_factory=list, repr=False)
    _events: List[ExecutionEvent] = field(default_factory=list, repr=False)
    _head: int = 0
    _count: int = 0

    def add(self, frame: TrajectoryFrame) -> None:
        """Add a frame to the buffer (ring buffer behavior)"""
        if len(self._frames) < self.max_size:
            self._frames.append(frame)
        else:
            self._frames[self._head] = frame
        self._head = (self._head + 1) % self.max_size
        self._count = min(self._count + 1, self.max_size)

    def add_event(self, event: ExecutionEvent) -> None:
        """Add an event (no ring buffer - events are rare)"""
        self._events.append(event)

    def get_all_frames(self) -> List[TrajectoryFrame]:
        """Get all frames in chronological order"""
        if len(self._frames) < self.max_size:
            return self._frames[:]
        # Ring buffer is full, need to reorder
        return self._frames[self._head:] + self._frames[:self._head]

    def get_all_events(self) -> List[ExecutionEvent]:
        """Get all events"""
        return self._events[:]

    def flush(self) -> tuple:
        """Return all data and clear buffer"""
        frames = self.get_all_frames()
        events = self.get_all_events()
        self.clear()
        return frames, events

    def clear(self) -> None:
        """Clear the buffer"""
        self._frames = []
        self._events = []
        self._head = 0
        self._count = 0

    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return len(self._frames) == 0 and len(self._events) == 0

    @property
    def frame_count(self) -> int:
        """Number of frames in buffer"""
        return len(self._frames)

    @property
    def event_count(self) -> int:
        """Number of events in buffer"""
        return len(self._events)
