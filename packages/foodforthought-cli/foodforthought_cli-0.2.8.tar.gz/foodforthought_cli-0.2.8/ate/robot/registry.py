"""
Registry of known robot types and their configurations.

This is how we know what robots are supported and how to configure them.
Community contributions can add new robots here.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Type, Any
from enum import Enum, auto


class ConnectionType(Enum):
    """How to connect to the robot."""
    SERIAL = auto()      # USB serial (pyserial)
    WIFI = auto()        # WiFi/HTTP
    ROS2 = auto()        # ROS2 topics/services
    BLUETOOTH = auto()   # Bluetooth serial
    ETHERNET = auto()    # Direct ethernet
    SIMULATION = auto()  # No hardware, simulated


@dataclass
class RobotType:
    """Definition of a known robot type."""
    id: str                              # Unique identifier
    name: str                            # Display name
    manufacturer: str                    # Who makes it
    archetype: str                       # quadruped, humanoid, arm, etc.
    description: str                     # Human description

    # Connection
    connection_types: Set[ConnectionType] = field(default_factory=set)
    default_connection: Optional[ConnectionType] = None

    # Serial settings
    serial_patterns: List[str] = field(default_factory=list)  # USB patterns to match
    baud_rate: int = 115200

    # Network settings
    default_ports: Dict[str, int] = field(default_factory=dict)  # camera_port, stream_port, etc.
    mdns_service: Optional[str] = None  # mDNS service type to discover

    # Capabilities
    capabilities: Set[str] = field(default_factory=set)
    optional_capabilities: Set[str] = field(default_factory=set)

    # Driver info
    driver_module: str = ""              # Python module path
    driver_class: str = ""               # Class name
    config_class: str = ""               # Config class name

    # Documentation
    setup_url: Optional[str] = None
    image_url: Optional[str] = None


# Registry of known robot types
KNOWN_ROBOTS: Dict[str, RobotType] = {}


def register_robot(robot: RobotType) -> None:
    """Register a robot type."""
    KNOWN_ROBOTS[robot.id] = robot


def get_robot_info(robot_id: str) -> Optional[RobotType]:
    """Get information about a robot type."""
    return KNOWN_ROBOTS.get(robot_id)


def list_robot_types() -> List[RobotType]:
    """List all known robot types."""
    return list(KNOWN_ROBOTS.values())


def find_by_archetype(archetype: str) -> List[RobotType]:
    """Find robots by archetype (quadruped, humanoid, etc.)."""
    return [r for r in KNOWN_ROBOTS.values() if r.archetype == archetype]


# =============================================================================
# Built-in robot definitions
# =============================================================================

# HiWonder MechDog
register_robot(RobotType(
    id="hiwonder_mechdog",
    name="MechDog",
    manufacturer="HiWonder",
    archetype="quadruped",
    description="12 DOF quadruped robot with optional arm and camera. ESP32-based with MicroPython.",

    connection_types={ConnectionType.SERIAL, ConnectionType.WIFI},
    default_connection=ConnectionType.SERIAL,

    serial_patterns=[
        "/dev/cu.usbserial-*",      # macOS
        "/dev/ttyUSB*",             # Linux
        "COM*",                      # Windows
    ],
    baud_rate=115200,

    default_ports={
        "camera_port": 80,
        "camera_stream_port": 81,
    },

    capabilities={
        "quadruped_locomotion",
        "body_pose",
        "imu",
    },
    optional_capabilities={
        "camera",
        "arm",
        "gripper",
    },

    driver_module="ate.drivers.mechdog",
    driver_class="MechDogDriver",
    config_class="MechDogConfig",

    setup_url="https://docs.kindly.fyi/robots/mechdog",
))


# Unitree Go1
register_robot(RobotType(
    id="unitree_go1",
    name="Go1",
    manufacturer="Unitree",
    archetype="quadruped",
    description="High-performance quadruped robot with cameras and optional arm.",

    connection_types={ConnectionType.WIFI, ConnectionType.ETHERNET},
    default_connection=ConnectionType.WIFI,

    default_ports={
        "control_port": 8082,
        "camera_port": 8080,
    },

    capabilities={
        "quadruped_locomotion",
        "body_pose",
        "imu",
        "camera",
        "depth_camera",
    },
    optional_capabilities={
        "arm",
        "gripper",
        "lidar",
    },

    driver_module="ate.drivers.go1",
    driver_class="Go1Driver",
    config_class="Go1Config",
))


# Unitree Go2
register_robot(RobotType(
    id="unitree_go2",
    name="Go2",
    manufacturer="Unitree",
    archetype="quadruped",
    description="Advanced quadruped with AI capabilities, LiDAR, and ROS2 support.",

    connection_types={ConnectionType.ROS2, ConnectionType.WIFI},
    default_connection=ConnectionType.ROS2,

    capabilities={
        "quadruped_locomotion",
        "body_pose",
        "imu",
        "camera",
        "depth_camera",
        "lidar",
    },
    optional_capabilities={
        "arm",
        "gripper",
    },

    driver_module="ate.drivers.go2",
    driver_class="Go2Driver",
    config_class="Go2Config",
))


# Boston Dynamics Spot
register_robot(RobotType(
    id="boston_dynamics_spot",
    name="Spot",
    manufacturer="Boston Dynamics",
    archetype="quadruped",
    description="Industrial quadruped robot with arm, cameras, and high autonomy.",

    connection_types={ConnectionType.WIFI, ConnectionType.ETHERNET},
    default_connection=ConnectionType.WIFI,

    capabilities={
        "quadruped_locomotion",
        "body_pose",
        "imu",
        "camera",
        "depth_camera",
    },
    optional_capabilities={
        "arm",
        "gripper",
        "lidar",
    },

    driver_module="ate.drivers.spot",
    driver_class="SpotDriver",
    config_class="SpotConfig",
))


# Generic ROS2 robot
register_robot(RobotType(
    id="ros2_generic",
    name="Generic ROS2 Robot",
    manufacturer="Various",
    archetype="custom",
    description="Any robot accessible via ROS2 topics and services.",

    connection_types={ConnectionType.ROS2},
    default_connection=ConnectionType.ROS2,

    capabilities=set(),  # Discovered from ROS2 topics
    optional_capabilities={
        "quadruped_locomotion",
        "bipedal_locomotion",
        "wheeled_locomotion",
        "arm",
        "gripper",
        "camera",
        "depth_camera",
        "lidar",
        "imu",
    },

    driver_module="ate.drivers.ros2_bridge",
    driver_class="ROS2Bridge",
    config_class="ROS2Config",
))


# Simulation robot
register_robot(RobotType(
    id="simulation",
    name="Simulated Robot",
    manufacturer="FoodforThought",
    archetype="custom",
    description="Software simulation for testing without hardware.",

    connection_types={ConnectionType.SIMULATION},
    default_connection=ConnectionType.SIMULATION,

    capabilities={
        "quadruped_locomotion",
        "body_pose",
        "camera",
    },
    optional_capabilities={
        "arm",
        "gripper",
        "lidar",
    },

    driver_module="ate.drivers.simulation",
    driver_class="SimulationDriver",
    config_class="SimulationConfig",
))


class RobotRegistry:
    """
    Registry interface for robot types.

    Provides methods to find and filter known robots.
    """

    @staticmethod
    def list_all() -> List[RobotType]:
        """List all known robot types."""
        return list(KNOWN_ROBOTS.values())

    @staticmethod
    def get(robot_id: str) -> Optional[RobotType]:
        """Get robot type by ID."""
        return KNOWN_ROBOTS.get(robot_id)

    @staticmethod
    def find_by_archetype(archetype: str) -> List[RobotType]:
        """Find robots by archetype."""
        return [r for r in KNOWN_ROBOTS.values() if r.archetype == archetype]

    @staticmethod
    def find_by_capability(capability: str) -> List[RobotType]:
        """Find robots that have a specific capability."""
        return [
            r for r in KNOWN_ROBOTS.values()
            if capability in r.capabilities or capability in r.optional_capabilities
        ]

    @staticmethod
    def find_by_connection(conn_type: ConnectionType) -> List[RobotType]:
        """Find robots that support a connection type."""
        return [r for r in KNOWN_ROBOTS.values() if conn_type in r.connection_types]

    @staticmethod
    def register(robot: RobotType) -> None:
        """Register a new robot type."""
        KNOWN_ROBOTS[robot.id] = robot
