"""
Common data types for robot interfaces.

All units are SI:
- Distance: meters (m)
- Angle: radians (rad)
- Time: seconds (s)
- Force: Newtons (N)
- Torque: Newton-meters (Nm)
- Velocity: m/s or rad/s
- Acceleration: m/s² or rad/s²

These types are designed to be:
1. Serializable (for telemetry recording)
2. Immutable (for safety)
3. Hardware-agnostic (no servo IDs, raw values, etc.)
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple
import math


# =============================================================================
# Spatial Types
# =============================================================================

@dataclass(frozen=True)
class Vector3:
    """3D vector in meters (for position) or m/s (for velocity)."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: "Vector3") -> "Vector3":
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3") -> "Vector3":
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3":
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalized(self) -> "Vector3":
        mag = self.magnitude()
        if mag == 0:
            return Vector3(0, 0, 0)
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @classmethod
    def from_tuple(cls, t: Tuple[float, float, float]) -> "Vector3":
        return cls(t[0], t[1], t[2])

    @classmethod
    def zero(cls) -> "Vector3":
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def forward(cls) -> "Vector3":
        """Unit vector in forward direction (+X in robot frame)."""
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def up(cls) -> "Vector3":
        """Unit vector in up direction (+Z in robot frame)."""
        return cls(0.0, 0.0, 1.0)


