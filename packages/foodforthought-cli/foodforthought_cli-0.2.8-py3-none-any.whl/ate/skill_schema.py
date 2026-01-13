"""
Skill Schema - Data classes for skill specifications.

This module defines the complete schema for robot skill specifications,
which are the input to the Skill Compiler.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import yaml


class ParameterType(str, Enum):
    """Supported parameter types for skill definitions."""
    POSE = "Pose"
    FLOAT = "float"
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    ARRAY = "array"
    JOINT_STATE = "JointState"
    TRAJECTORY = "Trajectory"
    POINT = "Point"
    QUATERNION = "Quaternion"
    TRANSFORM = "Transform"


class HardwareType(str, Enum):
    """Types of hardware components."""
    ARM = "arm"
    GRIPPER = "gripper"
    MOBILE_BASE = "mobile_base"
    SENSOR = "sensor"
    CAMERA = "camera"
    FORCE_SENSOR = "force_sensor"
    LIDAR = "lidar"
    IMU = "imu"


class ComparisonOperator(str, Enum):
    """Operators for hardware constraints."""
    EQ = "=="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="


@dataclass
class SkillParameter:
    """
    Definition of a skill parameter.

    Parameters define the inputs a skill accepts, their types,
    defaults, and constraints.
    """
    name: str
    type: str  # ParameterType value as string
    description: str
    default: Optional[Any] = None
    range: Optional[Tuple[Any, Any]] = None
    required: bool = True
    units: Optional[str] = None  # e.g., "meters", "radians", "newtons"

    def validate_value(self, value: Any) -> List[str]:
        """Validate a value against this parameter's constraints."""
        errors = []

        if value is None:
            if self.required and self.default is None:
                errors.append(f"Parameter '{self.name}' is required but not provided")
            return errors

        # Type validation
        type_validators = {
            "float": lambda v: isinstance(v, (int, float)),
            "int": lambda v: isinstance(v, int),
            "bool": lambda v: isinstance(v, bool),
            "string": lambda v: isinstance(v, str),
            "array": lambda v: isinstance(v, (list, tuple)),
            "Pose": lambda v: isinstance(v, dict) and all(
                k in v for k in ["position", "orientation"]
            ),
        }

        validator = type_validators.get(self.type)
        if validator and not validator(value):
            errors.append(
                f"Parameter '{self.name}' expected type {self.type}, "
                f"got {type(value).__name__}"
            )

        # Range validation
        if self.range and isinstance(value, (int, float)):
            min_val, max_val = self.range
            if value < min_val or value > max_val:
                errors.append(
                    f"Parameter '{self.name}' value {value} out of range "
                    f"[{min_val}, {max_val}]"
                )

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = {
            "type": self.type,
            "description": self.description,
        }
        if self.default is not None:
            d["default"] = self.default
        if self.range is not None:
            d["range"] = list(self.range)
        if not self.required:
            d["required"] = False
        if self.units:
            d["units"] = self.units
        return d

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "SkillParameter":
        """Create from dictionary representation."""
        range_val = data.get("range")
        if range_val:
            range_val = tuple(range_val)

        return cls(
            name=name,
            type=data["type"],
            description=data.get("description", ""),
            default=data.get("default"),
            range=range_val,
            required=data.get("required", True),
            units=data.get("units"),
        )


@dataclass
class HardwareConstraint:
    """A single constraint on hardware (e.g., dof >= 6)."""
    property: str
    operator: str  # ComparisonOperator value
    value: Any

    def evaluate(self, actual_value: Any) -> bool:
        """Evaluate this constraint against an actual value."""
        ops = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
        }

        # Handle string comparison operators like ">=6"
        op = self.operator
        if op not in ops:
            # Try to parse from value string like ">=6"
            if isinstance(self.value, str):
                for test_op in [">=", "<=", "!=", "==", ">", "<"]:
                    if self.value.startswith(test_op):
                        op = test_op
                        self.value = self._parse_value(self.value[len(test_op):])
                        break

        op_func = ops.get(op, ops["=="])
        try:
            return op_func(actual_value, self.value)
        except TypeError:
            return False

    def _parse_value(self, val_str: str) -> Any:
        """Parse a value string to appropriate type."""
        val_str = val_str.strip()
        # Try int
        try:
            return int(val_str)
        except ValueError:
            pass
        # Try float
        try:
            return float(val_str)
        except ValueError:
            pass
        # Return as string
        return val_str


