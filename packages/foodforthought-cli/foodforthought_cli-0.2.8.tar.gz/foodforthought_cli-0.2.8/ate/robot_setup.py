#!/usr/bin/env python3
"""
Robot Setup Wizard - Automated discovery and primitive skill generation for any robot.

This wizard:
1. Discovers connected USB/serial devices
2. Enumerates servos/motors on each device
3. Characterizes each component's parameters
4. Guides interactive labeling with AI assistance
5. Generates primitive skills and protocol definitions

Usage:
    ate robot-setup                    # Interactive wizard
    ate robot-setup --port /dev/tty... # Skip device selection
    ate robot-setup --output ./robot   # Specify output directory
"""

import json
import os
import sys
import time
import struct
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple, Callable
from datetime import datetime

# Optional imports with fallbacks
try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class DeviceType(str, Enum):
    """Types of robot communication devices."""
    SERIAL = "serial"
    USB_HID = "usb_hid"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    UNKNOWN = "unknown"


class ActuatorType(str, Enum):
    """Types of actuators."""
    SERIAL_BUS_SERVO = "serial_bus_servo"
    PWM_SERVO = "pwm_servo"
    STEPPER_MOTOR = "stepper_motor"
    DC_MOTOR = "dc_motor"
    LINEAR_ACTUATOR = "linear_actuator"
    UNKNOWN = "unknown"


class ProtocolType(str, Enum):
    """Known servo protocols."""
    HIWONDER = "hiwonder"          # HiWonder/LewanSoul serial bus servos
    DYNAMIXEL = "dynamixel"        # Dynamixel servos (Robotis)
    FEETECH = "feetech"            # Feetech/SCS servos
    WAVESHARE = "waveshare"        # Waveshare serial servos
    CUSTOM = "custom"
    UNKNOWN = "unknown"


@dataclass
class DiscoveredDevice:
    """A discovered communication device."""
    port: str
    device_type: DeviceType
    description: str = ""
    vid: Optional[int] = None
    pid: Optional[int] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    detected_protocol: Optional[ProtocolType] = None
    baud_rate: int = 115200


@dataclass
class ActuatorCharacteristics:
    """Characteristics of an actuator determined through testing."""
    position_min: int = 0
    position_max: int = 1000
    position_center: int = 500
    speed_min: int = 0
    speed_max: int = 2000
    supports_torque_control: bool = False
    supports_position_read: bool = True
    supports_voltage_read: bool = False
    supports_temperature_read: bool = False
    response_time_ms: float = 0.0


@dataclass
class DiscoveredActuator:
    """A discovered actuator (servo, motor, etc.)."""
    id: int
    actuator_type: ActuatorType
    protocol: ProtocolType
    characteristics: ActuatorCharacteristics = field(default_factory=ActuatorCharacteristics)

    # User-assigned labels
    label: str = ""  # e.g., "front_left_hip", "arm_shoulder"
    group: str = ""  # e.g., "left_front_leg", "arm"
    role: str = ""   # e.g., "hip", "knee", "ankle", "shoulder"

    # Test results
    verified_working: bool = False
    notes: str = ""


@dataclass
class RobotProfile:
    """Complete profile of a discovered robot."""
    name: str = "unnamed_robot"
    robot_type: str = ""  # e.g., "quadruped", "humanoid", "arm"
    manufacturer: str = ""
    model: str = ""

    # Communication
    device: Optional[DiscoveredDevice] = None

    # Actuators
    actuators: List[DiscoveredActuator] = field(default_factory=list)

    # Groups (legs, arms, etc.)
    groups: Dict[str, List[int]] = field(default_factory=dict)  # group_name -> [actuator_ids]

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    wizard_version: str = "1.0.0"


class WizardUI:
    """Console UI helpers for the wizard."""

    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
    }

    @classmethod
    def print_header(cls, text: str):
        """Print a section header."""
        print(f"\n{cls.COLORS['bold']}{cls.COLORS['cyan']}{'='*60}{cls.COLORS['reset']}")
        print(f"{cls.COLORS['bold']}{cls.COLORS['cyan']}  {text}{cls.COLORS['reset']}")
        print(f"{cls.COLORS['bold']}{cls.COLORS['cyan']}{'='*60}{cls.COLORS['reset']}\n")

    @classmethod
    def print_step(cls, step: int, total: int, text: str):
        """Print a wizard step indicator."""
        print(f"\n{cls.COLORS['magenta']}[Step {step}/{total}]{cls.COLORS['reset']} {cls.COLORS['bold']}{text}{cls.COLORS['reset']}")

    @classmethod
    def print_success(cls, text: str):
        """Print success message."""
        print(f"{cls.COLORS['green']}✓ {text}{cls.COLORS['reset']}")

    @classmethod
    def print_warning(cls, text: str):
        """Print warning message."""
        print(f"{cls.COLORS['yellow']}⚠ {text}{cls.COLORS['reset']}")

    @classmethod
    def print_error(cls, text: str):
        """Print error message."""
        print(f"{cls.COLORS['red']}✗ {text}{cls.COLORS['reset']}")

    @classmethod
    def print_info(cls, text: str):
        """Print info message."""
        print(f"{cls.COLORS['blue']}ℹ {text}{cls.COLORS['reset']}")

    @classmethod
    def prompt(cls, text: str, default: str = "") -> str:
        """Prompt user for input."""
        if default:
            result = input(f"{text} [{default}]: ").strip()
            return result if result else default
        return input(f"{text}: ").strip()

    @classmethod
    def confirm(cls, text: str, default: bool = True) -> bool:
        """Prompt for yes/no confirmation."""
        suffix = "[Y/n]" if default else "[y/N]"
        result = input(f"{text} {suffix}: ").strip().lower()
        if not result:
            return default
        return result in ('y', 'yes')

    @classmethod
    def select(cls, text: str, options: List[str], allow_multiple: bool = False) -> List[int]:
        """Prompt user to select from options."""
        print(f"\n{text}")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")

        if allow_multiple:
            print(f"\n  Enter numbers separated by commas (e.g., 1,3,5) or 'all':")

        while True:
            selection = input("  Selection: ").strip()

            if allow_multiple and selection.lower() == 'all':
                return list(range(len(options)))

            try:
                if allow_multiple:
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                else:
                    indices = [int(selection) - 1]

                if all(0 <= i < len(options) for i in indices):
                    return indices
            except ValueError:
                pass

            print(f"  {cls.COLORS['red']}Invalid selection. Please try again.{cls.COLORS['reset']}")


class ServoProtocolHandler:
    """Handles communication with serial bus servos."""

    def __init__(self, port: str, baud_rate: int = 115200, protocol: ProtocolType = ProtocolType.HIWONDER):
        self.port = port
        self.baud_rate = baud_rate
        self.protocol = protocol
        self.serial: Optional[serial.Serial] = None

    def connect(self) -> bool:
        """Open serial connection."""
        if not HAS_SERIAL:
            WizardUI.print_error("pyserial not installed. Run: pip install pyserial")
            return False

        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=0.1)
            time.sleep(0.1)  # Let it stabilize
            return True
        except Exception as e:
            WizardUI.print_error(f"Failed to open {self.port}: {e}")
            return False

    def disconnect(self):
        """Close serial connection."""
        if self.serial:
            self.serial.close()
            self.serial = None

    def _send_command(self, servo_id: int, cmd: int, params: bytes = b'') -> Optional[bytes]:
        """Send a command and receive response (HiWonder protocol)."""
        if not self.serial:
            return None

        # HiWonder packet: 0x55 0x55 ID LEN CMD [PARAMS...] CHECKSUM
        length = len(params) + 3  # cmd + params + checksum
        packet = bytes([0x55, 0x55, servo_id, length, cmd]) + params
        checksum = (~sum(packet[2:]) & 0xFF)
        packet += bytes([checksum])

        try:
            self.serial.reset_input_buffer()
            self.serial.write(packet)
            self.serial.flush()

            # Read response header
            time.sleep(0.01)
            header = self.serial.read(5)
            if len(header) < 5:
                return None

            if header[0:2] != b'\x55\x55':
                return None

            resp_len = header[3]
            remaining = self.serial.read(resp_len - 2)  # -2 because length includes cmd+checksum

            return header + remaining
        except Exception:
            return None

    def ping(self, servo_id: int) -> bool:
        """Check if a servo responds at given ID."""
        if self.protocol == ProtocolType.HIWONDER:
            # Read position command (14)
            response = self._send_command(servo_id, 14)
            return response is not None and len(response) >= 7
        return False

    def read_position(self, servo_id: int) -> Optional[int]:
        """Read current position of servo."""
        if self.protocol == ProtocolType.HIWONDER:
            response = self._send_command(servo_id, 28)  # Read position
            if response and len(response) >= 8:
                pos_low = response[5]
                pos_high = response[6]
                return pos_low | (pos_high << 8)
        return None

    def move_servo(self, servo_id: int, position: int, time_ms: int = 500):
        """Move servo to position."""
        if self.protocol == ProtocolType.HIWONDER:
            # Move command (1): ID, time_low, time_high, pos_low, pos_high
            params = struct.pack('<HH', time_ms, position)
            self._send_command(servo_id, 1, params)

    def scan_servos(self, id_range: range = range(0, 32), progress_callback: Optional[Callable[[int, int], None]] = None) -> List[int]:
        """Scan for servos in ID range."""
        found = []
        total = len(id_range)

        for i, servo_id in enumerate(id_range):
            if progress_callback:
                progress_callback(i + 1, total)

            if self.ping(servo_id):
                found.append(servo_id)

        return found

    def characterize_servo(self, servo_id: int) -> ActuatorCharacteristics:
        """Determine servo characteristics through safe testing."""
        chars = ActuatorCharacteristics()

        # Try to read current position
        pos = self.read_position(servo_id)
        if pos is not None:
            chars.supports_position_read = True
            chars.position_center = pos

        # HiWonder servos typically have 0-1000 range
        if self.protocol == ProtocolType.HIWONDER:
            chars.position_min = 0
            chars.position_max = 1000
            chars.position_center = 500
            chars.speed_min = 0
            chars.speed_max = 30000  # time in ms (lower = faster)

        return chars


