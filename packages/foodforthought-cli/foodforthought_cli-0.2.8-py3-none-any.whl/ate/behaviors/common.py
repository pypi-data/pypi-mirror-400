"""
Common behavior tree nodes for robotics.

These are reusable building blocks that wrap interface calls
into behavior tree-compatible actions and conditions.

The key insight: Each of these represents a SKILL that can be:
1. Recorded as a demonstration
2. Labeled by the community
3. Trained into a model
4. Deployed across robots
"""

from typing import Optional, List, Any
from .tree import (
    BehaviorNode,
    BehaviorStatus,
    Sequence,
    Selector,
    Repeater,
    RepeatUntilFail,
    Action,
    Condition,
)
from ..interfaces import (
    NavigationInterface,
    ObjectDetectionInterface,
    GripperInterface,
    Vector3,
    NavigationGoal,
    NavigationState,
)


# =============================================================================
# Navigation Actions
# =============================================================================

class NavigateToPoint(BehaviorNode):
    """
    Navigate to a specific point.

    Blackboard:
    - Writes: "navigation_status"
    """

    def __init__(
        self,
        nav: NavigationInterface,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        name: str = ""
    ):
        super().__init__(name or f"NavigateTo({x:.1f}, {y:.1f})")
        self.nav = nav
        self.target = Vector3(x, y, z)
        self.started = False

    def tick(self) -> BehaviorStatus:
        if not self.started:
            result = self.nav.navigate_to_point(
                self.target.x, self.target.y, self.target.z
            )
            if not result.success:
                return BehaviorStatus.FAILURE
            self.started = True

        status = self.nav.get_status()
        if self.blackboard:
            self.blackboard.set("navigation_status", status)

        if status.state == NavigationState.COMPLETED:
            return BehaviorStatus.SUCCESS
        elif status.state == NavigationState.FAILED:
            return BehaviorStatus.FAILURE
        else:
            return BehaviorStatus.RUNNING

    def reset(self) -> None:
        super().reset()
        self.started = False


class NavigateToPose(BehaviorNode):
    """
    Navigate to a specific pose (position + heading).

    Blackboard:
    - Writes: "navigation_status"
    """

    def __init__(
        self,
        nav: NavigationInterface,
        x: float = 0,
        y: float = 0,
        yaw: float = 0,
        name: str = ""
    ):
        super().__init__(name or f"NavigateToPose({x:.1f}, {y:.1f}, {yaw:.1f})")
        self.nav = nav
        self.x = x
        self.y = y
        self.yaw = yaw
        self.started = False

    def tick(self) -> BehaviorStatus:
        if not self.started:
            result = self.nav.navigate_to_pose(self.x, self.y, self.yaw)
            if not result.success:
                return BehaviorStatus.FAILURE
            self.started = True

        status = self.nav.get_status()
        if self.blackboard:
            self.blackboard.set("navigation_status", status)

        if status.state == NavigationState.COMPLETED:
            return BehaviorStatus.SUCCESS
        elif status.state == NavigationState.FAILED:
            return BehaviorStatus.FAILURE
        else:
            return BehaviorStatus.RUNNING

    def reset(self) -> None:
        super().reset()
        self.started = False


class Patrol(BehaviorNode):
    """
    Patrol a set of waypoints.

    Blackboard:
    - Writes: "patrol_waypoint_index", "patrol_loop_count"
    """

    def __init__(
        self,
        nav: NavigationInterface,
        waypoints: List[Vector3],
        loops: int = 1,
        name: str = ""
    ):
        super().__init__(name or f"Patrol({len(waypoints)} waypoints)")
        self.nav = nav
        self.waypoints = waypoints
        self.loops = loops
        self.current_waypoint = 0
        self.current_loop = 0
        self.navigating = False

    def tick(self) -> BehaviorStatus:
        # Check if we're done
        if self.loops > 0 and self.current_loop >= self.loops:
            return BehaviorStatus.SUCCESS

        # Start navigating to current waypoint
        if not self.navigating:
            wp = self.waypoints[self.current_waypoint]
            result = self.nav.navigate_to_point(wp.x, wp.y, wp.z)
            if not result.success:
                return BehaviorStatus.FAILURE
            self.navigating = True

        # Check navigation status
        status = self.nav.get_status()
        if self.blackboard:
            self.blackboard.set("patrol_waypoint_index", self.current_waypoint)
            self.blackboard.set("patrol_loop_count", self.current_loop)

        if status.state == NavigationState.COMPLETED:
            # Move to next waypoint
            self.current_waypoint += 1
            self.navigating = False

            if self.current_waypoint >= len(self.waypoints):
                self.current_waypoint = 0
                self.current_loop += 1

                if self.loops > 0 and self.current_loop >= self.loops:
                    return BehaviorStatus.SUCCESS

            return BehaviorStatus.RUNNING

        elif status.state == NavigationState.FAILED:
            return BehaviorStatus.FAILURE

        return BehaviorStatus.RUNNING

    def reset(self) -> None:
        super().reset()
        self.current_waypoint = 0
        self.current_loop = 0
        self.navigating = False


