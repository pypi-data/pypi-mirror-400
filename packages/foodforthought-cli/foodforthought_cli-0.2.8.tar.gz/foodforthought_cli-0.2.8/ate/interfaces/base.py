"""
Base interfaces that all robots must implement.

Every robot, regardless of type, has:
1. Identity - what it is, what it can do
2. Safety - emergency stop, status monitoring
3. Lifecycle - connect, disconnect, ready state
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Set, Type, TYPE_CHECKING
from enum import Enum, auto

from .types import RobotStatus, BatteryState, ActionResult

if TYPE_CHECKING:
    from .locomotion import LocomotionInterface
    from .manipulation import ArmInterface, GripperInterface
    from .perception import CameraInterface, LidarInterface, IMUInterface


class Capability(Enum):
    """
    Capabilities a robot can have.
    Used for runtime capability checking and skill compatibility.
    """
    # Locomotion
    QUADRUPED = auto()
    BIPED = auto()
    WHEELED = auto()
    AERIAL = auto()
    AQUATIC = auto()

    # Manipulation
    ARM = auto()
    DUAL_ARM = auto()
    GRIPPER = auto()
    SUCTION = auto()

    # Perception
    CAMERA = auto()
    DEPTH_CAMERA = auto()
    LIDAR = auto()
    IMU = auto()
    FORCE_TORQUE = auto()
    TACTILE = auto()

    # Body control
    BODY_POSE = auto()

    # Communication
    AUDIO_INPUT = auto()
    AUDIO_OUTPUT = auto()


@dataclass
class RobotInfo:
    """
    Static information about a robot.
    Used for compatibility checking and UI display.
    """
    # Identity
    name: str                           # Human-readable name
    model: str                          # Model identifier (e.g., "hiwonder_mechdog")
    manufacturer: str                   # Manufacturer name
    archetype: str                      # Primary type: "quadruped", "humanoid", "arm", etc.

    # Capabilities
    capabilities: Set[Capability] = field(default_factory=set)

    # Physical properties
    mass: Optional[float] = None        # kg
    payload_capacity: Optional[float] = None  # kg
    reach: Optional[float] = None       # meters (for arms)
    dimensions: Optional[tuple] = None  # (length, width, height) in meters

    # Workspace limits (in base frame)
    workspace_min: Optional[tuple] = None  # (x, y, z) min bounds
    workspace_max: Optional[tuple] = None  # (x, y, z) max bounds

    # Performance
    max_speed: Optional[float] = None   # m/s
    battery_capacity: Optional[float] = None  # Wh

    # Metadata
    firmware_version: Optional[str] = None
    serial_number: Optional[str] = None
    description: str = ""

    def has_capability(self, cap: Capability) -> bool:
        return cap in self.capabilities

    def has_all_capabilities(self, caps: Set[Capability]) -> bool:
        return caps.issubset(self.capabilities)


class RobotInterface(ABC):
    """
    Base interface that ALL robots must implement.

    This provides:
    - Identity and capability information
    - Connection lifecycle
    - Status monitoring

    Specific capabilities (locomotion, manipulation, etc.) are added via mixins.
    """

    @abstractmethod
    def get_info(self) -> RobotInfo:
        """
        Get static information about this robot.

        Returns:
            RobotInfo with name, model, capabilities, etc.
        """
        pass

    @abstractmethod
    def connect(self) -> ActionResult:
        """
        Establish connection to the robot hardware.

        Returns:
            ActionResult indicating success/failure
        """
        pass

    @abstractmethod
    def disconnect(self) -> ActionResult:
        """
        Safely disconnect from the robot hardware.

        Returns:
            ActionResult indicating success/failure
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if currently connected to the robot.

        Returns:
            True if connected and communication is working
        """
        pass

    @abstractmethod
    def get_status(self) -> RobotStatus:
        """
        Get current robot status.

        Returns:
            RobotStatus with mode, errors, battery, etc.
        """
        pass

    def has_capability(self, cap: Capability) -> bool:
        """Check if robot has a specific capability."""
        return self.get_info().has_capability(cap)

    def get_capabilities(self) -> Set[Capability]:
        """Get all capabilities of this robot."""
        return self.get_info().capabilities


class SafetyInterface(ABC):
    """
    Safety interface that all robots should implement.

    Provides emergency stop and safety monitoring.
    """

    @abstractmethod
    def emergency_stop(self) -> ActionResult:
        """
        Immediately stop all motion and enter safe state.

        This should:
        - Stop all actuators immediately
        - Disable motor power if possible
        - Set robot to ESTOPPED mode

        Returns:
            ActionResult (should rarely fail)
        """
        pass

    @abstractmethod
    def reset_emergency_stop(self) -> ActionResult:
        """
        Clear emergency stop state and return to ready.

        Returns:
            ActionResult indicating if reset was successful
        """
        pass

    @abstractmethod
    def is_estopped(self) -> bool:
        """
        Check if emergency stop is active.

        Returns:
            True if robot is in emergency stop state
        """
        pass

    @abstractmethod
    def get_battery_state(self) -> Optional[BatteryState]:
        """
        Get current battery status.

        Returns:
            BatteryState or None if no battery
        """
        pass

    def check_safety(self) -> List[str]:
        """
        Run safety checks and return list of issues.

        Returns:
            List of safety warning/error messages (empty if all OK)
        """
        issues = []

        battery = self.get_battery_state()
        if battery:
            if battery.percentage < 0.1:
                issues.append(f"Critical battery: {battery.percentage*100:.0f}%")
            elif battery.percentage < 0.2:
                issues.append(f"Low battery: {battery.percentage*100:.0f}%")

        if self.is_estopped():
            issues.append("Emergency stop is active")

        return issues


# =============================================================================
# Utility functions for capability checking
# =============================================================================

def requires_capabilities(*caps: Capability):
    """
    Decorator to mark that a skill requires certain capabilities.

    Usage:
        @requires_capabilities(Capability.QUADRUPED, Capability.GRIPPER)
        def pick_up_object(robot, target):
            ...
    """
    def decorator(func):
        func._required_capabilities = set(caps)
        return func
    return decorator


def check_robot_compatibility(robot: RobotInterface, required: Set[Capability]) -> List[str]:
    """
    Check if a robot is compatible with required capabilities.

    Returns:
        List of missing capabilities (empty if compatible)
    """
    robot_caps = robot.get_capabilities()
    missing = required - robot_caps
    return [cap.name for cap in missing]
