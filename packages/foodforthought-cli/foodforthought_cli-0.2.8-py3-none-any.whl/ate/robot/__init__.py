"""
Robot management system for ATE.

Provides:
- Auto-discovery of robots on network and USB
- Robot profiles for easy configuration
- Capability introspection
- Interactive setup wizard

Example usage:
    from ate.robot import RobotManager, discover_robots

    # Auto-discover robots
    found = discover_robots()
    # > [DiscoveredRobot(type='mechdog', port='/dev/cu.usbserial-10', camera_ip='192.168.1.100')]

    # Load saved profile
    manager = RobotManager()
    dog = manager.get_robot("my_mechdog")

    # Introspect capabilities
    info = manager.get_capabilities(dog)
    # > {'locomotion': ['walk', 'turn', 'stand'], 'camera': ['get_image']}
"""

from .discovery import (
    DiscoveredRobot,
    discover_robots,
    discover_serial_robots,
    discover_network_cameras,
)

from .profiles import (
    RobotProfile,
    load_profile,
    save_profile,
    list_profiles,
    delete_profile,
)

from .registry import (
    RobotRegistry,
    KNOWN_ROBOTS,
    get_robot_info,
)

from .introspection import (
    get_capabilities,
    get_methods,
    test_capability,
)

from .manager import (
    RobotManager,
)

__all__ = [
    # Discovery
    "DiscoveredRobot",
    "discover_robots",
    "discover_serial_robots",
    "discover_network_cameras",
    # Profiles
    "RobotProfile",
    "load_profile",
    "save_profile",
    "list_profiles",
    "delete_profile",
    # Registry
    "RobotRegistry",
    "KNOWN_ROBOTS",
    "get_robot_info",
    # Introspection
    "get_capabilities",
    "get_methods",
    "test_capability",
    # Manager
    "RobotManager",
]
