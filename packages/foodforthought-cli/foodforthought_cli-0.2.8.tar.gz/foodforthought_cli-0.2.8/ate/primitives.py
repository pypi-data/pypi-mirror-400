"""
Primitive Registry - Catalog of all available robot primitives.

Primitives are the atomic building blocks of robot skills. This module
provides a registry of all available primitives with their signatures,
hardware requirements, and documentation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class PrimitiveCategory(str, Enum):
    """Categories of primitives."""
    MOTION = "motion"  # Movement primitives
    GRIPPER = "gripper"  # Gripper/end-effector actions
    SENSING = "sensing"  # Sensor reading primitives
    WAIT = "wait"  # Timing and condition waits
    CONTROL = "control"  # Control flow primitives
    COMMUNICATION = "communication"  # Inter-system communication


@dataclass
class ParameterDefinition:
    """Definition of a primitive parameter."""
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    range: Optional[tuple] = None
    units: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"type": self.type, "description": self.description}
        if not self.required:
            d["required"] = False
        if self.default is not None:
            d["default"] = self.default
        if self.range:
            d["range"] = list(self.range)
        if self.units:
            d["units"] = self.units
        return d


@dataclass
class PrimitiveDefinition:
    """Complete definition of a primitive."""
    name: str
    description: str
    category: PrimitiveCategory
    parameters: Dict[str, ParameterDefinition]
    returns: str
    hardware: List[str]
    blocking: bool = True  # Whether this primitive blocks execution
    timeout_default: Optional[float] = None
    example: Optional[str] = None

    def validate_parameters(self, provided: Dict[str, Any]) -> List[str]:
        """Validate provided parameters against this primitive's signature."""
        errors = []

        # Check required parameters
        for name, param_def in self.parameters.items():
            if param_def.required and name not in provided:
                errors.append(f"Missing required parameter: {name}")

        # Check for unknown parameters
        for name in provided:
            if name not in self.parameters:
                errors.append(f"Unknown parameter: {name}")

        # Validate types and ranges
        for name, value in provided.items():
            if name not in self.parameters:
                continue
            param_def = self.parameters[name]

            # Range validation
            if param_def.range and isinstance(value, (int, float)):
                min_val, max_val = param_def.range
                if value < min_val or value > max_val:
                    errors.append(
                        f"Parameter '{name}' value {value} out of range "
                        f"[{min_val}, {max_val}]"
                    )

        return errors

    def get_signature(self) -> str:
        """Get a function signature string for this primitive."""
        params = []
        for name, param_def in self.parameters.items():
            if param_def.required:
                params.append(f"{name}: {param_def.type}")
            else:
                default = repr(param_def.default)
                params.append(f"{name}: {param_def.type} = {default}")
        return f"{self.name}({', '.join(params)}) -> {self.returns}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "category": self.category.value,
            "parameters": {
                name: param.to_dict()
                for name, param in self.parameters.items()
            },
            "returns": self.returns,
            "hardware": self.hardware,
            "blocking": self.blocking,
            "timeout_default": self.timeout_default,
            "example": self.example,
        }


# =============================================================================
# PRIMITIVE REGISTRY
# =============================================================================
# All available primitives organized by category

PRIMITIVE_REGISTRY: Dict[str, PrimitiveDefinition] = {}


def register_primitive(prim: PrimitiveDefinition) -> PrimitiveDefinition:
    """Register a primitive in the global registry."""
    PRIMITIVE_REGISTRY[prim.name] = prim
    return prim


# -----------------------------------------------------------------------------
# Motion Primitives
# -----------------------------------------------------------------------------

