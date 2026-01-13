"""
Visual Labeling System for Robot Skill Development.

Uses dual cameras (external webcam + robot camera) to interactively:
1. Discover and label servos by their physical effect
2. Record named poses with visual confirmation
3. Sequence poses into actions
4. Generate reusable skill code

This creates a "bedrock" of basic skills that can be:
- Reused across similar robots
- Composed into complex behaviors
- Shared in the FoodforThought marketplace
"""

import json
import time
import os
import sys
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
from pathlib import Path
from datetime import datetime
from enum import Enum

from .calibration import (
    ServoCalibration,
    Pose,
    RobotCalibration,
    JointType,
    VisualCalibrator,
    save_calibration,
    load_calibration,
)


# =============================================================================
# Robot Preset Mappings - Pre-populated servo configurations
# =============================================================================

ROBOT_PRESETS = {
    "hiwonder_mechdog": {
        "name": "HiWonder MechDog",
        "servos": {
            # Front Right Leg
            1: {"name": "front_right_hip", "joint_type": "hip_roll", "min": 500, "max": 2500},
            2: {"name": "front_right_thigh", "joint_type": "hip_pitch", "min": 500, "max": 2500},
            # Front Left Leg
            3: {"name": "front_left_hip", "joint_type": "hip_roll", "min": 500, "max": 2500},
            4: {"name": "front_left_thigh", "joint_type": "hip_pitch", "min": 500, "max": 2500},
            # Rear Right Leg
            5: {"name": "rear_right_hip", "joint_type": "hip_roll", "min": 500, "max": 2500},
            6: {"name": "rear_right_thigh", "joint_type": "hip_pitch", "min": 500, "max": 2500},
            # Rear Left Leg
            7: {"name": "rear_left_hip", "joint_type": "hip_roll", "min": 500, "max": 2500},
            8: {"name": "rear_left_thigh", "joint_type": "hip_pitch", "min": 500, "max": 2500},
            # Arm (optional attachment)
            9: {"name": "arm_shoulder", "joint_type": "shoulder_lift", "min": 500, "max": 2500},
            10: {"name": "arm_elbow", "joint_type": "elbow", "min": 500, "max": 2500},
            11: {"name": "gripper", "joint_type": "gripper", "min": 200, "max": 2500},
        },
        "joint_groups": {
            "front_right_leg": [1, 2],
            "front_left_leg": [3, 4],
            "rear_right_leg": [5, 6],
            "rear_left_leg": [7, 8],
            "arm": [9, 10, 11],
            "all_legs": [1, 2, 3, 4, 5, 6, 7, 8],
        },
        "default_poses": {
            "stand": {1: 2096, 2: 1621, 3: 2170, 4: 1611, 5: 904, 6: 1379, 7: 830, 8: 1389},
            "gripper_open": {11: 2500},
            "gripper_closed": {11: 200},
            "arm_up": {9: 500, 10: 1500},
            "arm_down": {9: 1800, 10: 1200},
        },
    },
}


def get_preset(robot_model: str) -> Optional[Dict]:
    """Get preset mappings for a robot model."""
    return ROBOT_PRESETS.get(robot_model)


def apply_preset_to_calibration(calibration: RobotCalibration, preset: Dict):
    """Apply preset servo mappings to a calibration."""
    for servo_id, info in preset.get("servos", {}).items():
        if servo_id not in calibration.servos:
            jtype = JointType(info["joint_type"]) if info.get("joint_type") else JointType.UNKNOWN
            calibration.servos[servo_id] = ServoCalibration(
                servo_id=servo_id,
                name=info["name"],
                joint_type=jtype,
                min_value=info.get("min", 500),
                max_value=info.get("max", 2500),
                center_value=(info.get("min", 500) + info.get("max", 2500)) // 2,
            )


class ActionType(Enum):
    """Types of robot actions."""
    LOCOMOTION = "locomotion"      # Walking, turning
    MANIPULATION = "manipulation"  # Picking, placing
    GESTURE = "gesture"            # Waving, nodding
    POSTURE = "posture"            # Standing, sitting
    COMPOSITE = "composite"        # Multi-step actions


