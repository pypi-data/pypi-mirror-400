"""
Robot profiles - saved configurations for easy robot setup.

Profiles are stored in ~/.ate/robots/ as JSON files.
Users can create, edit, and share profiles.
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path


# Default profile directory
def get_profiles_dir() -> Path:
    """Get the profiles directory, creating if needed."""
    ate_dir = Path.home() / ".ate"
    profiles_dir = ate_dir / "robots"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    return profiles_dir


@dataclass
class RobotProfile:
    """
    A saved robot configuration.

    Contains everything needed to connect to and use a robot.
    """
    # Identity
    name: str                           # User-chosen name for this robot
    robot_type: str                     # ID of robot type from registry

    # Serial connection
    serial_port: Optional[str] = None
    baud_rate: int = 115200

    # Network connection
    ip_address: Optional[str] = None
    camera_ip: Optional[str] = None
    camera_port: int = 80
    camera_stream_port: int = 81

    # Robot-specific config
    has_arm: bool = False
    has_camera: bool = False
    has_gripper: bool = False

    # Custom settings
    settings: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    description: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RobotProfile":
        """Create from dictionary."""
        return cls(**data)


def load_profile(name: str) -> Optional[RobotProfile]:
    """
    Load a robot profile by name.

    Args:
        name: Profile name (without .json extension)

    Returns:
        RobotProfile or None if not found
    """
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{name}.json"

    if not profile_path.exists():
        return None

    try:
        with open(profile_path, "r") as f:
            data = json.load(f)
            return RobotProfile.from_dict(data)
    except Exception as e:
        print(f"Error loading profile: {e}")
        return None


def save_profile(profile: RobotProfile) -> bool:
    """
    Save a robot profile.

    Args:
        profile: Profile to save

    Returns:
        True if saved successfully
    """
    from datetime import datetime

    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{profile.name}.json"

    # Update timestamps
    now = datetime.now().isoformat()
    if profile.created_at is None:
        profile.created_at = now
    profile.updated_at = now

    try:
        with open(profile_path, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False


def list_profiles() -> List[RobotProfile]:
    """
    List all saved robot profiles.

    Returns:
        List of profiles
    """
    profiles_dir = get_profiles_dir()
    profiles = []

    for file in profiles_dir.glob("*.json"):
        try:
            with open(file, "r") as f:
                data = json.load(f)
                profiles.append(RobotProfile.from_dict(data))
        except Exception:
            pass

    return profiles


def delete_profile(name: str) -> bool:
    """
    Delete a robot profile.

    Args:
        name: Profile name

    Returns:
        True if deleted
    """
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{name}.json"

    if profile_path.exists():
        profile_path.unlink()
        return True
    return False


def profile_exists(name: str) -> bool:
    """Check if a profile exists."""
    profiles_dir = get_profiles_dir()
    return (profiles_dir / f"{name}.json").exists()


def get_default_profile() -> Optional[RobotProfile]:
    """
    Get the default profile (if set).

    The default profile is stored as 'default.yaml' or
    a profile named 'default'.
    """
    profiles_dir = get_profiles_dir()

    # Check for default marker
    default_marker = profiles_dir / ".default"
    if default_marker.exists():
        with open(default_marker, "r") as f:
            default_name = f.read().strip()
            return load_profile(default_name)

    # Fall back to profile named 'default'
    return load_profile("default")


def set_default_profile(name: str) -> bool:
    """
    Set a profile as the default.

    Args:
        name: Profile name

    Returns:
        True if set successfully
    """
    if not profile_exists(name):
        return False

    profiles_dir = get_profiles_dir()
    default_marker = profiles_dir / ".default"

    with open(default_marker, "w") as f:
        f.write(name)

    return True


def create_profile_from_discovery(
    name: str,
    serial_port: Optional[str] = None,
    camera_ip: Optional[str] = None,
    robot_type: str = "hiwonder_mechdog",
) -> RobotProfile:
    """
    Create a profile from discovered devices.

    Helper for the setup wizard.
    """
    profile = RobotProfile(
        name=name,
        robot_type=robot_type,
        serial_port=serial_port,
        camera_ip=camera_ip,
        has_camera=camera_ip is not None,
    )

    return profile


# Built-in profile templates
PROFILE_TEMPLATES: Dict[str, RobotProfile] = {
    "mechdog_basic": RobotProfile(
        name="mechdog_basic",
        robot_type="hiwonder_mechdog",
        description="Basic MechDog setup without camera or arm",
        serial_port="/dev/cu.usbserial-10",  # Common macOS port
        has_camera=False,
        has_arm=False,
    ),
    "mechdog_camera": RobotProfile(
        name="mechdog_camera",
        robot_type="hiwonder_mechdog",
        description="MechDog with visual module (camera)",
        serial_port="/dev/cu.usbserial-10",
        has_camera=True,
        camera_ip="192.168.1.100",
    ),
    "mechdog_full": RobotProfile(
        name="mechdog_full",
        robot_type="hiwonder_mechdog",
        description="Full MechDog setup with arm and camera",
        serial_port="/dev/cu.usbserial-10",
        has_camera=True,
        has_arm=True,
        camera_ip="192.168.1.100",
    ),
    "simulation": RobotProfile(
        name="simulation",
        robot_type="simulation",
        description="Simulated robot for testing without hardware",
    ),
}


def get_template(template_name: str) -> Optional[RobotProfile]:
    """Get a profile template."""
    return PROFILE_TEMPLATES.get(template_name)


def list_templates() -> List[str]:
    """List available profile templates."""
    return list(PROFILE_TEMPLATES.keys())
