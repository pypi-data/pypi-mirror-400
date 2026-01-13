"""
Recording session for capturing robot demonstrations.
"""

import time
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Any, List, Optional, Dict, Callable
from functools import wraps

from ate.interfaces import RobotInterface, ActionResult


@dataclass
class RecordedCall:
    """A single recorded interface method call."""

    timestamp: float  # Unix timestamp (seconds)
    relative_time: float  # Time since recording started (seconds)
    interface: str  # Interface name (e.g., "QuadrupedLocomotion")
    method: str  # Method name (e.g., "walk")
    args: tuple  # Positional arguments (serialized)
    kwargs: dict  # Keyword arguments (serialized)
    result: Any  # Return value (serialized)
    success: bool  # Whether the call succeeded
    error: Optional[str] = None  # Error message if failed

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "relative_time": self.relative_time,
            "interface": self.interface,
            "method": self.method,
            "args": self._serialize_args(self.args),
            "kwargs": self._serialize_kwargs(self.kwargs),
            "result": self._serialize_result(self.result),
            "success": self.success,
            "error": self.error,
        }

    def _serialize_args(self, args: tuple) -> list:
        """Serialize arguments to JSON-compatible format."""
        return [self._serialize_value(arg) for arg in args]

    def _serialize_kwargs(self, kwargs: dict) -> dict:
        """Serialize keyword arguments to JSON-compatible format."""
        return {k: self._serialize_value(v) for k, v in kwargs.items()}

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a single value."""
        # Handle common types
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}

        # Handle our interface types
        if hasattr(value, '__dataclass_fields__'):
            return {"__type__": type(value).__name__, **asdict(value)}
        if hasattr(value, 'to_dict'):
            return {"__type__": type(value).__name__, **value.to_dict()}

        # Handle ActionResult
        if isinstance(value, ActionResult):
            return {
                "__type__": "ActionResult",
                "success": value.success,
                "message": value.message,
                "error": value.error,
            }

        # Fallback: convert to string
        return {"__type__": type(value).__name__, "__str__": str(value)}

    def _serialize_result(self, result: Any) -> Any:
        """Serialize return value."""
        return self._serialize_value(result)

    @classmethod
    def from_dict(cls, data: dict) -> "RecordedCall":
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            relative_time=data["relative_time"],
            interface=data["interface"],
            method=data["method"],
            args=tuple(data["args"]),
            kwargs=data["kwargs"],
            result=data["result"],
            success=data["success"],
            error=data.get("error"),
        )


@dataclass
class RecordingMetadata:
    """Metadata for a recording session."""

    id: str  # Unique recording ID
    name: str  # Human-readable name
    robot_name: str  # Robot name from driver
    robot_model: str  # Robot model from driver
    robot_archetype: str  # Robot archetype (quadruped, etc.)
    capabilities: List[str]  # Robot capabilities
    start_time: float  # Unix timestamp
    end_time: Optional[float] = None  # Unix timestamp
    duration: Optional[float] = None  # Seconds
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RecordingMetadata":
        return cls(**data)


class RecordingSession:
    """
    Context manager for recording robot demonstrations.

    Wraps a robot driver to intercept and record all interface method calls.

    Usage:
        with RecordingSession(driver, name="my_demo") as session:
            driver.stand()
            driver.walk(Vector3.forward(), speed=0.3)

        session.save("my_demo.demonstration")
    """

    def __init__(
        self,
        driver: RobotInterface,
        name: str = "recording",
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        auto_save: bool = False,
        save_path: Optional[str] = None,
    ):
        """
        Initialize a recording session.

        Args:
            driver: Robot driver to record
            name: Human-readable name for the recording
            description: Optional description
            tags: Optional tags for categorization
            auto_save: If True, save automatically on exit
            save_path: Path for auto-save (uses name if not provided)
        """
        self._driver = driver
        self._name = name
        self._description = description
        self._tags = tags or []
        self._auto_save = auto_save
        self._save_path = save_path

        self._calls: List[RecordedCall] = []
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self._original_methods: Dict[str, Callable] = {}
        self._recording = False

    @property
    def calls(self) -> List[RecordedCall]:
        """Get all recorded calls."""
        return self._calls.copy()

    @property
    def duration(self) -> Optional[float]:
        """Get recording duration in seconds."""
        if self._start_time is None:
            return None
        end = self._end_time or time.time()
        return end - self._start_time

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording

    def __enter__(self) -> "RecordingSession":
        """Start recording."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop recording."""
        self.stop()
        if self._auto_save:
            path = self._save_path or f"{self._name}.demonstration"
            self.save(path)
        return False  # Don't suppress exceptions

    def start(self) -> None:
        """Start recording interface calls."""
        if self._recording:
            return

        self._start_time = time.time()
        self._recording = True
        self._wrap_driver_methods()

    def stop(self) -> None:
        """Stop recording interface calls."""
        if not self._recording:
            return

        self._end_time = time.time()
        self._recording = False
        self._unwrap_driver_methods()

    def _wrap_driver_methods(self) -> None:
        """Wrap all driver methods to intercept calls."""
        # Get all interfaces the driver implements
        interfaces = self._get_driver_interfaces()

        for interface_name, interface_cls in interfaces.items():
            # Get methods defined in this interface
            for method_name in self._get_interface_methods(interface_cls):
                if hasattr(self._driver, method_name):
                    original = getattr(self._driver, method_name)
                    if callable(original) and not method_name.startswith('_'):
                        # Store original
                        key = f"{interface_name}.{method_name}"
                        self._original_methods[key] = original

                        # Create wrapper
                        wrapper = self._create_wrapper(interface_name, method_name, original)
                        setattr(self._driver, method_name, wrapper)

    def _unwrap_driver_methods(self) -> None:
        """Restore original driver methods."""
        for key, original in self._original_methods.items():
            _, method_name = key.split(".", 1)
            setattr(self._driver, method_name, original)
        self._original_methods.clear()

    def _get_driver_interfaces(self) -> Dict[str, type]:
        """Get all interface classes the driver implements."""
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
            name: cls for name, cls in all_interfaces.items()
            if isinstance(self._driver, cls)
        }

    def _get_interface_methods(self, interface_cls: type) -> List[str]:
        """Get public methods defined in an interface class."""
        methods = []
        for name in dir(interface_cls):
            if not name.startswith('_'):
                attr = getattr(interface_cls, name, None)
                if callable(attr):
                    methods.append(name)
        return methods

    def _create_wrapper(
        self,
        interface_name: str,
        method_name: str,
        original: Callable
    ) -> Callable:
        """Create a wrapper function that records the call."""

        @wraps(original)
        def wrapper(*args, **kwargs):
            timestamp = time.time()
            relative_time = timestamp - self._start_time

            try:
                result = original(*args, **kwargs)
                success = True
                error = None

                # Check ActionResult for failure
                if isinstance(result, ActionResult) and not result.success:
                    error = result.error

            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                # Record the call
                call = RecordedCall(
                    timestamp=timestamp,
                    relative_time=relative_time,
                    interface=interface_name,
                    method=method_name,
                    args=args,
                    kwargs=kwargs,
                    result=result,
                    success=success,
                    error=error,
                )
                self._calls.append(call)

            return result

        return wrapper

    def get_metadata(self) -> RecordingMetadata:
        """Get recording metadata."""
        info = self._driver.get_info()
        return RecordingMetadata(
            id=str(uuid.uuid4()),
            name=self._name,
            robot_name=info.name,
            robot_model=info.model,
            robot_archetype=info.archetype,
            capabilities=[c.name for c in info.capabilities],
            start_time=self._start_time or 0,
            end_time=self._end_time,
            duration=self.duration,
            description=self._description,
            tags=self._tags,
        )

    def save(self, path: str) -> None:
        """
        Save recording to a file.

        Args:
            path: File path (should end with .demonstration)
        """
        data = {
            "version": "1.0",
            "metadata": self.get_metadata().to_dict(),
            "calls": [call.to_dict() for call in self._calls],
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def to_dict(self) -> dict:
        """Convert to dictionary for API upload."""
        return {
            "version": "1.0",
            "metadata": self.get_metadata().to_dict(),
            "calls": [call.to_dict() for call in self._calls],
        }

    def summary(self) -> str:
        """Get a human-readable summary of the recording."""
        if not self._calls:
            return "No calls recorded"

        # Group by interface
        by_interface: Dict[str, List[RecordedCall]] = {}
        for call in self._calls:
            if call.interface not in by_interface:
                by_interface[call.interface] = []
            by_interface[call.interface].append(call)

        lines = [
            f"Recording: {self._name}",
            f"Duration: {self.duration:.2f}s" if self.duration else "Duration: N/A",
            f"Total calls: {len(self._calls)}",
            "",
            "By interface:",
        ]

        for interface, calls in by_interface.items():
            lines.append(f"  {interface}: {len(calls)} calls")
            # Count by method
            by_method: Dict[str, int] = {}
            for call in calls:
                by_method[call.method] = by_method.get(call.method, 0) + 1
            for method, count in sorted(by_method.items()):
                lines.append(f"    - {method}: {count}")

        return "\n".join(lines)
