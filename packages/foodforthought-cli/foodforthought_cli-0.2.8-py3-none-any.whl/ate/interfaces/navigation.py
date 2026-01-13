"""
Navigation interface for autonomous robot movement.

This is a HIGHER-LEVEL interface that abstracts:
- Path planning
- Obstacle avoidance
- Localization
- Goal-directed movement

Design principle: The interface handles "navigate to X" commands
without exposing the underlying locomotion complexity.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Tuple
from enum import Enum, auto

from .types import Vector3, Quaternion, Pose, ActionResult


class NavigationState(Enum):
    """Current state of the navigation system."""
    IDLE = auto()           # Not navigating
    NAVIGATING = auto()     # Moving toward goal
    ROTATING = auto()       # Rotating in place
    AVOIDING = auto()       # Avoiding obstacle
    PAUSED = auto()         # Navigation paused
    COMPLETED = auto()      # Reached goal
    FAILED = auto()         # Failed to reach goal


@dataclass
class NavigationGoal:
    """A navigation goal."""
    position: Vector3               # Target position
    orientation: Optional[Quaternion] = None  # Target orientation (optional)
    tolerance_position: float = 0.1  # Position tolerance in meters
    tolerance_rotation: float = 0.1  # Rotation tolerance in radians
    timeout: float = 60.0           # Timeout in seconds
    frame_id: str = "world"         # Coordinate frame


@dataclass
class NavigationStatus:
    """Current status of navigation."""
    state: NavigationState
    goal: Optional[NavigationGoal] = None
    distance_to_goal: float = 0.0
    estimated_time_remaining: float = 0.0
    current_pose: Optional[Pose] = None
    path_length: float = 0.0
    obstacles_detected: int = 0
    error_message: str = ""


@dataclass
class Waypoint:
    """A waypoint in a path."""
    position: Vector3
    orientation: Optional[Quaternion] = None
    speed: float = 0.5  # Desired speed at this waypoint
    name: str = ""


class NavigationInterface(ABC):
    """
    Interface for autonomous navigation.

    Abstracts the complexity of:
    - SLAM (mapping and localization)
    - Path planning (global and local)
    - Obstacle avoidance
    - Recovery behaviors

    Use cases:
    - Navigate to a specific location
    - Follow a predefined path
    - Patrol an area
    - Return to home/charging station
    """

    @abstractmethod
    def navigate_to(self, goal: NavigationGoal) -> ActionResult:
        """
        Start navigating to a goal.

        This is NON-BLOCKING - returns immediately.
        Use get_status() or wait_for_goal() to monitor progress.

        Args:
            goal: Navigation goal

        Returns:
            ActionResult indicating if navigation started
        """
        pass

    @abstractmethod
    def get_status(self) -> NavigationStatus:
        """
        Get current navigation status.

        Returns:
            NavigationStatus with current state
        """
        pass

    @abstractmethod
    def cancel(self) -> ActionResult:
        """
        Cancel current navigation.

        Returns:
            ActionResult indicating if cancelled
        """
        pass

    @abstractmethod
    def get_pose(self) -> Pose:
        """
        Get current robot pose.

        Returns:
            Pose in the world frame
        """
        pass

    # =========================================================================
    # Convenience methods
    # =========================================================================

    def navigate_to_point(
        self,
        x: float,
        y: float,
        z: float = 0.0,
        timeout: float = 60.0
    ) -> ActionResult:
        """
        Navigate to a point (convenience wrapper).

        Args:
            x, y, z: Target coordinates
            timeout: Maximum time to reach goal

        Returns:
            ActionResult
        """
        goal = NavigationGoal(
            position=Vector3(x, y, z),
            timeout=timeout
        )
        return self.navigate_to(goal)

    def navigate_to_pose(
        self,
        x: float,
        y: float,
        yaw: float,
        timeout: float = 60.0
    ) -> ActionResult:
        """
        Navigate to a specific pose (position + heading).

        Args:
            x, y: Target position
            yaw: Target heading in radians
            timeout: Maximum time

        Returns:
            ActionResult
        """
        import math
        goal = NavigationGoal(
            position=Vector3(x, y, 0),
            orientation=Quaternion.from_euler(0, 0, yaw),
            timeout=timeout
        )
        return self.navigate_to(goal)

    def wait_for_goal(self, timeout: float = 60.0) -> NavigationStatus:
        """
        Block until navigation completes or times out.

        Args:
            timeout: Maximum wait time

        Returns:
            Final NavigationStatus
        """
        import time
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_status()
            if status.state in [NavigationState.COMPLETED, NavigationState.FAILED, NavigationState.IDLE]:
                return status
            time.sleep(0.1)
        return self.get_status()

    def rotate_to(self, yaw: float) -> ActionResult:
        """
        Rotate in place to face a direction.

        Args:
            yaw: Target heading in radians

        Returns:
            ActionResult
        """
        current = self.get_pose()
        return self.navigate_to_pose(
            current.position.x,
            current.position.y,
            yaw,
            timeout=10.0
        )

    def move_forward(self, distance: float) -> ActionResult:
        """
        Move forward by a distance.

        Args:
            distance: Distance in meters

        Returns:
            ActionResult
        """
        import math
        current = self.get_pose()
        _, _, yaw = current.orientation.to_euler()
        target_x = current.position.x + distance * math.cos(yaw)
        target_y = current.position.y + distance * math.sin(yaw)
        return self.navigate_to_point(target_x, target_y)

    def move_backward(self, distance: float) -> ActionResult:
        """
        Move backward by a distance.

        Args:
            distance: Distance in meters

        Returns:
            ActionResult
        """
        return self.move_forward(-distance)

    # =========================================================================
    # Path following
    # =========================================================================

    def follow_path(self, waypoints: List[Waypoint]) -> ActionResult:
        """
        Follow a sequence of waypoints.

        Args:
            waypoints: List of waypoints to follow

        Returns:
            ActionResult
        """
        for i, wp in enumerate(waypoints):
            goal = NavigationGoal(
                position=wp.position,
                orientation=wp.orientation
            )
            result = self.navigate_to(goal)
            if not result.success:
                return ActionResult.error(f"Failed at waypoint {i}: {result.message}")
            status = self.wait_for_goal()
            if status.state != NavigationState.COMPLETED:
                return ActionResult.error(f"Failed at waypoint {i}: {status.error_message}")
        return ActionResult.success("Path completed")

    def patrol(
        self,
        waypoints: List[Waypoint],
        loops: int = 1,
        callback: Optional[Callable[[int, Waypoint], None]] = None
    ) -> ActionResult:
        """
        Patrol a set of waypoints.

        Args:
            waypoints: List of patrol waypoints
            loops: Number of patrol loops (0 = infinite)
            callback: Called at each waypoint (loop_num, waypoint)

        Returns:
            ActionResult
        """
        loop_count = 0
        while loops == 0 or loop_count < loops:
            for wp in waypoints:
                if callback:
                    callback(loop_count, wp)
                result = self.navigate_to(NavigationGoal(position=wp.position))
                if not result.success:
                    return result
                status = self.wait_for_goal()
                if status.state != NavigationState.COMPLETED:
                    return ActionResult.error(status.error_message)
            loop_count += 1
        return ActionResult.success(f"Completed {loop_count} patrol loops")

    # =========================================================================
    # Obstacle handling
    # =========================================================================

    def is_path_clear(self) -> bool:
        """
        Check if the current path is clear of obstacles.

        Returns:
            True if path is clear
        """
        status = self.get_status()
        return status.obstacles_detected == 0

    def get_obstacle_distance(self) -> Optional[float]:
        """
        Get distance to nearest obstacle.

        Returns:
            Distance in meters, or None if no obstacles
        """
        return None  # Default implementation

    # =========================================================================
    # Home/docking
    # =========================================================================

    def go_home(self) -> ActionResult:
        """
        Navigate to the home position.

        Returns:
            ActionResult
        """
        return ActionResult.error("Home position not configured")

    def set_home(self) -> ActionResult:
        """
        Set current position as home.

        Returns:
            ActionResult
        """
        return ActionResult.error("Home position not supported")


class SimpleNavigationInterface(NavigationInterface):
    """
    Simple navigation using dead reckoning.

    For robots without full SLAM - uses odometry/IMU only.
    Good for short distances in clear environments.
    """

    def __init__(self, locomotion_interface):
        """
        Args:
            locomotion_interface: QuadrupedLocomotion or similar
        """
        self._locomotion = locomotion_interface
        self._state = NavigationState.IDLE
        self._current_goal = None
        self._pose = Pose(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

    def navigate_to(self, goal: NavigationGoal) -> ActionResult:
        """Simple point-to-point navigation."""
        self._current_goal = goal
        self._state = NavigationState.NAVIGATING
        return ActionResult.success("Navigation started")

    def get_status(self) -> NavigationStatus:
        return NavigationStatus(
            state=self._state,
            goal=self._current_goal,
            current_pose=self._pose
        )

    def cancel(self) -> ActionResult:
        self._state = NavigationState.IDLE
        self._current_goal = None
        return ActionResult.success("Cancelled")

    def get_pose(self) -> Pose:
        return self._pose
