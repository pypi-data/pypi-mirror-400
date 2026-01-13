"""
Demonstration file format for cross-robot skill transfer.

A demonstration is a recorded sequence of interface calls that can be:
- Loaded and inspected
- Replayed on compatible robots
- Filtered by interface
- Labeled with task segments
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Type

from ate.interfaces import RobotInterface, ActionResult
from .session import RecordedCall, RecordingMetadata


@dataclass
class TaskSegment:
    """A labeled segment within a demonstration."""

    start_time: float  # Relative time (seconds)
    end_time: float  # Relative time (seconds)
    label: str  # Task label (e.g., "approaching", "grasping")
    description: Optional[str] = None
    confidence: float = 1.0  # Labeler confidence (0-1)

    def to_dict(self) -> dict:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "label": self.label,
            "description": self.description,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskSegment":
        return cls(**data)


class Demonstration:
    """
    A recorded demonstration that can be replayed on compatible robots.

    Demonstrations are the transferable unit of robot intelligence.
    They capture what the robot did (interface calls) without how it did it
    (hardware-specific commands).
    """

    def __init__(
        self,
        metadata: RecordingMetadata,
        calls: List[RecordedCall],
        segments: Optional[List[TaskSegment]] = None,
    ):
        """
        Initialize a demonstration.

        Args:
            metadata: Recording metadata
            calls: List of recorded calls
            segments: Optional labeled task segments
        """
        self.metadata = metadata
        self.calls = calls
        self.segments = segments or []

    @property
    def duration(self) -> float:
        """Get total duration in seconds."""
        if not self.calls:
            return 0.0
        return self.calls[-1].relative_time

    @property
    def robot_archetype(self) -> str:
        """Get the robot archetype (quadruped, biped, etc.)."""
        return self.metadata.robot_archetype

    @property
    def capabilities(self) -> List[str]:
        """Get required capabilities."""
        return self.metadata.capabilities

    def filter(
        self,
        interface: Optional[str] = None,
        method: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> List[RecordedCall]:
        """
        Filter calls by interface, method, or time range.

        Args:
            interface: Filter by interface name
            method: Filter by method name
            start_time: Filter by minimum relative time
            end_time: Filter by maximum relative time

        Returns:
            Filtered list of calls
        """
        result = self.calls

        if interface:
            result = [c for c in result if c.interface == interface]
        if method:
            result = [c for c in result if c.method == method]
        if start_time is not None:
            result = [c for c in result if c.relative_time >= start_time]
        if end_time is not None:
            result = [c for c in result if c.relative_time <= end_time]

        return result

    def get_calls_in_segment(self, segment: TaskSegment) -> List[RecordedCall]:
        """Get calls within a labeled segment."""
        return self.filter(
            start_time=segment.start_time,
            end_time=segment.end_time,
        )

    def get_interfaces_used(self) -> List[str]:
        """Get list of interfaces used in this demonstration."""
        return list(set(c.interface for c in self.calls))

    def get_methods_used(self) -> Dict[str, List[str]]:
        """Get methods used per interface."""
        result: Dict[str, set] = {}
        for call in self.calls:
            if call.interface not in result:
                result[call.interface] = set()
            result[call.interface].add(call.method)
        return {k: list(v) for k, v in result.items()}

    def is_compatible(self, driver: RobotInterface) -> bool:
        """
        Check if this demonstration is compatible with a driver.

        Compatibility means the driver implements all interfaces
        used in the demonstration.
        """
        driver_interfaces = self._get_driver_interfaces(driver)
        required = set(self.get_interfaces_used())
        return required.issubset(driver_interfaces)

    def _get_driver_interfaces(self, driver: RobotInterface) -> set:
        """Get interface names implemented by a driver."""
        from ate.interfaces import (
            RobotInterface, SafetyInterface,
            QuadrupedLocomotion, BipedLocomotion, WheeledLocomotion, AerialLocomotion,
            ArmInterface, GripperInterface, DualArmInterface,
            CameraInterface, DepthCameraInterface, LidarInterface, IMUInterface, ForceTorqueInterface,
            BodyPoseInterface,
        )

        all_interfaces = {
            "RobotInterface": RobotInterface,
            "SafetyInterface": SafetyInterface,
            "QuadrupedLocomotion": QuadrupedLocomotion,
            "BipedLocomotion": BipedLocomotion,
            "WheeledLocomotion": WheeledLocomotion,
            "AerialLocomotion": AerialLocomotion,
            "ArmInterface": ArmInterface,
            "GripperInterface": GripperInterface,
            "DualArmInterface": DualArmInterface,
            "CameraInterface": CameraInterface,
            "DepthCameraInterface": DepthCameraInterface,
            "LidarInterface": LidarInterface,
            "IMUInterface": IMUInterface,
            "ForceTorqueInterface": ForceTorqueInterface,
            "BodyPoseInterface": BodyPoseInterface,
        }

        return {
            name for name, cls in all_interfaces.items()
            if isinstance(driver, cls)
        }

    def replay(
        self,
        driver: RobotInterface,
        speed: float = 1.0,
        skip_perception: bool = True,
        dry_run: bool = False,
    ) -> List[ActionResult]:
        """
        Replay this demonstration on a compatible driver.

        Args:
            driver: Robot driver to replay on
            speed: Playback speed (1.0 = realtime, 2.0 = 2x speed)
            skip_perception: Skip perception calls (get_image, etc.)
            dry_run: If True, don't actually execute commands

        Returns:
            List of ActionResults from each call
        """
        if not self.is_compatible(driver):
            missing = set(self.get_interfaces_used()) - self._get_driver_interfaces(driver)
            raise ValueError(f"Driver missing required interfaces: {missing}")

        # Filter perception calls if requested
        calls = self.calls
        if skip_perception:
            perception_methods = {
                "get_image", "get_depth_image", "get_point_cloud",
                "get_scan", "get_reading", "get_orientation",
                "get_force", "get_torque",
            }
            calls = [c for c in calls if c.method not in perception_methods]

        results = []
        prev_time = 0.0

        for call in calls:
            # Wait for timing (unless first call)
            if call.relative_time > prev_time:
                wait_time = (call.relative_time - prev_time) / speed
                if not dry_run:
                    time.sleep(wait_time)

            prev_time = call.relative_time

            if dry_run:
                results.append(ActionResult.ok(f"[DRY RUN] {call.method}"))
                continue

            # Execute the call
            method = getattr(driver, call.method, None)
            if method is None:
                results.append(ActionResult.error(f"Method not found: {call.method}"))
                continue

            try:
                # Deserialize arguments
                args = self._deserialize_args(call.args)
                kwargs = self._deserialize_kwargs(call.kwargs)
                result = method(*args, **kwargs)
                results.append(result if isinstance(result, ActionResult) else ActionResult.ok())
            except Exception as e:
                results.append(ActionResult.error(str(e)))

        return results

    def _deserialize_args(self, args: tuple) -> tuple:
        """Deserialize arguments back to interface types."""
        from ate.interfaces import Vector3, Quaternion, Pose

        result = []
        for arg in args:
            result.append(self._deserialize_value(arg))
        return tuple(result)

    def _deserialize_kwargs(self, kwargs: dict) -> dict:
        """Deserialize keyword arguments."""
        return {k: self._deserialize_value(v) for k, v in kwargs.items()}

    def _deserialize_value(self, value: Any) -> Any:
        """Deserialize a single value back to interface type."""
        from ate.interfaces import Vector3, Quaternion, Pose

        if isinstance(value, dict) and "__type__" in value:
            type_name = value["__type__"]
            if type_name == "Vector3":
                return Vector3(value["x"], value["y"], value["z"])
            if type_name == "Quaternion":
                return Quaternion(value["x"], value["y"], value["z"], value["w"])
            if type_name == "Pose":
                pos = self._deserialize_value(value["position"])
                ori = self._deserialize_value(value["orientation"])
                return Pose(pos, ori)
            # Return dict as-is for unknown types
            return value

        if isinstance(value, list):
            return [self._deserialize_value(v) for v in value]

        return value

    def add_segment(self, segment: TaskSegment) -> None:
        """Add a labeled task segment."""
        self.segments.append(segment)
        # Keep segments sorted by start time
        self.segments.sort(key=lambda s: s.start_time)

    def label_range(
        self,
        start_time: float,
        end_time: float,
        label: str,
        description: Optional[str] = None,
    ) -> TaskSegment:
        """
        Label a time range with a task.

        Args:
            start_time: Start of segment (relative time)
            end_time: End of segment (relative time)
            label: Task label
            description: Optional description

        Returns:
            Created TaskSegment
        """
        segment = TaskSegment(
            start_time=start_time,
            end_time=end_time,
            label=label,
            description=description,
        )
        self.add_segment(segment)
        return segment

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "version": "1.0",
            "metadata": self.metadata.to_dict(),
            "calls": [c.to_dict() for c in self.calls],
            "segments": [s.to_dict() for s in self.segments],
        }

    def save(self, path: str) -> None:
        """Save to file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "Demonstration":
        """Create from dictionary."""
        metadata = RecordingMetadata.from_dict(data["metadata"])
        calls = [RecordedCall.from_dict(c) for c in data["calls"]]
        segments = [TaskSegment.from_dict(s) for s in data.get("segments", [])]
        return cls(metadata, calls, segments)

    def summary(self) -> str:
        """Get human-readable summary."""
        lines = [
            f"Demonstration: {self.metadata.name}",
            f"Robot: {self.metadata.robot_name} ({self.metadata.robot_archetype})",
            f"Duration: {self.duration:.2f}s",
            f"Total calls: {len(self.calls)}",
            f"Labeled segments: {len(self.segments)}",
            "",
        ]

        if self.segments:
            lines.append("Segments:")
            for seg in self.segments:
                lines.append(f"  [{seg.start_time:.2f}s - {seg.end_time:.2f}s] {seg.label}")

        lines.append("")
        lines.append("Interfaces used:")
        for interface, methods in self.get_methods_used().items():
            lines.append(f"  {interface}: {', '.join(methods)}")

        return "\n".join(lines)


def load_demonstration(path: str) -> Demonstration:
    """
    Load a demonstration from file.

    Args:
        path: Path to .demonstration file

    Returns:
        Demonstration object
    """
    with open(path, 'r') as f:
        data = json.load(f)
    return Demonstration.from_dict(data)