class AILabelingAssistant:
    """AI-powered assistant for labeling robot components."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if HAS_ANTHROPIC and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def suggest_robot_type(self, num_servos: int, servo_ids: List[int]) -> str:
        """Suggest robot type based on servo count and ID distribution.

        Args:
            num_servos: Total number of servos found
            servo_ids: List of servo IDs (used to detect core vs peripheral servos)
        """
        # Analyze servo ID distribution to find "core" actuators
        # Many robots have main actuators in low IDs (0-15) and peripherals in higher IDs
        core_servo_count = self._count_core_servos(servo_ids)

        # Use core count for detection if it differs significantly from total
        effective_count = core_servo_count if core_servo_count < num_servos * 0.7 else num_servos

        if not self.client:
            # Rule-based detection
            return self._detect_robot_type_by_count(effective_count, num_servos)

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": f"""Detected {num_servos} servos total, but analysis suggests {effective_count} are main actuators.
Servo IDs found: {sorted(servo_ids)[:20]}{'...' if len(servo_ids) > 20 else ''}

What type of robot is this likely to be?

Common patterns:
- 12 servos: quadruped (4 legs × 3 joints)
- 13-15 servos: quadruped_with_arm (4 legs + arm)
- 18 servos: hexapod (6 legs × 3 joints)
- 6 servos: 6dof_arm
- 16-17 servos: humanoid_basic (arms + legs only)
- 18-20 servos: humanoid (arms + legs + some torso)
- 21-24 servos: humanoid_advanced (full body)
- 25+ servos: humanoid_full (with dexterous hands)

