"""
MechDog driver implementation.

Implements the FoodforThought interfaces for HiWonder MechDog.

The MechDog runs MicroPython with the HW_MechDog library.
Communication is via serial REPL commands.

Hardware specs:
- 12 servos (3 per leg: hip, thigh, calf)
- Optional arm attachment (3 servos)
- ESP32-based controller
- LX-16A serial bus servos
"""

import time
import math
from typing import Optional, List, Set, Tuple
from dataclasses import dataclass

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

from ..interfaces.types import (
    Vector3,
    Quaternion,
    Pose,
    Twist,
    JointState,
    GaitType,
    ActionResult,
    RobotStatus,
    RobotMode,
    BatteryState,
    IMUReading,
)
from ..interfaces.base import (
    RobotInterface,
    SafetyInterface,
    RobotInfo,
    Capability,
)
from ..interfaces.locomotion import QuadrupedLocomotion
from ..interfaces.body import BodyPoseInterface


# =============================================================================
# MechDog-specific constants
# =============================================================================

# Servo value ranges (raw values from MechDog)
SERVO_MIN = 0
SERVO_MAX = 4096
SERVO_CENTER = 2048

# Body dimensions (meters)
BODY_LENGTH = 0.20    # Front to back
BODY_WIDTH = 0.10     # Side to side
LEG_LENGTH = 0.12     # Total leg length

# Height limits (meters)
HEIGHT_MIN = 0.05
HEIGHT_MAX = 0.18
HEIGHT_DEFAULT = 0.12

# Speed limits
MAX_STRIDE_MM = 100   # Maximum stride in mm
MAX_TURN_DEG = 30     # Maximum turn rate in degrees


@dataclass
class MechDogConfig:
    """Configuration for MechDog connection."""
    port: str = "/dev/cu.usbserial-10"
    baud_rate: int = 115200
    timeout: float = 2.0
    has_arm: bool = False
    has_camera: bool = False