register_primitive(PrimitiveDefinition(
    name="move_to_pose",
    description="Move end effector to target pose in Cartesian space",
    category=PrimitiveCategory.MOTION,
    parameters={
        "pose": ParameterDefinition(
            type="Pose",
            description="Target pose with position (x, y, z) and orientation (quaternion)",
            required=True
        ),
        "speed": ParameterDefinition(
            type="float",
            description="Movement speed as fraction of max (0.0-1.0)",
            required=False,
            default=0.5,
            range=(0.0, 1.0)
        ),
        "acceleration": ParameterDefinition(
            type="float",
            description="Acceleration as fraction of max (0.0-1.0)",
            required=False,
            default=0.3,
            range=(0.0, 1.0)
        ),
        "blend_radius": ParameterDefinition(
            type="float",
            description="Blend radius for smooth path (meters)",
            required=False,
            default=0.0,
            units="meters"
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=30.0,
    example='move_to_pose(pose={"position": [0.5, 0.0, 0.3], "orientation": [0, 0, 0, 1]})'
))

register_primitive(PrimitiveDefinition(
    name="move_to_joints",
    description="Move to target joint configuration",
    category=PrimitiveCategory.MOTION,
    parameters={
        "joint_positions": ParameterDefinition(
            type="array",
            description="Target joint positions in radians",
            required=True
        ),
        "speed": ParameterDefinition(
            type="float",
            description="Movement speed as fraction of max (0.0-1.0)",
            required=False,
            default=0.5,
            range=(0.0, 1.0)
        ),
        "acceleration": ParameterDefinition(
            type="float",
            description="Acceleration as fraction of max (0.0-1.0)",
            required=False,
            default=0.3,
            range=(0.0, 1.0)
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=30.0,
    example="move_to_joints(joint_positions=[0, -1.57, 1.57, 0, 0, 0])"
))

register_primitive(PrimitiveDefinition(
    name="move_linear",
    description="Move end effector in a straight line to target pose",
    category=PrimitiveCategory.MOTION,
    parameters={
        "pose": ParameterDefinition(
            type="Pose",
            description="Target pose",
            required=True
        ),
        "speed": ParameterDefinition(
            type="float",
            description="Linear speed (m/s)",
            required=False,
            default=0.1,
            range=(0.001, 1.0),
            units="m/s"
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=60.0,
    example='move_linear(pose={"position": [0.5, 0.0, 0.3], "orientation": [0, 0, 0, 1]}, speed=0.05)'
))

register_primitive(PrimitiveDefinition(
    name="move_relative",
    description="Move end effector relative to current pose",
    category=PrimitiveCategory.MOTION,
    parameters={
        "delta_position": ParameterDefinition(
            type="array",
            description="Relative position change [dx, dy, dz] in meters",
            required=False,
            default=[0, 0, 0]
        ),
        "delta_rotation": ParameterDefinition(
            type="array",
            description="Relative rotation [rx, ry, rz] in radians",
            required=False,
            default=[0, 0, 0]
        ),
        "frame": ParameterDefinition(
            type="string",
            description="Reference frame: 'base', 'tool', or 'world'",
            required=False,
            default="tool"
        ),
        "speed": ParameterDefinition(
            type="float",
            description="Movement speed as fraction of max (0.0-1.0)",
            required=False,
            default=0.3,
            range=(0.0, 1.0)
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=30.0,
    example="move_relative(delta_position=[0, 0, -0.1], frame='tool')"
))

register_primitive(PrimitiveDefinition(
    name="move_servo",
    description="Move a single servo to target position",
    category=PrimitiveCategory.MOTION,
    parameters={
        "servo_id": ParameterDefinition(
            type="int",
            description="Servo ID",
            required=True
        ),
        "position": ParameterDefinition(
            type="float",
            description="Target position (unit depends on servo type)",
            required=True
        ),
        "time_ms": ParameterDefinition(
            type="int",
            description="Movement duration in milliseconds",
            required=False,
            default=500
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=5.0,
    example="move_servo(servo_id=1, position=512, time_ms=1000)"
))

register_primitive(PrimitiveDefinition(
    name="move_servos",
    description="Move multiple servos simultaneously",
    category=PrimitiveCategory.MOTION,
    parameters={
        "commands": ParameterDefinition(
            type="array",
            description="List of {servo_id, position, time_ms} commands",
            required=True
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=5.0,
    example="move_servos(commands=[{'servo_id': 1, 'position': 512}, {'servo_id': 2, 'position': 600}])"
))

register_primitive(PrimitiveDefinition(
    name="execute_trajectory",
    description="Execute a pre-planned trajectory",
    category=PrimitiveCategory.MOTION,
    parameters={
        "trajectory": ParameterDefinition(
            type="Trajectory",
            description="Trajectory with waypoints and timing",
            required=True
        ),
        "speed_scale": ParameterDefinition(
            type="float",
            description="Speed scaling factor (0.0-2.0)",
            required=False,
            default=1.0,
            range=(0.1, 2.0)
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=300.0,
    example="execute_trajectory(trajectory=planned_traj, speed_scale=0.8)"
))

register_primitive(PrimitiveDefinition(
    name="home",
    description="Move robot to home/neutral position",
    category=PrimitiveCategory.MOTION,
    parameters={
        "speed": ParameterDefinition(
            type="float",
            description="Movement speed as fraction of max (0.0-1.0)",
            required=False,
            default=0.3,
            range=(0.0, 1.0)
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=30.0,
    example="home(speed=0.5)"
))

# -----------------------------------------------------------------------------
# Gripper Primitives
# -----------------------------------------------------------------------------

register_primitive(PrimitiveDefinition(
    name="close_gripper",
    description="Close gripper to grasp an object",
    category=PrimitiveCategory.GRIPPER,
    parameters={
        "force": ParameterDefinition(
            type="float",
            description="Gripping force in Newtons",
            required=False,
            default=10.0,
            range=(1.0, 100.0),
            units="N"
        ),
        "width": ParameterDefinition(
            type="float",
            description="Target gripper width (optional, for partial close)",
            required=False,
            default=None,
            units="meters"
        ),
        "speed": ParameterDefinition(
            type="float",
            description="Closing speed as fraction of max (0.0-1.0)",
            required=False,
            default=0.5,
            range=(0.0, 1.0)
        ),
    },
    returns="bool",
    hardware=["gripper"],
    blocking=True,
    timeout_default=5.0,
    example="close_gripper(force=20.0)"
))

register_primitive(PrimitiveDefinition(
    name="open_gripper",
    description="Open gripper to release an object",
    category=PrimitiveCategory.GRIPPER,
    parameters={
        "width": ParameterDefinition(
            type="float",
            description="Target opening width",
            required=False,
            default=None,
            units="meters"
        ),
        "speed": ParameterDefinition(
            type="float",
            description="Opening speed as fraction of max (0.0-1.0)",
            required=False,
            default=0.5,
            range=(0.0, 1.0)
        ),
    },
    returns="bool",
    hardware=["gripper"],
    blocking=True,
    timeout_default=5.0,
    example="open_gripper(width=0.08)"
))

register_primitive(PrimitiveDefinition(
    name="set_gripper_position",
    description="Set gripper to specific position",
    category=PrimitiveCategory.GRIPPER,
    parameters={
        "position": ParameterDefinition(
            type="float",
            description="Target position (0.0=closed, 1.0=fully open)",
            required=True,
            range=(0.0, 1.0)
        ),
        "speed": ParameterDefinition(
            type="float",
            description="Movement speed as fraction of max (0.0-1.0)",
            required=False,
            default=0.5,
            range=(0.0, 1.0)
        ),
    },
    returns="bool",
    hardware=["gripper"],
    blocking=True,
    timeout_default=5.0,
    example="set_gripper_position(position=0.5)"
))

# -----------------------------------------------------------------------------
# Sensing Primitives
# -----------------------------------------------------------------------------

register_primitive(PrimitiveDefinition(
    name="read_position",
    description="Read current end effector pose",
    category=PrimitiveCategory.SENSING,
    parameters={
        "frame": ParameterDefinition(
            type="string",
            description="Reference frame: 'base' or 'world'",
            required=False,
            default="base"
        ),
    },
    returns="Pose",
    hardware=["arm"],
    blocking=False,
    example="current_pose = read_position()"
))

register_primitive(PrimitiveDefinition(
    name="read_joints",
    description="Read current joint positions",
    category=PrimitiveCategory.SENSING,
    parameters={},
    returns="array",
    hardware=["arm"],
    blocking=False,
    example="joint_positions = read_joints()"
))

register_primitive(PrimitiveDefinition(
    name="read_force",
    description="Read force/torque sensor values",
    category=PrimitiveCategory.SENSING,
    parameters={
        "frame": ParameterDefinition(
            type="string",
            description="Reference frame: 'sensor', 'base', or 'world'",
            required=False,
            default="sensor"
        ),
    },
    returns="array",
    hardware=["force_sensor"],
    blocking=False,
    example="forces = read_force()  # Returns [fx, fy, fz, tx, ty, tz]"
))

register_primitive(PrimitiveDefinition(
    name="read_gripper_state",
    description="Read gripper position and force",
    category=PrimitiveCategory.SENSING,
    parameters={},
    returns="dict",
    hardware=["gripper"],
    blocking=False,
    example="state = read_gripper_state()  # Returns {'position': 0.04, 'force': 5.2, 'object_detected': True}"
))

register_primitive(PrimitiveDefinition(
    name="read_servo_state",
    description="Read state of a single servo",
    category=PrimitiveCategory.SENSING,
    parameters={
        "servo_id": ParameterDefinition(
            type="int",
            description="Servo ID to read",
            required=True
        ),
    },
    returns="dict",
    hardware=["arm"],
    blocking=False,
    example="state = read_servo_state(servo_id=1)"
))

register_primitive(PrimitiveDefinition(
    name="detect_object",
    description="Detect objects in camera view",
    category=PrimitiveCategory.SENSING,
    parameters={
        "object_type": ParameterDefinition(
            type="string",
            description="Type of object to detect (or 'any')",
            required=False,
            default="any"
        ),
        "confidence_threshold": ParameterDefinition(
            type="float",
            description="Minimum detection confidence (0.0-1.0)",
            required=False,
            default=0.7,
            range=(0.0, 1.0)
        ),
    },
    returns="array",
    hardware=["camera"],
    blocking=False,
    example="objects = detect_object(object_type='cube', confidence_threshold=0.8)"
))

register_primitive(PrimitiveDefinition(
    name="get_object_pose",
    description="Get pose of a detected object",
    category=PrimitiveCategory.SENSING,
    parameters={
        "object_id": ParameterDefinition(
            type="string",
            description="ID of detected object",
            required=True
        ),
        "frame": ParameterDefinition(
            type="string",
            description="Reference frame for pose",
            required=False,
            default="base"
        ),
    },
    returns="Pose",
    hardware=["camera"],
    blocking=False,
    example="object_pose = get_object_pose(object_id='cube_1')"
))

# -----------------------------------------------------------------------------
# Wait Primitives
# -----------------------------------------------------------------------------

register_primitive(PrimitiveDefinition(
    name="wait",
    description="Wait for specified duration",
    category=PrimitiveCategory.WAIT,
    parameters={
        "duration": ParameterDefinition(
            type="float",
            description="Wait duration in seconds",
            required=True,
            range=(0.0, 300.0),
            units="seconds"
        ),
    },
    returns="bool",
    hardware=[],
    blocking=True,
    example="wait(duration=2.0)"
))

register_primitive(PrimitiveDefinition(
    name="wait_for_contact",
    description="Wait until force threshold is detected",
    category=PrimitiveCategory.WAIT,
    parameters={
        "force_threshold": ParameterDefinition(
            type="float",
            description="Force threshold in Newtons",
            required=False,
            default=5.0,
            range=(0.1, 100.0),
            units="N"
        ),
        "timeout": ParameterDefinition(
            type="float",
            description="Maximum wait time in seconds",
            required=False,
            default=10.0,
            units="seconds"
        ),
        "direction": ParameterDefinition(
            type="string",
            description="Force direction to monitor: 'any', 'x', 'y', 'z', '-x', '-y', '-z'",
            required=False,
            default="any"
        ),
    },
    returns="bool",
    hardware=["force_sensor"],
    blocking=True,
    timeout_default=10.0,
    example="contact = wait_for_contact(force_threshold=3.0, timeout=5.0)"
))

register_primitive(PrimitiveDefinition(
    name="wait_for_motion_complete",
    description="Wait until current motion is complete",
    category=PrimitiveCategory.WAIT,
    parameters={
        "timeout": ParameterDefinition(
            type="float",
            description="Maximum wait time in seconds",
            required=False,
            default=30.0,
            units="seconds"
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=30.0,
    example="wait_for_motion_complete()"
))

register_primitive(PrimitiveDefinition(
    name="wait_for_gripper",
    description="Wait until gripper motion is complete",
    category=PrimitiveCategory.WAIT,
    parameters={
        "timeout": ParameterDefinition(
            type="float",
            description="Maximum wait time in seconds",
            required=False,
            default=5.0,
            units="seconds"
        ),
    },
    returns="bool",
    hardware=["gripper"],
    blocking=True,
    timeout_default=5.0,
    example="wait_for_gripper()"
))

register_primitive(PrimitiveDefinition(
    name="wait_for_condition",
    description="Wait until a condition is met",
    category=PrimitiveCategory.WAIT,
    parameters={
        "condition": ParameterDefinition(
            type="string",
            description="Condition expression to evaluate",
            required=True
        ),
        "timeout": ParameterDefinition(
            type="float",
            description="Maximum wait time in seconds",
            required=False,
            default=30.0,
            units="seconds"
        ),
        "poll_rate": ParameterDefinition(
            type="float",
            description="Condition check frequency in Hz",
            required=False,
            default=10.0,
            units="Hz"
        ),
    },
    returns="bool",
    hardware=[],
    blocking=True,
    timeout_default=30.0,
    example="wait_for_condition(condition='gripper.object_detected', timeout=10.0)"
))

# -----------------------------------------------------------------------------
# Control Primitives
# -----------------------------------------------------------------------------

register_primitive(PrimitiveDefinition(
    name="set_torque",
    description="Enable or disable servo torque",
    category=PrimitiveCategory.CONTROL,
    parameters={
        "enabled": ParameterDefinition(
            type="bool",
            description="Enable (True) or disable (False) torque",
            required=True
        ),
        "servo_ids": ParameterDefinition(
            type="array",
            description="List of servo IDs (empty for all)",
            required=False,
            default=[]
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=False,
    example="set_torque(enabled=False)  # Disable all servos"
))

register_primitive(PrimitiveDefinition(
    name="set_compliance",
    description="Set servo compliance/stiffness mode",
    category=PrimitiveCategory.CONTROL,
    parameters={
        "mode": ParameterDefinition(
            type="string",
            description="Compliance mode: 'stiff', 'soft', 'free'",
            required=True
        ),
        "servo_ids": ParameterDefinition(
            type="array",
            description="List of servo IDs (empty for all)",
            required=False,
            default=[]
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=False,
    example="set_compliance(mode='soft', servo_ids=[1, 2, 3])"
))

register_primitive(PrimitiveDefinition(
    name="set_speed_limit",
    description="Set maximum speed for subsequent motions",
    category=PrimitiveCategory.CONTROL,
    parameters={
        "max_speed": ParameterDefinition(
            type="float",
            description="Maximum speed as fraction of absolute max (0.0-1.0)",
            required=True,
            range=(0.0, 1.0)
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=False,
    example="set_speed_limit(max_speed=0.3)"
))

register_primitive(PrimitiveDefinition(
    name="stop",
    description="Immediately stop all motion",
    category=PrimitiveCategory.CONTROL,
    parameters={
        "deceleration": ParameterDefinition(
            type="float",
            description="Deceleration rate (0.0=instant, 1.0=smooth)",
            required=False,
            default=0.5,
            range=(0.0, 1.0)
        ),
    },
    returns="bool",
    hardware=["arm"],
    blocking=True,
    timeout_default=2.0,
    example="stop(deceleration=0.0)  # Emergency stop"
))

register_primitive(PrimitiveDefinition(
    name="enable_force_control",
    description="Enable force control mode",
    category=PrimitiveCategory.CONTROL,
    parameters={
        "target_force": ParameterDefinition(
            type="array",
            description="Target force/torque [fx, fy, fz, tx, ty, tz]",
            required=True
        ),
        "stiffness": ParameterDefinition(
            type="array",
            description="Stiffness for each axis",
            required=False,
            default=[1000, 1000, 1000, 100, 100, 100]
        ),
    },
    returns="bool",
    hardware=["arm", "force_sensor"],
    blocking=False,
    example="enable_force_control(target_force=[0, 0, -10, 0, 0, 0])"
))

register_primitive(PrimitiveDefinition(
    name="disable_force_control",
    description="Disable force control mode",
    category=PrimitiveCategory.CONTROL,
    parameters={},
    returns="bool",
    hardware=["arm"],
    blocking=False,
    example="disable_force_control()"
))


# =============================================================================
# REGISTRY FUNCTIONS
# =============================================================================

def get_primitive(name: str) -> Optional[PrimitiveDefinition]:
    """Get a primitive definition by name."""
    return PRIMITIVE_REGISTRY.get(name)


def list_primitives(
    category: Optional[PrimitiveCategory] = None,
    hardware: Optional[str] = None
) -> List[PrimitiveDefinition]:
    """
    List all primitives, optionally filtered by category or hardware.

    Args:
        category: Filter by primitive category
        hardware: Filter by required hardware type

    Returns:
        List of matching primitive definitions
    """
    primitives = list(PRIMITIVE_REGISTRY.values())

    if category:
        primitives = [p for p in primitives if p.category == category]

    if hardware:
        primitives = [p for p in primitives if hardware in p.hardware]

    return primitives


def get_primitive_names() -> List[str]:
    """Get all registered primitive names."""
    return list(PRIMITIVE_REGISTRY.keys())


def validate_primitive_chain(primitives: List[str]) -> List[str]:
    """
    Validate a chain of primitives for a skill.

    Checks that:
    - All primitives exist
    - Hardware requirements are consistent
    - No obvious sequencing issues

    Args:
        primitives: List of primitive names

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check all primitives exist
    for name in primitives:
        if name not in PRIMITIVE_REGISTRY:
            errors.append(f"Unknown primitive: {name}")

    if errors:
        return errors

    # Collect hardware requirements
    all_hardware: Set[str] = set()
    for name in primitives:
        prim = PRIMITIVE_REGISTRY[name]
        all_hardware.update(prim.hardware)

    # Check for common issues
    prim_sequence = [PRIMITIVE_REGISTRY[name] for name in primitives]

    # Warn if force sensing used without force sensor
    uses_force = any(
        "force_sensor" in p.hardware or "force" in p.name.lower()
        for p in prim_sequence
    )
    has_force_sensor = "force_sensor" in all_hardware
    if uses_force and not has_force_sensor:
        errors.append(
            "Skill uses force-related primitives but no force_sensor "
            "in hardware requirements"
        )

    # Warn if gripper used without gripper hardware
    uses_gripper = any("gripper" in p.hardware for p in prim_sequence)
    has_gripper = "gripper" in all_hardware
    if uses_gripper and not has_gripper:
        errors.append(
            "Skill uses gripper primitives but no gripper "
            "in hardware requirements"
        )

    return errors


def get_required_hardware(primitives: List[str]) -> Set[str]:
    """
    Get the set of all hardware required by a list of primitives.

    Args:
        primitives: List of primitive names

    Returns:
        Set of required hardware types
    """
    hardware: Set[str] = set()
    for name in primitives:
        prim = PRIMITIVE_REGISTRY.get(name)
        if prim:
            hardware.update(prim.hardware)
    return hardware


def get_primitives_by_hardware(hardware: str) -> List[PrimitiveDefinition]:
    """Get all primitives that require specific hardware."""
    return [
        p for p in PRIMITIVE_REGISTRY.values()
        if hardware in p.hardware
    ]


def format_primitive_docs(name: str) -> str:
    """Format documentation for a primitive."""
    prim = PRIMITIVE_REGISTRY.get(name)
    if not prim:
        return f"Unknown primitive: {name}"

    lines = [
        f"## {prim.name}",
        "",
        f"{prim.description}",
        "",
        f"**Category:** {prim.category.value}",
        f"**Hardware:** {', '.join(prim.hardware) or 'None'}",
        f"**Blocking:** {'Yes' if prim.blocking else 'No'}",
        "",
        "### Signature",
        f"```python",
        f"{prim.get_signature()}",
        f"```",
        "",
        "### Parameters",
    ]

    for param_name, param_def in prim.parameters.items():
        required = "(required)" if param_def.required else "(optional)"
        default = f" = {param_def.default}" if param_def.default is not None else ""
        lines.append(f"- **{param_name}** `{param_def.type}` {required}{default}")
        lines.append(f"  - {param_def.description}")
        if param_def.range:
            lines.append(f"  - Range: {param_def.range}")
        if param_def.units:
            lines.append(f"  - Units: {param_def.units}")

    if prim.example:
        lines.extend([
            "",
            "### Example",
            f"```python",
            f"{prim.example}",
            f"```",
        ])

    return "\n".join(lines)


# Export commonly used items
__all__ = [
    "PrimitiveCategory",
    "ParameterDefinition",
    "PrimitiveDefinition",
    "PRIMITIVE_REGISTRY",
    "get_primitive",
    "list_primitives",
    "get_primitive_names",
    "validate_primitive_chain",
    "get_required_hardware",
    "get_primitives_by_hardware",
    "format_primitive_docs",
    "register_primitive",
]
