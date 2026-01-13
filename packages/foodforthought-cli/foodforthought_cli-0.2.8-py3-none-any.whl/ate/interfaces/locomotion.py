"""
Locomotion interfaces for mobile robots.

Supports:
- Quadrupeds (MechDog, Spot, Unitree, ANYmal)
- Bipeds (Humanoids, Digit, Atlas)
- Wheeled robots (TurtleBot, AMRs)
- Aerial (Drones)

Each interface defines normalized actions that are hardware-agnostic.
A "walk forward 0.5m" command works the same on MechDog and Spot.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Callable
from enum import Enum, auto

from .types import (
    Vector3,
    Quaternion,
    Pose,
    Twist,
    GaitType,
    GaitParameters,
    JointState,
    ActionResult,
)


class LocomotionInterface(ABC):
    """
    Base interface for all locomotion.

    All mobile robots share these concepts:
    - Current pose in some frame
    - Velocity control
    - Stop
    """

    @abstractmethod
    def get_pose(self) -> Pose:
        """
        Get current pose (position + orientation) in odometry frame.

        Returns:
            Pose in odom frame
        """
        pass

    @abstractmethod
    def get_velocity(self) -> Twist:
        """
        Get current velocity (linear + angular).

        Returns:
            Twist with linear (m/s) and angular (rad/s) velocity
        """
        pass

    @abstractmethod
    def stop(self) -> ActionResult:
        """
        Immediately stop all locomotion.

        Returns:
            ActionResult
        """
        pass

    @abstractmethod
    def is_moving(self) -> bool:
        """
        Check if robot is currently moving.

        Returns:
            True if any locomotion is active
        """
        pass


class QuadrupedLocomotion(LocomotionInterface):
    """
    Interface for quadruped (4-legged) robots.

    Implemented by: MechDog, Spot, Unitree Go1/Go2, ANYmal, etc.

    Coordinate frame conventions:
    - X: Forward (positive = front of robot)
    - Y: Left (positive = left side of robot)
    - Z: Up (positive = above robot)

    All distances in meters, angles in radians.
    """

    # =========================================================================
    # High-level movement commands
    # =========================================================================

    @abstractmethod
    def walk(self, direction: Vector3, speed: float = 0.5) -> ActionResult:
        """
        Walk in a direction at given speed.

        This is a continuous command - robot keeps walking until stop() is called.

        Args:
            direction: Unit vector for direction (in robot frame)
                       Vector3(1, 0, 0) = forward
                       Vector3(0, 1, 0) = left
                       Vector3(-1, 0, 0) = backward
            speed: Speed in m/s (clamped to robot's max)

        Returns:
            ActionResult
        """
        pass

    @abstractmethod
    def walk_to(self, target: Vector3, speed: float = 0.5) -> ActionResult:
        """
        Walk to a target position (blocking).

        Args:
            target: Target position in odometry frame
            speed: Speed in m/s

        Returns:
            ActionResult (when target reached or failed)
        """
        pass

    @abstractmethod
    def turn(self, angle: float, speed: float = 0.5) -> ActionResult:
        """
        Turn in place by given angle (blocking).

        Args:
            angle: Angle in radians (positive = counterclockwise)
            speed: Angular speed in rad/s

        Returns:
            ActionResult (when turn complete)
        """
        pass

    @abstractmethod
    def turn_continuous(self, angular_velocity: float) -> ActionResult:
        """
        Turn continuously at given angular velocity.

        Args:
            angular_velocity: rad/s (positive = counterclockwise)

        Returns:
            ActionResult
        """
        pass

    # =========================================================================
    # Posture commands
    # =========================================================================

    @abstractmethod
    def stand(self) -> ActionResult:
        """
        Stand up from any position.

        Returns:
            ActionResult (when standing complete)
        """
        pass

    @abstractmethod
    def sit(self) -> ActionResult:
        """
        Sit down (lower body to ground).

        Returns:
            ActionResult (when sit complete)
        """
        pass

    @abstractmethod
    def lie_down(self) -> ActionResult:
        """
        Lie down completely (motors may turn off).

        Returns:
            ActionResult
        """
        pass

    # =========================================================================
    # Gait control
    # =========================================================================

    @abstractmethod
    def set_gait(self, gait: GaitType) -> ActionResult:
        """
        Set the gait pattern.

        Args:
            gait: GaitType (WALK, TROT, BOUND, etc.)

        Returns:
            ActionResult
        """
        pass

    @abstractmethod
    def get_gait(self) -> GaitType:
        """
        Get current gait pattern.

        Returns:
            Current GaitType
        """
        pass

    def set_gait_parameters(self, params: GaitParameters) -> ActionResult:
        """
        Set detailed gait parameters.

        Default implementation just sets gait type.
        Override for robots with fine-grained gait control.

        Args:
            params: GaitParameters with stride, step height, etc.

        Returns:
            ActionResult
        """
        return self.set_gait(params.gait_type)

    # =========================================================================
    # Leg control (for advanced use)
    # =========================================================================

    @abstractmethod
    def get_foot_positions(self) -> List[Vector3]:
        """
        Get current foot positions relative to body.

        Returns:
            List of 4 Vector3 positions [front_left, front_right, back_left, back_right]
        """
        pass

    def set_foot_position(self, leg_index: int, position: Vector3) -> ActionResult:
        """
        Set a single foot position using inverse kinematics.

        Args:
            leg_index: 0=front_left, 1=front_right, 2=back_left, 3=back_right
            position: Target position relative to body

        Returns:
            ActionResult
        """
        # Default: not implemented
        return ActionResult.error("set_foot_position not implemented for this robot")

    # =========================================================================
    # Joint-level access (for telemetry/recording)
    # =========================================================================

    @abstractmethod
    def get_joint_state(self) -> JointState:
        """
        Get current state of all leg joints.

        Returns:
            JointState with positions, velocities, efforts
        """
        pass

    def get_joint_names(self) -> List[str]:
        """
        Get names of all leg joints in order.

        Default naming convention:
        [FL_hip, FL_thigh, FL_calf, FR_hip, FR_thigh, FR_calf,
         BL_hip, BL_thigh, BL_calf, BR_hip, BR_thigh, BR_calf]

        Returns:
            List of joint names
        """
        return [
            "FL_hip", "FL_thigh", "FL_calf",
            "FR_hip", "FR_thigh", "FR_calf",
            "BL_hip", "BL_thigh", "BL_calf",
            "BR_hip", "BR_thigh", "BR_calf",
        ]


class BipedLocomotion(LocomotionInterface):
    """
    Interface for biped (2-legged) robots.

    Implemented by: Humanoids, Digit, Cassie, etc.
    """

    @abstractmethod
    def walk(self, direction: Vector3, speed: float = 0.5) -> ActionResult:
        """Walk in direction."""
        pass

    @abstractmethod
    def walk_to(self, target: Vector3, speed: float = 0.5) -> ActionResult:
        """Walk to target position."""
        pass

    @abstractmethod
    def turn(self, angle: float, speed: float = 0.5) -> ActionResult:
        """Turn by angle."""
        pass

    @abstractmethod
    def stand(self) -> ActionResult:
        """Stand up."""
        pass

    @abstractmethod
    def crouch(self) -> ActionResult:
        """Lower body while standing."""
        pass

    @abstractmethod
    def get_joint_state(self) -> JointState:
        """Get leg joint states."""
        pass

    # Biped-specific
    @abstractmethod
    def step_over(self, obstacle_height: float) -> ActionResult:
        """Step over an obstacle of given height."""
        pass

    @abstractmethod
    def climb_stairs(self, step_height: float, num_steps: int) -> ActionResult:
        """Climb stairs."""
        pass


class WheeledLocomotion(LocomotionInterface):
    """
    Interface for wheeled robots.

    Implemented by: TurtleBot, AMRs, differential drive, Ackermann, etc.
    """

    @abstractmethod
    def drive(self, linear: float, angular: float) -> ActionResult:
        """
        Drive with given linear and angular velocity.

        Args:
            linear: Forward velocity in m/s
            angular: Angular velocity in rad/s

        Returns:
            ActionResult
        """
        pass

    @abstractmethod
    def drive_to(self, target: Vector3, speed: float = 0.5) -> ActionResult:
        """Drive to target position."""
        pass

    @abstractmethod
    def turn(self, angle: float, speed: float = 0.5) -> ActionResult:
        """Turn by angle."""
        pass

    @abstractmethod
    def get_wheel_velocities(self) -> List[float]:
        """Get current wheel velocities in rad/s."""
        pass


class AerialLocomotion(LocomotionInterface):
    """
    Interface for aerial robots (drones).

    Implemented by: Quadcopters, fixed-wing, etc.
    """

    @abstractmethod
    def takeoff(self, altitude: float = 1.0) -> ActionResult:
        """Take off to given altitude."""
        pass

    @abstractmethod
    def land(self) -> ActionResult:
        """Land at current position."""
        pass

    @abstractmethod
    def hover(self) -> ActionResult:
        """Hover in place."""
        pass

    @abstractmethod
    def fly_to(self, target: Vector3, speed: float = 1.0) -> ActionResult:
        """Fly to target position."""
        pass

    @abstractmethod
    def set_velocity(self, velocity: Vector3) -> ActionResult:
        """Set 3D velocity."""
        pass

    @abstractmethod
    def get_altitude(self) -> float:
        """Get current altitude in meters."""
        pass

    @abstractmethod
    def is_flying(self) -> bool:
        """Check if currently airborne."""
        pass
