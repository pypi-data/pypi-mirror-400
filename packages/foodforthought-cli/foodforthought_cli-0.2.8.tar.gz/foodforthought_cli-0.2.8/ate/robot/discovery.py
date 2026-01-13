"""
Auto-discovery of robots on network and USB.

Scans for:
- Serial devices matching known patterns
- Network cameras (ESP32-CAM, IP cameras)
- ROS2 topics (if ROS2 available)
- mDNS services
"""

import os
import glob
import time
import platform
import concurrent.futures
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum, auto

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from .registry import KNOWN_ROBOTS, RobotType, ConnectionType


class DiscoveryStatus(Enum):
    """Status of discovered device."""
    FOUND = auto()        # Device found
    IDENTIFIED = auto()   # Device identified as known robot
    CONNECTED = auto()    # Successfully connected
    ERROR = auto()        # Error during discovery


@dataclass
class DiscoveredRobot:
    """A robot discovered on the network or USB."""
    robot_type: Optional[str] = None    # ID of matched robot type
    name: str = ""                       # Display name
    status: DiscoveryStatus = DiscoveryStatus.FOUND

    # Connection info
    connection: Optional[ConnectionType] = None
    port: Optional[str] = None           # Serial port
    ip: Optional[str] = None             # Network IP
    ports: Dict[str, int] = field(default_factory=dict)  # Network ports

    # Additional info
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware: Optional[str] = None

    # Raw data
    raw_data: Dict[str, Any] = field(default_factory=dict)


def discover_robots(
    timeout: float = 5.0,
    scan_serial: bool = True,
    scan_network: bool = True,
    network_subnet: Optional[str] = None,
) -> List[DiscoveredRobot]:
    """
    Discover all robots on network and USB.

    Args:
        timeout: Timeout for network scans
        scan_serial: Scan USB serial devices
        scan_network: Scan network for cameras/robots
        network_subnet: Subnet to scan (e.g., "192.168.1")

    Returns:
        List of discovered robots
    """
    discovered = []

    if scan_serial:
        discovered.extend(discover_serial_robots())

    if scan_network:
        discovered.extend(discover_network_cameras(
            timeout=timeout,
            subnet=network_subnet
        ))

    return discovered


def discover_serial_robots() -> List[DiscoveredRobot]:
    """
    Discover robots connected via USB serial.

    Matches connected serial devices against known robot patterns.
    """
    if not HAS_SERIAL:
        return []

    discovered = []
    ports = serial.tools.list_ports.comports()

    for port in ports:
        robot = DiscoveredRobot(
            connection=ConnectionType.SERIAL,
            port=port.device,
            raw_data={
                "vid": port.vid,
                "pid": port.pid,
                "serial_number": port.serial_number,
                "manufacturer": port.manufacturer,
                "product": port.product,
                "description": port.description,
            }
        )

        # Try to identify robot type by matching patterns
        for robot_type in KNOWN_ROBOTS.values():
            if ConnectionType.SERIAL not in robot_type.connection_types:
                continue

            for pattern in robot_type.serial_patterns:
                # Convert glob pattern to check
                if _matches_pattern(port.device, pattern):
                    robot.robot_type = robot_type.id
                    robot.name = f"{robot_type.name} ({port.device})"
                    robot.manufacturer = robot_type.manufacturer
                    robot.model = robot_type.name
                    robot.status = DiscoveryStatus.IDENTIFIED
                    break

            if robot.robot_type:
                break

        if not robot.robot_type:
            robot.name = f"Unknown Device ({port.device})"
            robot.manufacturer = port.manufacturer
            robot.model = port.product

        discovered.append(robot)

    return discovered