@dataclass
class ActionStep:
    """A single step in an action sequence."""
    pose_name: str
    duration_ms: int = 500
    wait_after_ms: int = 0
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "pose_name": self.pose_name,
            "duration_ms": self.duration_ms,
            "wait_after_ms": self.wait_after_ms,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActionStep":
        return cls(**data)


@dataclass
class Action:
    """A named action consisting of pose sequences."""
    name: str
    action_type: ActionType = ActionType.COMPOSITE
    description: str = ""
    steps: List[ActionStep] = field(default_factory=list)

    # Visual recordings
    preview_image: Optional[str] = None  # Path to preview image
    video_path: Optional[str] = None     # Path to recorded video

    # Metadata
    created_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def add_step(self, pose_name: str, duration_ms: int = 500, wait_after_ms: int = 0):
        self.steps.append(ActionStep(pose_name, duration_ms, wait_after_ms))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "action_type": self.action_type.value,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "preview_image": self.preview_image,
            "video_path": self.video_path,
            "created_at": self.created_at,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Action":
        action = cls(
            name=data["name"],
            action_type=ActionType(data.get("action_type", "composite")),
            description=data.get("description", ""),
            preview_image=data.get("preview_image"),
            video_path=data.get("video_path"),
            created_at=data.get("created_at"),
            tags=data.get("tags", []),
        )
        for step_data in data.get("steps", []):
            action.steps.append(ActionStep.from_dict(step_data))
        return action