@dataclass
class HardwareRequirement:
    """
    Hardware requirement for a skill.

    Defines what hardware components a skill needs and their constraints.
    """
    component_type: str  # HardwareType value as string
    constraints: Dict[str, Any] = field(default_factory=dict)
    optional: bool = False

    def get_constraints(self) -> List[HardwareConstraint]:
        """Parse constraints into HardwareConstraint objects."""
        result = []
        for prop, value in self.constraints.items():
            if isinstance(value, str) and any(
                value.startswith(op) for op in [">=", "<=", "!=", "==", ">", "<"]
            ):
                # Parse operator from value
                for op in [">=", "<=", "!=", "==", ">", "<"]:
                    if value.startswith(op):
                        result.append(HardwareConstraint(
                            property=prop,
                            operator=op,
                            value=value[len(op):].strip()
                        ))
                        break
            else:
                # Equality constraint
                result.append(HardwareConstraint(
                    property=prop,
                    operator="==",
                    value=value
                ))
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {self.component_type: self.constraints}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HardwareRequirement":
        """Create from dictionary representation."""
        # Handle format: {"arm": {"dof": ">=6"}}
        if len(data) == 1:
            component_type = list(data.keys())[0]
            constraints = data[component_type]
            if isinstance(constraints, dict):
                return cls(
                    component_type=component_type,
                    constraints=constraints
                )

        # Handle format: {"component_type": "arm", "constraints": {...}}
        return cls(
            component_type=data.get("component_type", "unknown"),
            constraints=data.get("constraints", {}),
            optional=data.get("optional", False)
        )


@dataclass
class SuccessCriterion:
    """
    Success criterion for skill completion.

    Defines how to determine if a skill has succeeded.
    """
    name: str
    condition: str  # Condition expression
    tolerance: Optional[float] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = {"condition": self.condition}
        if self.tolerance is not None:
            d["tolerance"] = self.tolerance
        if self.description:
            d["description"] = self.description
        return d

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "SuccessCriterion":
        """Create from dictionary representation."""
        if isinstance(data, str):
            # Simple format: "object_at_place_pose"
            return cls(name=name, condition=data)

        return cls(
            name=name,
            condition=data.get("condition", ""),
            tolerance=data.get("tolerance"),
            description=data.get("description")
        )


@dataclass
class PrimitiveCall:
    """
    A call to a primitive within a skill's execution flow.
    """
    primitive: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None  # Optional condition to execute
    on_failure: Optional[str] = None  # Action on failure: "abort", "retry", "continue"
    retries: int = 0