Reply with just the robot type from the list above."""
                }]
            )
            return response.content[0].text.strip().lower()
        except Exception:
            return self._detect_robot_type_by_count(effective_count, num_servos)

    def _count_core_servos(self, servo_ids: List[int]) -> int:
        """Count core servos by analyzing ID distribution.

        Heuristics:
        - IDs 0-15 are typically main actuators
        - Look for gaps in ID sequence as boundaries
        - Contiguous low IDs are more likely to be core actuators
        """
        if not servo_ids:
            return 0

        sorted_ids = sorted(servo_ids)

        # Count servos in the "core" range (0-15)
        core_range_count = sum(1 for id in sorted_ids if id <= 15)

        # Also look for the first significant gap (gap > 1)
        last_id = -1
        contiguous_count = 0
        for id in sorted_ids:
            if last_id >= 0 and id - last_id > 1:
                # Found a gap - servos before this are likely core
                break
            contiguous_count += 1
            last_id = id

        # Use the more conservative estimate
        return min(core_range_count, contiguous_count) if contiguous_count > 0 else core_range_count

    def _detect_robot_type_by_count(self, effective_count: int, total_count: int) -> str:
        """Detect robot type based on servo count."""
        # Show both counts in suggestions if they differ
        count = effective_count

        if count == 12:
            return "quadruped"
        elif count in (13, 14, 15):
            return "quadruped_with_arm"  # 12 leg + 1-3 arm servos
        elif count == 6:
            return "6dof_arm"
        elif count == 18:
            return "hexapod"
        elif count in (16, 17):
            return "humanoid_basic"
        elif count in (18, 19, 20):
            return "humanoid"
        elif count in (21, 22, 23, 24):
            return "humanoid_advanced"
        elif count >= 25:
            return "humanoid_full"
        elif count <= 4:
            return "robotic_arm"
        return "custom"

    def suggest_labels(self, robot_type: str, servo_ids: List[int]) -> Dict[int, Dict[str, str]]:
        """Suggest labels for servos based on robot type."""
        labels = {}

        if robot_type == "quadruped":
            # Standard quadruped mapping
            leg_names = ["front_right", "front_left", "back_right", "back_left"]
            joint_names = ["hip", "upper", "lower"]

            for i, servo_id in enumerate(sorted(servo_ids)):
                leg_idx = i // 3
                joint_idx = i % 3

                if leg_idx < len(leg_names) and joint_idx < len(joint_names):
                    labels[servo_id] = {
                        "label": f"{leg_names[leg_idx]}_{joint_names[joint_idx]}",
                        "group": leg_names[leg_idx] + "_leg",
                        "role": joint_names[joint_idx]
                    }
                else:
                    labels[servo_id] = {
                        "label": f"servo_{servo_id}",
                        "group": "other",
                        "role": "unknown"
                    }

        elif robot_type == "hexapod":
            leg_names = ["front_right", "middle_right", "back_right",
                        "back_left", "middle_left", "front_left"]
            joint_names = ["coxa", "femur", "tibia"]

            for i, servo_id in enumerate(sorted(servo_ids)):
                leg_idx = i // 3
                joint_idx = i % 3

                if leg_idx < len(leg_names) and joint_idx < len(joint_names):
                    labels[servo_id] = {
                        "label": f"{leg_names[leg_idx]}_{joint_names[joint_idx]}",
                        "group": leg_names[leg_idx] + "_leg",
                        "role": joint_names[joint_idx]
                    }
                else:
                    labels[servo_id] = {
                        "label": f"servo_{servo_id}",
                        "group": "other",
                        "role": "unknown"
                    }

        elif robot_type == "quadruped_with_arm":
            # 12 leg servos + up to 3 arm servos
            leg_names = ["front_right", "front_left", "back_right", "back_left"]
            joint_names = ["hip", "upper", "lower"]
            arm_joints = ["shoulder", "elbow", "gripper"]

            sorted_ids = sorted(servo_ids)
            for i, servo_id in enumerate(sorted_ids):
                if i < 12:
                    # Leg servos
                    leg_idx = i // 3
                    joint_idx = i % 3
                    labels[servo_id] = {
                        "label": f"{leg_names[leg_idx]}_{joint_names[joint_idx]}",
                        "group": leg_names[leg_idx] + "_leg",
                        "role": joint_names[joint_idx]
                    }
                elif i < 12 + len(arm_joints):
                    # Arm servos
                    arm_idx = i - 12
                    labels[servo_id] = {
                        "label": f"arm_{arm_joints[arm_idx]}",
                        "group": "arm",
                        "role": arm_joints[arm_idx]
                    }
                else:
                    labels[servo_id] = {
                        "label": f"servo_{servo_id}",
                        "group": "other",
                        "role": "unknown"
                    }

        elif robot_type in ("humanoid_basic", "humanoid", "humanoid_advanced", "humanoid_full"):
            # Humanoid labeling - organized by body part
            # Standard humanoid servo layout (varies by manufacturer):
            # - Right arm: shoulder_pitch, shoulder_roll, elbow
            # - Left arm: shoulder_pitch, shoulder_roll, elbow
            # - Right leg: hip_yaw, hip_roll, hip_pitch, knee, ankle_pitch, ankle_roll
            # - Left leg: hip_yaw, hip_roll, hip_pitch, knee, ankle_pitch, ankle_roll
            # - Torso: torso_yaw (optional)
            # - Head: head_pan, head_tilt (optional)

            sorted_ids = sorted(servo_ids)
            num_servos = len(sorted_ids)

            # Define humanoid body parts based on servo count
            if robot_type == "humanoid_basic":
                # 16-17 servos: basic arms (3 each) + legs (5 each)
                body_map = [
                    # Right arm (3)
                    ("right_shoulder_pitch", "right_arm", "shoulder_pitch"),
                    ("right_shoulder_roll", "right_arm", "shoulder_roll"),
                    ("right_elbow", "right_arm", "elbow"),
                    # Left arm (3)
                    ("left_shoulder_pitch", "left_arm", "shoulder_pitch"),
                    ("left_shoulder_roll", "left_arm", "shoulder_roll"),
                    ("left_elbow", "left_arm", "elbow"),
                    # Right leg (5)
                    ("right_hip_roll", "right_leg", "hip_roll"),
                    ("right_hip_pitch", "right_leg", "hip_pitch"),
                    ("right_knee", "right_leg", "knee"),
                    ("right_ankle_pitch", "right_leg", "ankle_pitch"),
                    ("right_ankle_roll", "right_leg", "ankle_roll"),
                    # Left leg (5)
                    ("left_hip_roll", "left_leg", "hip_roll"),
                    ("left_hip_pitch", "left_leg", "hip_pitch"),
                    ("left_knee", "left_leg", "knee"),
                    ("left_ankle_pitch", "left_leg", "ankle_pitch"),
                    ("left_ankle_roll", "left_leg", "ankle_roll"),
                    # Extra (1)
                    ("torso_yaw", "torso", "yaw"),
                ]
            elif robot_type == "humanoid":
                # 18-20 servos: arms (3 each) + legs (6 each) + torso
                body_map = [
                    # Right arm (3)
                    ("right_shoulder_pitch", "right_arm", "shoulder_pitch"),
                    ("right_shoulder_roll", "right_arm", "shoulder_roll"),
                    ("right_elbow", "right_arm", "elbow"),
                    # Left arm (3)
                    ("left_shoulder_pitch", "left_arm", "shoulder_pitch"),
                    ("left_shoulder_roll", "left_arm", "shoulder_roll"),
                    ("left_elbow", "left_arm", "elbow"),
                    # Right leg (6)
                    ("right_hip_yaw", "right_leg", "hip_yaw"),
                    ("right_hip_roll", "right_leg", "hip_roll"),
                    ("right_hip_pitch", "right_leg", "hip_pitch"),
                    ("right_knee", "right_leg", "knee"),
                    ("right_ankle_pitch", "right_leg", "ankle_pitch"),
                    ("right_ankle_roll", "right_leg", "ankle_roll"),
                    # Left leg (6)
                    ("left_hip_yaw", "left_leg", "hip_yaw"),
                    ("left_hip_roll", "left_leg", "hip_roll"),
                    ("left_hip_pitch", "left_leg", "hip_pitch"),
                    ("left_knee", "left_leg", "knee"),
                    ("left_ankle_pitch", "left_leg", "ankle_pitch"),
                    ("left_ankle_roll", "left_leg", "ankle_roll"),
                    # Torso (2)
                    ("torso_yaw", "torso", "yaw"),
                    ("torso_pitch", "torso", "pitch"),
                ]
            elif robot_type == "humanoid_advanced":
                # 21-24 servos: full arms (4 each) + legs (6 each) + torso + head
                body_map = [
                    # Right arm (4)
                    ("right_shoulder_pitch", "right_arm", "shoulder_pitch"),
                    ("right_shoulder_roll", "right_arm", "shoulder_roll"),
                    ("right_shoulder_yaw", "right_arm", "shoulder_yaw"),
                    ("right_elbow", "right_arm", "elbow"),
                    # Left arm (4)
                    ("left_shoulder_pitch", "left_arm", "shoulder_pitch"),
                    ("left_shoulder_roll", "left_arm", "shoulder_roll"),
                    ("left_shoulder_yaw", "left_arm", "shoulder_yaw"),
                    ("left_elbow", "left_arm", "elbow"),
                    # Right leg (6)
                    ("right_hip_yaw", "right_leg", "hip_yaw"),
                    ("right_hip_roll", "right_leg", "hip_roll"),
                    ("right_hip_pitch", "right_leg", "hip_pitch"),
                    ("right_knee", "right_leg", "knee"),
                    ("right_ankle_pitch", "right_leg", "ankle_pitch"),
                    ("right_ankle_roll", "right_leg", "ankle_roll"),
                    # Left leg (6)
                    ("left_hip_yaw", "left_leg", "hip_yaw"),
                    ("left_hip_roll", "left_leg", "hip_roll"),
                    ("left_hip_pitch", "left_leg", "hip_pitch"),
                    ("left_knee", "left_leg", "knee"),
                    ("left_ankle_pitch", "left_leg", "ankle_pitch"),
                    ("left_ankle_roll", "left_leg", "ankle_roll"),
                    # Head (2)
                    ("head_pan", "head", "pan"),
                    ("head_tilt", "head", "tilt"),
                    # Torso (2)
                    ("torso_yaw", "torso", "yaw"),
                    ("torso_pitch", "torso", "pitch"),
                ]
            else:  # humanoid_full
                # 25+ servos: full body with wrists/grippers
                body_map = [
                    # Right arm (6)
                    ("right_shoulder_pitch", "right_arm", "shoulder_pitch"),
                    ("right_shoulder_roll", "right_arm", "shoulder_roll"),
                    ("right_shoulder_yaw", "right_arm", "shoulder_yaw"),
                    ("right_elbow", "right_arm", "elbow"),
                    ("right_wrist_yaw", "right_arm", "wrist_yaw"),
                    ("right_gripper", "right_arm", "gripper"),
                    # Left arm (6)
                    ("left_shoulder_pitch", "left_arm", "shoulder_pitch"),
                    ("left_shoulder_roll", "left_arm", "shoulder_roll"),
                    ("left_shoulder_yaw", "left_arm", "shoulder_yaw"),
                    ("left_elbow", "left_arm", "elbow"),
                    ("left_wrist_yaw", "left_arm", "wrist_yaw"),
                    ("left_gripper", "left_arm", "gripper"),
                    # Right leg (6)
                    ("right_hip_yaw", "right_leg", "hip_yaw"),
                    ("right_hip_roll", "right_leg", "hip_roll"),
                    ("right_hip_pitch", "right_leg", "hip_pitch"),
                    ("right_knee", "right_leg", "knee"),
                    ("right_ankle_pitch", "right_leg", "ankle_pitch"),
                    ("right_ankle_roll", "right_leg", "ankle_roll"),
                    # Left leg (6)
                    ("left_hip_yaw", "left_leg", "hip_yaw"),
                    ("left_hip_roll", "left_leg", "hip_roll"),
                    ("left_hip_pitch", "left_leg", "hip_pitch"),
                    ("left_knee", "left_leg", "knee"),
                    ("left_ankle_pitch", "left_leg", "ankle_pitch"),
                    ("left_ankle_roll", "left_leg", "ankle_roll"),
                    # Head (2)
                    ("head_pan", "head", "pan"),
                    ("head_tilt", "head", "tilt"),
                    # Torso (2)
                    ("torso_yaw", "torso", "yaw"),
                    ("torso_pitch", "torso", "pitch"),
                    # Extra slots for variations
                    ("head_roll", "head", "roll"),
                    ("waist_yaw", "torso", "waist_yaw"),
                ]

            # Apply labels
            for i, servo_id in enumerate(sorted_ids):
                if i < len(body_map):
                    label, group, role = body_map[i]
                    labels[servo_id] = {
                        "label": label,
                        "group": group,
                        "role": role
                    }
                else:
                    labels[servo_id] = {
                        "label": f"extra_{servo_id}",
                        "group": "extra",
                        "role": "unknown"
                    }

        elif robot_type == "6dof_arm":
            # 6-DOF robotic arm
            arm_joints = [
                ("base_rotation", "arm", "base"),
                ("shoulder_pitch", "arm", "shoulder"),
                ("elbow_pitch", "arm", "elbow"),
                ("wrist_pitch", "arm", "wrist_pitch"),
                ("wrist_roll", "arm", "wrist_roll"),
                ("gripper", "arm", "gripper"),
            ]
            for i, servo_id in enumerate(sorted(servo_ids)):
                if i < len(arm_joints):
                    label, group, role = arm_joints[i]
                    labels[servo_id] = {"label": label, "group": group, "role": role}
                else:
                    labels[servo_id] = {"label": f"servo_{servo_id}", "group": "extra", "role": "unknown"}

        else:
            # Generic numbering for custom/unknown types
            for servo_id in servo_ids:
                labels[servo_id] = {
                    "label": f"servo_{servo_id}",
                    "group": "main",
                    "role": "actuator"
                }

        return labels

    def interactive_label_session(self,
                                   robot_profile: RobotProfile,
                                   protocol_handler: ServoProtocolHandler) -> RobotProfile:
        """Run interactive labeling session with AI assistance."""

        WizardUI.print_header("AI-Assisted Component Labeling")

        # Suggest robot type based on servo count and ID distribution
        servo_ids = [a.id for a in robot_profile.actuators]
        suggested_type = self.suggest_robot_type(len(servo_ids), servo_ids)

        # Show detection info
        core_count = self._count_core_servos(servo_ids)
        if core_count < len(servo_ids):
            WizardUI.print_info(f"Found {len(servo_ids)} servos total, {core_count} appear to be main actuators")
        WizardUI.print_info(f"Detected robot type: {suggested_type}")
        robot_type = WizardUI.prompt("Robot type", suggested_type)
        robot_profile.robot_type = robot_type

        # Get suggested labels
        suggested_labels = self.suggest_labels(robot_type, servo_ids)

        # Separate core and peripheral servos for display
        core_servo_ids = [id for id in servo_ids if id <= 15 or suggested_labels.get(id, {}).get('group') != 'other']
        peripheral_servo_ids = [id for id in servo_ids if id not in core_servo_ids]

        print("\nSuggested servo labels (main actuators):")
        print("-" * 50)

        for servo_id in sorted(core_servo_ids):
            if servo_id in suggested_labels:
                s = suggested_labels[servo_id]
                print(f"  Servo {servo_id:2d}: {s['label']} ({s['group']}/{s['role']})")

        if peripheral_servo_ids:
            print(f"\n  + {len(peripheral_servo_ids)} peripheral servos (IDs: {min(peripheral_servo_ids)}-{max(peripheral_servo_ids)})")

        # Offer three options
        print("\nHow would you like to proceed?")
        options = [
            "Accept suggested labels",
            "🔍 Verify interactively (wiggle each servo to confirm)",
            "Label manually from scratch"
        ]
        choice = WizardUI.select("Choose an option:", options)

        if not choice:
            choice = [0]  # Default to accept

        if choice[0] == 0:
            # Accept suggested labels
            for actuator in robot_profile.actuators:
                if actuator.id in suggested_labels:
                    actuator.label = suggested_labels[actuator.id]['label']
                    actuator.group = suggested_labels[actuator.id]['group']
                    actuator.role = suggested_labels[actuator.id]['role']

        elif choice[0] == 1:
            # Interactive verification - wiggle each core servo
            WizardUI.print_info("Interactive verification mode")
            WizardUI.print_info("I'll wiggle each servo - press Enter to confirm or type a new label\n")

            # Group actuators by suggested group for organized verification
            groups_order = ['front_right_leg', 'front_left_leg', 'back_right_leg', 'back_left_leg', 'arm', 'other']
            actuators_by_group = {}
            for actuator in robot_profile.actuators:
                group = suggested_labels.get(actuator.id, {}).get('group', 'other')
                if group not in actuators_by_group:
                    actuators_by_group[group] = []
                actuators_by_group[group].append(actuator)

            for group in groups_order:
                if group not in actuators_by_group:
                    continue

                actuators = actuators_by_group[group]
                if group == 'other' and len(actuators) > 5:
                    # Skip bulk peripheral servos
                    WizardUI.print_info(f"\nSkipping {len(actuators)} peripheral servos in '{group}' group")
                    for actuator in actuators:
                        actuator.label = f"servo_{actuator.id}"
                        actuator.group = "other"
                        actuator.role = "unknown"
                    continue

                print(f"\n--- {group.replace('_', ' ').title()} ---")

                for actuator in actuators:
                    suggestion = suggested_labels.get(actuator.id, {})
                    default_label = suggestion.get('label', f'servo_{actuator.id}')

                    # Wiggle the servo
                    print(f"\n  Servo {actuator.id}: Wiggling... ", end='', flush=True)
                    try:
                        current_pos = protocol_handler.read_position(actuator.id) or 500
                        protocol_handler.move_servo(actuator.id, current_pos + 60, 150)
                        time.sleep(0.2)
                        protocol_handler.move_servo(actuator.id, current_pos - 60, 150)
                        time.sleep(0.2)
                        protocol_handler.move_servo(actuator.id, current_pos, 150)
                        time.sleep(0.2)
                        print("done")
                    except Exception as e:
                        print(f"(error: {e})")

                    # Ask for confirmation
                    user_label = WizardUI.prompt(f"  Label [{default_label}]", "")
                    actuator.label = user_label if user_label else default_label
                    actuator.group = suggestion.get('group', 'main')
                    actuator.role = suggestion.get('role', 'actuator')

        else:
            # Full manual labeling
            WizardUI.print_info("Manual labeling mode")
            WizardUI.print_info("I'll wiggle each servo so you can identify and label it.\n")

            for actuator in robot_profile.actuators:
                print(f"\n--- Servo ID {actuator.id} ---")

                if WizardUI.confirm("Wiggle this servo?", default=True):
                    try:
                        current_pos = protocol_handler.read_position(actuator.id) or 500
                        protocol_handler.move_servo(actuator.id, current_pos + 50, 200)
                        time.sleep(0.3)
                        protocol_handler.move_servo(actuator.id, current_pos - 50, 200)
                        time.sleep(0.3)
                        protocol_handler.move_servo(actuator.id, current_pos, 200)
                        time.sleep(0.3)
                    except Exception:
                        pass

                default_label = suggested_labels.get(actuator.id, {}).get('label', f'servo_{actuator.id}')
                actuator.label = WizardUI.prompt("Label", default_label)
                actuator.group = WizardUI.prompt("Group (e.g., left_leg, arm)",
                                                  suggested_labels.get(actuator.id, {}).get('group', 'main'))
                actuator.role = WizardUI.prompt("Role (e.g., hip, knee, shoulder)",
                                                 suggested_labels.get(actuator.id, {}).get('role', 'actuator'))

        # Build groups
        robot_profile.groups = {}
        for actuator in robot_profile.actuators:
            if actuator.group not in robot_profile.groups:
                robot_profile.groups[actuator.group] = []
            robot_profile.groups[actuator.group].append(actuator.id)

        return robot_profile


class PrimitiveSkillGenerator:
    """Generates Python code and JSON definitions for primitive skills."""

    def __init__(self, robot_profile: RobotProfile):
        self.profile = robot_profile
        self.generated_primitives: List[Dict[str, Any]] = []  # Track for batch push

    def generate_protocol_definition(self) -> Dict[str, Any]:
        """Generate protocol.json definition."""
        return {
            "version": "1.0",
            "robot_model": self.profile.name,
            "robot_type": self.profile.robot_type,
            "manufacturer": self.profile.manufacturer,
            "model": self.profile.model,
            "transport": {
                "type": "serial",
                "port": self.profile.device.port if self.profile.device else "",
                "baud_rate": self.profile.device.baud_rate if self.profile.device else 115200,
                "protocol": self.profile.device.detected_protocol.value if self.profile.device and self.profile.device.detected_protocol else "hiwonder"
            },
            "actuators": [
                {
                    "id": a.id,
                    "label": a.label,
                    "group": a.group,
                    "role": a.role,
                    "type": a.actuator_type.value,
                    "characteristics": asdict(a.characteristics)
                }
                for a in self.profile.actuators
            ],
            "groups": self.profile.groups,
            "created_at": self.profile.created_at,
            "wizard_version": self.profile.wizard_version
        }

    def generate_servo_map(self) -> str:
        """Generate Python servo map code."""
        lines = [
            '"""',
            f'Servo map for {self.profile.name}',
            f'Generated by ate robot-setup wizard',
            f'Robot type: {self.profile.robot_type}',
            '"""',
            '',
            'from enum import IntEnum',
            '',
            '',
            'class ServoID(IntEnum):',
            '    """Servo IDs mapped to descriptive names."""',
        ]

        for actuator in sorted(self.profile.actuators, key=lambda a: a.id):
            name = actuator.label.upper().replace(' ', '_').replace('-', '_')
            lines.append(f'    {name} = {actuator.id}')

        lines.extend([
            '',
            '',
            '# Servo groups',
        ])

        for group_name, servo_ids in self.profile.groups.items():
            var_name = group_name.upper().replace(' ', '_').replace('-', '_')
            servo_names = [f'ServoID.{self.profile.actuators[i].label.upper().replace(" ", "_").replace("-", "_")}'
                          for i, a in enumerate(self.profile.actuators) if a.id in servo_ids]
            lines.append(f'{var_name} = [{", ".join(servo_names)}]')

        lines.extend([
            '',
            '',
            '# All servos',
            f'ALL_SERVOS = list(ServoID)',
            '',
            '',
            '# Servo characteristics',
            'SERVO_LIMITS = {',
        ])

        for actuator in self.profile.actuators:
            chars = actuator.characteristics
            lines.append(f'    ServoID.{actuator.label.upper().replace(" ", "_").replace("-", "_")}: {{')
            lines.append(f'        "min": {chars.position_min},')
            lines.append(f'        "max": {chars.position_max},')
            lines.append(f'        "center": {chars.position_center},')
            lines.append(f'    }},')

        lines.append('}')

        return '\n'.join(lines)

    def generate_primitives(self) -> str:
        """Generate primitive skill code."""
        lines = [
            '"""',
            f'Primitive skills for {self.profile.name}',
            f'Generated by ate robot-setup wizard',
            '"""',
            '',
            'import time',
            'from typing import List, Dict, Optional',
            'from dataclasses import dataclass',
            '',
            'from .servo_map import ServoID, SERVO_LIMITS, ALL_SERVOS',
            '',
            '',
            '@dataclass',
            'class ServoCommand:',
            '    """Command for a single servo."""',
            '    servo_id: int',
            '    position: int',
            '    time_ms: int = 500',
            '',
            '',
            'class PrimitiveSkills:',
            '    """Low-level primitive skills for the robot."""',
            '',
            '    def __init__(self, robot_controller):',
            '        """',
            '        Args:',
            '            robot_controller: Controller with move_servo(), read_position() methods',
            '        """',
            '        self.controller = robot_controller',
            '',
            '    def move_servo(self, servo_id: ServoID, position: int, time_ms: int = 500):',
            '        """Move a single servo to position."""',
            '        limits = SERVO_LIMITS.get(servo_id, {"min": 0, "max": 1000})',
            '        position = max(limits["min"], min(limits["max"], position))',
            '        self.controller.move_servo(servo_id, position, time_ms)',
            '',
            '    def move_servos(self, commands: List[ServoCommand]):',
            '        """Move multiple servos simultaneously."""',
            '        for cmd in commands:',
            '            limits = SERVO_LIMITS.get(cmd.servo_id, {"min": 0, "max": 1000})',
            '            pos = max(limits["min"], min(limits["max"], cmd.position))',
            '            self.controller.move_servo(cmd.servo_id, pos, cmd.time_ms)',
            '',
            '    def home(self):',
            '        """Move all servos to center/home position."""',
            '        commands = [',
            '            ServoCommand(servo_id, SERVO_LIMITS[servo_id]["center"])',
            '            for servo_id in ALL_SERVOS',
            '        ]',
            '        self.move_servos(commands)',
            '',
            '    def read_positions(self) -> Dict[ServoID, int]:',
            '        """Read all servo positions."""',
            '        positions = {}',
            '        for servo_id in ALL_SERVOS:',
            '            pos = self.controller.read_position(servo_id)',
            '            if pos is not None:',
            '                positions[servo_id] = pos',
            '        return positions',
            '',
        ]

        # Add group-specific methods
        for group_name, servo_ids in self.profile.groups.items():
            method_name = group_name.lower().replace(' ', '_').replace('-', '_')
            group_var = group_name.upper().replace(' ', '_').replace('-', '_')

            lines.extend([
                f'    def move_{method_name}(self, positions: Dict[ServoID, int], time_ms: int = 500):',
                f'        """Move {group_name} servos."""',
                f'        commands = [',
                f'            ServoCommand(servo_id, pos, time_ms)',
                f'            for servo_id, pos in positions.items()',
                f'            if servo_id in {group_var}',
                f'        ]',
                f'        self.move_servos(commands)',
                '',
            ])

        return '\n'.join(lines)

    def generate_primitive_jsons(self, output_dir: Path) -> List[str]:
        """Generate .primitive.json files for CLI push workflow.

        This is the PostHog-style auto-generation - from discovered hardware
        we automatically create a comprehensive library of primitive skills.
        """
        primitives_dir = output_dir / "primitives"
        primitives_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []
        self.generated_primitives = []

        device = self.profile.device
        protocol_type = device.detected_protocol.value if device and device.detected_protocol else "hiwonder"
        baud_rate = device.baud_rate if device else 115200

        # ====================================================================
        # 1. Per-Servo Primitives - Direct control of each labeled actuator
        # ====================================================================
        for actuator in self.profile.actuators:
            chars = actuator.characteristics

            # move_<label>(position, speed) - Move servo to absolute position
            primitive = {
                "name": f"move_{actuator.label}",
                "description": f"Move {actuator.label.replace('_', ' ')} servo to specified position",
                "category": "motion",
                "commandType": "single",
                "commandTemplate": self._build_move_command(actuator.id, protocol_type),
                "parameters": {
                    "position": {
                        "type": "integer",
                        "min": chars.position_min,
                        "max": chars.position_max,
                        "default": chars.position_center,
                        "description": f"Target position ({chars.position_min}-{chars.position_max})"
                    },
                    "time_ms": {
                        "type": "integer",
                        "min": 0,
                        "max": 5000,
                        "default": 500,
                        "description": "Movement duration in milliseconds"
                    }
                },
                "servoId": actuator.id,
                "group": actuator.group,
                "role": actuator.role,
                "protocol": {
                    "type": protocol_type,
                    "baudRate": baud_rate
                },
                "robotModel": self.profile.name,
                "robotType": self.profile.robot_type,
                "executionTimeMs": 500,
                "settleTimeMs": 100,
                "safetyNotes": f"Ensure {actuator.label} has clearance before moving"
            }

            filename = f"move_{actuator.label}.primitive.json"
            filepath = primitives_dir / filename
            with open(filepath, 'w') as f:
                json.dump(primitive, f, indent=2)
            generated_files.append(str(filepath))
            self.generated_primitives.append(primitive)

            # center_<label>() - Move to center/home position
            center_primitive = {
                "name": f"center_{actuator.label}",
                "description": f"Move {actuator.label.replace('_', ' ')} to center position",
                "category": "motion",
                "commandType": "single",
                "commandTemplate": self._build_move_command(actuator.id, protocol_type, chars.position_center),
                "parameters": {
                    "time_ms": {
                        "type": "integer",
                        "min": 0,
                        "max": 5000,
                        "default": 500,
                        "description": "Movement duration in milliseconds"
                    }
                },
                "servoId": actuator.id,
                "protocol": {"type": protocol_type, "baudRate": baud_rate},
                "robotModel": self.profile.name,
                "robotType": self.profile.robot_type
            }

            filename = f"center_{actuator.label}.primitive.json"
            filepath = primitives_dir / filename
            with open(filepath, 'w') as f:
                json.dump(center_primitive, f, indent=2)
            generated_files.append(str(filepath))
            self.generated_primitives.append(center_primitive)

        # ====================================================================
        # 2. Group Primitives - Coordinated control of actuator groups
        # ====================================================================
        for group_name, servo_ids in self.profile.groups.items():
            if group_name in ('other', 'extra'):
                continue  # Skip misc groups

            group_actuators = [a for a in self.profile.actuators if a.id in servo_ids]

            # move_<group>(positions) - Move all servos in group
            group_primitive = {
                "name": f"move_{group_name}",
                "description": f"Move all servos in {group_name.replace('_', ' ')} group",
                "category": "motion",
                "commandType": "sequence",
                "commandTemplate": json.dumps([
                    {"servoId": a.id, "position": "${" + a.role + "_position}", "time_ms": "${time_ms}"}
                    for a in group_actuators
                ]),
                "parameters": {
                    **{
                        f"{a.role}_position": {
                            "type": "integer",
                            "min": a.characteristics.position_min,
                            "max": a.characteristics.position_max,
                            "default": a.characteristics.position_center,
                            "description": f"{a.role} servo position"
                        }
                        for a in group_actuators
                    },
                    "time_ms": {
                        "type": "integer",
                        "min": 0,
                        "max": 5000,
                        "default": 500,
                        "description": "Movement duration"
                    }
                },
                "servoIds": servo_ids,
                "group": group_name,
                "protocol": {"type": protocol_type, "baudRate": baud_rate},
                "robotModel": self.profile.name,
                "robotType": self.profile.robot_type,
                "executionTimeMs": 500,
                "settleTimeMs": 200
            }

            filename = f"move_{group_name}.primitive.json"
            filepath = primitives_dir / filename
            with open(filepath, 'w') as f:
                json.dump(group_primitive, f, indent=2)
            generated_files.append(str(filepath))
            self.generated_primitives.append(group_primitive)

            # home_<group>() - Move all servos in group to center
            home_group = {
                "name": f"home_{group_name}",
                "description": f"Move all {group_name.replace('_', ' ')} servos to home position",
                "category": "motion",
                "commandType": "sequence",
                "commandTemplate": json.dumps([
                    {"servoId": a.id, "position": a.characteristics.position_center, "time_ms": 500}
                    for a in group_actuators
                ]),
                "parameters": {},
                "servoIds": servo_ids,
                "group": group_name,
                "protocol": {"type": protocol_type, "baudRate": baud_rate},
                "robotModel": self.profile.name,
                "robotType": self.profile.robot_type
            }

            filename = f"home_{group_name}.primitive.json"
            filepath = primitives_dir / filename
            with open(filepath, 'w') as f:
                json.dump(home_group, f, indent=2)
            generated_files.append(str(filepath))
            self.generated_primitives.append(home_group)

        # ====================================================================
        # 3. Utility Primitives - System-wide control
        # ====================================================================
        all_servo_ids = [a.id for a in self.profile.actuators]

        # home_all() - All servos to center
        home_all = {
            "name": "home_all",
            "description": "Move all servos to their center/home positions",
            "category": "motion",
            "commandType": "sequence",
            "commandTemplate": json.dumps([
                {"servoId": a.id, "position": a.characteristics.position_center, "time_ms": 800}
                for a in self.profile.actuators
            ]),
            "parameters": {},
            "servoIds": all_servo_ids,
            "protocol": {"type": protocol_type, "baudRate": baud_rate},
            "robotModel": self.profile.name,
            "robotType": self.profile.robot_type,
            "executionTimeMs": 1000,
            "settleTimeMs": 500,
            "safetyNotes": "Ensure robot has clearance. May cause significant movement."
        }

        filepath = primitives_dir / "home_all.primitive.json"
        with open(filepath, 'w') as f:
            json.dump(home_all, f, indent=2)
        generated_files.append(str(filepath))
        self.generated_primitives.append(home_all)

        # disable_torque() - Release all servos
        disable_torque = {
            "name": "disable_torque",
            "description": "Disable torque on all servos (robot goes limp)",
            "category": "safety",
            "commandType": "sequence",
            "commandTemplate": json.dumps([
                {"servoId": a.id, "command": "disable_torque"}
                for a in self.profile.actuators
            ]),
            "parameters": {},
            "servoIds": all_servo_ids,
            "protocol": {"type": protocol_type, "baudRate": baud_rate},
            "robotModel": self.profile.name,
            "robotType": self.profile.robot_type,
            "safetyNotes": "Robot will go limp. Ensure it is supported."
        }

        filepath = primitives_dir / "disable_torque.primitive.json"
        with open(filepath, 'w') as f:
            json.dump(disable_torque, f, indent=2)
        generated_files.append(str(filepath))
        self.generated_primitives.append(disable_torque)

        # enable_torque() - Enable all servos
        enable_torque = {
            "name": "enable_torque",
            "description": "Enable torque on all servos",
            "category": "safety",
            "commandType": "sequence",
            "commandTemplate": json.dumps([
                {"servoId": a.id, "command": "enable_torque"}
                for a in self.profile.actuators
            ]),
            "parameters": {},
            "servoIds": all_servo_ids,
            "protocol": {"type": protocol_type, "baudRate": baud_rate},
            "robotModel": self.profile.name,
            "robotType": self.profile.robot_type
        }

        filepath = primitives_dir / "enable_torque.primitive.json"
        with open(filepath, 'w') as f:
            json.dump(enable_torque, f, indent=2)
        generated_files.append(str(filepath))
        self.generated_primitives.append(enable_torque)

        # read_all_positions() - Read state of all servos
        read_positions = {
            "name": "read_all_positions",
            "description": "Read current positions of all servos",
            "category": "sensing",
            "commandType": "sequence",
            "commandTemplate": json.dumps([
                {"servoId": a.id, "command": "read_position"}
                for a in self.profile.actuators
            ]),
            "parameters": {},
            "servoIds": all_servo_ids,
            "protocol": {"type": protocol_type, "baudRate": baud_rate},
            "robotModel": self.profile.name,
            "robotType": self.profile.robot_type
        }

        filepath = primitives_dir / "read_all_positions.primitive.json"
        with open(filepath, 'w') as f:
            json.dump(read_positions, f, indent=2)
        generated_files.append(str(filepath))
        self.generated_primitives.append(read_positions)

        # ====================================================================
        # 4. Robot-Type Specific Poses
        # ====================================================================
        generated_files.extend(self._generate_pose_primitives(primitives_dir, protocol_type, baud_rate))

        return generated_files

    def _build_move_command(self, servo_id: int, protocol: str, fixed_position: Optional[int] = None) -> str:
        """Build command template for moving a servo."""
        if protocol == "hiwonder":
            if fixed_position is not None:
                return json.dumps({
                    "servoId": servo_id,
                    "position": fixed_position,
                    "time_ms": "${time_ms}"
                })
            return json.dumps({
                "servoId": servo_id,
                "position": "${position}",
                "time_ms": "${time_ms}"
            })
        # Generic fallback
        if fixed_position is not None:
            return f"MOVE {servo_id} {fixed_position} ${{time_ms}}"
        return f"MOVE {servo_id} ${{position}} ${{time_ms}}"

    def _generate_pose_primitives(self, output_dir: Path, protocol: str, baud_rate: int) -> List[str]:
        """Generate robot-type specific pose primitives."""
        generated_files = []
        robot_type = self.profile.robot_type

        if robot_type == "quadruped":
            poses = self._generate_quadruped_poses()
        elif robot_type in ("humanoid", "humanoid_basic", "humanoid_advanced", "humanoid_full"):
            poses = self._generate_humanoid_poses()
        elif robot_type == "6dof_arm":
            poses = self._generate_arm_poses()
        else:
            poses = []

        for pose in poses:
            pose["protocol"] = {"type": protocol, "baudRate": baud_rate}
            pose["robotModel"] = self.profile.name
            pose["robotType"] = self.profile.robot_type

            filename = f"{pose['name']}.primitive.json"
            filepath = output_dir / filename
            with open(filepath, 'w') as f:
                json.dump(pose, f, indent=2)
            generated_files.append(str(filepath))
            self.generated_primitives.append(pose)

        return generated_files

    def _generate_quadruped_poses(self) -> List[Dict[str, Any]]:
        """Generate poses for quadruped robots."""
        poses = []

        # Find leg groups
        leg_groups = [g for g in self.profile.groups.keys() if 'leg' in g.lower()]

        if not leg_groups:
            return poses

        # stand - All legs at standing position
        stand_commands = []
        for actuator in self.profile.actuators:
            if 'leg' in actuator.group.lower():
                # For standing: hips at center, upper legs forward, lower legs back
                if 'hip' in actuator.role:
                    pos = actuator.characteristics.position_center
                elif 'upper' in actuator.role:
                    pos = actuator.characteristics.position_center + 100
                elif 'lower' in actuator.role:
                    pos = actuator.characteristics.position_center - 100
                else:
                    pos = actuator.characteristics.position_center
                stand_commands.append({"servoId": actuator.id, "position": pos, "time_ms": 800})

        poses.append({
            "name": "stand",
            "description": "Move to standing pose with all legs extended",
            "category": "pose",
            "commandType": "sequence",
            "commandTemplate": json.dumps(stand_commands),
            "parameters": {},
            "servoIds": [a.id for a in self.profile.actuators if 'leg' in a.group.lower()],
            "executionTimeMs": 1000,
            "settleTimeMs": 500
        })

        # crouch - Low stance
        crouch_commands = []
        for actuator in self.profile.actuators:
            if 'leg' in actuator.group.lower():
                if 'hip' in actuator.role:
                    pos = actuator.characteristics.position_center
                elif 'upper' in actuator.role:
                    pos = actuator.characteristics.position_center + 200
                elif 'lower' in actuator.role:
                    pos = actuator.characteristics.position_center - 200
                else:
                    pos = actuator.characteristics.position_center
                crouch_commands.append({"servoId": actuator.id, "position": pos, "time_ms": 600})

        poses.append({
            "name": "crouch",
            "description": "Move to crouched/low stance",
            "category": "pose",
            "commandType": "sequence",
            "commandTemplate": json.dumps(crouch_commands),
            "parameters": {},
            "servoIds": [a.id for a in self.profile.actuators if 'leg' in a.group.lower()],
            "executionTimeMs": 800,
            "settleTimeMs": 300
        })

        # sit - Sitting pose (back legs tucked)
        sit_commands = []
        for actuator in self.profile.actuators:
            if 'back' in actuator.group.lower() and 'leg' in actuator.group.lower():
                # Back legs tucked under
                if 'upper' in actuator.role:
                    pos = actuator.characteristics.position_center + 300
                elif 'lower' in actuator.role:
                    pos = actuator.characteristics.position_center - 300
                else:
                    pos = actuator.characteristics.position_center
            elif 'front' in actuator.group.lower() and 'leg' in actuator.group.lower():
                # Front legs extended
                if 'upper' in actuator.role:
                    pos = actuator.characteristics.position_center
                else:
                    pos = actuator.characteristics.position_center
            else:
                continue
            sit_commands.append({"servoId": actuator.id, "position": pos, "time_ms": 800})

        if sit_commands:
            poses.append({
                "name": "sit",
                "description": "Move to sitting pose with back legs tucked",
                "category": "pose",
                "commandType": "sequence",
                "commandTemplate": json.dumps(sit_commands),
                "parameters": {},
                "servoIds": [c["servoId"] for c in sit_commands],
                "executionTimeMs": 1000,
                "settleTimeMs": 500
            })

        return poses

    def _generate_humanoid_poses(self) -> List[Dict[str, Any]]:
        """Generate poses for humanoid robots."""
        poses = []

        # t_pose - Arms out, standing straight
        t_pose_commands = []
        for actuator in self.profile.actuators:
            if 'arm' in actuator.group.lower():
                # Arms out horizontal
                if 'shoulder_pitch' in actuator.role:
                    pos = actuator.characteristics.position_center
                elif 'shoulder_roll' in actuator.role:
                    pos = actuator.characteristics.position_max - 100  # Arms out
                elif 'elbow' in actuator.role:
                    pos = actuator.characteristics.position_center  # Straight
                else:
                    pos = actuator.characteristics.position_center
            elif 'leg' in actuator.group.lower():
                pos = actuator.characteristics.position_center  # Standing straight
            else:
                pos = actuator.characteristics.position_center
            t_pose_commands.append({"servoId": actuator.id, "position": pos, "time_ms": 1000})

        poses.append({
            "name": "t_pose",
            "description": "T-pose: arms out horizontal, standing straight",
            "category": "pose",
            "commandType": "sequence",
            "commandTemplate": json.dumps(t_pose_commands),
            "parameters": {},
            "servoIds": [a.id for a in self.profile.actuators],
            "executionTimeMs": 1200,
            "settleTimeMs": 500,
            "safetyNotes": "Ensure clearance for arm movement"
        })

        # arms_down - Relaxed standing
        arms_down_commands = []
        for actuator in self.profile.actuators:
            if 'arm' in actuator.group.lower():
                if 'shoulder_roll' in actuator.role:
                    pos = actuator.characteristics.position_center  # Arms at sides
                elif 'elbow' in actuator.role:
                    pos = actuator.characteristics.position_center + 50  # Slightly bent
                else:
                    pos = actuator.characteristics.position_center
            else:
                pos = actuator.characteristics.position_center
            arms_down_commands.append({"servoId": actuator.id, "position": pos, "time_ms": 800})

        poses.append({
            "name": "arms_down",
            "description": "Relaxed stance with arms at sides",
            "category": "pose",
            "commandType": "sequence",
            "commandTemplate": json.dumps(arms_down_commands),
            "parameters": {},
            "servoIds": [a.id for a in self.profile.actuators],
            "executionTimeMs": 1000,
            "settleTimeMs": 300
        })

        # wave_ready - One arm up, ready to wave
        wave_commands = []
        for actuator in self.profile.actuators:
            if 'right_arm' in actuator.group.lower():
                if 'shoulder_pitch' in actuator.role:
                    pos = actuator.characteristics.position_max - 200  # Arm up
                elif 'shoulder_roll' in actuator.role:
                    pos = actuator.characteristics.position_center + 100
                elif 'elbow' in actuator.role:
                    pos = actuator.characteristics.position_center - 100  # Bent
                else:
                    pos = actuator.characteristics.position_center
                wave_commands.append({"servoId": actuator.id, "position": pos, "time_ms": 600})

        if wave_commands:
            poses.append({
                "name": "wave_ready",
                "description": "Right arm raised, ready to wave",
                "category": "pose",
                "commandType": "sequence",
                "commandTemplate": json.dumps(wave_commands),
                "parameters": {},
                "servoIds": [c["servoId"] for c in wave_commands],
                "executionTimeMs": 800,
                "settleTimeMs": 200
            })

        return poses

    def _generate_arm_poses(self) -> List[Dict[str, Any]]:
        """Generate poses for robotic arms."""
        poses = []

        # home_arm - Safe home position
        home_commands = [
            {"servoId": a.id, "position": a.characteristics.position_center, "time_ms": 1000}
            for a in self.profile.actuators
        ]

        poses.append({
            "name": "home_arm",
            "description": "Move arm to safe home position",
            "category": "pose",
            "commandType": "sequence",
            "commandTemplate": json.dumps(home_commands),
            "parameters": {},
            "servoIds": [a.id for a in self.profile.actuators],
            "executionTimeMs": 1200,
            "settleTimeMs": 500
        })

        # gripper_open
        gripper = next((a for a in self.profile.actuators if 'gripper' in a.label.lower()), None)
        if gripper:
            poses.append({
                "name": "gripper_open",
                "description": "Open the gripper fully",
                "category": "gripper",
                "commandType": "single",
                "commandTemplate": json.dumps({
                    "servoId": gripper.id,
                    "position": gripper.characteristics.position_max,
                    "time_ms": 300
                }),
                "parameters": {},
                "servoIds": [gripper.id],
                "executionTimeMs": 400,
                "settleTimeMs": 100
            })

            poses.append({
                "name": "gripper_close",
                "description": "Close the gripper fully",
                "category": "gripper",
                "commandType": "single",
                "commandTemplate": json.dumps({
                    "servoId": gripper.id,
                    "position": gripper.characteristics.position_min,
                    "time_ms": 300
                }),
                "parameters": {},
                "servoIds": [gripper.id],
                "executionTimeMs": 400,
                "settleTimeMs": 100
            })

        # reach_forward - Extend arm forward
        reach_commands = []
        for actuator in self.profile.actuators:
            if 'base' in actuator.role:
                pos = actuator.characteristics.position_center
            elif 'shoulder' in actuator.role:
                pos = actuator.characteristics.position_center + 150
            elif 'elbow' in actuator.role:
                pos = actuator.characteristics.position_center - 100
            elif 'wrist' in actuator.role:
                pos = actuator.characteristics.position_center
            else:
                pos = actuator.characteristics.position_center
            reach_commands.append({"servoId": actuator.id, "position": pos, "time_ms": 800})

        poses.append({
            "name": "reach_forward",
            "description": "Extend arm forward for picking",
            "category": "pose",
            "commandType": "sequence",
            "commandTemplate": json.dumps(reach_commands),
            "parameters": {},
            "servoIds": [a.id for a in self.profile.actuators],
            "executionTimeMs": 1000,
            "settleTimeMs": 300
        })

        return poses

    def generate_all(self, output_dir: Path) -> List[str]:
        """Generate all files to output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []

        # protocol.json
        protocol_path = output_dir / "protocol.json"
        with open(protocol_path, 'w') as f:
            json.dump(self.generate_protocol_definition(), f, indent=2)
        generated_files.append(str(protocol_path))

        # servo_map.py
        servo_map_path = output_dir / "servo_map.py"
        with open(servo_map_path, 'w') as f:
            f.write(self.generate_servo_map())
        generated_files.append(str(servo_map_path))

        # primitives.py
        primitives_path = output_dir / "primitives.py"
        with open(primitives_path, 'w') as f:
            f.write(self.generate_primitives())
        generated_files.append(str(primitives_path))

        # __init__.py
        init_path = output_dir / "__init__.py"
        with open(init_path, 'w') as f:
            f.write(f'"""Generated robot package for {self.profile.name}."""\n')
            f.write('from .servo_map import ServoID, SERVO_LIMITS, ALL_SERVOS\n')
            f.write('from .primitives import PrimitiveSkills, ServoCommand\n')
        generated_files.append(str(init_path))

        # Generate .primitive.json files for CLI workflow
        # This is the PostHog-style auto-generation from discovered hardware
        primitive_json_files = self.generate_primitive_jsons(output_dir)
        generated_files.extend(primitive_json_files)

        return generated_files


class RobotSetupWizard:
    """Main wizard orchestrator."""

    TOTAL_STEPS = 5

    def __init__(self, output_dir: str = "./robot"):
        self.output_dir = Path(output_dir)
        self.profile = RobotProfile()
        self.protocol_handler: Optional[ServoProtocolHandler] = None
        self.ai_assistant = AILabelingAssistant()

    def run(self,
            port: Optional[str] = None,
            skip_labeling: bool = False,
            robot_type: Optional[str] = None,
            non_interactive: bool = False,
            push: bool = False,
            api_url: Optional[str] = None) -> bool:
        """Run the complete setup wizard.

        Args:
            port: Serial port to use (skip device selection)
            skip_labeling: Skip labeling (use generic names)
            robot_type: Force robot type (uses AI-suggested labels for that type)
            non_interactive: Run without user prompts
            push: Auto-push primitives to FoodforThought (skip confirmation)
            api_url: FoodforThought API URL (defaults to production)
        """

        WizardUI.print_header("Robot Setup Wizard")
        print("This wizard will help you set up primitive skills for your robot.\n")

        if not non_interactive:
            print("Requirements:")
            print("  - Robot connected via USB/serial")
            print("  - Robot powered on")
            print("  - Servos in safe position (not bearing load)\n")

            if not WizardUI.confirm("Ready to begin?"):
                return False

        try:
            # Step 1: Device Discovery
            WizardUI.print_step(1, self.TOTAL_STEPS, "Device Discovery")

            if port:
                device = DiscoveredDevice(port=port, device_type=DeviceType.SERIAL)
            else:
                device = self._discover_device(non_interactive=non_interactive)

            if not device:
                WizardUI.print_error("No device selected. Aborting.")
                return False

            self.profile.device = device
            WizardUI.print_success(f"Using device: {device.port}")

            # Step 2: Protocol Detection & Connection
            WizardUI.print_step(2, self.TOTAL_STEPS, "Protocol Detection")

            if not self._connect_and_detect_protocol(device, non_interactive=non_interactive):
                return False

            # Step 3: Servo Enumeration
            WizardUI.print_step(3, self.TOTAL_STEPS, "Servo Enumeration")

            if not self._enumerate_servos():
                return False

            # Step 4: Component Labeling
            WizardUI.print_step(4, self.TOTAL_STEPS, "Component Labeling")

            if skip_labeling:
                # Apply generic labels
                for actuator in self.profile.actuators:
                    actuator.label = f"servo_{actuator.id}"
                    actuator.group = "main"
                    actuator.role = "actuator"
            elif robot_type or non_interactive:
                # Apply AI-suggested labels for specified or detected robot type
                self._auto_label_components(robot_type)
            else:
                # Interactive labeling
                self._label_components()

            # Step 5: Generate Primitive Skills
            WizardUI.print_step(5, self.TOTAL_STEPS, "Primitive Skill Generation")

            self._generate_output(auto_push=push, api_url=api_url)

            WizardUI.print_header("Setup Complete!")
            WizardUI.print_success(f"Generated files in: {self.output_dir}")

            return True

        except KeyboardInterrupt:
            print("\n")
            WizardUI.print_warning("Setup cancelled by user.")
            return False
        except Exception as e:
            WizardUI.print_error(f"Setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.protocol_handler:
                self.protocol_handler.disconnect()

    def _discover_device(self, non_interactive: bool = False) -> Optional[DiscoveredDevice]:
        """Discover and select communication device."""
        if not HAS_SERIAL:
            WizardUI.print_error("pyserial not installed. Run: pip install pyserial")
            return None

        WizardUI.print_info("Scanning for serial ports...")

        ports = list(serial.tools.list_ports.comports())

        if not ports:
            WizardUI.print_warning("No serial ports found.")
            if non_interactive:
                return None
            manual_port = WizardUI.prompt("Enter port manually (or press Enter to abort)")
            if manual_port:
                return DiscoveredDevice(port=manual_port, device_type=DeviceType.SERIAL)
            return None

        # Build device list
        devices = []
        for port in ports:
            device = DiscoveredDevice(
                port=port.device,
                device_type=DeviceType.SERIAL,
                description=port.description,
                vid=port.vid,
                pid=port.pid,
                serial_number=port.serial_number,
                manufacturer=port.manufacturer
            )
            devices.append(device)

        # In non-interactive mode, always auto-detect
        if non_interactive:
            return self._auto_detect_robot(devices)

        # Build options list with auto-detect first
        options = ["🔍 Auto-detect robot (recommended)"]
        for device in devices:
            desc = f"{device.port}"
            if device.description:
                desc += f" - {device.description}"
            if device.manufacturer:
                desc += f" ({device.manufacturer})"
            options.append(desc)

        selected = WizardUI.select("Select the robot's serial port:", options)
        if not selected:
            return None

        selection_idx = selected[0]

        # Handle auto-detect option (index 0)
        if selection_idx == 0:
            return self._auto_detect_robot(devices)

        # Otherwise return the selected device (subtract 1 for auto-detect option)
        return devices[selection_idx - 1]

    def _auto_detect_robot(self, devices: List[DiscoveredDevice]) -> Optional[DiscoveredDevice]:
        """Try each port to find one with a robot (servos responding)."""
        WizardUI.print_info("Auto-detecting robot... (this may take a moment)")

        # Filter out known system ports
        system_ports = ['debug-console', 'Bluetooth', 'MALS', 'SOC']
        candidate_devices = [
            d for d in devices
            if not any(sp.lower() in d.port.lower() for sp in system_ports)
        ]

        # If no candidates after filtering, try all
        if not candidate_devices:
            candidate_devices = devices

        # Try each port
        for device in candidate_devices:
            WizardUI.print_info(f"  Trying {device.port}...")

            # Try common baud rates
            for baud in [115200, 1000000, 500000]:
                try:
                    handler = ServoProtocolHandler(device.port, baud, ProtocolType.HIWONDER)
                    if handler.connect():
                        # Try to ping a few servo IDs
                        for test_id in [1, 0, 2, 3, 5, 10]:
                            if handler.ping(test_id):
                                WizardUI.print_success(f"Found robot on {device.port} at {baud} baud!")
                                device.baud_rate = baud
                                device.detected_protocol = ProtocolType.HIWONDER
                                handler.disconnect()
                                return device
                        handler.disconnect()
                except Exception:
                    pass

        WizardUI.print_warning("Could not auto-detect robot on any port.")
        WizardUI.print_info("Please select a port manually or check connections.")

        # Fall back to manual selection (without auto-detect option)
        options = [f"{d.port} - {d.description or 'n/a'}" for d in devices]
        selected = WizardUI.select("Select port manually:", options)
        if selected:
            return devices[selected[0]]
        return None

    def _connect_and_detect_protocol(self, device: DiscoveredDevice, non_interactive: bool = False) -> bool:
        """Connect to device and detect servo protocol."""

        # Try common baud rates
        baud_rates = [115200, 1000000, 500000, 57600, 9600]

        WizardUI.print_info(f"Connecting to {device.port}...")

        for baud in baud_rates:
            WizardUI.print_info(f"  Trying {baud} baud...")

            handler = ServoProtocolHandler(device.port, baud, ProtocolType.HIWONDER)

            if handler.connect():
                # Try to find any servo
                for test_id in [1, 0, 2, 3]:
                    if handler.ping(test_id):
                        WizardUI.print_success(f"Connected at {baud} baud (HiWonder protocol)")
                        device.baud_rate = baud
                        device.detected_protocol = ProtocolType.HIWONDER
                        self.protocol_handler = handler
                        return True

                handler.disconnect()

        # Fallback: let user specify or use default
        WizardUI.print_warning("Could not auto-detect protocol.")

        if non_interactive:
            device.baud_rate = 115200
        else:
            baud = WizardUI.prompt("Enter baud rate", "115200")
            try:
                device.baud_rate = int(baud)
            except ValueError:
                device.baud_rate = 115200

        self.protocol_handler = ServoProtocolHandler(device.port, device.baud_rate)
        if self.protocol_handler.connect():
            device.detected_protocol = ProtocolType.HIWONDER
            return True

        return False

    def _auto_label_components(self, forced_robot_type: Optional[str] = None):
        """Apply AI-suggested labels automatically (non-interactive)."""
        servo_ids = [a.id for a in self.profile.actuators]

        # Get robot type
        if forced_robot_type:
            robot_type = forced_robot_type
        else:
            robot_type = self.ai_assistant.suggest_robot_type(len(servo_ids), servo_ids)

        # Show detection info
        core_count = self.ai_assistant._count_core_servos(servo_ids)
        if core_count < len(servo_ids):
            WizardUI.print_info(f"Found {len(servo_ids)} servos total, {core_count} appear to be main actuators")
        WizardUI.print_info(f"Detected robot type: {robot_type}")
        self.profile.robot_type = robot_type

        # Get suggested labels
        suggested_labels = self.ai_assistant.suggest_labels(robot_type, servo_ids)

        print("\nApplying suggested labels:")
        print("-" * 50)

        for actuator in self.profile.actuators:
            if actuator.id in suggested_labels:
                actuator.label = suggested_labels[actuator.id]['label']
                actuator.group = suggested_labels[actuator.id]['group']
                actuator.role = suggested_labels[actuator.id]['role']
                print(f"  Servo {actuator.id}: {actuator.label} ({actuator.group}/{actuator.role})")
            else:
                actuator.label = f"servo_{actuator.id}"
                actuator.group = "extra"
                actuator.role = "unknown"
                print(f"  Servo {actuator.id}: {actuator.label} (extra/unknown)")

        # Build groups
        self.profile.groups = {}
        for actuator in self.profile.actuators:
            if actuator.group not in self.profile.groups:
                self.profile.groups[actuator.group] = []
            self.profile.groups[actuator.group].append(actuator.id)

    def _enumerate_servos(self) -> bool:
        """Scan for and enumerate all servos."""

        WizardUI.print_info("Scanning for servos (this may take a moment)...")

        id_range = range(0, 32)  # Typical range for small robots

        def progress(current, total):
            bar_len = 30
            filled = int(bar_len * current / total)
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f"\r  Scanning: [{bar}] {current}/{total}", end='', flush=True)

        found_ids = self.protocol_handler.scan_servos(id_range, progress)
        print()  # New line after progress bar

        if not found_ids:
            WizardUI.print_warning("No servos found in ID range 0-31.")

            if WizardUI.confirm("Scan extended range (0-253)?"):
                found_ids = self.protocol_handler.scan_servos(range(0, 254), progress)
                print()

        if not found_ids:
            WizardUI.print_error("No servos found. Check connections and power.")
            return False

        WizardUI.print_success(f"Found {len(found_ids)} servos: {found_ids}")

        # Create actuator entries
        for servo_id in found_ids:
            chars = self.protocol_handler.characterize_servo(servo_id)

            actuator = DiscoveredActuator(
                id=servo_id,
                actuator_type=ActuatorType.SERIAL_BUS_SERVO,
                protocol=self.profile.device.detected_protocol or ProtocolType.HIWONDER,
                characteristics=chars,
                verified_working=True
            )
            self.profile.actuators.append(actuator)

        return True

    def _label_components(self):
        """Run interactive labeling session."""

        # Get robot name
        self.profile.name = WizardUI.prompt("Robot name", "my_robot")
        self.profile.manufacturer = WizardUI.prompt("Manufacturer (optional)", "")
        self.profile.model = WizardUI.prompt("Model (optional)", "")

        # AI-assisted labeling
        self.ai_assistant.interactive_label_session(self.profile, self.protocol_handler)

    def _generate_output(self, auto_push: bool = False, api_url: Optional[str] = None):
        """Generate all output files and optionally push to platform.

        Args:
            auto_push: If True, push primitives to FoodforThought without prompting
            api_url: FoodforThought API URL (defaults to production)
        """
        generator = PrimitiveSkillGenerator(self.profile)
        generated_files = generator.generate_all(self.output_dir)

        # Separate by type
        json_files = [f for f in generated_files if f.endswith('.primitive.json')]
        other_files = [f for f in generated_files if not f.endswith('.primitive.json')]

        print("\nGenerated files:")
        for f in other_files:
            print(f"  - {f}")

        if json_files:
            print(f"\n{WizardUI.COLORS['cyan']}Generated {len(json_files)} primitive skills:{WizardUI.COLORS['reset']}")
            primitives_dir = self.output_dir / "primitives"
            print(f"  - {primitives_dir}/*.primitive.json")

            # Show breakdown by category
            categories = {}
            for p in generator.generated_primitives:
                cat = p.get('category', 'other')
                categories[cat] = categories.get(cat, 0) + 1
            print("\n  Breakdown:")
            for cat, count in sorted(categories.items()):
                print(f"    - {cat}: {count}")

        # Push flow
        self.generator = generator  # Store for access to primitives

        if generator.generated_primitives:
            if auto_push:
                self._push_primitives(api_url)
            else:
                print(f"\n{WizardUI.COLORS['bold']}Ready to share with the community?{WizardUI.COLORS['reset']}")
                if WizardUI.confirm(f"Push {len(generator.generated_primitives)} primitives to FoodforThought?"):
                    self._push_primitives(api_url)
                else:
                    print("\nYou can push later with:")
                    print(f"  ate primitive push {self.output_dir / 'primitives'}/*.primitive.json")

    def _push_primitives(self, api_url: Optional[str] = None):
        """Push generated primitives to FoodforThought platform."""
        import requests

        base_url = api_url or os.getenv("FOODFORTHOUGHT_API_URL", "https://kindlyrobotics.com")
        api_endpoint = f"{base_url}/api/primitives"

        # Check for auth token
        token = os.getenv("FOODFORTHOUGHT_TOKEN") or os.getenv("ATE_TOKEN")
        if not token:
            WizardUI.print_warning("No API token found. Set FOODFORTHOUGHT_TOKEN or ATE_TOKEN")
            WizardUI.print_info("Get your token at: https://kindlyrobotics.com/foodforthought/settings")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        print(f"\n{WizardUI.COLORS['cyan']}Pushing primitives to FoodforThought...{WizardUI.COLORS['reset']}")

        success_count = 0
        fail_count = 0

        for primitive in self.generator.generated_primitives:
            try:
                # Transform to API format
                payload = {
                    "name": primitive["name"],
                    "description": primitive.get("description", ""),
                    "category": primitive.get("category", "motion"),
                    "commandTemplate": primitive.get("commandTemplate", ""),
                    "commandType": primitive.get("commandType", "single"),
                    "parameters": primitive.get("parameters", {}),
                    "executionTimeMs": primitive.get("executionTimeMs"),
                    "settleTimeMs": primitive.get("settleTimeMs"),
                    "cooldownMs": primitive.get("cooldownMs"),
                    "safetyNotes": primitive.get("safetyNotes"),
                    "robotModel": primitive.get("robotModel"),
                    "robotType": primitive.get("robotType"),
                }

                # Add protocol reference if available
                if primitive.get("protocol"):
                    payload["protocol"] = primitive["protocol"]

                response = requests.post(api_endpoint, json=payload, headers=headers, timeout=10)

                if response.status_code in (200, 201):
                    success_count += 1
                else:
                    fail_count += 1
                    if fail_count == 1:
                        # Show first error
                        WizardUI.print_warning(f"Failed to push {primitive['name']}: {response.text[:100]}")

            except requests.exceptions.RequestException as e:
                fail_count += 1
                if fail_count == 1:
                    WizardUI.print_error(f"Network error: {e}")
                    if "kindlyrobotics.com" in str(api_endpoint):
                        WizardUI.print_info("Make sure you're connected to the internet")

        # Summary
        if success_count > 0:
            WizardUI.print_success(f"Pushed {success_count} primitives to FoodforThought!")
            print(f"  View at: {base_url}/foodforthought/robots")
        if fail_count > 0:
            WizardUI.print_warning(f"{fail_count} primitives failed to push")
            print(f"  Retry with: ate primitive push {self.output_dir / 'primitives'}/*.primitive.json")


def run_wizard(port: Optional[str] = None,
               output: str = "./robot",
               skip_labeling: bool = False,
               robot_type: Optional[str] = None,
               non_interactive: bool = False,
               push: bool = False,
               api_url: Optional[str] = None) -> bool:
    """Entry point for CLI.

    Args:
        port: Serial port to use
        output: Output directory for generated files
        skip_labeling: Skip labeling entirely (generic names)
        robot_type: Force robot type (e.g., 'quadruped', 'humanoid_full')
        non_interactive: Run without user prompts (use defaults)
        push: Auto-push primitives to FoodforThought platform
        api_url: FoodforThought API URL (defaults to production)
    """
    wizard = RobotSetupWizard(output_dir=output)
    return wizard.run(
        port=port,
        skip_labeling=skip_labeling,
        robot_type=robot_type,
        non_interactive=non_interactive,
        push=push,
        api_url=api_url
    )


if __name__ == "__main__":
    # Quick test
    import argparse
    parser = argparse.ArgumentParser(description="Robot Setup Wizard")
    parser.add_argument("--port", "-p", help="Serial port (skip device selection)")
    parser.add_argument("--output", "-o", default="./robot", help="Output directory")
    parser.add_argument("--skip-labeling", action="store_true", help="Skip interactive labeling")

    args = parser.parse_args()

    success = run_wizard(
        port=args.port,
        output=args.output,
        skip_labeling=args.skip_labeling
    )

    sys.exit(0 if success else 1)