@dataclass
class SkillLibrary:
    """Collection of labeled servos, poses, and actions for a robot."""
    robot_name: str
    robot_model: str

    # Core data
    calibration: Optional[RobotCalibration] = None
    actions: Dict[str, Action] = field(default_factory=dict)

    # Semantic mappings
    servo_labels: Dict[int, str] = field(default_factory=dict)  # servo_id -> description
    joint_groups: Dict[str, List[int]] = field(default_factory=dict)  # group_name -> servo_ids

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def save(self, path: Path):
        """Save skill library to JSON."""
        data = {
            "robot_name": self.robot_name,
            "robot_model": self.robot_model,
            "servo_labels": self.servo_labels,
            "joint_groups": self.joint_groups,
            "actions": {name: a.to_dict() for name, a in self.actions.items()},
            "created_at": self.created_at,
            "updated_at": datetime.now().isoformat(),
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: Path, calibration: Optional[RobotCalibration] = None) -> "SkillLibrary":
        """Load skill library from JSON."""
        with open(path) as f:
            data = json.load(f)

        lib = cls(
            robot_name=data["robot_name"],
            robot_model=data["robot_model"],
            calibration=calibration,
            servo_labels=data.get("servo_labels", {}),
            joint_groups=data.get("joint_groups", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

        for name, action_data in data.get("actions", {}).items():
            lib.actions[name] = Action.from_dict(action_data)

        return lib


class WebcamCapture:
    """Captures frames from local webcam using OpenCV."""

    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self._cap = None
        self._frame = None
        self._running = False
        self._thread = None

    def start(self) -> bool:
        """Start webcam capture."""
        try:
            import cv2
            self._cap = cv2.VideoCapture(self.device_id)
            if not self._cap.isOpened():
                return False

            self._running = True
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()
            return True
        except ImportError:
            print("OpenCV not installed. Run: pip install opencv-python")
            return False
        except Exception as e:
            print(f"Failed to start webcam: {e}")
            return False

    def _capture_loop(self):
        """Background capture loop."""
        import cv2
        while self._running:
            ret, frame = self._cap.read()
            if ret:
                self._frame = frame
            time.sleep(0.033)  # ~30fps

    def stop(self):
        """Stop webcam capture."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._cap:
            self._cap.release()

    def get_frame(self):
        """Get latest frame as numpy array."""
        return self._frame

    def capture_image(self, save_path: Optional[str] = None) -> Optional[bytes]:
        """Capture current frame as JPEG bytes."""
        import cv2

        if self._frame is None:
            return None

        _, jpeg = cv2.imencode('.jpg', self._frame)
        img_bytes = jpeg.tobytes()

        if save_path:
            with open(save_path, 'wb') as f:
                f.write(img_bytes)

        return img_bytes

    def show_preview(self, window_name: str = "Webcam"):
        """Show live preview window."""
        import cv2

        if self._frame is not None:
            cv2.imshow(window_name, self._frame)
            cv2.waitKey(1)


class DualCameraLabeler:
    """
    Interactive labeling system using dual cameras.

    - External webcam: See the robot's body from outside
    - Robot camera: See what the robot sees (for manipulation)

    Workflow:
    1. Discover servos and label by physical effect
    2. Record named poses with dual-camera snapshots
    3. Sequence poses into named actions
    4. Generate Python skill code
    """

    def __init__(
        self,
        serial_port: str,
        robot_name: str = "robot",
        robot_model: str = "unknown",
        webcam_id: int = 0,
        robot_camera_url: Optional[str] = None,
    ):
        self.serial_port = serial_port
        self.robot_name = robot_name
        self.robot_model = robot_model

        # Cameras
        self.webcam = WebcamCapture(webcam_id)
        self.robot_camera_url = robot_camera_url

        # Core components
        self.calibrator = VisualCalibrator(
            serial_port=serial_port,
            robot_model=robot_model,
            robot_name=robot_name,
        )

        if robot_camera_url:
            self.calibrator.set_camera(robot_camera_url)

        # Skill library
        self.library = SkillLibrary(
            robot_name=robot_name,
            robot_model=robot_model,
            created_at=datetime.now().isoformat(),
        )

        # State
        self._connected = False
        self._display_thread = None
        self._display_running = False

    def connect(self) -> bool:
        """Connect to robot and start cameras."""
        print("Connecting to robot...")
        if not self.calibrator.connect():
            return False

        # Initialize robot
        self.calibrator.send_command("from HW_MechDog import MechDog; dog = MechDog()", wait=1.5)

        print("Starting webcam...")
        if not self.webcam.start():
            print("Warning: Webcam not available")

        self._connected = True
        return True

    def disconnect(self):
        """Disconnect and cleanup."""
        self._display_running = False
        self.webcam.stop()
        self.calibrator.disconnect()
        self._connected = False

        try:
            import cv2
            cv2.destroyAllWindows()
        except:
            pass

    def capture_dual_images(self, base_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Capture images from both cameras."""
        img_dir = Path.home() / ".ate" / "skill_images" / self.robot_name
        img_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Webcam (external view)
        webcam_path = img_dir / f"{base_name}_external_{timestamp}.jpg"
        webcam_img = self.webcam.capture_image(str(webcam_path))

        # Robot camera (robot's view)
        robot_path = img_dir / f"{base_name}_robot_{timestamp}.jpg"
        robot_img = self.calibrator.capture_image(str(robot_path))

        return (
            str(webcam_path) if webcam_img else None,
            str(robot_path) if robot_img else None,
        )

    def label_servo_interactive(self, servo_id: int) -> ServoCalibration:
        """
        Interactively label a servo by moving it and observing the effect.

        Shows live webcam feed while user adjusts servo position.
        """
        print(f"\n=== Labeling Servo {servo_id} ===")
        print("Watch the webcam window to see what this servo controls.")
        print("Commands: +/- (adjust), min/max (extremes), name (set name), done (finish)")

        # Start with center position
        current_value = 1500
        self.calibrator.set_servo(servo_id, current_value, 300)

        cal = ServoCalibration(servo_id=servo_id, name=f"servo_{servo_id}")
        tested_values = [current_value]

        while True:
            # Show webcam
            self.webcam.show_preview(f"Servo {servo_id} - Webcam View")

            cmd = input(f"Servo {servo_id} @ {current_value} > ").strip().lower()

            if cmd in ('+', 'up', 'u'):
                current_value = min(current_value + 200, 2500)
                self.calibrator.set_servo(servo_id, current_value, 300)
                tested_values.append(current_value)

            elif cmd in ('-', 'down', 'd'):
                current_value = max(current_value - 200, 200)
                self.calibrator.set_servo(servo_id, current_value, 300)
                tested_values.append(current_value)

            elif cmd == 'min':
                current_value = 200
                self.calibrator.set_servo(servo_id, current_value, 500)
                tested_values.append(current_value)

            elif cmd == 'max':
                current_value = 2500
                self.calibrator.set_servo(servo_id, current_value, 500)
                tested_values.append(current_value)

            elif cmd.startswith('='):
                try:
                    current_value = int(cmd[1:])
                    self.calibrator.set_servo(servo_id, current_value, 300)
                    tested_values.append(current_value)
                except ValueError:
                    print("Invalid value. Use =1500 format.")

            elif cmd == 'name' or cmd.startswith('name '):
                name = cmd[5:].strip() if cmd.startswith('name ') else input("Name: ").strip()
                if name:
                    cal.name = name
                    print(f"Named: {name}")

            elif cmd == 'type':
                print("Joint types:", [jt.value for jt in JointType])
                jt = input("Joint type: ").strip()
                try:
                    cal.joint_type = JointType(jt)
                    print(f"Set type: {cal.joint_type.value}")
                except ValueError:
                    print("Invalid type")

            elif cmd == 'snap':
                ext_path, robot_path = self.capture_dual_images(f"servo_{servo_id}")
                print(f"Captured: {ext_path}")

            elif cmd == 'pos':
                pos_name = input("Position name: ").strip()
                if pos_name:
                    cal.positions[pos_name] = current_value
                    print(f"Saved position '{pos_name}' = {current_value}")

            elif cmd in ('done', 'q', 'quit'):
                break

            elif cmd == 'help' or cmd == '?':
                print("""
Commands:
  +/-      Adjust by 200
  =VALUE   Set to exact value (e.g., =1500)
  min/max  Go to extremes
  name X   Set servo name
  type     Set joint type
  pos      Save current as named position
  snap     Capture image
  done     Finish labeling
""")

        # Calculate range from tested values
        cal.min_value = min(tested_values)
        cal.max_value = max(tested_values)
        cal.center_value = (cal.min_value + cal.max_value) // 2

        return cal

    def record_pose_interactive(self) -> Optional[Pose]:
        """
        Record current robot position as a named pose.

        Shows both camera views for confirmation.
        """
        print("\n=== Record Pose ===")
        print("Position the robot manually or use servo commands first.")

        # Show current state
        self.webcam.show_preview("Current Pose - External")

        name = input("Pose name: ").strip()
        if not name:
            print("Cancelled")
            return None

        desc = input("Description: ").strip()

        # Create pose from current servo positions
        pose = Pose(name=name, description=desc)

        for servo_id in self.calibrator.calibration.servos:
            pos = self.calibrator.read_servo(servo_id)
            if pos is not None:
                pose.servo_positions[servo_id] = pos

        # Capture images
        ext_path, robot_path = self.capture_dual_images(f"pose_{name}")
        pose.image_path = ext_path

        # Add to calibration
        self.calibrator.calibration.add_pose(pose)

        print(f"Recorded pose '{name}' with {len(pose.servo_positions)} servos")
        return pose

    def create_action_interactive(self) -> Optional[Action]:
        """
        Create an action by sequencing poses.

        User selects poses and timing to create a multi-step action.
        """
        print("\n=== Create Action ===")

        # Show available poses
        poses = list(self.calibrator.calibration.poses.keys())
        if not poses:
            print("No poses recorded. Record some poses first.")
            return None

        print(f"Available poses: {poses}")

        name = input("Action name: ").strip()
        if not name:
            print("Cancelled")
            return None

        desc = input("Description: ").strip()

        # Select action type
        print(f"Action types: {[at.value for at in ActionType]}")
        action_type_str = input("Action type [composite]: ").strip() or "composite"
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            action_type = ActionType.COMPOSITE

        action = Action(
            name=name,
            action_type=action_type,
            description=desc,
            created_at=datetime.now().isoformat(),
        )

        print("\nAdd steps (pose names). Type 'done' when finished.")
        print("Format: pose_name [duration_ms] [wait_after_ms]")

        while True:
            step_input = input(f"Step {len(action.steps) + 1}: ").strip()

            if step_input.lower() in ('done', 'q', ''):
                break

            parts = step_input.split()
            pose_name = parts[0]

            if pose_name not in poses:
                print(f"Unknown pose: {pose_name}")
                continue

            duration = int(parts[1]) if len(parts) > 1 else 500
            wait = int(parts[2]) if len(parts) > 2 else 0

            action.add_step(pose_name, duration, wait)
            print(f"  Added: {pose_name} ({duration}ms, wait {wait}ms)")

        if not action.steps:
            print("No steps added, cancelled")
            return None

        # Preview action
        preview = input("Preview action? [Y/n]: ").strip().lower()
        if preview != 'n':
            self.execute_action(action)

        # Save
        self.library.actions[name] = action
        print(f"Created action '{name}' with {len(action.steps)} steps")

        return action

    def execute_action(self, action: Action):
        """Execute an action by applying its pose sequence."""
        print(f"\nExecuting action: {action.name}")

        for i, step in enumerate(action.steps):
            pose = self.calibrator.calibration.get_pose(step.pose_name)
            if not pose:
                print(f"  Warning: Pose '{step.pose_name}' not found")
                continue

            print(f"  Step {i+1}: {step.pose_name}")

            # Apply pose
            for servo_id, value in pose.servo_positions.items():
                self.calibrator.set_servo(servo_id, value, step.duration_ms)

            # Wait for movement to complete
            time.sleep(step.duration_ms / 1000 + 0.1)

            # Additional wait if specified
            if step.wait_after_ms > 0:
                time.sleep(step.wait_after_ms / 1000)

        print("Action complete")

    def generate_skill_code(self, action: Action) -> str:
        """
        Generate Python skill code from an action.

        Creates a function that can be used as a reusable skill.
        """
        func_name = action.name.lower().replace(" ", "_").replace("-", "_")

        code = f'''"""
Auto-generated skill: {action.name}
Type: {action.action_type.value}
Description: {action.description}
Generated: {datetime.now().isoformat()}
"""

from typing import Optional
from ate.interfaces import RobotInterface


def {func_name}(robot: RobotInterface, speed_factor: float = 1.0) -> bool:
    """
    {action.description or action.name}

    Args:
        robot: Robot interface with set_servo method
        speed_factor: Multiplier for movement speed (1.0 = normal)

    Returns:
        True if action completed successfully
    """
    import time

    try:
'''

        for i, step in enumerate(action.steps):
            pose = self.calibrator.calibration.get_pose(step.pose_name)
            if not pose:
                continue

            code += f'''
        # Step {i+1}: {step.pose_name}
'''
            for servo_id, value in pose.servo_positions.items():
                servo_name = self.calibrator.calibration.servos.get(servo_id)
                name_comment = f"  # {servo_name.name}" if servo_name else ""
                code += f'''        robot.set_servo({servo_id}, {value}, int({step.duration_ms} / speed_factor)){name_comment}
'''

            code += f'''        time.sleep({step.duration_ms / 1000} / speed_factor)
'''

            if step.wait_after_ms > 0:
                code += f'''        time.sleep({step.wait_after_ms / 1000})
'''

        code += '''
        return True

    except Exception as e:
        print(f"Skill failed: {e}")
        return False
'''

        return code

    def run_interactive_session(self):
        """
        Run a full interactive labeling session.

        Main workflow:
        1. Discover and label servos
        2. Define joint groups
        3. Record poses
        4. Create actions
        5. Generate skills
        """
        print("\n" + "=" * 60)
        print("  FoodforThought Visual Skill Labeler")
        print("=" * 60)
        print(f"\nRobot: {self.robot_name} ({self.robot_model})")
        print(f"Serial: {self.serial_port}")
        print(f"Robot Camera: {self.robot_camera_url or 'None'}")
        print(f"Webcam: Device {self.webcam.device_id}")

        if not self.connect():
            print("Failed to connect!")
            return

        try:
            self._main_menu()
        finally:
            self.disconnect()

    def _main_menu(self):
        """Main interactive menu."""
        while True:
            print("\n" + "-" * 40)
            print("Main Menu:")
            print("  1. Discover & Label Servos")
            print("  2. Define Joint Groups")
            print("  3. Record Poses")
            print("  4. Create Actions")
            print("  5. Generate Skills")
            print("  6. Execute Action")
            print("  7. Save Library")
            print("  8. Quick Servo Test")
            print("  q. Quit")
            print("-" * 40)

            choice = input("Choice: ").strip().lower()

            if choice == '1':
                self._servo_discovery_flow()
            elif choice == '2':
                self._joint_groups_flow()
            elif choice == '3':
                self._pose_recording_flow()
            elif choice == '4':
                self._action_creation_flow()
            elif choice == '5':
                self._skill_generation_flow()
            elif choice == '6':
                self._execute_action_flow()
            elif choice == '7':
                self._save_library()
            elif choice == '8':
                self._quick_servo_test()
            elif choice in ('q', 'quit', 'exit'):
                break

    def _servo_discovery_flow(self):
        """Discover and label all servos."""
        print("\n=== Servo Discovery ===")

        # Auto-discover
        active_servos = self.calibrator.discover_servos()

        if not active_servos:
            print("No servos found!")
            return

        print(f"\nFound {len(active_servos)} servos: {active_servos}")
        print("\nLabel each servo by moving it and observing the effect.")

        for servo_id in active_servos:
            label = input(f"\nLabel servo {servo_id}? [y/n/skip all]: ").strip().lower()
            if label == 'skip all':
                break
            if label != 'y':
                continue

            cal = self.label_servo_interactive(servo_id)
            self.calibrator.calibration.servos[servo_id] = cal
            self.library.servo_labels[servo_id] = cal.name

            print(f"Servo {servo_id} labeled as '{cal.name}'")

    def _joint_groups_flow(self):
        """Define joint groups (e.g., left_leg, right_arm)."""
        print("\n=== Joint Groups ===")
        print("Group servos by function (e.g., 'left_front_leg': [1, 2, 3])")

        servos = list(self.calibrator.calibration.servos.keys())
        if not servos:
            print("No servos discovered yet. Run servo discovery first.")
            return

        print(f"Available servos: {servos}")
        for sid, cal in self.calibrator.calibration.servos.items():
            print(f"  {sid}: {cal.name}")

        while True:
            group_name = input("\nGroup name (or 'done'): ").strip()
            if group_name.lower() == 'done':
                break

            servo_ids = input("Servo IDs (comma-separated): ").strip()
            try:
                ids = [int(s.strip()) for s in servo_ids.split(",")]
                self.library.joint_groups[group_name] = ids
                print(f"Created group '{group_name}': {ids}")
            except ValueError:
                print("Invalid input. Use: 1, 2, 3")

    def _pose_recording_flow(self):
        """Record multiple poses."""
        print("\n=== Pose Recording ===")
        print("Record named poses for the robot.")
        print("Commands: record, list, delete, test, done")

        while True:
            cmd = input("\nPose> ").strip().lower()

            if cmd == 'record' or cmd == 'r':
                self.record_pose_interactive()

            elif cmd == 'list' or cmd == 'l':
                poses = self.calibrator.calibration.poses
                if poses:
                    for name, pose in poses.items():
                        print(f"  {name}: {len(pose.servo_positions)} servos")
                else:
                    print("No poses recorded")

            elif cmd.startswith('delete '):
                name = cmd[7:].strip()
                if name in self.calibrator.calibration.poses:
                    del self.calibrator.calibration.poses[name]
                    print(f"Deleted pose '{name}'")
                else:
                    print(f"Pose not found: {name}")

            elif cmd.startswith('test '):
                name = cmd[5:].strip()
                pose = self.calibrator.calibration.get_pose(name)
                if pose:
                    print(f"Applying pose '{name}'...")
                    self.calibrator.apply_pose(pose)
                else:
                    print(f"Pose not found: {name}")

            elif cmd in ('done', 'q'):
                break

    def _action_creation_flow(self):
        """Create actions from poses."""
        print("\n=== Action Creation ===")
        print("Create multi-step actions from recorded poses.")
        print("Commands: create, list, preview, delete, done")

        while True:
            cmd = input("\nAction> ").strip().lower()

            if cmd == 'create' or cmd == 'c':
                self.create_action_interactive()

            elif cmd == 'list' or cmd == 'l':
                if self.library.actions:
                    for name, action in self.library.actions.items():
                        print(f"  {name}: {len(action.steps)} steps ({action.action_type.value})")
                else:
                    print("No actions created")

            elif cmd.startswith('preview '):
                name = cmd[8:].strip()
                action = self.library.actions.get(name)
                if action:
                    self.execute_action(action)
                else:
                    print(f"Action not found: {name}")

            elif cmd.startswith('delete '):
                name = cmd[7:].strip()
                if name in self.library.actions:
                    del self.library.actions[name]
                    print(f"Deleted action '{name}'")
                else:
                    print(f"Action not found: {name}")

            elif cmd in ('done', 'q'):
                break

    def _skill_generation_flow(self):
        """Generate Python skill code."""
        print("\n=== Skill Generation ===")

        if not self.library.actions:
            print("No actions to generate skills from.")
            return

        print("Available actions:")
        for name in self.library.actions:
            print(f"  {name}")

        action_name = input("\nAction to generate (or 'all'): ").strip()

        skills_dir = Path.home() / ".ate" / "skills" / self.robot_name
        skills_dir.mkdir(parents=True, exist_ok=True)

        if action_name == 'all':
            for name, action in self.library.actions.items():
                code = self.generate_skill_code(action)
                path = skills_dir / f"{name}.py"
                with open(path, 'w') as f:
                    f.write(code)
                print(f"Generated: {path}")
        else:
            action = self.library.actions.get(action_name)
            if action:
                code = self.generate_skill_code(action)
                path = skills_dir / f"{action_name}.py"
                with open(path, 'w') as f:
                    f.write(code)
                print(f"Generated: {path}")
                print("\n--- Generated Code ---")
                print(code)
            else:
                print(f"Action not found: {action_name}")

    def _execute_action_flow(self):
        """Execute a saved action."""
        if not self.library.actions:
            print("No actions available.")
            return

        print("Available actions:")
        for name in self.library.actions:
            print(f"  {name}")

        name = input("Action to execute: ").strip()
        action = self.library.actions.get(name)

        if action:
            self.execute_action(action)
        else:
            print(f"Action not found: {name}")

    def _save_library(self):
        """Save skill library and calibration."""
        # Save calibration
        save_calibration(self.calibrator.calibration)

        # Save skill library
        lib_path = Path.home() / ".ate" / "skill_libraries" / f"{self.robot_name}.json"
        self.library.calibration = self.calibrator.calibration
        self.library.save(lib_path)

        print(f"Saved calibration: ~/.ate/calibrations/{self.robot_name}.json")
        print(f"Saved skill library: {lib_path}")

    def _quick_servo_test(self):
        """Quick servo test without full labeling."""
        print("\n=== Quick Servo Test ===")
        print("Commands: <servo_id> <value> (e.g., '11 2500'), or 'done'")

        while True:
            cmd = input("Test> ").strip()
            if cmd.lower() in ('done', 'q'):
                break

            try:
                parts = cmd.split()
                servo_id = int(parts[0])
                value = int(parts[1]) if len(parts) > 1 else 1500

                print(f"Moving servo {servo_id} to {value}...")
                self.calibrator.set_servo(servo_id, value, 500)
                self.webcam.show_preview("Servo Test")

            except (ValueError, IndexError):
                print("Format: <servo_id> <value> (e.g., '11 2500')")


# =============================================================================
# CLI Integration
# =============================================================================

def visual_label_command(
    port: str,
    name: str = "robot",
    robot_type: str = "unknown",
    webcam_id: int = 0,
    camera_url: Optional[str] = None,
):
    """Run the visual labeling session."""
    labeler = DualCameraLabeler(
        serial_port=port,
        robot_name=name,
        robot_model=robot_type,
        webcam_id=webcam_id,
        robot_camera_url=camera_url,
    )

    labeler.run_interactive_session()


def load_skill_library(robot_name: str) -> Optional[SkillLibrary]:
    """Load a saved skill library."""
    lib_path = Path.home() / ".ate" / "skill_libraries" / f"{robot_name}.json"
    cal = load_calibration(robot_name)

    if lib_path.exists():
        return SkillLibrary.load(lib_path, cal)
    return None


def list_skill_libraries() -> List[str]:
    """List available skill libraries."""
    lib_dir = Path.home() / ".ate" / "skill_libraries"
    if not lib_dir.exists():
        return []
    return [p.stem for p in lib_dir.glob("*.json")]
