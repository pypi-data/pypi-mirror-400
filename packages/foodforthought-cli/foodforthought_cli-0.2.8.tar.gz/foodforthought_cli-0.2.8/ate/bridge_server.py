#!/usr/bin/env python3
"""
ATE Bridge Server - WebSocket server for Artifex integration.

This module provides a WebSocket server that allows Artifex Desktop to:
1. Discover connected robots
2. Connect to robot hardware
3. Control servos and read states
4. Execute trajectories
5. Deploy and run skills
6. Sync URDF configurations

Usage:
    ate bridge                    # Start on default port 8765
    ate bridge --port 9000        # Start on custom port
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Set, Optional, List
from pathlib import Path

# Optional imports
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


@dataclass
class ServoState:
    """Current state of a servo."""
    id: int
    position: float = 0.0  # radians
    velocity: float = 0.0
    temperature: float = 0.0
    load: float = 0.0
    voltage: float = 0.0
    torque_enabled: bool = False


@dataclass
class RobotConnection:
    """Active robot connection."""
    port: str
    baud_rate: int
    robot_type: str
    servo_ids: List[int]
    servo_states: Dict[int, ServoState] = field(default_factory=dict)
    serial_conn: Any = None


@dataclass
class PortInfo:
    """Information about a serial port."""
    path: str
    description: str
    vid: Optional[int] = None
    pid: Optional[int] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None


class ATEBridgeServer:
    """
    WebSocket server for Artifex-ATE integration.

    Handles bidirectional communication between Artifex Desktop and
    physical robot hardware through a WebSocket connection.
    """

    def __init__(self, port: int = 8765, verbose: bool = False):
        self.port = port
        self.verbose = verbose
        self.connections: Set[WebSocketServerProtocol] = set()
        self.robot: Optional[RobotConnection] = None
        self.handlers: Dict[str, Callable] = {}
        self._running = False
        self._broadcast_task: Optional[asyncio.Task] = None
        self._setup_handlers()

    def _setup_handlers(self):
        """Register request handlers."""
        self.handlers = {
            # Connection management
            "ping": self._handle_ping,
            "discover_ports": self._handle_discover_ports,
            "connect_robot": self._handle_connect_robot,
            "disconnect_robot": self._handle_disconnect_robot,

            # Servo control
            "get_servo_state": self._handle_get_servo_state,
            "set_servo_position": self._handle_set_servo_position,
            "set_servo_torque": self._handle_set_servo_torque,

            # Trajectory execution
            "execute_trajectory": self._handle_execute_trajectory,

            # Configuration sync
            "get_robot_config": self._handle_get_robot_config,
            "sync_urdf": self._handle_sync_urdf,
            "sync_config": self._handle_sync_config,

            # Skill management
            "list_skills": self._handle_list_skills,
            "deploy_skill": self._handle_deploy_skill,
            "run_skill": self._handle_run_skill,
        }

    def _log(self, message: str):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[ATE Bridge] {message}")

    async def handle_connection(self, websocket: WebSocketServerProtocol):
        """Handle a new WebSocket connection."""
        self.connections.add(websocket)
        client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self._log(f"Client connected: {client_addr}")

        try:
            async for message in websocket:
                try:
                    request = json.loads(message)
                    response = await self._handle_request(request)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError as e:
                    await websocket.send(json.dumps({
                        "error": f"Invalid JSON: {str(e)}"
                    }))
        except websockets.exceptions.ConnectionClosed:
            self._log(f"Client disconnected: {client_addr}")
        finally:
            self.connections.discard(websocket)

    async def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate handler."""
        action = request.get("action")
        params = request.get("params", {})
        request_id = request.get("id")

        self._log(f"Request: {action} (id={request_id})")

        handler = self.handlers.get(action)
        if not handler:
            return {
                "id": request_id,
                "error": f"Unknown action: {action}"
            }

        try:
            result = await handler(params)
            return {"id": request_id, "result": result}
        except Exception as e:
            self._log(f"Error handling {action}: {str(e)}")
            return {"id": request_id, "error": str(e)}

    # =========================================================================
    # Connection Handlers
    # =========================================================================

    async def _handle_ping(self, params: Dict) -> Dict:
        """Simple ping for connection testing."""
        return {"pong": True, "timestamp": time.time()}

    async def _handle_discover_ports(self, params: Dict) -> Dict:
        """Discover available serial ports with robots."""
        if not HAS_SERIAL:
            return {"ports": [], "error": "pyserial not installed"}

        ports = []
        for port in serial.tools.list_ports.comports():
            port_info = PortInfo(
                path=port.device,
                description=port.description or "",
                vid=port.vid,
                pid=port.pid,
                serial_number=port.serial_number,
                manufacturer=port.manufacturer
            )
            ports.append({
                "path": port_info.path,
                "description": port_info.description,
                "vid": port_info.vid,
                "pid": port_info.pid,
                "serialNumber": port_info.serial_number,
                "manufacturer": port_info.manufacturer
            })

        return {"ports": ports}

    async def _handle_connect_robot(self, params: Dict) -> Dict:
        """Connect to robot on specified port."""
        port = params.get("port")
        robot_type = params.get("robot_type", "auto")
        baud_rate = params.get("baud_rate", 115200)

        if not port:
            raise ValueError("Port is required")

        if not HAS_SERIAL:
            # Mock connection for testing without hardware
            self._log(f"Mock connecting to {port}")
            self.robot = RobotConnection(
                port=port,
                baud_rate=baud_rate,
                robot_type=robot_type,
                servo_ids=[1, 2, 3, 4, 5, 6],  # Mock 6 servos
            )
            # Initialize mock servo states
            for sid in self.robot.servo_ids:
                self.robot.servo_states[sid] = ServoState(id=sid)

            return {
                "connected": True,
                "port": port,
                "robotType": robot_type,
                "servos": [
                    {"id": sid, "position": 0.0, "velocity": 0.0}
                    for sid in self.robot.servo_ids
                ]
            }

        # Real connection
        try:
            ser = serial.Serial(port, baud_rate, timeout=1)

            # Scan for servos
            servo_ids = await self._scan_servos(ser)

            self.robot = RobotConnection(
                port=port,
                baud_rate=baud_rate,
                robot_type=robot_type,
                servo_ids=servo_ids,
                serial_conn=ser
            )

            # Initialize servo states
            for sid in servo_ids:
                self.robot.servo_states[sid] = ServoState(id=sid)

            self._log(f"Connected to {port}, found {len(servo_ids)} servos")

            return {
                "connected": True,
                "port": port,
                "robotType": robot_type,
                "servos": [
                    {"id": sid, "position": 0.0, "velocity": 0.0}
                    for sid in servo_ids
                ]
            }
        except serial.SerialException as e:
            raise ValueError(f"Failed to connect: {str(e)}")

    async def _scan_servos(self, ser: Any) -> List[int]:
        """Scan for connected servos."""
        # This is a placeholder - actual implementation depends on protocol
        # For HiWonder servos, we'd send a broadcast read and collect responses
        found_ids = []

        # Try scanning IDs 1-20
        for servo_id in range(1, 21):
            # Send ping command (protocol-specific)
            # For now, return mock IDs
            pass

        # Return mock servo IDs for now
        return [1, 2, 3, 4, 5, 6]

    async def _handle_disconnect_robot(self, params: Dict) -> Dict:
        """Disconnect from robot."""
        if self.robot:
            if self.robot.serial_conn:
                self.robot.serial_conn.close()
            self.robot = None
            self._log("Robot disconnected")

        return {"disconnected": True}

    # =========================================================================
    # Servo Control Handlers
    # =========================================================================

    async def _handle_get_servo_state(self, params: Dict) -> Dict:
        """Get current state of all servos."""
        if not self.robot:
            raise ValueError("No robot connected")

        # Read current servo states
        servo_states = []
        for sid, state in self.robot.servo_states.items():
            servo_states.append({
                "id": sid,
                "position": state.position,
                "velocity": state.velocity,
                "temperature": state.temperature,
                "load": state.load,
                "voltage": state.voltage,
                "torqueEnabled": state.torque_enabled
            })

        return {"servos": servo_states}

    async def _handle_set_servo_position(self, params: Dict) -> Dict:
        """Set position of a single servo."""
        if not self.robot:
            raise ValueError("No robot connected")

        servo_id = params.get("servo_id")
        position = params.get("position")  # radians
        speed = params.get("speed", 1.0)   # 0-1 normalized

        if servo_id is None or position is None:
            raise ValueError("servo_id and position are required")

        if servo_id not in self.robot.servo_states:
            raise ValueError(f"Unknown servo ID: {servo_id}")

        # Update state (real implementation would send to hardware)
        self.robot.servo_states[servo_id].position = position
        self._log(f"Set servo {servo_id} to {position:.3f} rad")

        return {"success": True, "servoId": servo_id, "position": position}

    async def _handle_set_servo_torque(self, params: Dict) -> Dict:
        """Enable/disable torque on a servo or all servos."""
        if not self.robot:
            raise ValueError("No robot connected")

        servo_id = params.get("servo_id")  # None = all servos
        enabled = params.get("enabled", True)

        if servo_id is not None:
            if servo_id not in self.robot.servo_states:
                raise ValueError(f"Unknown servo ID: {servo_id}")
            self.robot.servo_states[servo_id].torque_enabled = enabled
            affected = [servo_id]
        else:
            for state in self.robot.servo_states.values():
                state.torque_enabled = enabled
            affected = list(self.robot.servo_states.keys())

        return {"success": True, "servoIds": affected, "enabled": enabled}

    # =========================================================================
    # Trajectory Handlers
    # =========================================================================

    async def _handle_execute_trajectory(self, params: Dict) -> Dict:
        """Execute a trajectory on the robot."""
        if not self.robot:
            raise ValueError("No robot connected")

        trajectory = params.get("trajectory", [])
        if not trajectory:
            raise ValueError("Empty trajectory")

        self._log(f"Executing trajectory with {len(trajectory)} waypoints")

        start_time = time.time()

        for i, waypoint in enumerate(trajectory):
            wp_time = waypoint.get("time", 0)
            positions = waypoint.get("positions", {})

            # Wait until waypoint time
            elapsed = time.time() - start_time
            if wp_time > elapsed:
                await asyncio.sleep(wp_time - elapsed)

            # Apply positions
            for joint_name, position in positions.items():
                # Map joint name to servo ID (simplified)
                servo_id = int(joint_name.split("_")[-1]) if "_" in joint_name else 1
                if servo_id in self.robot.servo_states:
                    self.robot.servo_states[servo_id].position = position

            # Broadcast state update
            await self._broadcast_servo_state()

        duration = time.time() - start_time
        self._log(f"Trajectory completed in {duration:.2f}s")

        return {"success": True, "duration": duration}

    # =========================================================================
    # Configuration Handlers
    # =========================================================================

    async def _handle_get_robot_config(self, params: Dict) -> Dict:
        """Get current robot configuration."""
        if not self.robot:
            raise ValueError("No robot connected")

        return {
            "port": self.robot.port,
            "baudRate": self.robot.baud_rate,
            "robotType": self.robot.robot_type,
            "servoIds": self.robot.servo_ids
        }

    async def _handle_sync_urdf(self, params: Dict) -> Dict:
        """Sync URDF from Artifex to create joint mapping."""
        urdf_content = params.get("urdf")
        if not urdf_content:
            raise ValueError("URDF content is required")

        # Parse URDF to extract joint names
        # This is a simplified parser - real implementation would use urdfpy
        import re
        joint_pattern = r'<joint\s+name="([^"]+)"'
        joint_names = re.findall(joint_pattern, urdf_content)

        # Create suggested mapping
        mapping = []
        for i, joint_name in enumerate(joint_names):
            if self.robot and i < len(self.robot.servo_ids):
                mapping.append({
                    "jointName": joint_name,
                    "servoId": self.robot.servo_ids[i],
                    "inverted": False,
                    "offset": 0.0
                })

        return {"mapping": mapping, "joints": joint_names}

    async def _handle_sync_config(self, params: Dict) -> Dict:
        """Sync full robot configuration from Artifex."""
        config = params.get("config", {})

        # Store configuration
        self._log(f"Received config for robot: {config.get('robot_name', 'unnamed')}")

        # Apply joint mapping if provided
        if "joints" in config:
            for joint in config["joints"]:
                servo_id = joint.get("servo_id")
                if servo_id and self.robot and servo_id in self.robot.servo_states:
                    # Store any additional config per servo
                    pass

        return {"success": True}

    # =========================================================================
    # Skill Handlers
    # =========================================================================

    async def _handle_list_skills(self, params: Dict) -> Dict:
        """List available skills."""
        # Look for skills in the current directory
        skills = []
        skills_dir = Path("./skills")

        if skills_dir.exists():
            for skill_path in skills_dir.glob("*/skill.json"):
                try:
                    with open(skill_path) as f:
                        skill_meta = json.load(f)
                        skills.append({
                            "name": skill_meta.get("name", skill_path.parent.name),
                            "version": skill_meta.get("version", "1.0.0"),
                            "description": skill_meta.get("description", ""),
                            "parameters": skill_meta.get("parameters", [])
                        })
                except Exception:
                    pass

        return {"skills": skills}

    async def _handle_deploy_skill(self, params: Dict) -> Dict:
        """Deploy a skill package to the robot."""
        skill_name = params.get("skill_name")
        package = params.get("package")  # Base64 encoded skill package

        if not skill_name:
            raise ValueError("skill_name is required")

        self._log(f"Deploying skill: {skill_name}")

        # In real implementation, this would:
        # 1. Decode the package
        # 2. Validate the skill
        # 3. Save to robot's skill directory
        # 4. Register with skill executor

        return {"success": True, "skillName": skill_name}

    async def _handle_run_skill(self, params: Dict) -> Dict:
        """Run a skill on the robot."""
        skill_name = params.get("skill_name")
        skill_params = params.get("params", {})

        if not skill_name:
            raise ValueError("skill_name is required")

        self._log(f"Running skill: {skill_name} with params: {skill_params}")

        # In real implementation, this would:
        # 1. Load the skill
        # 2. Execute with parameters
        # 3. Return results

        # Mock execution
        await asyncio.sleep(1.0)  # Simulate skill execution

        return {
            "success": True,
            "skillName": skill_name,
            "message": f"Skill {skill_name} completed",
            "data": {}
        }

    # =========================================================================
    # Broadcasting
    # =========================================================================

    async def _broadcast_servo_state(self):
        """Broadcast current servo state to all connected clients."""
        if not self.robot or not self.connections:
            return

        servo_states = []
        for sid, state in self.robot.servo_states.items():
            servo_states.append({
                "id": sid,
                "position": state.position,
                "velocity": state.velocity,
                "temperature": state.temperature,
                "load": state.load
            })

        message = json.dumps({
            "event": "servo_state",
            "data": {"servos": servo_states}
        })

        await asyncio.gather(
            *[ws.send(message) for ws in self.connections],
            return_exceptions=True
        )

    async def _broadcast_loop(self):
        """Periodically broadcast servo state to all clients."""
        while self._running:
            try:
                await self._broadcast_servo_state()
            except Exception as e:
                self._log(f"Broadcast error: {e}")
            await asyncio.sleep(0.05)  # 20Hz update rate

    # =========================================================================
    # Server Control
    # =========================================================================

    async def start(self):
        """Start the WebSocket server."""
        if not HAS_WEBSOCKETS:
            raise RuntimeError("websockets library not installed. Run: pip install websockets")

        self._running = True

        async with websockets.serve(
            self.handle_connection,
            "localhost",
            self.port
        ) as server:
            self._log(f"Server started on ws://localhost:{self.port}")

            # Start broadcast loop
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())

            # Wait forever
            await asyncio.Future()

    def stop(self):
        """Stop the server."""
        self._running = False
        if self._broadcast_task:
            self._broadcast_task.cancel()


def run_bridge_server(port: int = 8765, verbose: bool = False):
    """
    Run the ATE bridge server.

    Args:
        port: WebSocket port to listen on
        verbose: Enable verbose logging
    """
    server = ATEBridgeServer(port=port, verbose=verbose)

    print(f"\n{'='*50}")
    print(f"  ATE Bridge Server")
    print(f"{'='*50}")
    print(f"  Port: {port}")
    print(f"  URL:  ws://localhost:{port}")
    print(f"{'='*50}")
    print("\nWaiting for Artifex to connect...")
    print("Press Ctrl+C to stop\n")

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()


if __name__ == "__main__":
    run_bridge_server(verbose=True)
