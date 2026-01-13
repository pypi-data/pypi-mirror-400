"""
Compatibility Checker - Verify skill compatibility with robots.

This module checks whether a skill can run on a given robot by:
- Comparing hardware requirements vs robot capabilities
- Identifying potential issues and their severity
- Suggesting adaptations to make incompatible skills work
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .skill_schema import SkillSpecification, HardwareRequirement
from .generators.hardware_config import URDFInfo, parse_urdf, ATEConfig


class IssueSeverity(str, Enum):
    """Severity levels for compatibility issues."""
    INFO = "info"  # Informational, no action needed
    WARNING = "warning"  # May work but with limitations
    ERROR = "error"  # Will not work without changes
    CRITICAL = "critical"  # Fundamentally incompatible


class AdaptationType(str, Enum):
    """Types of adaptations to make skills compatible."""
    IK_CONSTRAINT = "ik_constraint"  # Lock or limit certain joints
    SPEED_LIMIT = "speed_limit"  # Reduce maximum speed
    WORKSPACE_LIMIT = "workspace_limit"  # Limit operational workspace
    FORCE_LIMIT = "force_limit"  # Reduce force limits
    TRAJECTORY_REMAP = "trajectory_remap"  # Remap joint trajectories
    GRIPPER_ADAPT = "gripper_adapt"  # Adapt gripper behavior
    SENSOR_SUBSTITUTE = "sensor_substitute"  # Use alternative sensor


@dataclass
class CompatibilityIssue:
    """A single compatibility issue between skill and robot."""
    severity: IssueSeverity
    category: str  # e.g., "hardware", "kinematics", "safety"
    message: str
    details: Optional[str] = None
    mitigation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "details": self.details,
            "mitigation": self.mitigation,
        }


@dataclass
class Adaptation:
    """An adaptation to make a skill compatible with a robot."""
    type: AdaptationType
    description: str
    config: Dict[str, Any] = field(default_factory=dict)
    automated: bool = False  # Can this be automatically applied?

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "description": self.description,
            "config": self.config,
            "automated": self.automated,
        }


@dataclass
class CompatibilityReport:
    """Complete compatibility report between a skill and robot."""
    skill_name: str
    robot_name: str
    compatible: bool
    score: float  # 0.0 to 1.0 compatibility score
    issues: List[CompatibilityIssue] = field(default_factory=list)
    adaptations: List[Adaptation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "robot_name": self.robot_name,
            "compatible": self.compatible,
            "score": self.score,
            "issues": [i.to_dict() for i in self.issues],
            "adaptations": [a.to_dict() for a in self.adaptations],
        }

    def __str__(self) -> str:
        status = "COMPATIBLE" if self.compatible else "INCOMPATIBLE"
        lines = [
            f"Compatibility Report: {self.skill_name} -> {self.robot_name}",
            f"Status: {status} (Score: {self.score:.1%})",
            "",
        ]

        if self.issues:
            lines.append("Issues:")
            for issue in self.issues:
                severity_icon = {
                    IssueSeverity.INFO: "ℹ️",
                    IssueSeverity.WARNING: "⚠️",
                    IssueSeverity.ERROR: "❌",
                    IssueSeverity.CRITICAL: "🚫",
                }.get(issue.severity, "•")
                lines.append(f"  {severity_icon} [{issue.category}] {issue.message}")
                if issue.mitigation:
                    lines.append(f"      Mitigation: {issue.mitigation}")

        if self.adaptations:
            lines.append("")
            lines.append("Suggested Adaptations:")
            for adapt in self.adaptations:
                auto = " (automatic)" if adapt.automated else ""
                lines.append(f"  • {adapt.description}{auto}")

        return "\n".join(lines)


@dataclass
class RobotProfile:
    """Profile describing a robot's capabilities."""
    name: str
    urdf_info: Optional[URDFInfo] = None
    ate_config: Optional[ATEConfig] = None

    # Hardware capabilities
    arm_dof: int = 0
    has_gripper: bool = False
    gripper_type: Optional[str] = None
    has_force_sensor: bool = False
    has_camera: bool = False
    has_mobile_base: bool = False

    # Kinematic properties
    max_reach: Optional[float] = None  # meters
    payload: Optional[float] = None  # kg
    workspace_bounds: Optional[Dict[str, Tuple[float, float]]] = None

    # Performance limits
    max_joint_velocity: Optional[float] = None  # rad/s
    max_cartesian_velocity: Optional[float] = None  # m/s
    max_force: Optional[float] = None  # N

    @classmethod
    def from_urdf(cls, urdf_path: str, name: Optional[str] = None) -> "RobotProfile":
        """Create a robot profile from URDF file."""
        urdf_info = parse_urdf(urdf_path)

        profile = cls(
            name=name or urdf_info.name,
            urdf_info=urdf_info,
            arm_dof=urdf_info.dof,
        )

        # Detect gripper from joint names
        gripper_joints = [
            j for j in urdf_info.movable_joints
            if any(kw in j.name.lower() for kw in ["gripper", "finger", "hand"])
        ]
        if gripper_joints:
            profile.has_gripper = True
            profile.gripper_type = "parallel"  # Default assumption

        # Extract velocity limits
        velocities = [
            j.velocity_limit for j in urdf_info.movable_joints
            if j.velocity_limit is not None
        ]
        if velocities:
            profile.max_joint_velocity = min(velocities)

        return profile

    @classmethod
    def from_ate_dir(cls, ate_dir: str, name: Optional[str] = None) -> "RobotProfile":
        """Create a robot profile from ATE configuration directory."""
        ate_config = ATEConfig.from_directory(ate_dir)

        profile = cls(
            name=name or Path(ate_dir).name,
            ate_config=ate_config,
            arm_dof=len(ate_config.servo_map),
        )

        # Detect gripper (typically last servo or specific IDs)
        if ate_config.servo_map:
            max_id = max(ate_config.servo_map.keys())
            # Heuristic: if there's a servo with different characteristics, it might be gripper
            profile.has_gripper = True

        return profile


