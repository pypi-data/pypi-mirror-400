"""
Manipulation interfaces for robot arms and grippers.

Supports:
- Single arms (Franka, UR5, xArm, low-cost arms)
- Dual arms (PR2, humanoids)
- Grippers (parallel jaw, vacuum, soft grippers)

Key design principle: The interface is about WHAT you want to do,
not HOW the hardware does it. "Move end effector to position X"
works whether you have a 6-DOF arm or a 7-DOF arm.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from enum import Enum, auto

from .types import (
    Vector3,
    Quaternion,
    Pose,
    JointState,
    JointLimits,
    GripperState,
    GripperStatus,
    ForceTorqueReading,
    ActionResult,
)


class MotionType(Enum):
    """Type of motion for arm movements."""
    JOINT = auto()      # Move joints directly
    LINEAR = auto()     # Straight line in Cartesian space
    ARC = auto()        # Arc motion through via point


class ArmInterface(ABC):
    """
    Interface for a robot arm (manipulator).

    All positions are in the robot's base frame unless otherwise specified.
    All units are SI (meters, radians, Newtons).
    """

    # =========================================================================
    # End-effector control (Cartesian space)
    # =========================================================================

    @abstractmethod
    def get_end_effector_pose(self) -> Pose:
        """
        Get current end-effector pose.

        Returns:
            Pose of end-effector in base frame
        """
        pass

    @abstractmethod
    def move_to_pose(
        self,
        pose: Pose,
        speed: float = 0.1,
        motion_type: MotionType = MotionType.LINEAR
    ) -> ActionResult:
        """
        Move end-effector to target pose.

        Args:
            pose: Target pose in base frame
            speed: Speed in m/s
            motion_type: Type of motion path

        Returns:
            ActionResult (when motion complete)
        """
        pass

    @abstractmethod
    def move_to_position(
        self,
        position: Vector3,
        orientation: Optional[Quaternion] = None,
        speed: float = 0.1
    ) -> ActionResult:
        """
        Move end-effector to position, optionally with orientation.

        Args:
            position: Target position in base frame
            orientation: Target orientation (None = keep current)
            speed: Speed in m/s

        Returns:
            ActionResult
        """
        pass

    def move_relative(
        self,
        delta: Vector3,
        speed: float = 0.1
    ) -> ActionResult:
        """
        Move end-effector relative to current position.

        Args:
            delta: Relative movement in base frame
            speed: Speed in m/s

        Returns:
            ActionResult
        """
        current = self.get_end_effector_pose()
        target = Vector3(
            current.position.x + delta.x,
            current.position.y + delta.y,
            current.position.z + delta.z
        )
        return self.move_to_position(target, current.orientation, speed)

    # =========================================================================
    # Joint control
    # =========================================================================

    @abstractmethod
    def get_joint_state(self) -> JointState:
        """
        Get current joint state.

        Returns:
            JointState with positions, velocities, efforts
        """
        pass

    @abstractmethod
    def move_to_joints(
        self,
        positions: List[float],
        speed: float = 0.5
    ) -> ActionResult:
        """
        Move to target joint positions.

        Args:
            positions: Target joint angles in radians
            speed: Joint speed in rad/s

        Returns:
            ActionResult
        """
        pass

    @abstractmethod
    def get_joint_limits(self) -> List[JointLimits]:
        """
        Get limits for all joints.

        Returns:
            List of JointLimits for each joint
        """
        pass

    def get_num_joints(self) -> int:
        """Get number of joints in the arm."""
        return len(self.get_joint_state().positions)

    def get_joint_names(self) -> List[str]:
        """
        Get joint names.

        Default: joint_0, joint_1, ...
        Override for meaningful names.
        """
        return [f"joint_{i}" for i in range(self.get_num_joints())]

    # =========================================================================
    # Common poses
    # =========================================================================

    @abstractmethod
    def go_home(self) -> ActionResult:
        """
        Move to home/ready position.

        Returns:
            ActionResult
        """
        pass

    def go_to_named_pose(self, name: str) -> ActionResult:
        """
        Move to a named pose (e.g., "home", "ready", "stow").

        Override to support robot-specific poses.
        """
        if name == "home":
            return self.go_home()
        return ActionResult.error(f"Unknown pose: {name}")

    # =========================================================================
    # Motion control
    # =========================================================================

    @abstractmethod
    def stop(self) -> ActionResult:
        """Stop current motion immediately."""
        pass

    @abstractmethod
    def is_moving(self) -> bool:
        """Check if arm is currently moving."""
        pass

    def set_speed_factor(self, factor: float) -> ActionResult:
        """
        Set global speed factor (0.0 to 1.0).

        Affects all subsequent motions.
        """
        return ActionResult.error("Speed factor not supported")

    # =========================================================================
    # Force/compliance control (optional)
    # =========================================================================

    def enable_compliance(self, stiffness: Vector3) -> ActionResult:
        """
        Enable compliant/impedance control.

        Args:
            stiffness: Stiffness in N/m for x, y, z

        Returns:
            ActionResult
        """
        return ActionResult.error("Compliance control not supported")

    def disable_compliance(self) -> ActionResult:
        """Disable compliant control, return to position control."""
        return ActionResult.error("Compliance control not supported")

    def get_force_torque(self) -> Optional[ForceTorqueReading]:
        """
        Get force/torque at end effector.

        Returns:
            ForceTorqueReading or None if no sensor
        """
        return None


class GripperInterface(ABC):
    """
    Interface for grippers/end-effectors.

    Supports various gripper types:
    - Parallel jaw (most common)
    - Vacuum/suction
    - Soft grippers
    - Multi-finger hands
    """

    @abstractmethod
    def grasp(self, force: float = 10.0) -> ActionResult:
        """
        Close gripper to grasp an object.

        Args:
            force: Gripping force in Newtons

        Returns:
            ActionResult (success if object detected)
        """
        pass

    @abstractmethod
    def release(self) -> ActionResult:
        """
        Open gripper to release object.

        Returns:
            ActionResult
        """
        pass

    @abstractmethod
    def get_state(self) -> GripperState:
        """
        Get current gripper state.

        Returns:
            GripperState (OPEN, CLOSED, HOLDING, etc.)
        """
        pass

    @abstractmethod
    def get_status(self) -> GripperStatus:
        """
        Get detailed gripper status.

        Returns:
            GripperStatus with position, force, object detection
        """
        pass

    def set_position(self, position: float) -> ActionResult:
        """
        Set gripper to specific position.

        Args:
            position: 0.0 = fully closed, 1.0 = fully open

        Returns:
            ActionResult
        """
        if position < 0.5:
            return self.grasp()
        else:
            return self.release()

    def is_holding_object(self) -> bool:
        """Check if gripper is holding an object."""
        return self.get_state() == GripperState.HOLDING

    # =========================================================================
    # Gripper-specific capabilities
    # =========================================================================

    def set_speed(self, speed: float) -> ActionResult:
        """
        Set gripper open/close speed.

        Args:
            speed: Speed factor (0.0 to 1.0)
        """
        return ActionResult.error("Speed control not supported")

    def calibrate(self) -> ActionResult:
        """Calibrate gripper (find limits)."""
        return ActionResult.error("Calibration not supported")


class DualArmInterface(ABC):
    """
    Interface for dual-arm robots.

    Adds coordination primitives beyond two separate arms.
    """

    @abstractmethod
    def get_left_arm(self) -> ArmInterface:
        """Get interface to left arm."""
        pass

    @abstractmethod
    def get_right_arm(self) -> ArmInterface:
        """Get interface to right arm."""
        pass

    @abstractmethod
    def move_both_to_poses(
        self,
        left_pose: Pose,
        right_pose: Pose,
        speed: float = 0.1
    ) -> ActionResult:
        """
        Move both arms simultaneously to target poses.

        Args:
            left_pose: Target for left arm
            right_pose: Target for right arm
            speed: Speed in m/s

        Returns:
            ActionResult
        """
        pass

    def bimanual_grasp(
        self,
        left_pose: Pose,
        right_pose: Pose,
        force: float = 10.0
    ) -> ActionResult:
        """
        Coordinated grasp with both arms.

        Moves arms to approach poses, then closes both grippers
        with coordinated force control.
        """
        # Default implementation - override for better coordination
        result = self.move_both_to_poses(left_pose, right_pose)
        if not result.success:
            return result

        # Close grippers
        left_gripper = getattr(self.get_left_arm(), 'gripper', None)
        right_gripper = getattr(self.get_right_arm(), 'gripper', None)

        if left_gripper:
            left_gripper.grasp(force)
        if right_gripper:
            right_gripper.grasp(force)

        return ActionResult.ok("Bimanual grasp complete")