@dataclass(frozen=True)
class Quaternion:
    """Rotation as quaternion (w, x, y, z). Normalized."""
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_euler(self) -> Tuple[float, float, float]:
        """Convert to Euler angles (roll, pitch, yaw) in radians."""
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (self.w * self.x + self.y * self.z)
        cosr_cosp = 1 - 2 * (self.x * self.x + self.y * self.y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2 * (self.w * self.y - self.z * self.x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)

        # Yaw (z-axis rotation)
        siny_cosp = 2 * (self.w * self.z + self.x * self.y)
        cosy_cosp = 1 - 2 * (self.y * self.y + self.z * self.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return (roll, pitch, yaw)

    @classmethod
    def from_euler(cls, roll: float, pitch: float, yaw: float) -> "Quaternion":
        """Create from Euler angles (roll, pitch, yaw) in radians."""
        cr, cp, cy = math.cos(roll/2), math.cos(pitch/2), math.cos(yaw/2)
        sr, sp, sy = math.sin(roll/2), math.sin(pitch/2), math.sin(yaw/2)

        return cls(
            w=cr * cp * cy + sr * sp * sy,
            x=sr * cp * cy - cr * sp * sy,
            y=cr * sp * cy + sr * cp * sy,
            z=cr * cp * sy - sr * sp * cy,
        )

    @classmethod
    def identity(cls) -> "Quaternion":
        return cls(1.0, 0.0, 0.0, 0.0)


@dataclass(frozen=True)
class Pose:
    """6DOF pose: position + orientation."""
    position: Vector3 = field(default_factory=Vector3.zero)
    orientation: Quaternion = field(default_factory=Quaternion.identity)

    @classmethod
    def identity(cls) -> "Pose":
        return cls(Vector3.zero(), Quaternion.identity())


@dataclass(frozen=True)
class Twist:
    """Velocity in 6DOF: linear + angular velocity."""
    linear: Vector3 = field(default_factory=Vector3.zero)   # m/s
    angular: Vector3 = field(default_factory=Vector3.zero)  # rad/s

    @classmethod
    def zero(cls) -> "Twist":
        return cls(Vector3.zero(), Vector3.zero())


# =============================================================================
# Joint/Motor Types
# =============================================================================

@dataclass(frozen=True)
class JointState:
    """State of all joints. Lists are ordered by joint index."""
    positions: Tuple[float, ...] = ()   # radians
    velocities: Tuple[float, ...] = ()  # rad/s
    efforts: Tuple[float, ...] = ()     # Nm (torque)

    @property
    def num_joints(self) -> int:
        return len(self.positions)


@dataclass(frozen=True)
class JointLimits:
    """Limits for a single joint."""
    position_min: float  # radians
    position_max: float  # radians
    velocity_max: float  # rad/s
    effort_max: float    # Nm


# =============================================================================
# Perception Types
# =============================================================================

@dataclass
class Image:
    """RGB image from camera."""
    data: bytes
    width: int
    height: int
    encoding: str = "rgb8"  # rgb8, bgr8, mono8, jpeg, png
    timestamp: float = 0.0  # seconds since epoch
    frame_id: str = "camera"  # coordinate frame

    def to_numpy(self):
        """Convert to numpy array. Requires numpy."""
        import numpy as np
        if self.encoding in ("rgb8", "bgr8"):
            return np.frombuffer(self.data, dtype=np.uint8).reshape(
                (self.height, self.width, 3)
            )
        elif self.encoding == "mono8":
            return np.frombuffer(self.data, dtype=np.uint8).reshape(
                (self.height, self.width)
            )
        else:
            raise ValueError(f"Cannot convert encoding {self.encoding} to numpy")


@dataclass
class DepthImage:
    """Depth image from depth camera."""
    data: bytes
    width: int
    height: int
    encoding: str = "32FC1"  # 32FC1 (float meters), 16UC1 (uint16 mm)
    timestamp: float = 0.0
    frame_id: str = "depth_camera"
    min_range: float = 0.1   # meters
    max_range: float = 10.0  # meters


@dataclass
class PointCloud:
    """3D point cloud from lidar or depth camera."""
    points: List[Vector3]  # List of 3D points in sensor frame
    intensities: Optional[List[float]] = None
    colors: Optional[List[Tuple[int, int, int]]] = None  # RGB
    timestamp: float = 0.0
    frame_id: str = "lidar"


@dataclass(frozen=True)
class IMUReading:
    """Reading from Inertial Measurement Unit."""
    orientation: Quaternion
    angular_velocity: Vector3   # rad/s
    linear_acceleration: Vector3  # m/s²
    timestamp: float = 0.0

    # Covariance matrices (optional, for Kalman filtering)
    orientation_covariance: Optional[Tuple[float, ...]] = None
    angular_velocity_covariance: Optional[Tuple[float, ...]] = None
    linear_acceleration_covariance: Optional[Tuple[float, ...]] = None


@dataclass(frozen=True)
class ForceTorqueReading:
    """Reading from force-torque sensor."""
    force: Vector3   # Newtons
    torque: Vector3  # Nm
    timestamp: float = 0.0
    frame_id: str = "ft_sensor"


# =============================================================================
# Robot State Types
# =============================================================================

@dataclass(frozen=True)
class BatteryState:
    """Battery status."""
    percentage: float  # 0.0 to 1.0
    voltage: float     # Volts
    current: float = 0.0  # Amps (positive = discharging)
    is_charging: bool = False
    time_remaining: Optional[float] = None  # seconds


class RobotMode(Enum):
    """Operating mode of the robot."""
    IDLE = auto()
    READY = auto()
    MOVING = auto()
    ESTOPPED = auto()
    FAULT = auto()
    CHARGING = auto()
    CALIBRATING = auto()


@dataclass
class RobotStatus:
    """Overall robot status."""
    mode: RobotMode = RobotMode.IDLE
    is_ready: bool = False
    is_moving: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    battery: Optional[BatteryState] = None
    uptime: float = 0.0  # seconds since boot


# =============================================================================
# Locomotion Types
# =============================================================================

class GaitType(Enum):
    """Gait patterns for legged robots."""
    # Quadruped gaits
    STAND = auto()
    WALK = auto()
    TROT = auto()
    PACE = auto()
    BOUND = auto()
    GALLOP = auto()
    CRAWL = auto()

    # Biped gaits
    BIPED_WALK = auto()
    BIPED_RUN = auto()

    # Special
    CUSTOM = auto()


@dataclass(frozen=True)
class GaitParameters:
    """Parameters for gait control."""
    gait_type: GaitType = GaitType.WALK
    stride_length: float = 0.1    # meters
    step_height: float = 0.05     # meters
    cycle_time: float = 0.5       # seconds per gait cycle
    duty_factor: float = 0.6      # fraction of cycle foot is on ground


# =============================================================================
# Manipulation Types
# =============================================================================

class GripperState(Enum):
    """State of a gripper."""
    OPEN = auto()
    CLOSED = auto()
    HOLDING = auto()  # Closed and holding an object
    MOVING = auto()
    FAULT = auto()


@dataclass(frozen=True)
class GripperStatus:
    """Detailed gripper status."""
    state: GripperState
    position: float = 1.0     # 0.0 = closed, 1.0 = fully open
    force: float = 0.0        # Newtons (gripping force)
    object_detected: bool = False


# =============================================================================
# Coordinate Frames
# =============================================================================

class Frame(Enum):
    """Standard coordinate frames."""
    WORLD = "world"           # Global/map frame
    ODOM = "odom"             # Odometry frame
    BASE = "base_link"        # Robot base
    BODY = "body"             # Robot body center
    CAMERA = "camera"         # Camera optical frame
    GRIPPER = "gripper"       # End effector frame
    IMU = "imu"               # IMU sensor frame
    LIDAR = "lidar"           # Lidar sensor frame


# =============================================================================
# Action Types (for skill definitions)
# =============================================================================

@dataclass
class ActionResult:
    """Result of an action/command."""
    success: bool
    message: str = ""
    error_code: Optional[int] = None
    duration: float = 0.0  # How long the action took

    @classmethod
    def ok(cls, message: str = "Success", duration: float = 0.0) -> "ActionResult":
        return cls(success=True, message=message, duration=duration)

    @classmethod
    def error(cls, message: str, code: int = -1) -> "ActionResult":
        return cls(success=False, message=message, error_code=code)
