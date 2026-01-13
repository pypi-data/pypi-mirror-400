"""
Hardware Config Generator - Map skill requirements to robot hardware.

This generator creates hardware configuration that bridges:
- Abstract skill hardware requirements (arm, gripper, etc.)
- Concrete robot hardware (joint names, controllers, servo IDs)
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

from ..skill_schema import SkillSpecification, HardwareRequirement


@dataclass
class JointInfo:
    """Information about a robot joint from URDF."""
    name: str
    type: str  # revolute, prismatic, continuous, fixed
    parent_link: str
    child_link: str
    axis: Tuple[float, float, float] = (0, 0, 1)
    lower_limit: Optional[float] = None
    upper_limit: Optional[float] = None
    velocity_limit: Optional[float] = None
    effort_limit: Optional[float] = None


@dataclass
class LinkInfo:
    """Information about a robot link from URDF."""
    name: str
    has_visual: bool = False
    has_collision: bool = False
    has_inertial: bool = False


@dataclass
class URDFInfo:
    """Parsed information from a URDF file."""
    name: str
    joints: List[JointInfo] = field(default_factory=list)
    links: List[LinkInfo] = field(default_factory=list)

    @property
    def movable_joints(self) -> List[JointInfo]:
        """Get joints that can move (not fixed)."""
        return [j for j in self.joints if j.type != "fixed"]

    @property
    def dof(self) -> int:
        """Get degrees of freedom."""
        return len(self.movable_joints)

    def get_joint_chain(self, start_link: str, end_link: str) -> List[JointInfo]:
        """Get the kinematic chain between two links."""
        chain = []
        current = end_link

        # Build parent map
        child_to_parent = {}
        child_to_joint = {}
        for joint in self.joints:
            child_to_parent[joint.child_link] = joint.parent_link
            child_to_joint[joint.child_link] = joint

        # Traverse from end to start
        while current != start_link and current in child_to_parent:
            if current in child_to_joint:
                chain.append(child_to_joint[current])
            current = child_to_parent.get(current)

        return list(reversed(chain))


def parse_urdf(urdf_path: str) -> URDFInfo:
    """
    Parse a URDF file and extract robot information.

    Args:
        urdf_path: Path to URDF file

    Returns:
        URDFInfo with parsed robot data
    """
    tree = ET.parse(urdf_path)
    root = tree.getroot()

    robot_name = root.get("name", "unknown")

    # Parse joints
    joints = []
    for joint_elem in root.findall("joint"):
        joint_name = joint_elem.get("name", "")
        joint_type = joint_elem.get("type", "fixed")

        parent_elem = joint_elem.find("parent")
        child_elem = joint_elem.find("child")

        parent_link = parent_elem.get("link", "") if parent_elem is not None else ""
        child_link = child_elem.get("link", "") if child_elem is not None else ""

        # Parse axis
        axis_elem = joint_elem.find("axis")
        if axis_elem is not None:
            xyz = axis_elem.get("xyz", "0 0 1")
            axis = tuple(float(x) for x in xyz.split())
        else:
            axis = (0, 0, 1)

        # Parse limits
        limit_elem = joint_elem.find("limit")
        lower_limit = None
        upper_limit = None
        velocity_limit = None
        effort_limit = None

        if limit_elem is not None:
            if "lower" in limit_elem.attrib:
                lower_limit = float(limit_elem.get("lower"))
            if "upper" in limit_elem.attrib:
                upper_limit = float(limit_elem.get("upper"))
            if "velocity" in limit_elem.attrib:
                velocity_limit = float(limit_elem.get("velocity"))
            if "effort" in limit_elem.attrib:
                effort_limit = float(limit_elem.get("effort"))

        joints.append(JointInfo(
            name=joint_name,
            type=joint_type,
            parent_link=parent_link,
            child_link=child_link,
            axis=axis,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            velocity_limit=velocity_limit,
            effort_limit=effort_limit,
        ))

    # Parse links
    links = []
    for link_elem in root.findall("link"):
        link_name = link_elem.get("name", "")
        links.append(LinkInfo(
            name=link_name,
            has_visual=link_elem.find("visual") is not None,
            has_collision=link_elem.find("collision") is not None,
            has_inertial=link_elem.find("inertial") is not None,
        ))

    return URDFInfo(name=robot_name, joints=joints, links=links)


@dataclass
class ATEConfig:
    """Configuration from ATE CLI (.ate/config.json or primitives)."""
    servo_map: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    protocol: Optional[str] = None
    port: Optional[str] = None
    baud_rate: int = 115200

    @classmethod
    def from_directory(cls, dir_path: str) -> "ATEConfig":
        """Load ATE configuration from a directory."""
        dir_path = Path(dir_path)
        config = cls()

        # Try to load servo_map.py
        servo_map_path = dir_path / "servo_map.py"
        if servo_map_path.exists():
            config.servo_map = cls._parse_servo_map(servo_map_path)

        # Try to load protocol.json
        protocol_path = dir_path / "protocol.json"
        if protocol_path.exists():
            import json
            with open(protocol_path) as f:
                proto_data = json.load(f)
                config.protocol = proto_data.get("type")
                config.port = proto_data.get("port")
                config.baud_rate = proto_data.get("baud_rate", 115200)

        return config

    @staticmethod
    def _parse_servo_map(servo_map_path: Path) -> Dict[int, Dict[str, Any]]:
        """Parse servo_map.py to extract servo configuration."""
        content = servo_map_path.read_text()
        servo_map = {}

        # Extract SERVO_LIMITS dict
        limits_match = re.search(
            r"SERVO_LIMITS\s*=\s*\{([^}]+)\}",
            content,
            re.MULTILINE | re.DOTALL
        )

        if limits_match:
            # Parse limits (simplified parsing)
            limits_content = limits_match.group(1)
            # Match patterns like ServoID.SERVO_0: {"min": 0, "max": 1000, ...}
            pattern = r"ServoID\.(\w+):\s*\{([^}]+)\}"
            for match in re.finditer(pattern, limits_content):
                servo_name = match.group(1)
                # Extract servo ID from name (SERVO_0 -> 0)
                id_match = re.search(r"(\d+)", servo_name)
                if id_match:
                    servo_id = int(id_match.group(1))
                    # Parse the dict content
                    dict_content = match.group(2)
                    servo_data = {}
                    for kv_match in re.finditer(r'"(\w+)":\s*([\d.]+)', dict_content):
                        key = kv_match.group(1)
                        value = float(kv_match.group(2))
                        servo_data[key] = value
                    servo_map[servo_id] = servo_data

        return servo_map


class HardwareConfigGenerator:
    """
    Generate hardware configuration for a skill.

    Maps abstract hardware requirements to concrete robot hardware
    based on URDF and ATE configuration.
    """

    def __init__(
        self,
        spec: SkillSpecification,
        urdf_info: Optional[URDFInfo] = None,
        ate_config: Optional[ATEConfig] = None,
    ):
        """
        Initialize the generator.

        Args:
            spec: Skill specification with hardware requirements
            urdf_info: Parsed URDF information (optional)
            ate_config: ATE configuration (optional)
        """
        self.spec = spec
        self.urdf_info = urdf_info
        self.ate_config = ate_config

    def generate(self) -> Dict[str, Any]:
        """
        Generate hardware configuration.

        Returns:
            Hardware configuration dictionary
        """
        config = {}

        for req in self.spec.hardware_requirements:
            if req.component_type == "arm":
                config["arm"] = self._generate_arm_config(req)
            elif req.component_type == "gripper":
                config["gripper"] = self._generate_gripper_config(req)
            elif req.component_type == "camera":
                config["camera"] = self._generate_camera_config(req)
            elif req.component_type == "force_sensor":
                config["force_sensor"] = self._generate_force_sensor_config(req)
            elif req.component_type == "mobile_base":
                config["mobile_base"] = self._generate_mobile_base_config(req)
            else:
                config[req.component_type] = self._generate_generic_config(req)

        return config

    def _generate_arm_config(self, req: HardwareRequirement) -> Dict[str, Any]:
        """Generate arm configuration."""
        config = {
            "driver": "mock",
            "controller": "/arm_controller",
            "joints": [],
            "ik_solver": "kdl",
        }

        # If we have URDF info, use actual joint names
        if self.urdf_info:
            arm_joints = self._detect_arm_joints()
            config["joints"] = [j.name for j in arm_joints]
            config["joint_limits"] = {
                j.name: {
                    "lower": j.lower_limit,
                    "upper": j.upper_limit,
                    "velocity": j.velocity_limit,
                    "effort": j.effort_limit,
                }
                for j in arm_joints
                if j.lower_limit is not None
            }

        # If we have ATE config, add servo mapping
        if self.ate_config and self.ate_config.servo_map:
            config["servo_mapping"] = {}
            # Map joints to servos (simplified - assumes 1:1 mapping)
            for i, joint_name in enumerate(config.get("joints", [])):
                if i in self.ate_config.servo_map:
                    config["servo_mapping"][joint_name] = {
                        "servo_id": i,
                        **self.ate_config.servo_map[i]
                    }

            config["driver"] = "serial"
            if self.ate_config.protocol:
                config["protocol"] = self.ate_config.protocol
            if self.ate_config.port:
                config["port"] = self.ate_config.port
            config["baud_rate"] = self.ate_config.baud_rate

        return config

    def _detect_arm_joints(self) -> List[JointInfo]:
        """Detect arm joints from URDF (heuristic-based)."""
        if not self.urdf_info:
            return []

        # Look for common arm joint patterns
        arm_patterns = [
            r"shoulder|elbow|wrist|arm|joint_\d",
            r"j[1-7]|joint[1-7]",
            r"axis_[1-6]",
        ]

        pattern = re.compile("|".join(arm_patterns), re.IGNORECASE)
        arm_joints = [
            j for j in self.urdf_info.movable_joints
            if pattern.search(j.name)
        ]

        # If no matches, return all movable joints (excluding gripper-like names)
        if not arm_joints:
            gripper_pattern = re.compile(r"gripper|finger|hand|grasp", re.IGNORECASE)
            arm_joints = [
                j for j in self.urdf_info.movable_joints
                if not gripper_pattern.search(j.name)
            ]

        return arm_joints

    def _generate_gripper_config(self, req: HardwareRequirement) -> Dict[str, Any]:
        """Generate gripper configuration."""
        config = {
            "driver": "mock",
            "controller": "/gripper_controller",
            "type": req.constraints.get("type", "parallel"),
            "open_position": 0.08,
            "close_position": 0.0,
            "max_force": 100.0,
        }

        # If we have URDF info, detect gripper joints
        if self.urdf_info:
            gripper_joints = self._detect_gripper_joints()
            if gripper_joints:
                config["joints"] = [j.name for j in gripper_joints]

        # If we have ATE config, add gripper servo
        if self.ate_config and self.ate_config.servo_map:
            # Gripper is typically the last servo
            max_servo_id = max(self.ate_config.servo_map.keys(), default=-1)
            if max_servo_id >= 0:
                config["servo_id"] = max_servo_id
                config["driver"] = "serial"
                gripper_limits = self.ate_config.servo_map.get(max_servo_id, {})
                config["open_position"] = gripper_limits.get("max", 1000)
                config["close_position"] = gripper_limits.get("min", 0)

        return config

    def _detect_gripper_joints(self) -> List[JointInfo]:
        """Detect gripper joints from URDF (heuristic-based)."""
        if not self.urdf_info:
            return []

        gripper_pattern = re.compile(
            r"gripper|finger|hand|grasp|claw",
            re.IGNORECASE
        )

        return [
            j for j in self.urdf_info.movable_joints
            if gripper_pattern.search(j.name)
        ]

    def _generate_camera_config(self, req: HardwareRequirement) -> Dict[str, Any]:
        """Generate camera configuration."""
        return {
            "driver": "mock",
            "device": "/dev/video0",
            "width": req.constraints.get("width", 640),
            "height": req.constraints.get("height", 480),
            "fps": req.constraints.get("fps", 30),
            "topic": "/camera/image_raw",
        }

    def _generate_force_sensor_config(self, req: HardwareRequirement) -> Dict[str, Any]:
        """Generate force/torque sensor configuration."""
        return {
            "driver": "mock",
            "topic": "/ft_sensor/wrench",
            "frame": "ft_sensor_link",
            "rate": req.constraints.get("rate", 100),
        }

    def _generate_mobile_base_config(self, req: HardwareRequirement) -> Dict[str, Any]:
        """Generate mobile base configuration."""
        return {
            "driver": "mock",
            "type": req.constraints.get("type", "differential"),
            "cmd_vel_topic": "/cmd_vel",
            "odom_topic": "/odom",
            "max_linear_velocity": req.constraints.get("max_velocity", 1.0),
            "max_angular_velocity": req.constraints.get("max_angular_velocity", 2.0),
        }

    def _generate_generic_config(self, req: HardwareRequirement) -> Dict[str, Any]:
        """Generate generic hardware configuration."""
        return {
            "driver": "mock",
            "type": req.component_type,
            **req.constraints,
        }

    def to_yaml(self) -> str:
        """Generate YAML configuration string."""
        config = self.generate()
        return yaml.dump(config, default_flow_style=False, sort_keys=False)

    def save(self, output_path: str) -> None:
        """Save configuration to YAML file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_yaml())


def generate_hardware_config(
    spec: SkillSpecification,
    urdf_path: Optional[str] = None,
    ate_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to generate hardware configuration.

    Args:
        spec: Skill specification
        urdf_path: Path to URDF file (optional)
        ate_dir: Path to ATE configuration directory (optional)

    Returns:
        Hardware configuration dictionary
    """
    urdf_info = None
    if urdf_path:
        urdf_info = parse_urdf(urdf_path)

    ate_config = None
    if ate_dir:
        ate_config = ATEConfig.from_directory(ate_dir)

    generator = HardwareConfigGenerator(spec, urdf_info, ate_config)
    return generator.generate()