class ReturnHome(BehaviorNode):
    """
    Navigate to home position.

    Blackboard:
    - Reads: "home_position" (optional, falls back to nav.go_home())
    """

    def __init__(self, nav: NavigationInterface, name: str = ""):
        super().__init__(name or "ReturnHome")
        self.nav = nav
        self.started = False

    def tick(self) -> BehaviorStatus:
        if not self.started:
            # Try blackboard first
            if self.blackboard and self.blackboard.has("home_position"):
                home = self.blackboard.get("home_position")
                result = self.nav.navigate_to_point(home.x, home.y, home.z)
            else:
                result = self.nav.go_home()

            if not result.success:
                return BehaviorStatus.FAILURE
            self.started = True

        status = self.nav.get_status()
        if status.state == NavigationState.COMPLETED:
            return BehaviorStatus.SUCCESS
        elif status.state == NavigationState.FAILED:
            return BehaviorStatus.FAILURE
        return BehaviorStatus.RUNNING

    def reset(self) -> None:
        super().reset()
        self.started = False


# =============================================================================
# Detection Actions
# =============================================================================

class DetectObject(BehaviorNode):
    """
    Run object detection and store results.

    Blackboard:
    - Writes: "detections", "detection_count"
    """

    def __init__(
        self,
        detector: ObjectDetectionInterface,
        class_name: Optional[str] = None,
        min_confidence: float = 0.5,
        name: str = ""
    ):
        super().__init__(name or f"Detect({class_name or 'any'})")
        self.detector = detector
        self.class_name = class_name
        self.min_confidence = min_confidence

    def tick(self) -> BehaviorStatus:
        if self.class_name:
            detections = self.detector.detect_class(
                self.class_name, self.min_confidence
            )
        else:
            result = self.detector.detect()
            detections = result.filter_by_confidence(self.min_confidence)

        if self.blackboard:
            self.blackboard.set("detections", detections)
            self.blackboard.set("detection_count", len(detections))

        if detections:
            return BehaviorStatus.SUCCESS
        return BehaviorStatus.FAILURE


class IsObjectVisible(BehaviorNode):
    """
    Check if an object class is visible.

    This is a CONDITION - returns immediately, never RUNNING.
    """

    def __init__(
        self,
        detector: ObjectDetectionInterface,
        class_name: str,
        min_confidence: float = 0.5,
        name: str = ""
    ):
        super().__init__(name or f"IsVisible({class_name})")
        self.detector = detector
        self.class_name = class_name
        self.min_confidence = min_confidence

    def tick(self) -> BehaviorStatus:
        detections = self.detector.detect_class(
            self.class_name, self.min_confidence
        )
        if detections:
            return BehaviorStatus.SUCCESS
        return BehaviorStatus.FAILURE


class FindNearest(BehaviorNode):
    """
    Find the nearest object of a class.

    Blackboard:
    - Writes: "target_detection", "target_position"
    """

    def __init__(
        self,
        detector: ObjectDetectionInterface,
        class_name: str,
        name: str = ""
    ):
        super().__init__(name or f"FindNearest({class_name})")
        self.detector = detector
        self.class_name = class_name

    def tick(self) -> BehaviorStatus:
        detection = self.detector.find_nearest(self.class_name)

        if detection:
            if self.blackboard:
                self.blackboard.set("target_detection", detection)
                if detection.position_3d:
                    self.blackboard.set("target_position", detection.position_3d)
            return BehaviorStatus.SUCCESS
        return BehaviorStatus.FAILURE