def discover_network_cameras(
    timeout: float = 2.0,
    subnet: Optional[str] = None,
    max_workers: int = 50,
) -> List[DiscoveredRobot]:
    """
    Discover network cameras (ESP32-CAM, IP cameras).

    Scans common camera endpoints on the local subnet.
    """
    if not HAS_REQUESTS:
        return []

    # Determine subnet to scan
    if subnet is None:
        subnet = _get_local_subnet()
        if subnet is None:
            return []

    discovered = []
    ips_to_scan = [f"{subnet}.{i}" for i in range(1, 255)]

    def check_camera(ip: str) -> Optional[DiscoveredRobot]:
        """Check if IP has a camera endpoint."""
        try:
            # Try ESP32-CAM status endpoint
            response = requests.get(
                f"http://{ip}/status",
                timeout=timeout
            )
            if response.status_code == 200:
                return DiscoveredRobot(
                    robot_type=None,  # Camera only, not a robot
                    name=f"ESP32-CAM ({ip})",
                    status=DiscoveryStatus.FOUND,
                    connection=ConnectionType.WIFI,
                    ip=ip,
                    ports={"camera_port": 80, "camera_stream_port": 81},
                    raw_data={"type": "esp32cam", "response": response.text[:200]},
                )
        except requests.RequestException:
            pass

        try:
            # Try generic camera snapshot
            response = requests.get(
                f"http://{ip}/capture",
                timeout=timeout,
                stream=True
            )
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if "image" in content_type:
                    return DiscoveredRobot(
                        name=f"Network Camera ({ip})",
                        status=DiscoveryStatus.FOUND,
                        connection=ConnectionType.WIFI,
                        ip=ip,
                        ports={"camera_port": 80},
                        raw_data={"type": "generic_camera"},
                    )
        except requests.RequestException:
            pass

        return None

    # Parallel scan
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_camera, ip): ip for ip in ips_to_scan}

        try:
            for future in concurrent.futures.as_completed(futures, timeout=timeout * 3):
                try:
                    result = future.result(timeout=0.1)
                    if result:
                        discovered.append(result)
                except Exception:
                    pass
        except TimeoutError:
            # Some futures didn't complete in time, that's ok
            pass

    return discovered


def probe_serial_device(port: str, baud_rate: int = 115200) -> Optional[Dict[str, Any]]:
    """
    Probe a serial device to identify what type of robot it is.

    Sends identification commands and parses response.
    """
    if not HAS_SERIAL:
        return None

    try:
        with serial.Serial(port, baud_rate, timeout=2) as ser:
            time.sleep(0.5)

            # Try MicroPython REPL identification
            ser.write(b'\x03')  # Ctrl+C
            time.sleep(0.2)
            ser.write(b'\x02')  # Ctrl+B for friendly REPL
            time.sleep(0.3)

            # Check for MicroPython
            ser.write(b'import sys; print(sys.implementation)\r\n')
            time.sleep(0.5)
            response = ser.read(1000).decode('utf-8', errors='ignore')

            if 'micropython' in response.lower():
                info = {"type": "micropython", "response": response}

                # Try to detect MechDog
                ser.write(b'from HW_MechDog import MechDog\r\n')
                time.sleep(0.3)
                response2 = ser.read(500).decode('utf-8', errors='ignore')

                if 'Error' not in response2 and 'Traceback' not in response2:
                    info["robot"] = "hiwonder_mechdog"

                return info

    except Exception as e:
        return {"error": str(e)}

    return None


def _matches_pattern(device: str, pattern: str) -> bool:
    """Check if device matches a glob pattern."""
    import fnmatch
    return fnmatch.fnmatch(device, pattern)


def _get_local_subnet() -> Optional[str]:
    """Get the local network subnet (e.g., '192.168.1')."""
    system = platform.system()

    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()

        # Extract subnet
        parts = ip.split(".")
        if len(parts) == 4:
            return ".".join(parts[:3])
    except Exception:
        pass

    return None


def quick_scan() -> Dict[str, Any]:
    """
    Quick scan for common robot configurations.

    Returns summary of what was found.
    """
    result = {
        "serial_ports": [],
        "network_cameras": [],
        "identified_robots": [],
    }

    # Scan serial
    serial_robots = discover_serial_robots()
    for robot in serial_robots:
        result["serial_ports"].append({
            "port": robot.port,
            "type": robot.robot_type,
            "name": robot.name,
        })
        if robot.robot_type:
            result["identified_robots"].append(robot)

    # Quick network scan (just local subnet, fast timeout)
    network_cameras = discover_network_cameras(timeout=1.0)
    for camera in network_cameras:
        result["network_cameras"].append({
            "ip": camera.ip,
            "name": camera.name,
            "ports": camera.ports,
        })

    return result
