"""
Robot capability introspection.

Inspect what a robot can do by examining its interfaces and methods.
"""

import inspect
from typing import Dict, List, Set, Any, Optional, Type
from dataclasses import dataclass

from ..interfaces import (
    RobotInterface,
    SafetyInterface,
    QuadrupedLocomotion,
    BipedLocomotion,
    WheeledLocomotion,
    AerialLocomotion,
    ArmInterface,
    GripperInterface,
    CameraInterface,
    DepthCameraInterface,
    LidarInterface,
    IMUInterface,
    BodyPoseInterface,
    NavigationInterface,
    ObjectDetectionInterface,
)


@dataclass
class MethodInfo:
    """Information about a robot method."""
    name: str
    interface: str
    description: str
    parameters: List[str]
    return_type: str


@dataclass
class CapabilityInfo:
    """Information about a robot capability."""
    name: str
    interface_class: str
    description: str
    methods: List[MethodInfo]
    available: bool = True


# Map interfaces to capability names
INTERFACE_CAPABILITIES = {
    QuadrupedLocomotion: "quadruped_locomotion",
    BipedLocomotion: "bipedal_locomotion",
    WheeledLocomotion: "wheeled_locomotion",
    AerialLocomotion: "aerial_locomotion",
    ArmInterface: "arm",
    GripperInterface: "gripper",
    CameraInterface: "camera",
    DepthCameraInterface: "depth_camera",
    LidarInterface: "lidar",
    IMUInterface: "imu",
    BodyPoseInterface: "body_pose",
    SafetyInterface: "safety",
    NavigationInterface: "navigation",
    ObjectDetectionInterface: "object_detection",
}


def get_capabilities(robot: Any) -> Dict[str, CapabilityInfo]:
    """
    Get all capabilities of a robot instance.

    Args:
        robot: Robot instance

    Returns:
        Dict mapping capability name to CapabilityInfo
    """
    capabilities = {}

    for interface, cap_name in INTERFACE_CAPABILITIES.items():
        if isinstance(robot, interface):
            methods = get_interface_methods(interface)
            capabilities[cap_name] = CapabilityInfo(
                name=cap_name,
                interface_class=interface.__name__,
                description=interface.__doc__ or "",
                methods=methods,
                available=True,
            )

    return capabilities


def get_methods(robot: Any) -> Dict[str, List[MethodInfo]]:
    """
    Get all available methods grouped by capability.

    Args:
        robot: Robot instance

    Returns:
        Dict mapping capability name to list of methods
    """
    result = {}

    for interface, cap_name in INTERFACE_CAPABILITIES.items():
        if isinstance(robot, interface):
            methods = get_interface_methods(interface)
            if methods:
                result[cap_name] = methods

    return result


