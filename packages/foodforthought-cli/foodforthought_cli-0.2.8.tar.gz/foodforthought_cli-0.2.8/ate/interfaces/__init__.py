"""
FoodforThought Robot Interfaces

Abstract interfaces that define capabilities for any robot.
Implementations are hardware-specific, but skills are written against these interfaces.

Architecture:
    RobotInterface (base)
    ├── Capabilities (mixins)
    │   ├── Locomotion
    │   │   ├── QuadrupedLocomotion
    │   │   ├── BipedLocomotion
    │   │   ├── WheeledLocomotion
    │   │   └── AerialLocomotion
    │   ├── Manipulation
    │   │   ├── ArmInterface
    │   │   └── GripperInterface
    │   ├── Perception
    │   │   ├── CameraInterface
    │   │   ├── DepthCameraInterface
    │   │   ├── LidarInterface
    │   │   └── IMUInterface
    │   └── Body
    │       └── BodyPoseInterface
    └── Safety
        └── SafetyInterface

Example:
    # MechDog implements:
    class MechDogDriver(QuadrupedLocomotion, BodyPoseInterface, SafetyInterface):
        ...

    # Spot with arm implements:
    class SpotDriver(QuadrupedLocomotion, BodyPoseInterface, ArmInterface,
                     GripperInterface, CameraInterface, LidarInterface, SafetyInterface):
        ...

    # Skills are written against interfaces:
    def pick_and_place(robot: QuadrupedLocomotion & GripperInterface, target: Vector3):
        robot.walk_to(target)
        robot.lower_body(height=0.1)
        robot.grasp()
        ...
"""

from .types import (
    Vector3,
    Quaternion,
    Pose,
    Twist,
    JointState,
    JointLimits,
    Image,
    DepthImage,
    PointCloud,
    IMUReading,
    ForceTorqueReading,
    BatteryState,
    RobotStatus,
    GaitType,
    GripperState,
    GripperStatus,
    ActionResult,
)

from .base import (
    RobotInterface,
    SafetyInterface,
    Capability,
    RobotInfo,
)

from .locomotion import (
    LocomotionInterface,
    QuadrupedLocomotion,
    BipedLocomotion,
    WheeledLocomotion,
    AerialLocomotion,
)

from .manipulation import (
    ArmInterface,
    GripperInterface,
    DualArmInterface,
)

from .perception import (
    CameraInterface,
    DepthCameraInterface,
    LidarInterface,
    IMUInterface,
    ForceTorqueInterface,
)

from .body import (
    BodyPoseInterface,
)

from .detection import (
    BoundingBox,
    Detection,
    DetectionResult,
    ObjectDetectionInterface,
    TrashDetectionInterface,
)

from .navigation import (
    NavigationState,
    NavigationGoal,
    NavigationStatus,
    Waypoint,
    NavigationInterface,
    SimpleNavigationInterface,
)

__all__ = [
    # Types
    "Vector3",
    "Quaternion",
    "Pose",
    "Twist",
    "JointState",
    "JointLimits",
    "Image",
    "DepthImage",
    "PointCloud",
    "IMUReading",
    "ForceTorqueReading",
    "BatteryState",
    "RobotStatus",
    "GaitType",
    "GripperState",
    "GripperStatus",
    "ActionResult",
    # Base
    "RobotInterface",
    "SafetyInterface",
    "Capability",
    "RobotInfo",
    # Locomotion
    "LocomotionInterface",
    "QuadrupedLocomotion",
    "BipedLocomotion",
    "WheeledLocomotion",
    "AerialLocomotion",
    # Manipulation
    "ArmInterface",
    "GripperInterface",
    "DualArmInterface",
    # Perception
    "CameraInterface",
    "DepthCameraInterface",
    "LidarInterface",
    "IMUInterface",
    "ForceTorqueInterface",
    # Body
    "BodyPoseInterface",
    # Detection (higher-level)
    "BoundingBox",
    "Detection",
    "DetectionResult",
    "ObjectDetectionInterface",
    "TrashDetectionInterface",
    # Navigation (higher-level)
    "NavigationState",
    "NavigationGoal",
    "NavigationStatus",
    "Waypoint",
    "NavigationInterface",
    "SimpleNavigationInterface",
]