@dataclass
class SkillSpecification:
    """
    Complete specification for a robot skill.

    This is the main data structure that the Skill Compiler uses
    to generate deployable skill packages.
    """
    name: str
    version: str
    description: str
    parameters: List[SkillParameter]
    primitives: List[str]  # List of primitive names used
    hardware_requirements: List[HardwareRequirement]
    success_criteria: List[SuccessCriterion]

    # Optional fields
    author: Optional[str] = None
    license: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Other skills
    execution_flow: List[PrimitiveCall] = field(default_factory=list)

    # Safety constraints
    max_velocity: Optional[float] = None  # m/s
    max_force: Optional[float] = None  # N
    workspace_bounds: Optional[Dict[str, Tuple[float, float]]] = None

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "SkillSpecification":
        """Load skill specification from YAML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Skill specification not found: {path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillSpecification":
        """Create skill specification from dictionary."""
        # Parse parameters
        parameters = []
        params_data = data.get("parameters", {})
        for name, param_data in params_data.items():
            parameters.append(SkillParameter.from_dict(name, param_data))

        # Parse hardware requirements
        hardware_requirements = []
        hw_data = data.get("hardware_requirements", [])
        for hw in hw_data:
            hardware_requirements.append(HardwareRequirement.from_dict(hw))

        # Parse success criteria
        success_criteria = []
        criteria_data = data.get("success_criteria", {})
        for name, criterion_data in criteria_data.items():
            success_criteria.append(SuccessCriterion.from_dict(name, criterion_data))

        # Parse execution flow
        execution_flow = []
        flow_data = data.get("execution_flow", [])
        for step in flow_data:
            if isinstance(step, str):
                execution_flow.append(PrimitiveCall(primitive=step))
            else:
                execution_flow.append(PrimitiveCall(
                    primitive=step.get("primitive", ""),
                    parameters=step.get("parameters", {}),
                    condition=step.get("condition"),
                    on_failure=step.get("on_failure"),
                    retries=step.get("retries", 0)
                ))

        # Parse workspace bounds
        workspace_bounds = None
        if "workspace_bounds" in data:
            wb = data["workspace_bounds"]
            workspace_bounds = {
                axis: tuple(bounds) for axis, bounds in wb.items()
            }

        return cls(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            parameters=parameters,
            primitives=data.get("primitives", []),
            hardware_requirements=hardware_requirements,
            success_criteria=success_criteria,
            author=data.get("author"),
            license=data.get("license"),
            category=data.get("category"),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            execution_flow=execution_flow,
            max_velocity=data.get("max_velocity"),
            max_force=data.get("max_force"),
            workspace_bounds=workspace_bounds,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        d = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "parameters": {p.name: p.to_dict() for p in self.parameters},
            "primitives": self.primitives,
            "hardware_requirements": [hr.to_dict() for hr in self.hardware_requirements],
            "success_criteria": {sc.name: sc.to_dict() for sc in self.success_criteria},
        }

        if self.author:
            d["author"] = self.author
        if self.license:
            d["license"] = self.license
        if self.category:
            d["category"] = self.category
        if self.tags:
            d["tags"] = self.tags
        if self.dependencies:
            d["dependencies"] = self.dependencies
        if self.execution_flow:
            d["execution_flow"] = [
                {
                    "primitive": pc.primitive,
                    "parameters": pc.parameters,
                    "condition": pc.condition,
                    "on_failure": pc.on_failure,
                    "retries": pc.retries
                } if pc.parameters or pc.condition else pc.primitive
                for pc in self.execution_flow
            ]
        if self.max_velocity:
            d["max_velocity"] = self.max_velocity
        if self.max_force:
            d["max_force"] = self.max_force
        if self.workspace_bounds:
            d["workspace_bounds"] = {
                k: list(v) for k, v in self.workspace_bounds.items()
            }

        return d

    def to_yaml(self, path: Union[str, Path]) -> None:
        """Save skill specification to YAML file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    def validate(self) -> List[str]:
        """
        Validate the skill specification.

        Returns a list of validation errors, or empty list if valid.
        """
        errors = []

        # Name validation
        if not self.name:
            errors.append("Skill name cannot be empty")
        elif not self.name.replace("_", "").replace("-", "").isalnum():
            errors.append(
                f"Skill name '{self.name}' contains invalid characters. "
                "Use only alphanumeric characters, underscores, and hyphens."
            )

        # Version validation
        if not self.version:
            errors.append("Version cannot be empty")
        else:
            # Simple semver check
            parts = self.version.split(".")
            if len(parts) != 3:
                errors.append(
                    f"Version '{self.version}' should be in semver format (x.y.z)"
                )

        # Parameters validation
        param_names = set()
        for param in self.parameters:
            if param.name in param_names:
                errors.append(f"Duplicate parameter name: {param.name}")
            param_names.add(param.name)

            if not param.type:
                errors.append(f"Parameter '{param.name}' missing type")

        # Primitives validation
        if not self.primitives:
            errors.append("At least one primitive is required")

        # Hardware requirements validation
        if not self.hardware_requirements:
            errors.append("At least one hardware requirement is required")

        # Success criteria validation
        if not self.success_criteria:
            errors.append("At least one success criterion is required")

        return errors

    def get_parameter(self, name: str) -> Optional[SkillParameter]:
        """Get a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def get_required_hardware_types(self) -> List[str]:
        """Get list of required hardware component types."""
        return [
            req.component_type
            for req in self.hardware_requirements
            if not req.optional
        ]

    def __repr__(self) -> str:
        return (
            f"SkillSpecification(name='{self.name}', version='{self.version}', "
            f"primitives={self.primitives}, "
            f"parameters={[p.name for p in self.parameters]})"
        )


# Convenience type aliases
SkillSpec = SkillSpecification
Param = SkillParameter
HWReq = HardwareRequirement