class CompatibilityChecker:
    """
    Check compatibility between a skill and a robot.

    Performs comprehensive checks including:
    - Hardware requirements
    - Kinematic constraints
    - Safety limits
    - Sensor requirements
    """

    def __init__(self, spec: SkillSpecification, robot: RobotProfile):
        """
        Initialize the checker.

        Args:
            spec: Skill specification to check
            robot: Robot profile to check against
        """
        self.spec = spec
        self.robot = robot
        self.issues: List[CompatibilityIssue] = []
        self.adaptations: List[Adaptation] = []

    def check(self) -> CompatibilityReport:
        """
        Perform all compatibility checks.

        Returns:
            CompatibilityReport with results
        """
        self.issues = []
        self.adaptations = []

        # Run all checks
        self._check_hardware_requirements()
        self._check_kinematic_requirements()
        self._check_safety_requirements()
        self._check_primitive_support()

        # Calculate compatibility
        compatible, score = self._calculate_compatibility()

        return CompatibilityReport(
            skill_name=self.spec.name,
            robot_name=self.robot.name,
            compatible=compatible,
            score=score,
            issues=self.issues,
            adaptations=self.adaptations,
        )

    def _check_hardware_requirements(self) -> None:
        """Check hardware requirements against robot capabilities."""
        for req in self.spec.hardware_requirements:
            if req.component_type == "arm":
                self._check_arm_requirement(req)
            elif req.component_type == "gripper":
                self._check_gripper_requirement(req)
            elif req.component_type == "force_sensor":
                self._check_force_sensor_requirement(req)
            elif req.component_type == "camera":
                self._check_camera_requirement(req)
            elif req.component_type == "mobile_base":
                self._check_mobile_base_requirement(req)

    def _check_arm_requirement(self, req: HardwareRequirement) -> None:
        """Check arm hardware requirements."""
        # Check DOF
        required_dof = req.constraints.get("dof")
        if required_dof:
            # Parse requirement like ">=6" or "6"
            if isinstance(required_dof, str):
                if required_dof.startswith(">="):
                    min_dof = int(required_dof[2:])
                    if self.robot.arm_dof < min_dof:
                        self.issues.append(CompatibilityIssue(
                            severity=IssueSeverity.ERROR,
                            category="hardware",
                            message=f"Robot has {self.robot.arm_dof} DOF, skill requires >= {min_dof}",
                            mitigation="Consider using a different skill or robot"
                        ))
                    elif self.robot.arm_dof > min_dof:
                        # More DOF than needed - just informational
                        self.issues.append(CompatibilityIssue(
                            severity=IssueSeverity.INFO,
                            category="hardware",
                            message=f"Robot has {self.robot.arm_dof} DOF, skill designed for {min_dof}+",
                            details="Extra DOF may provide redundancy"
                        ))
            elif isinstance(required_dof, int):
                if self.robot.arm_dof < required_dof:
                    diff = required_dof - self.robot.arm_dof
                    severity = IssueSeverity.ERROR if diff > 1 else IssueSeverity.WARNING
                    self.issues.append(CompatibilityIssue(
                        severity=severity,
                        category="hardware",
                        message=f"Robot has {self.robot.arm_dof} DOF, skill designed for {required_dof}",
                        mitigation="Reduced workspace, may not reach all poses" if diff == 1 else None
                    ))
                    if diff == 1:
                        self.adaptations.append(Adaptation(
                            type=AdaptationType.IK_CONSTRAINT,
                            description="Lock one joint to compensate for missing DOF",
                            config={"fixed_joints": [], "note": "Auto-detect best joint to lock"},
                            automated=True
                        ))

        # Check payload
        required_payload = req.constraints.get("payload")
        if required_payload and self.robot.payload:
            # Parse ">=1kg" format
            if isinstance(required_payload, str):
                required_payload = required_payload.replace("kg", "").replace(">=", "")
                try:
                    required_payload = float(required_payload)
                except ValueError:
                    pass

            if isinstance(required_payload, (int, float)):
                if self.robot.payload < required_payload:
                    self.issues.append(CompatibilityIssue(
                        severity=IssueSeverity.WARNING,
                        category="hardware",
                        message=f"Robot payload ({self.robot.payload}kg) may be insufficient ({required_payload}kg required)",
                        mitigation="Reduce object weight or use slower movements"
                    ))
                    self.adaptations.append(Adaptation(
                        type=AdaptationType.SPEED_LIMIT,
                        description="Reduce speed to compensate for payload limit",
                        config={"max_speed_factor": self.robot.payload / required_payload},
                        automated=True
                    ))

    def _check_gripper_requirement(self, req: HardwareRequirement) -> None:
        """Check gripper hardware requirements."""
        if not self.robot.has_gripper:
            self.issues.append(CompatibilityIssue(
                severity=IssueSeverity.ERROR,
                category="hardware",
                message="Skill requires gripper but robot does not have one",
                mitigation="Add a gripper to the robot"
            ))
            return

        # Check gripper type
        required_type = req.constraints.get("type")
        if required_type and self.robot.gripper_type:
            if required_type != self.robot.gripper_type:
                self.issues.append(CompatibilityIssue(
                    severity=IssueSeverity.WARNING,
                    category="hardware",
                    message=f"Skill expects {required_type} gripper, robot has {self.robot.gripper_type}",
                    mitigation="Gripper behavior may need adaptation"
                ))
                self.adaptations.append(Adaptation(
                    type=AdaptationType.GRIPPER_ADAPT,
                    description=f"Adapt gripper commands from {required_type} to {self.robot.gripper_type}",
                    config={"source_type": required_type, "target_type": self.robot.gripper_type},
                    automated=True
                ))

    def _check_force_sensor_requirement(self, req: HardwareRequirement) -> None:
        """Check force sensor requirements."""
        if not self.robot.has_force_sensor:
            if req.optional:
                self.issues.append(CompatibilityIssue(
                    severity=IssueSeverity.WARNING,
                    category="hardware",
                    message="Skill can use force sensor but robot does not have one",
                    details="Force-based features will be disabled"
                ))
            else:
                self.issues.append(CompatibilityIssue(
                    severity=IssueSeverity.ERROR,
                    category="hardware",
                    message="Skill requires force sensor but robot does not have one",
                    mitigation="Consider using position-based control instead"
                ))
                self.adaptations.append(Adaptation(
                    type=AdaptationType.SENSOR_SUBSTITUTE,
                    description="Use current-based force estimation instead of F/T sensor",
                    config={"method": "current_estimation"},
                    automated=False
                ))

    def _check_camera_requirement(self, req: HardwareRequirement) -> None:
        """Check camera requirements."""
        if not self.robot.has_camera:
            self.issues.append(CompatibilityIssue(
                severity=IssueSeverity.ERROR if not req.optional else IssueSeverity.WARNING,
                category="hardware",
                message="Skill requires camera but robot does not have one",
                mitigation="Add a camera to the robot or provide pre-computed poses"
            ))

    def _check_mobile_base_requirement(self, req: HardwareRequirement) -> None:
        """Check mobile base requirements."""
        if not self.robot.has_mobile_base:
            self.issues.append(CompatibilityIssue(
                severity=IssueSeverity.ERROR,
                category="hardware",
                message="Skill requires mobile base but robot is stationary",
                mitigation="Skill cannot be executed on stationary robot"
            ))

    def _check_kinematic_requirements(self) -> None:
        """Check kinematic constraints and workspace."""
        # Check workspace bounds
        if self.spec.workspace_bounds and self.robot.workspace_bounds:
            for axis in ["x", "y", "z"]:
                if axis in self.spec.workspace_bounds and axis in self.robot.workspace_bounds:
                    skill_min, skill_max = self.spec.workspace_bounds[axis]
                    robot_min, robot_max = self.robot.workspace_bounds[axis]

                    if skill_min < robot_min or skill_max > robot_max:
                        self.issues.append(CompatibilityIssue(
                            severity=IssueSeverity.WARNING,
                            category="kinematics",
                            message=f"Skill workspace ({axis}: {skill_min} to {skill_max}) "
                                    f"exceeds robot workspace ({robot_min} to {robot_max})",
                            mitigation=f"Limit {axis} axis to robot range"
                        ))
                        self.adaptations.append(Adaptation(
                            type=AdaptationType.WORKSPACE_LIMIT,
                            description=f"Limit {axis} workspace to robot capability",
                            config={
                                "axis": axis,
                                "min": max(skill_min, robot_min),
                                "max": min(skill_max, robot_max)
                            },
                            automated=True
                        ))

    def _check_safety_requirements(self) -> None:
        """Check safety-related constraints."""
        # Check velocity limits
        if self.spec.max_velocity and self.robot.max_cartesian_velocity:
            if self.spec.max_velocity > self.robot.max_cartesian_velocity:
                self.issues.append(CompatibilityIssue(
                    severity=IssueSeverity.WARNING,
                    category="safety",
                    message=f"Skill max velocity ({self.spec.max_velocity}m/s) "
                            f"exceeds robot limit ({self.robot.max_cartesian_velocity}m/s)",
                    mitigation="Skill will run at reduced speed"
                ))
                self.adaptations.append(Adaptation(
                    type=AdaptationType.SPEED_LIMIT,
                    description="Cap velocity to robot maximum",
                    config={"max_velocity": self.robot.max_cartesian_velocity},
                    automated=True
                ))

        # Check force limits
        if self.spec.max_force and self.robot.max_force:
            if self.spec.max_force > self.robot.max_force:
                self.issues.append(CompatibilityIssue(
                    severity=IssueSeverity.WARNING,
                    category="safety",
                    message=f"Skill max force ({self.spec.max_force}N) "
                            f"exceeds robot limit ({self.robot.max_force}N)",
                    mitigation="Force-limited operations may fail"
                ))
                self.adaptations.append(Adaptation(
                    type=AdaptationType.FORCE_LIMIT,
                    description="Cap force commands to robot maximum",
                    config={"max_force": self.robot.max_force},
                    automated=True
                ))

    def _check_primitive_support(self) -> None:
        """Check if robot can execute required primitives."""
        from .primitives import PRIMITIVE_REGISTRY, get_required_hardware

        # Get hardware required by all primitives
        required_hardware = get_required_hardware(self.spec.primitives)

        # Check each required hardware type
        hardware_map = {
            "arm": self.robot.arm_dof > 0,
            "gripper": self.robot.has_gripper,
            "force_sensor": self.robot.has_force_sensor,
            "camera": self.robot.has_camera,
            "mobile_base": self.robot.has_mobile_base,
        }

        for hw in required_hardware:
            if hw in hardware_map and not hardware_map.get(hw, False):
                # Find which primitives need this hardware
                prims_needing_hw = [
                    p for p in self.spec.primitives
                    if p in PRIMITIVE_REGISTRY and hw in PRIMITIVE_REGISTRY[p].hardware
                ]
                self.issues.append(CompatibilityIssue(
                    severity=IssueSeverity.ERROR,
                    category="primitives",
                    message=f"Primitives {prims_needing_hw} require {hw} which robot lacks",
                    details=f"Missing hardware: {hw}"
                ))

    def _calculate_compatibility(self) -> Tuple[bool, float]:
        """
        Calculate overall compatibility score.

        Returns:
            Tuple of (is_compatible, score)
        """
        # Weight by severity
        severity_weights = {
            IssueSeverity.INFO: 0,
            IssueSeverity.WARNING: 0.1,
            IssueSeverity.ERROR: 0.4,
            IssueSeverity.CRITICAL: 1.0,
        }

        total_penalty = sum(
            severity_weights.get(issue.severity, 0)
            for issue in self.issues
        )

        # Cap penalty at 1.0
        score = max(0.0, 1.0 - min(1.0, total_penalty))

        # Not compatible if any critical or error issues without mitigation
        has_blocking = any(
            issue.severity in (IssueSeverity.CRITICAL, IssueSeverity.ERROR)
            and not issue.mitigation
            for issue in self.issues
        )

        compatible = not has_blocking and score >= 0.5

        return compatible, score