def get_interface_methods(interface: Type) -> List[MethodInfo]:
    """
    Get methods defined by an interface.

    Args:
        interface: Interface class

    Returns:
        List of MethodInfo
    """
    methods = []

    for name, method in inspect.getmembers(interface, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue

        # Get signature
        try:
            sig = inspect.signature(method)
            params = [
                p.name for p in sig.parameters.values()
                if p.name != "self"
            ]
            return_type = str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "None"
        except (ValueError, TypeError):
            params = []
            return_type = "Unknown"

        # Clean up return type
        return_type = return_type.replace("typing.", "").replace("<class '", "").replace("'>", "")

        methods.append(MethodInfo(
            name=name,
            interface=interface.__name__,
            description=method.__doc__ or "",
            parameters=params,
            return_type=return_type,
        ))

    return methods


def test_capability(robot: Any, capability: str) -> Dict[str, Any]:
    """
    Test if a capability is working.

    Args:
        robot: Robot instance
        capability: Capability name to test

    Returns:
        Test result with status and details
    """
    result = {
        "capability": capability,
        "status": "unknown",
        "tests": [],
    }

    # Find the interface for this capability
    interface = None
    for iface, cap_name in INTERFACE_CAPABILITIES.items():
        if cap_name == capability:
            interface = iface
            break

    if interface is None:
        result["status"] = "error"
        result["error"] = f"Unknown capability: {capability}"
        return result

    if not isinstance(robot, interface):
        result["status"] = "not_available"
        result["error"] = f"Robot does not have capability: {capability}"
        return result

    # Run capability-specific tests
    try:
        if capability == "camera":
            result["tests"].append(_test_camera(robot))
        elif capability == "quadruped_locomotion":
            result["tests"].append(_test_locomotion(robot))
        elif capability == "body_pose":
            result["tests"].append(_test_body_pose(robot))
        elif capability == "safety":
            result["tests"].append(_test_safety(robot))
        else:
            result["tests"].append({
                "name": "basic_check",
                "status": "passed",
                "message": f"Robot implements {interface.__name__}",
            })

        # Determine overall status
        if all(t.get("status") == "passed" for t in result["tests"]):
            result["status"] = "passed"
        elif any(t.get("status") == "failed" for t in result["tests"]):
            result["status"] = "failed"
        else:
            result["status"] = "partial"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def _test_camera(robot: Any) -> Dict[str, Any]:
    """Test camera capability."""
    test = {"name": "camera_capture", "status": "unknown"}

    try:
        image = robot.get_image()
        if image.width > 0 and image.height > 0:
            test["status"] = "passed"
            test["message"] = f"Captured {image.width}x{image.height} image"
        else:
            test["status"] = "failed"
            test["message"] = "Image capture returned empty"
    except Exception as e:
        test["status"] = "failed"
        test["error"] = str(e)

    return test


def _test_locomotion(robot: Any) -> Dict[str, Any]:
    """Test locomotion capability (non-destructive)."""
    test = {"name": "locomotion_status", "status": "unknown"}

    try:
        if hasattr(robot, "is_moving"):
            is_moving = robot.is_moving()
            test["status"] = "passed"
            test["message"] = f"Robot is {'moving' if is_moving else 'stationary'}"
        else:
            test["status"] = "passed"
            test["message"] = "Locomotion interface available"
    except Exception as e:
        test["status"] = "failed"
        test["error"] = str(e)

    return test


def _test_body_pose(robot: Any) -> Dict[str, Any]:
    """Test body pose capability."""
    test = {"name": "body_pose_read", "status": "unknown"}

    try:
        height = robot.get_body_height()
        test["status"] = "passed"
        test["message"] = f"Body height: {height:.3f}m"
    except Exception as e:
        test["status"] = "failed"
        test["error"] = str(e)

    return test


def _test_safety(robot: Any) -> Dict[str, Any]:
    """Test safety capability."""
    test = {"name": "safety_status", "status": "unknown"}

    try:
        estopped = robot.is_estopped()
        test["status"] = "passed"
        test["message"] = f"E-stop: {'active' if estopped else 'inactive'}"
    except Exception as e:
        test["status"] = "failed"
        test["error"] = str(e)

    return test


def format_capabilities(capabilities: Dict[str, CapabilityInfo]) -> str:
    """Format capabilities for CLI display."""
    lines = []

    for name, info in capabilities.items():
        lines.append(f"\n{name.upper()}")
        lines.append("-" * len(name))

        if info.description:
            first_line = info.description.strip().split("\n")[0]
            lines.append(f"  {first_line}")

        lines.append("  Methods:")
        for method in info.methods[:5]:  # Show first 5 methods
            params = ", ".join(method.parameters[:3])  # Show first 3 params
            if len(method.parameters) > 3:
                params += ", ..."
            lines.append(f"    - {method.name}({params})")

        if len(info.methods) > 5:
            lines.append(f"    ... and {len(info.methods) - 5} more")

    return "\n".join(lines)


def format_methods(methods: Dict[str, List[MethodInfo]]) -> str:
    """Format methods for CLI display."""
    lines = []

    for capability, method_list in methods.items():
        lines.append(f"\n[{capability}]")
        for method in method_list:
            params = ", ".join(method.parameters)
            lines.append(f"  {method.name}({params}) -> {method.return_type}")
            if method.description:
                first_line = method.description.strip().split("\n")[0][:60]
                lines.append(f"    {first_line}")

    return "\n".join(lines)