class MechDogDriver(QuadrupedLocomotion, BodyPoseInterface, SafetyInterface, RobotInterface):
    """
    Driver for HiWonder MechDog quadruped robot.

    Implements:
    - QuadrupedLocomotion: walk, turn, stand, sit, etc.
    - BodyPoseInterface: height, roll, pitch, yaw control
    - SafetyInterface: emergency stop, battery monitoring
    - RobotInterface: connection lifecycle, status

    Example:
        dog = MechDogDriver(port="/dev/cu.usbserial-10")
        dog.connect()

        dog.stand()
        dog.walk(Vector3.forward(), speed=0.3)
        dog.set_body_height(0.10)

        dog.disconnect()
    """

    def __init__(self, port: str = "/dev/cu.usbserial-10", config: Optional[MechDogConfig] = None):
        """
        Initialize MechDog driver.

        Args:
            port: Serial port for MechDog connection
            config: Optional configuration
        """
        self.config = config or MechDogConfig(port=port)
        self._serial: Optional[serial.Serial] = None
        self._connected = False
        self._estopped = False
        self._current_gait = GaitType.WALK

        # Cached state
        self._current_height = HEIGHT_DEFAULT
        self._current_orientation = (0.0, 0.0, 0.0)  # roll, pitch, yaw
        self._is_moving = False

        # Odometry (basic dead reckoning)
        self._pose = Pose.identity()
        self._velocity = Twist.zero()

    # =========================================================================
    # RobotInterface implementation
    # =========================================================================

    def get_info(self) -> RobotInfo:
        """Get MechDog information."""
        capabilities = {
            Capability.QUADRUPED,
            Capability.BODY_POSE,
            Capability.IMU,
        }

        if self.config.has_arm:
            capabilities.add(Capability.ARM)
            capabilities.add(Capability.GRIPPER)

        if self.config.has_camera:
            capabilities.add(Capability.CAMERA)

        return RobotInfo(
            name="MechDog",
            model="hiwonder_mechdog",
            manufacturer="HiWonder",
            archetype="quadruped",
            capabilities=capabilities,
            mass=1.5,  # kg
            dimensions=(BODY_LENGTH, BODY_WIDTH, HEIGHT_DEFAULT),
            workspace_min=(-2.0, -2.0, 0.0),
            workspace_max=(2.0, 2.0, 0.5),
            max_speed=0.3,  # m/s
            description="HiWonder MechDog quadruped robot with 12 DOF",
        )

    def connect(self) -> ActionResult:
        """Connect to MechDog via serial."""
        if not HAS_SERIAL:
            return ActionResult.error("pyserial not installed. Run: pip install pyserial")

        try:
            self._serial = serial.Serial(
                self.config.port,
                self.config.baud_rate,
                timeout=self.config.timeout
            )
            time.sleep(0.5)

            # Enter friendly REPL mode
            self._serial.write(b'\x03')  # Ctrl+C to interrupt
            time.sleep(0.3)
            self._serial.write(b'\x02')  # Ctrl+B for friendly REPL
            time.sleep(0.5)
            self._serial.reset_input_buffer()

            # Initialize MechDog library
            result = self._send_command("from HW_MechDog import MechDog")
            if "Error" in result or "Traceback" in result:
                return ActionResult.error(f"Failed to import HW_MechDog: {result}")

            result = self._send_command("dog = MechDog()")
            if "Error" in result or "Traceback" in result:
                return ActionResult.error(f"Failed to create MechDog: {result}")

            self._connected = True
            return ActionResult.ok("Connected to MechDog")

        except Exception as e:
            return ActionResult.error(f"Connection failed: {e}")

    def disconnect(self) -> ActionResult:
        """Disconnect from MechDog."""
        if self._serial:
            try:
                # Stop any movement first
                self.stop()
                self._serial.close()
            except Exception:
                pass
            finally:
                self._serial = None
                self._connected = False

        return ActionResult.ok("Disconnected")

    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected and self._serial is not None and self._serial.is_open

    def get_status(self) -> RobotStatus:
        """Get robot status."""
        mode = RobotMode.IDLE
        if self._estopped:
            mode = RobotMode.ESTOPPED
        elif self._is_moving:
            mode = RobotMode.MOVING
        elif self._connected:
            mode = RobotMode.READY

        return RobotStatus(
            mode=mode,
            is_ready=self._connected and not self._estopped,
            is_moving=self._is_moving,
            errors=[],
            battery=self.get_battery_state(),
        )

    # =========================================================================
    # SafetyInterface implementation
    # =========================================================================

    def emergency_stop(self) -> ActionResult:
        """Emergency stop - immediately stop all motion."""
        self._estopped = True
        self._is_moving = False

        if self._serial:
            # Send stop command
            self._send_command("dog.move(0, 0)")

        return ActionResult.ok("Emergency stop activated")

    def reset_emergency_stop(self) -> ActionResult:
        """Clear emergency stop."""
        self._estopped = False
        return ActionResult.ok("Emergency stop cleared")

    def is_estopped(self) -> bool:
        """Check if estopped."""
        return self._estopped

    def get_battery_state(self) -> Optional[BatteryState]:
        """Get battery state (not supported on basic MechDog)."""
        # MechDog doesn't report battery state via REPL
        return None

    # =========================================================================
    # QuadrupedLocomotion implementation
    # =========================================================================

    def get_pose(self) -> Pose:
        """Get current pose (from dead reckoning)."""
        return self._pose

    def get_velocity(self) -> Twist:
        """Get current velocity."""
        return self._velocity

    def stop(self) -> ActionResult:
        """Stop all movement."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        self._send_command("dog.move(0, 0)")
        self._is_moving = False
        self._velocity = Twist.zero()

        return ActionResult.ok("Stopped")

    def is_moving(self) -> bool:
        """Check if moving."""
        return self._is_moving

    def walk(self, direction: Vector3, speed: float = 0.5) -> ActionResult:
        """Walk in direction at speed."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        if self._estopped:
            return ActionResult.error("Emergency stop active")

        # Convert direction and speed to MechDog stride/angle
        # MechDog uses: move(stride_mm, angle_deg)
        # stride: -100 to +100 (negative = backward)
        # angle: -30 to +30 (negative = turn right)

        # Calculate stride from speed (simple mapping)
        stride = int(min(MAX_STRIDE_MM, max(-MAX_STRIDE_MM, speed * 200)))

        # Apply direction
        if direction.x < 0:  # Backward
            stride = -abs(stride)

        # Calculate turn from y component
        angle = int(direction.y * MAX_TURN_DEG)
        angle = max(-MAX_TURN_DEG, min(MAX_TURN_DEG, angle))

        self._send_command(f"dog.move({stride}, {angle})")
        self._is_moving = True

        # Update velocity estimate
        self._velocity = Twist(
            linear=Vector3(speed * direction.x, speed * direction.y, 0),
            angular=Vector3.zero()
        )

        return ActionResult.ok(f"Walking: stride={stride}, angle={angle}")

    def walk_to(self, target: Vector3, speed: float = 0.5) -> ActionResult:
        """Walk to target position (blocking)."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        # Simple implementation: walk toward target
        # In a real implementation, this would use feedback control

        current = self.get_pose().position
        delta = target - current
        distance = delta.magnitude()

        if distance < 0.05:  # Already at target
            return ActionResult.ok("Already at target")

        # Calculate direction
        direction = delta.normalized()

        # Walk toward target
        self.walk(direction, speed)

        # Wait for approximate time to reach target
        # (Very rough estimate - real implementation needs odometry)
        travel_time = distance / speed
        time.sleep(min(travel_time, 10.0))  # Cap at 10 seconds

        self.stop()

        return ActionResult.ok(f"Walked to target")

    def turn(self, angle: float, speed: float = 0.5) -> ActionResult:
        """Turn by angle (blocking)."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        # Convert radians to degrees
        angle_deg = math.degrees(angle)

        # MechDog turn is via move(0, angle)
        # Positive angle = turn left
        turn_deg = max(-MAX_TURN_DEG, min(MAX_TURN_DEG, angle_deg))

        # Estimate time based on turn rate
        turn_time = abs(angle_deg) / 30.0  # Rough estimate

        self._send_command(f"dog.move(0, {int(turn_deg)})")
        self._is_moving = True

        time.sleep(turn_time)

        self.stop()

        # Update pose estimate
        roll, pitch, yaw = self._pose.orientation.to_euler()
        yaw += angle
        self._pose = Pose(
            self._pose.position,
            Quaternion.from_euler(roll, pitch, yaw)
        )

        return ActionResult.ok(f"Turned {angle_deg:.1f} degrees")

    def turn_continuous(self, angular_velocity: float) -> ActionResult:
        """Turn continuously."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        # Map angular velocity to turn angle
        angle = int(angular_velocity * 20)  # Rough mapping
        angle = max(-MAX_TURN_DEG, min(MAX_TURN_DEG, angle))

        self._send_command(f"dog.move(0, {angle})")
        self._is_moving = True

        self._velocity = Twist(
            linear=Vector3.zero(),
            angular=Vector3(0, 0, angular_velocity)
        )

        return ActionResult.ok(f"Turning at {angular_velocity:.2f} rad/s")

    def stand(self) -> ActionResult:
        """Stand up."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        self._send_command("dog.set_default_pose()")
        self._is_moving = False
        self._current_height = HEIGHT_DEFAULT

        return ActionResult.ok("Standing")

    def sit(self) -> ActionResult:
        """Sit down."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        # Lower body to minimum height
        return self.set_body_height(HEIGHT_MIN)

    def lie_down(self) -> ActionResult:
        """Lie down (same as sit for MechDog)."""
        return self.sit()

    def set_gait(self, gait: GaitType) -> ActionResult:
        """Set gait (MechDog has limited gait support)."""
        self._current_gait = gait
        return ActionResult.ok(f"Gait set to {gait.name}")

    def get_gait(self) -> GaitType:
        """Get current gait."""
        return self._current_gait

    def get_foot_positions(self) -> List[Vector3]:
        """Get foot positions (estimated from body height)."""
        # Simplified: assume feet are at corners of body rectangle
        h = self._current_height
        return [
            Vector3(BODY_LENGTH/2, BODY_WIDTH/2, -h),   # Front left
            Vector3(BODY_LENGTH/2, -BODY_WIDTH/2, -h),  # Front right
            Vector3(-BODY_LENGTH/2, BODY_WIDTH/2, -h),  # Back left
            Vector3(-BODY_LENGTH/2, -BODY_WIDTH/2, -h), # Back right
        ]

    def get_joint_state(self) -> JointState:
        """Get all joint positions."""
        if not self._check_connection():
            return JointState()

        result = self._send_command("print(dog.read_all_servo())")

        # Parse result like "[2096, 1621, 2170, ...]"
        try:
            # Extract list from response
            import re
            match = re.search(r'\[([^\]]+)\]', result)
            if match:
                values = [int(x.strip()) for x in match.group(1).split(',')]
                # Convert to radians (rough conversion)
                positions = tuple(
                    (v - SERVO_CENTER) / SERVO_MAX * math.pi
                    for v in values
                )
                return JointState(positions=positions)
        except Exception:
            pass

        return JointState()

    # =========================================================================
    # BodyPoseInterface implementation
    # =========================================================================

    def set_body_height(self, height: float) -> ActionResult:
        """Set body height."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        # Clamp to limits
        height = max(HEIGHT_MIN, min(HEIGHT_MAX, height))

        # MechDog uses set_pose() for body position
        # Height is controlled via leg extension
        # This is a simplified implementation

        self._current_height = height
        return ActionResult.ok(f"Height set to {height:.3f}m")

    def get_body_height(self) -> float:
        """Get body height."""
        return self._current_height

    def get_height_limits(self) -> Tuple[float, float]:
        """Get height limits."""
        return (HEIGHT_MIN, HEIGHT_MAX)

    def set_body_orientation(
        self,
        roll: float = 0.0,
        pitch: float = 0.0,
        yaw: float = 0.0
    ) -> ActionResult:
        """Set body orientation."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        # MechDog can tilt body via set_pose or transform
        # Convert to degrees for MechDog
        roll_deg = math.degrees(roll)
        pitch_deg = math.degrees(pitch)
        yaw_deg = math.degrees(yaw)

        # MechDog's transform() takes (x, y, z, roll, pitch, yaw)
        self._send_command(f"dog.transform(0, 0, 0, {roll_deg}, {pitch_deg}, {yaw_deg})")

        self._current_orientation = (roll, pitch, yaw)
        return ActionResult.ok(f"Orientation set to R={roll_deg:.1f} P={pitch_deg:.1f} Y={yaw_deg:.1f}")

    def get_body_orientation(self) -> Tuple[float, float, float]:
        """Get body orientation."""
        return self._current_orientation

    def set_body_pose(
        self,
        height: Optional[float] = None,
        roll: Optional[float] = None,
        pitch: Optional[float] = None,
        yaw: Optional[float] = None,
        x_offset: Optional[float] = None,
        y_offset: Optional[float] = None
    ) -> ActionResult:
        """Set combined body pose."""
        if height is not None:
            self.set_body_height(height)

        # Get current values for any not specified
        curr_r, curr_p, curr_y = self._current_orientation
        if roll is None:
            roll = curr_r
        if pitch is None:
            pitch = curr_p
        if yaw is None:
            yaw = curr_y

        return self.set_body_orientation(roll, pitch, yaw)

    # =========================================================================
    # Internal methods
    # =========================================================================

    def _check_connection(self) -> bool:
        """Check if connected and ready."""
        return self._connected and self._serial is not None and not self._estopped

    def _send_command(self, cmd: str, wait: float = 0.5) -> str:
        """Send command to MicroPython REPL and get response."""
        if not self._serial:
            return ""

        try:
            self._serial.reset_input_buffer()
            self._serial.write(f"{cmd}\r\n".encode())
            time.sleep(wait)
            response = self._serial.read(4000).decode('utf-8', errors='ignore')
            return response
        except Exception as e:
            return f"Error: {e}"

    # =========================================================================
    # MechDog-specific methods (not in interface)
    # =========================================================================

    def read_servo(self, servo_id: int) -> Optional[int]:
        """Read single servo position (raw value)."""
        if not self._check_connection():
            return None

        result = self._send_command(f"print(dog.read_servo({servo_id}))")
        try:
            # Parse integer from response
            import re
            match = re.search(r'(\d+)', result.split('\n')[-2])
            if match:
                return int(match.group(1))
        except Exception:
            pass
        return None

    def set_servo(self, servo_id: int, position: int, time_ms: int = 500) -> ActionResult:
        """Set single servo position (raw value)."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        self._send_command(f"dog.set_servo({servo_id}, {position}, {time_ms})")
        return ActionResult.ok(f"Servo {servo_id} set to {position}")

    def run_action(self, action_name: str) -> ActionResult:
        """Run a pre-programmed action."""
        if not self._check_connection():
            return ActionResult.error("Not connected")

        self._send_command(f"dog.action_run('{action_name}')")
        return ActionResult.ok(f"Running action: {action_name}")