def check_compatibility(
    spec: SkillSpecification,
    robot: RobotProfile,
) -> CompatibilityReport:
    """
    Convenience function to check skill-robot compatibility.

    Args:
        spec: Skill specification
        robot: Robot profile

    Returns:
        CompatibilityReport with results
    """
    checker = CompatibilityChecker(spec, robot)
    return checker.check()


def check_compatibility_from_paths(
    skill_yaml: str,
    robot_urdf: Optional[str] = None,
    robot_ate_dir: Optional[str] = None,
    robot_name: Optional[str] = None,
) -> CompatibilityReport:
    """
    Check compatibility from file paths.

    Args:
        skill_yaml: Path to skill.yaml
        robot_urdf: Path to robot URDF (optional)
        robot_ate_dir: Path to ATE config directory (optional)
        robot_name: Name for the robot profile

    Returns:
        CompatibilityReport with results
    """
    spec = SkillSpecification.from_yaml(skill_yaml)

    if robot_urdf:
        robot = RobotProfile.from_urdf(robot_urdf, robot_name)
    elif robot_ate_dir:
        robot = RobotProfile.from_ate_dir(robot_ate_dir, robot_name)
    else:
        robot = RobotProfile(name=robot_name or "unknown")

    return check_compatibility(spec, robot)
