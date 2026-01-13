"""
Robot Manager - unified interface for managing robot connections.

Handles:
- Loading robots from profiles
- Connecting/disconnecting
- Managing multiple robots
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .profiles import RobotProfile, load_profile, list_profiles
from .registry import KNOWN_ROBOTS, RobotType
from .introspection import get_capabilities, get_methods


@dataclass
class ManagedRobot:
    """A robot instance managed by RobotManager."""
    profile: RobotProfile
    robot_type: RobotType
    instance: Any = None
    connected: bool = False


class RobotManager:
    """
    Manages robot connections and lifecycle.

    Example:
        manager = RobotManager()

        # Load from profile
        dog = manager.load("my_mechdog")
        dog.connect()

        # Use robot
        dog.instance.stand()
        dog.instance.walk(Vector3.forward())

        # Disconnect
        manager.disconnect_all()
    """

    def __init__(self):
        self._robots: Dict[str, ManagedRobot] = {}

    def load(self, profile_name: str) -> Optional[ManagedRobot]:
        """
        Load a robot from a saved profile.

        Args:
            profile_name: Name of the profile

        Returns:
            ManagedRobot or None if profile not found
        """
        profile = load_profile(profile_name)
        if profile is None:
            return None

        robot_type = KNOWN_ROBOTS.get(profile.robot_type)
        if robot_type is None:
            print(f"Unknown robot type: {profile.robot_type}")
            return None

        managed = ManagedRobot(
            profile=profile,
            robot_type=robot_type,
        )

        self._robots[profile_name] = managed
        return managed

    def create(
        self,
        name: str,
        robot_type: str,
        **config
    ) -> Optional[ManagedRobot]:
        """
        Create a robot instance without loading from profile.

        Args:
            name: Name for this robot
            robot_type: Robot type ID
            **config: Configuration options

        Returns:
            ManagedRobot
        """
        rtype = KNOWN_ROBOTS.get(robot_type)
        if rtype is None:
            print(f"Unknown robot type: {robot_type}")
            return None

        profile = RobotProfile(
            name=name,
            robot_type=robot_type,
            **config
        )

        managed = ManagedRobot(
            profile=profile,
            robot_type=rtype,
        )

        self._robots[name] = managed
        return managed

    def connect(self, name: str) -> bool:
        """
        Connect to a loaded robot.

        Args:
            name: Robot name

        Returns:
            True if connected successfully
        """
        managed = self._robots.get(name)
        if managed is None:
            print(f"Robot not loaded: {name}")
            return False

        # Create robot instance
        instance = self._create_instance(managed)
        if instance is None:
            return False

        managed.instance = instance

        # Connect
        result = instance.connect()
        if result.success:
            managed.connected = True
            return True
        else:
            print(f"Connection failed: {result.message}")
            return False

    def disconnect(self, name: str) -> bool:
        """
        Disconnect from a robot.

        Args:
            name: Robot name

        Returns:
            True if disconnected
        """
        managed = self._robots.get(name)
        if managed is None or not managed.connected:
            return True

        if managed.instance:
            managed.instance.disconnect()
            managed.connected = False

        return True

    def disconnect_all(self) -> None:
        """Disconnect from all robots."""
        for name in list(self._robots.keys()):
            self.disconnect(name)

    def get(self, name: str) -> Optional[Any]:
        """
        Get a robot instance.

        Args:
            name: Robot name

        Returns:
            Robot instance or None
        """
        managed = self._robots.get(name)
        if managed and managed.instance:
            return managed.instance
        return None

    def list_loaded(self) -> List[str]:
        """List all loaded robots."""
        return list(self._robots.keys())

    def list_connected(self) -> List[str]:
        """List all connected robots."""
        return [
            name for name, managed in self._robots.items()
            if managed.connected
        ]

    def get_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a loaded robot.

        Args:
            name: Robot name

        Returns:
            Dict with robot info
        """
        managed = self._robots.get(name)
        if managed is None:
            return None

        info = {
            "name": managed.profile.name,
            "type": managed.robot_type.name,
            "manufacturer": managed.robot_type.manufacturer,
            "archetype": managed.robot_type.archetype,
            "connected": managed.connected,
            "profile": {
                "serial_port": managed.profile.serial_port,
                "camera_ip": managed.profile.camera_ip,
                "has_camera": managed.profile.has_camera,
                "has_arm": managed.profile.has_arm,
            },
        }

        if managed.instance:
            info["capabilities"] = list(get_capabilities(managed.instance).keys())
            info["methods"] = {
                cap: [m.name for m in methods]
                for cap, methods in get_methods(managed.instance).items()
            }

        return info

    def _create_instance(self, managed: ManagedRobot) -> Optional[Any]:
        """Create a robot instance from profile and type."""
        rtype = managed.robot_type
        profile = managed.profile

        # Import the driver module dynamically
        try:
            import importlib
            module = importlib.import_module(rtype.driver_module)
            driver_class = getattr(module, rtype.driver_class)
            config_class = getattr(module, rtype.config_class, None)
        except (ImportError, AttributeError) as e:
            print(f"Failed to import driver: {e}")
            return None

        # Build configuration
        if config_class:
            config_kwargs = {
                "port": profile.serial_port or "/dev/ttyUSB0",
            }

            if profile.has_camera and profile.camera_ip:
                config_kwargs["has_camera"] = True
                config_kwargs["camera_ip"] = profile.camera_ip
                config_kwargs["camera_port"] = profile.camera_port
                config_kwargs["camera_stream_port"] = profile.camera_stream_port

            if profile.has_arm:
                config_kwargs["has_arm"] = True

            config = config_class(**config_kwargs)
            return driver_class(config=config)
        else:
            return driver_class()

    def __enter__(self) -> "RobotManager":
        return self

    def __exit__(self, *args) -> None:
        self.disconnect_all()
