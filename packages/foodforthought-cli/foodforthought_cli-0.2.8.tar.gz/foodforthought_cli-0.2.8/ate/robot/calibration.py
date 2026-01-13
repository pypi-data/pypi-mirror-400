"""
Visual calibration system for robot servo mapping.

Provides:
- ate robot calibrate - Interactive servo discovery and range mapping
- Visual feedback using webcam/robot camera
- Pose library management for semantic skill development

The goal is to eliminate manual servo value guessing by:
1. Auto-discovering servo IDs and their ranges
2. Using camera to visually confirm poses
3. Creating semantic mappings (e.g., "gripper_open" -> servo 11 @ 2500)
"""

import json
import time
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Callable
from pathlib import Path
from enum import Enum


class JointType(Enum):
    """Types of joints/servos."""
    UNKNOWN = "unknown"
    # Locomotion
    HIP_ROLL = "hip_roll"
    HIP_PITCH = "hip_pitch"
    KNEE = "knee"
    ANKLE = "ankle"
    # Arm
    SHOULDER_PAN = "shoulder_pan"
    SHOULDER_LIFT = "shoulder_lift"
    ELBOW = "elbow"
    WRIST_ROLL = "wrist_roll"
    WRIST_PITCH = "wrist_pitch"
    # Gripper
    GRIPPER = "gripper"
    # Body
    HEAD_PAN = "head_pan"
    HEAD_TILT = "head_tilt"
    BODY_PITCH = "body_pitch"
    BODY_ROLL = "body_roll"


@dataclass
class ServoCalibration:
    """Calibration data for a single servo."""
    servo_id: int
    name: str                           # Human-readable name
    joint_type: JointType = JointType.UNKNOWN

    # Range discovered during calibration
    min_value: int = 0
    max_value: int = 4096
    center_value: int = 2048

    # Semantic positions (name -> value)
    positions: Dict[str, int] = field(default_factory=dict)

    # Physical properties
    inverted: bool = False              # True if positive = clockwise
    speed_limit: int = 1000             # Max speed in ms per movement

    # Visual confirmation images (base64 or paths)
    position_images: Dict[str, str] = field(default_factory=dict)

    def get_position(self, name: str) -> Optional[int]:
        """Get servo value for a named position."""
        return self.positions.get(name)

    def set_position(self, name: str, value: int, image_path: Optional[str] = None):
        """Set a named position for this servo."""
        self.positions[name] = value
        if image_path:
            self.position_images[name] = image_path


@dataclass
class Pose:
    """A named pose consisting of multiple servo positions."""
    name: str
    description: str = ""
    servo_positions: Dict[int, int] = field(default_factory=dict)  # servo_id -> value
    transition_time_ms: int = 500
    image_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "servo_positions": self.servo_positions,
            "transition_time_ms": self.transition_time_ms,
            "image_path": self.image_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pose":
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            servo_positions={int(k): v for k, v in data["servo_positions"].items()},
            transition_time_ms=data.get("transition_time_ms", 500),
            image_path=data.get("image_path"),
        )