class ApproachObject(BehaviorNode):
    """
    Approach an object (navigate to it).

    Blackboard:
    - Reads: "target_position" or "target_detection"
    """

    def __init__(
        self,
        nav: NavigationInterface,
        approach_distance: float = 0.3,
        name: str = ""
    ):
        super().__init__(name or "ApproachObject")
        self.nav = nav
        self.approach_distance = approach_distance
        self.started = False

    def tick(self) -> BehaviorStatus:
        if not self.started:
            # Get target from blackboard
            if not self.blackboard:
                return BehaviorStatus.FAILURE

            target = self.blackboard.get("target_position")
            if not target:
                detection = self.blackboard.get("target_detection")
                if detection and detection.position_3d:
                    target = detection.position_3d
                else:
                    return BehaviorStatus.FAILURE

            # Navigate to target (with offset)
            result = self.nav.navigate_to_point(
                target.x - self.approach_distance,
                target.y,
                target.z
            )
            if not result.success:
                return BehaviorStatus.FAILURE
            self.started = True

        status = self.nav.get_status()
        if status.state == NavigationState.COMPLETED:
            return BehaviorStatus.SUCCESS
        elif status.state == NavigationState.FAILED:
            return BehaviorStatus.FAILURE
        return BehaviorStatus.RUNNING

    def reset(self) -> None:
        super().reset()
        self.started = False


# =============================================================================
# Manipulation Actions
# =============================================================================

class PickUp(BehaviorNode):
    """
    Pick up an object at the target position.

    Blackboard:
    - Reads: "target_position"
    - Writes: "has_object"
    """

    def __init__(self, gripper: GripperInterface, name: str = ""):
        super().__init__(name or "PickUp")
        self.gripper = gripper
        self.state = "init"

    def tick(self) -> BehaviorStatus:
        if self.state == "init":
            # Open gripper
            result = self.gripper.open()
            if not result.success:
                return BehaviorStatus.FAILURE
            self.state = "lowering"
            return BehaviorStatus.RUNNING

        elif self.state == "lowering":
            # Lower body (would need body interface)
            # For now, skip this step
            self.state = "grasping"
            return BehaviorStatus.RUNNING

        elif self.state == "grasping":
            result = self.gripper.grasp()
            if not result.success:
                return BehaviorStatus.FAILURE
            self.state = "checking"
            return BehaviorStatus.RUNNING

        elif self.state == "checking":
            # Check if we got something
            status = self.gripper.get_status()
            if self.blackboard:
                self.blackboard.set("has_object", status.has_object)
            if status.has_object:
                return BehaviorStatus.SUCCESS
            return BehaviorStatus.FAILURE

        return BehaviorStatus.FAILURE

    def reset(self) -> None:
        super().reset()
        self.state = "init"


class PlaceAt(BehaviorNode):
    """
    Place held object at a position.

    Blackboard:
    - Writes: "has_object" = False on success
    """

    def __init__(
        self,
        gripper: GripperInterface,
        x: float,
        y: float,
        z: float,
        name: str = ""
    ):
        super().__init__(name or f"PlaceAt({x:.1f}, {y:.1f}, {z:.1f})")
        self.gripper = gripper
        self.target = Vector3(x, y, z)
        self.state = "init"

    def tick(self) -> BehaviorStatus:
        # Simplified - just release
        if self.state == "init":
            result = self.gripper.release()
            if result.success:
                if self.blackboard:
                    self.blackboard.set("has_object", False)
                return BehaviorStatus.SUCCESS
            return BehaviorStatus.FAILURE
        return BehaviorStatus.FAILURE

    def reset(self) -> None:
        super().reset()
        self.state = "init"


class DropInBin(BehaviorNode):
    """
    Drop held object into a bin.

    Blackboard:
    - Reads: "bin_position" (optional)
    - Writes: "has_object" = False on success
    """

    def __init__(
        self,
        nav: NavigationInterface,
        gripper: GripperInterface,
        bin_position: Optional[Vector3] = None,
        name: str = ""
    ):
        super().__init__(name or "DropInBin")
        self.nav = nav
        self.gripper = gripper
        self.bin_position = bin_position
        self.state = "navigate"

    def tick(self) -> BehaviorStatus:
        if self.state == "navigate":
            # Get bin position
            pos = self.bin_position
            if not pos and self.blackboard:
                pos = self.blackboard.get("bin_position")
            if not pos:
                return BehaviorStatus.FAILURE

            result = self.nav.navigate_to_point(pos.x, pos.y, pos.z)
            if not result.success:
                return BehaviorStatus.FAILURE
            self.state = "navigating"
            return BehaviorStatus.RUNNING

        elif self.state == "navigating":
            status = self.nav.get_status()
            if status.state == NavigationState.COMPLETED:
                self.state = "dropping"
                return BehaviorStatus.RUNNING
            elif status.state == NavigationState.FAILED:
                return BehaviorStatus.FAILURE
            return BehaviorStatus.RUNNING

        elif self.state == "dropping":
            result = self.gripper.release()
            if result.success:
                if self.blackboard:
                    self.blackboard.set("has_object", False)
                return BehaviorStatus.SUCCESS
            return BehaviorStatus.FAILURE

        return BehaviorStatus.FAILURE

    def reset(self) -> None:
        super().reset()
        self.state = "navigate"


# =============================================================================
# Conditions
# =============================================================================

class IsBatteryLow(BehaviorNode):
    """Check if battery is below threshold."""

    def __init__(self, robot: Any, threshold: float = 20.0, name: str = ""):
        super().__init__(name or "IsBatteryLow")
        self.robot = robot
        self.threshold = threshold

    def tick(self) -> BehaviorStatus:
        try:
            status = self.robot.get_status()
            if status.battery_level < self.threshold:
                return BehaviorStatus.SUCCESS
        except Exception:
            pass
        return BehaviorStatus.FAILURE


class IsPathClear(BehaviorNode):
    """Check if navigation path is clear."""

    def __init__(self, nav: NavigationInterface, name: str = ""):
        super().__init__(name or "IsPathClear")
        self.nav = nav

    def tick(self) -> BehaviorStatus:
        if self.nav.is_path_clear():
            return BehaviorStatus.SUCCESS
        return BehaviorStatus.FAILURE


class HasObject(BehaviorNode):
    """Check if robot is holding an object."""

    def __init__(self, gripper: GripperInterface = None, name: str = ""):
        super().__init__(name or "HasObject")
        self.gripper = gripper

    def tick(self) -> BehaviorStatus:
        # Try gripper first
        if self.gripper:
            status = self.gripper.get_status()
            if status.has_object:
                return BehaviorStatus.SUCCESS
            return BehaviorStatus.FAILURE

        # Fall back to blackboard
        if self.blackboard and self.blackboard.get("has_object"):
            return BehaviorStatus.SUCCESS
        return BehaviorStatus.FAILURE


# =============================================================================
# Composite Behaviors (Higher-Level)
# =============================================================================

def PatrolAndCleanup(
    nav: NavigationInterface,
    detector: ObjectDetectionInterface,
    gripper: GripperInterface,
    waypoints: List[Vector3],
    bin_position: Vector3,
    target_class: str = "trash"
) -> BehaviorNode:
    """
    High-level behavior: Patrol an area, pick up trash, dispose in bin.

    This is the MechDog trash-picking behavior!

    Tree structure:
    RepeatUntilFail
    └── Sequence
        ├── Patrol waypoints
        └── RepeatUntilFail (cleanup loop)
            └── Sequence
                ├── FindNearest(trash)
                ├── ApproachObject
                ├── PickUp
                └── DropInBin
    """
    cleanup_loop = RepeatUntilFail(
        Sequence(children=[
            FindNearest(detector, target_class),
            ApproachObject(nav),
            PickUp(gripper),
            DropInBin(nav, gripper, bin_position),
        ]),
        name="CleanupLoop"
    )

    return RepeatUntilFail(
        Sequence(children=[
            Patrol(nav, waypoints, loops=1),
            cleanup_loop,
        ]),
        name="PatrolAndCleanup"
    )


def SearchAndRetrieve(
    nav: NavigationInterface,
    detector: ObjectDetectionInterface,
    gripper: GripperInterface,
    target_class: str,
    return_position: Vector3
) -> BehaviorNode:
    """
    Search for an object, pick it up, and bring it back.

    Tree structure:
    Sequence
    ├── Selector (find the object)
    │   ├── IsObjectVisible
    │   └── Sequence
    │       ├── Move forward
    │       └── IsObjectVisible
    ├── FindNearest
    ├── ApproachObject
    ├── PickUp
    └── NavigateToPoint (return)
    """
    return Sequence(
        name=f"SearchAndRetrieve({target_class})",
        children=[
            Selector(children=[
                IsObjectVisible(detector, target_class),
                Sequence(children=[
                    NavigateToPoint(nav, 1, 0, 0, "MoveForward"),
                    IsObjectVisible(detector, target_class),
                ]),
            ]),
            FindNearest(detector, target_class),
            ApproachObject(nav),
            PickUp(gripper),
            NavigateToPoint(nav, return_position.x, return_position.y, return_position.z, "Return"),
        ]
    )