@dataclass
class RobotCalibration:
    """Complete calibration for a robot."""
    robot_model: str
    robot_name: str

    # Servo calibrations by ID
    servos: Dict[int, ServoCalibration] = field(default_factory=dict)

    # Named poses
    poses: Dict[str, Pose] = field(default_factory=dict)

    # Camera configuration
    camera_url: Optional[str] = None
    camera_type: str = "wifi"  # wifi, usb, none

    # Connection info
    serial_port: Optional[str] = None
    baud_rate: int = 115200

    # Metadata
    calibrated_at: Optional[str] = None
    notes: str = ""

    def get_servo(self, servo_id: int) -> Optional[ServoCalibration]:
        return self.servos.get(servo_id)

    def get_pose(self, name: str) -> Optional[Pose]:
        return self.poses.get(name)

    def add_pose(self, pose: Pose):
        self.poses[pose.name] = pose

    def save(self, path: Path):
        """Save calibration to JSON file."""
        data = {
            "robot_model": self.robot_model,
            "robot_name": self.robot_name,
            "servos": {
                str(sid): {
                    "servo_id": s.servo_id,
                    "name": s.name,
                    "joint_type": s.joint_type.value,
                    "min_value": s.min_value,
                    "max_value": s.max_value,
                    "center_value": s.center_value,
                    "positions": s.positions,
                    "inverted": s.inverted,
                    "speed_limit": s.speed_limit,
                }
                for sid, s in self.servos.items()
            },
            "poses": {name: pose.to_dict() for name, pose in self.poses.items()},
            "camera_url": self.camera_url,
            "camera_type": self.camera_type,
            "serial_port": self.serial_port,
            "baud_rate": self.baud_rate,
            "calibrated_at": self.calibrated_at,
            "notes": self.notes,
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "RobotCalibration":
        """Load calibration from JSON file."""
        with open(path) as f:
            data = json.load(f)

        cal = cls(
            robot_model=data["robot_model"],
            robot_name=data["robot_name"],
            camera_url=data.get("camera_url"),
            camera_type=data.get("camera_type", "wifi"),
            serial_port=data.get("serial_port"),
            baud_rate=data.get("baud_rate", 115200),
            calibrated_at=data.get("calibrated_at"),
            notes=data.get("notes", ""),
        )

        # Load servos
        for sid, sdata in data.get("servos", {}).items():
            cal.servos[int(sid)] = ServoCalibration(
                servo_id=sdata["servo_id"],
                name=sdata["name"],
                joint_type=JointType(sdata.get("joint_type", "unknown")),
                min_value=sdata.get("min_value", 0),
                max_value=sdata.get("max_value", 4096),
                center_value=sdata.get("center_value", 2048),
                positions=sdata.get("positions", {}),
                inverted=sdata.get("inverted", False),
                speed_limit=sdata.get("speed_limit", 1000),
            )

        # Load poses
        for name, pdata in data.get("poses", {}).items():
            cal.poses[name] = Pose.from_dict(pdata)

        return cal


class VisualCalibrator:
    """
    Interactive calibration wizard with visual feedback.

    Usage:
        calibrator = VisualCalibrator(serial_port="/dev/cu.usbserial-10")
        calibrator.set_camera("http://192.168.50.98:80/capture")
        calibration = calibrator.run_interactive()
        calibration.save(Path("~/.ate/calibrations/mechdog.json"))
    """

    def __init__(
        self,
        serial_port: str,
        baud_rate: int = 115200,
        robot_model: str = "unknown",
        robot_name: str = "robot",
    ):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.robot_model = robot_model
        self.robot_name = robot_name

        self._serial = None
        self._camera_url = None
        self._camera_capture = None  # Function to capture image

        self.calibration = RobotCalibration(
            robot_model=robot_model,
            robot_name=robot_name,
            serial_port=serial_port,
            baud_rate=baud_rate,
        )

    def set_camera(self, camera_url: str):
        """Set camera URL for visual feedback."""
        self._camera_url = camera_url
        self.calibration.camera_url = camera_url

    def set_camera_capture(self, capture_fn: Callable[[], bytes]):
        """Set custom camera capture function."""
        self._camera_capture = capture_fn

    def connect(self) -> bool:
        """Connect to robot via serial."""
        try:
            import serial
            self._serial = serial.Serial(self.serial_port, self.baud_rate, timeout=2.0)
            time.sleep(0.5)
            self._serial.reset_input_buffer()

            # Get to REPL
            self._serial.write(b'\x03')
            time.sleep(0.3)
            self._serial.write(b'\x02')
            time.sleep(0.3)
            self._serial.read(self._serial.in_waiting or 1)

            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from robot."""
        if self._serial and self._serial.is_open:
            self._serial.close()

    def send_command(self, cmd: str, wait: float = 0.3) -> str:
        """Send command and return response."""
        if not self._serial:
            raise RuntimeError("Not connected")

        self._serial.write(f"{cmd}\r\n".encode())
        time.sleep(wait)
        response = self._serial.read(self._serial.in_waiting or 1)
        return response.decode("utf-8", errors="replace")

    def capture_image(self, save_path: Optional[str] = None) -> Optional[bytes]:
        """Capture image from camera."""
        if self._camera_capture:
            img_data = self._camera_capture()
        elif self._camera_url:
            import requests
            try:
                response = requests.get(self._camera_url, timeout=5)
                if response.status_code == 200:
                    img_data = response.content
                else:
                    return None
            except Exception:
                return None
        else:
            return None

        if save_path and img_data:
            with open(save_path, "wb") as f:
                f.write(img_data)

        return img_data

    def read_servo(self, servo_id: int) -> Optional[int]:
        """Read current servo position."""
        response = self.send_command(f"dog.read_servo({servo_id})")
        # Parse response for integer value
        for line in response.split("\n"):
            line = line.strip()
            if line.isdigit():
                return int(line)
            try:
                return int(line)
            except ValueError:
                continue
        return None

    def set_servo(self, servo_id: int, value: int, time_ms: int = 500) -> bool:
        """Set servo to position."""
        response = self.send_command(
            f"dog.set_servo({servo_id}, {value}, {time_ms})",
            wait=time_ms / 1000 + 0.3
        )
        return "True" in response

    def discover_servos(self, max_id: int = 16) -> List[int]:
        """Discover which servo IDs are active."""
        active = []
        print(f"Scanning servos 1-{max_id}...")

        for servo_id in range(1, max_id + 1):
            pos = self.read_servo(servo_id)
            if pos is not None:
                active.append(servo_id)
                print(f"  Found servo {servo_id} at position {pos}")

        return active

    def calibrate_servo_range(
        self,
        servo_id: int,
        name: str = "",
        test_values: List[int] = None,
    ) -> ServoCalibration:
        """
        Interactively calibrate a single servo.

        Moves servo through range while user confirms safe limits.
        """
        if test_values is None:
            test_values = [500, 1000, 1500, 2000, 2500]

        print(f"\n=== Calibrating Servo {servo_id} ===")
        if not name:
            name = input(f"Name for servo {servo_id} (e.g., 'gripper', 'arm_elbow'): ").strip()
            if not name:
                name = f"servo_{servo_id}"

        cal = ServoCalibration(servo_id=servo_id, name=name)

        # Test range
        print(f"\nTesting positions: {test_values}")
        print("Watch the servo and note safe range...")

        working_values = []
        for val in test_values:
            print(f"  Moving to {val}...", end=" ", flush=True)
            success = self.set_servo(servo_id, val)
            if success:
                print("OK")
                working_values.append(val)
            else:
                print("FAILED")
            time.sleep(0.5)

        if working_values:
            cal.min_value = min(working_values)
            cal.max_value = max(working_values)
            cal.center_value = working_values[len(working_values) // 2]
            print(f"\nRange: {cal.min_value} - {cal.max_value}")

        return cal

    def record_pose(self, name: str, description: str = "") -> Pose:
        """
        Record current robot position as a named pose.

        Reads all known servos and saves their positions.
        """
        pose = Pose(name=name, description=description)

        for servo_id in self.calibration.servos:
            pos = self.read_servo(servo_id)
            if pos is not None:
                pose.servo_positions[servo_id] = pos

        # Capture image if camera available
        if self._camera_url:
            img_dir = Path.home() / ".ate" / "calibrations" / "images"
            img_dir.mkdir(parents=True, exist_ok=True)
            img_path = img_dir / f"{self.robot_name}_{name}.jpg"
            self.capture_image(str(img_path))
            pose.image_path = str(img_path)

        self.calibration.add_pose(pose)
        return pose

    def apply_pose(self, pose: Pose, sequential: bool = True) -> bool:
        """
        Apply a saved pose to the robot.

        Args:
            pose: The pose to apply
            sequential: If True, move servos one at a time with waits
        """
        success = True

        for servo_id, value in pose.servo_positions.items():
            result = self.set_servo(servo_id, value, pose.transition_time_ms)
            if not result:
                success = False

            if sequential:
                time.sleep(pose.transition_time_ms / 1000 + 0.2)

        return success

    def run_interactive(self) -> RobotCalibration:
        """
        Run full interactive calibration wizard.

        Returns:
            Complete RobotCalibration object
        """
        from datetime import datetime

        print("\n" + "=" * 50)
        print("  FoodforThought Robot Calibration Wizard")
        print("=" * 50)

        # Connect
        print("\nConnecting to robot...")
        if not self.connect():
            raise RuntimeError("Failed to connect to robot")
        print("Connected!")

        # Initialize robot
        print("\nInitializing robot...")
        self.send_command("from HW_MechDog import MechDog; dog = MechDog()", wait=1.5)

        # Discover servos
        print("\n--- Servo Discovery ---")
        active_servos = self.discover_servos()
        print(f"\nFound {len(active_servos)} active servos: {active_servos}")

        # Calibrate each servo
        print("\n--- Servo Calibration ---")
        print("For each servo, we'll test its range.")
        print("Press Enter to continue or 'skip' to skip a servo.\n")

        for servo_id in active_servos:
            skip = input(f"Calibrate servo {servo_id}? [Enter/skip]: ").strip().lower()
            if skip == "skip":
                continue

            cal = self.calibrate_servo_range(servo_id)
            self.calibration.servos[servo_id] = cal

        # Record key poses
        print("\n--- Pose Recording ---")
        print("Now let's record some key poses.")
        print("Manually position the robot and type a pose name to save it.")
        print("Type 'done' when finished.\n")

        while True:
            pose_name = input("Pose name (or 'done'): ").strip()
            if pose_name.lower() == "done":
                break
            if not pose_name:
                continue

            desc = input("Description: ").strip()
            pose = self.record_pose(pose_name, desc)
            print(f"Recorded pose '{pose_name}' with {len(pose.servo_positions)} servos")

        # Finalize
        self.calibration.calibrated_at = datetime.now().isoformat()
        self.disconnect()

        print("\n" + "=" * 50)
        print("  Calibration Complete!")
        print("=" * 50)
        print(f"Servos: {len(self.calibration.servos)}")
        print(f"Poses: {len(self.calibration.poses)}")

        return self.calibration


# =============================================================================
# Quick calibration functions for common scenarios
# =============================================================================

def quick_gripper_calibration(
    serial_port: str,
    gripper_servo_id: int = 11,
    test_open: int = 2500,
    test_closed: int = 200,
) -> ServoCalibration:
    """
    Quick calibration for just a gripper servo.

    Usage:
        gripper = quick_gripper_calibration("/dev/cu.usbserial-10")
        print(f"Open: {gripper.positions['open']}, Closed: {gripper.positions['closed']}")
    """
    calibrator = VisualCalibrator(serial_port)

    if not calibrator.connect():
        raise RuntimeError("Failed to connect")

    try:
        calibrator.send_command("from HW_MechDog import MechDog; dog = MechDog()", wait=1.5)

        gripper = ServoCalibration(
            servo_id=gripper_servo_id,
            name="gripper",
            joint_type=JointType.GRIPPER,
        )

        # Test open
        print("Opening gripper...")
        calibrator.set_servo(gripper_servo_id, test_open)
        time.sleep(1.5)
        actual_open = calibrator.read_servo(gripper_servo_id)
        gripper.positions["open"] = actual_open or test_open
        gripper.max_value = gripper.positions["open"]

        # Test closed
        print("Closing gripper...")
        calibrator.set_servo(gripper_servo_id, test_closed)
        time.sleep(1.5)
        actual_closed = calibrator.read_servo(gripper_servo_id)
        gripper.positions["closed"] = actual_closed or test_closed
        gripper.min_value = gripper.positions["closed"]

        # Center
        gripper.center_value = (gripper.min_value + gripper.max_value) // 2

        return gripper
    finally:
        calibrator.disconnect()


def load_calibration(robot_name: str) -> Optional[RobotCalibration]:
    """Load calibration from default location."""
    path = Path.home() / ".ate" / "calibrations" / f"{robot_name}.json"
    if path.exists():
        return RobotCalibration.load(path)
    return None


def save_calibration(calibration: RobotCalibration):
    """Save calibration to default location."""
    path = Path.home() / ".ate" / "calibrations" / f"{calibration.robot_name}.json"
    calibration.save(path)
    print(f"Saved calibration to: {path}")


def list_calibrations() -> List[str]:
    """List available calibrations."""
    cal_dir = Path.home() / ".ate" / "calibrations"
    if not cal_dir.exists():
        return []
    return [p.stem for p in cal_dir.glob("*.json")]
