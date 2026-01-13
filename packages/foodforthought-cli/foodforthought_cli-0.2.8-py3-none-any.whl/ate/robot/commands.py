"""
Robot management CLI commands.

Provides:
- ate robot discover - Find robots on network/USB
- ate robot list - List known robot types
- ate robot info - Show robot capabilities
- ate robot setup - Interactive setup wizard
- ate robot test - Test robot capabilities
- ate robot profiles - Manage saved profiles
"""

import os
import sys
import json
from typing import Optional
from pathlib import Path

from .discovery import (
    discover_robots,
    discover_serial_robots,
    discover_network_cameras,
    discover_ble_robots,
    quick_scan,
)
from .profiles import (
    RobotProfile,
    load_profile,
    save_profile,
    list_profiles,
    delete_profile,
    get_template,
    list_templates,
    create_profile_from_discovery,
)
from .registry import (
    RobotRegistry,
    KNOWN_ROBOTS,
)
from .introspection import (
    get_capabilities,
    get_methods,
    test_capability,
    format_capabilities,
    format_methods,
)
from .manager import RobotManager
from .calibration import (
    VisualCalibrator,
    RobotCalibration,
    load_calibration,
    save_calibration,
    list_calibrations,
    quick_gripper_calibration,
)
from .visual_labeler import (
    DualCameraLabeler,
    SkillLibrary,
    load_skill_library,
    list_skill_libraries,
    visual_label_command,
)
from .skill_upload import (
    SkillLibraryUploader,
    upload_skill_library,
)
from .teach import teach_command
from .perception import LivePerceptionExecutor, PerceptionSystem


def robot_primitives_command(action: str = "list", name: Optional[str] = None):
    """
    List and inspect programmatic primitives.

    ate robot primitives list
    ate robot primitives show gripper_open
    ate robot primitives test pickup --port /dev/cu.usbserial-10
    """
    from .primitives import PrimitiveLibrary, SkillType

    lib = PrimitiveLibrary(robot_interface=None)

    if action == "list":
        print("=" * 60)
        print("SKILL PRIMITIVES")
        print("=" * 60)

        print(f"\nPrimitives ({len(lib.primitives)}):")
        print("-" * 40)
        for name, prim in lib.primitives.items():
            hw = ", ".join(r.value for r in prim.hardware) or "none"
            servos = len(prim.servo_targets)
            print(f"  {name:<20} [{hw}] ({servos} servos, {prim.duration_ms}ms)")

        print(f"\nCompound Skills ({len(lib.compounds)}):")
        print("-" * 40)
        for name, comp in lib.compounds.items():
            hw = ", ".join(r.value for r in comp.hardware) or "none"
            steps = len(comp.steps)
            print(f"  {name:<20} [{hw}] ({steps} steps)")
            print(f"    → {' → '.join(comp.steps)}")

        print(f"\nBehaviors ({len(lib.behaviors)}):")
        print("-" * 40)
        for name, beh in lib.behaviors.items():
            hw = ", ".join(r.value for r in beh.hardware) or "none"
            print(f"  {name:<20} [{hw}]")
            print(f"    {beh.description}")

        total = len(lib.primitives) + len(lib.compounds) + len(lib.behaviors)
        print(f"\nTotal: {total} skills")

    elif action == "show":
        if not name:
            print("Usage: ate robot primitives show <name>")
            sys.exit(1)

        # Find in primitives
        if name in lib.primitives:
            prim = lib.primitives[name]
            print(f"\nPrimitive: {name}")
            print("=" * 40)
            print(f"Description: {prim.description}")
            print(f"Duration: {prim.duration_ms}ms")
            print(f"Hardware: {[r.value for r in prim.hardware]}")
            print(f"\nServo Targets:")
            for sid, val in prim.servo_targets.items():
                print(f"  Servo {sid}: {val}")

        elif name in lib.compounds:
            comp = lib.compounds[name]
            print(f"\nCompound Skill: {name}")
            print("=" * 40)
            print(f"Description: {comp.description}")
            print(f"Wait between: {comp.wait_between_ms}ms")
            print(f"Hardware: {[r.value for r in comp.hardware]}")
            print(f"\nSteps:")
            for i, step in enumerate(comp.steps, 1):
                print(f"  {i}. {step}")

        elif name in lib.behaviors:
            beh = lib.behaviors[name]
            print(f"\nBehavior: {name}")
            print("=" * 40)
            print(f"Description: {beh.description}")
            print(f"Hardware: {[r.value for r in beh.hardware]}")
            print(f"\nSteps:")
            for i, step in enumerate(beh.steps, 1):
                if isinstance(step, dict):
                    print(f"  {i}. {step}")
                else:
                    print(f"  {i}. {step}")

        else:
            print(f"Skill not found: {name}")
            print("\nAvailable skills:")
            print(f"  Primitives: {', '.join(lib.primitives.keys())}")
            print(f"  Compounds: {', '.join(lib.compounds.keys())}")
            print(f"  Behaviors: {', '.join(lib.behaviors.keys())}")
            sys.exit(1)

    elif action == "test":
        if not name:
            print("Usage: ate robot primitives test <name> --port <port>")
            sys.exit(1)
        print(f"Testing skill: {name}")
        print("(Use 'ate robot behavior' for full behavior execution)")

    else:
        print(f"Unknown action: {action}")
        print("Available actions: list, show, test")
        sys.exit(1)


def robot_behavior_command(
    profile_name: Optional[str] = None,
    behavior: str = "pickup_green_ball",
    camera_ip: Optional[str] = None,
    simulate: bool = False,
):
    """
    Execute a high-level behavior.

    ate robot behavior pickup_green_ball --profile my_mechdog
    ate robot behavior pickup_green_ball --camera-ip 192.168.4.1
    ate robot behavior pickup_green_ball --simulate
    """
    # PREREQUISITE CHECK: Ensure direction calibration is complete
    # This is the enforcement that prevents catastrophic failures
    if profile_name and not simulate:
        from .calibration_state import CalibrationState

        state = CalibrationState.load(profile_name)
        passed, message = state.check_prerequisite("direction_calibrated")

        if not passed:
            print(message)
            print("\nThe behavior cannot run without direction calibration.")
            print("This prevents the arm from moving in the WRONG direction.")
            sys.exit(1)

    print(f"Behavior: {behavior}")
    print("=" * 50)

    robot = None

    if profile_name and not simulate:
        # Load robot from profile
        profile = load_profile(profile_name)
        if not profile:
            print(f"Profile not found: {profile_name}")
            sys.exit(1)

        manager = RobotManager()
        manager.load(profile_name)

        print("Connecting to robot...")
        if not manager.connect(profile_name):
            print("Connection failed")
            sys.exit(1)

        robot = manager.get(profile_name)
        camera_ip = camera_ip or profile.camera_ip

    # Create executor
    executor = LivePerceptionExecutor(
        robot_interface=robot,
        camera_ip=camera_ip or "192.168.4.1",
    )

    # Try to connect to camera (ok if it fails - will use simulation)
    if not simulate and camera_ip:
        if executor.connect():
            print(f"Camera connected: {camera_ip}")
        else:
            print("Camera not available - using simulated perception")

    try:
        # Execute behavior
        if behavior == "pickup_green_ball":
            success = executor.pickup_green_ball()
        else:
            print(f"Unknown behavior: {behavior}")
            print("Available: pickup_green_ball")
            sys.exit(1)

        print("\n" + "=" * 50)
        print(f"Result: {'SUCCESS' if success else 'FAILED'}")

    except KeyboardInterrupt:
        print("\n\nAborted by user")
    finally:
        executor.disconnect()
        if robot and profile_name:
            manager = RobotManager()
            manager.disconnect(profile_name)


def robot_discover_command(subnet: Optional[str] = None, timeout: float = 3.0, json_output: bool = False):
    """
    Discover robots on network and USB.

    ate robot discover
    ate robot discover --subnet 192.168.1 --timeout 5
    """
    print("Scanning for robots...\n")

    # Serial devices
    print("USB/Serial devices:")
    serial_robots = discover_serial_robots()

    if serial_robots:
        for robot in serial_robots:
            status = "✓" if robot.robot_type else "?"
            print(f"  {status} {robot.name}")
            print(f"      Port: {robot.port}")
            if robot.robot_type:
                print(f"      Type: {robot.robot_type}")
            if robot.manufacturer:
                print(f"      Manufacturer: {robot.manufacturer}")
    else:
        print("  (none found)")

    # Network cameras
    print("\nNetwork cameras:")
    cameras = discover_network_cameras(timeout=timeout, subnet=subnet)

    if cameras:
        for cam in cameras:
            print(f"  ✓ {cam.name}")
            print(f"      IP: {cam.ip}")
            if cam.ports:
                print(f"      Ports: {cam.ports}")
    else:
        print("  (none found)")

    # Summary
    total = len(serial_robots) + len(cameras)
    print(f"\nFound {total} device(s)")

    if json_output:
        result = {
            "serial": [
                {
                    "port": r.port,
                    "type": r.robot_type,
                    "name": r.name,
                }
                for r in serial_robots
            ],
            "cameras": [
                {
                    "ip": c.ip,
                    "name": c.name,
                    "ports": c.ports,
                }
                for c in cameras
            ],
        }
        print("\n" + json.dumps(result, indent=2))


def robot_ble_command(
    action: str = "discover",
    timeout: float = 10.0,
    address: Optional[str] = None,
    name_filter: Optional[str] = None,
    profile_name: Optional[str] = None,
    json_output: bool = False,
    # Capture/analyze arguments
    platform: str = "auto",
    output: str = "capture.pklg",
    capture_file: Optional[str] = None,
    generate_code: bool = False,
):
    """
    Bluetooth Low Energy robot discovery, connection, and protocol analysis.

    ate robot ble discover
    ate robot ble discover --timeout 15 --filter MechDog
    ate robot ble connect AA:BB:CC:DD:EE:FF --profile my_mechdog
    ate robot ble capture --platform ios -o capture.pklg
    ate robot ble analyze capture.pklg --generate
    ate robot ble inspect mechdog_00
    """
    if action == "discover":
        print("Scanning for BLE robots...")
        print(f"Timeout: {timeout}s")
        if name_filter:
            print(f"Filter: {name_filter}")
        print()

        try:
            from ..drivers.ble_transport import BLETransport, discover_ble_robots as ble_discover

            # Use name filter if provided
            if name_filter:
                devices = BLETransport.discover_sync(timeout=timeout, name_filter=name_filter)
            else:
                devices = ble_discover(timeout=timeout)

            if not devices:
                print("No BLE devices found.")
                print()
                print("Tips:")
                print("  - Ensure Bluetooth is enabled on your computer")
                print("  - Make sure the robot is powered on")
                print("  - Some robots need to be in pairing mode")
                print("  - Try: ate robot ble discover --timeout 15")
                return

            print(f"Found {len(devices)} device(s):\n")
            for i, device in enumerate(devices, 1):
                print(f"  [{i}] {device.name}")
                print(f"      Address: {device.address}")
                print(f"      RSSI: {device.rssi} dBm")
                print()

            if json_output:
                result = [{
                    "name": d.name,
                    "address": d.address,
                    "rssi": d.rssi,
                } for d in devices]
                print(json.dumps(result, indent=2))

            print("To connect:")
            print(f"  ate robot ble connect <address> --profile <name>")
            print()
            print("Or configure a profile for BLE:")
            print("  ate robot profiles create my_ble_robot")
            print("  # Edit ~/.ate/robots/my_ble_robot.json and add:")
            print('  # "use_ble": true, "ble_address": "<address>"')

        except ImportError:
            print("BLE support requires the 'bleak' library.")
            print("Install with: pip install bleak")
            sys.exit(1)
        except Exception as e:
            print(f"BLE scan failed: {e}")
            sys.exit(1)

    elif action == "connect":
        if not address:
            print("Usage: ate robot ble connect <address>")
            print()
            print("First discover BLE devices:")
            print("  ate robot ble discover")
            sys.exit(1)

        print(f"Connecting to BLE device: {address}")

        try:
            from ..drivers.ble_transport import BLETransport

            transport = BLETransport(address=address, timeout=10.0)

            print("Connecting...")
            if transport.connect():
                print("Connected!")
                print()

                # Try to identify robot
                print("Probing device...")
                transport.write(b'\x03')  # Ctrl+C
                import time
                time.sleep(0.2)
                transport.write(b'\x02')  # Ctrl+B
                time.sleep(0.5)

                transport.write(b'import sys; print(sys.implementation)\r\n')
                time.sleep(0.5)
                response = transport.read(1000).decode('utf-8', errors='ignore')

                if 'micropython' in response.lower():
                    print("Device: MicroPython device")

                    # Check for MechDog
                    transport.write(b'from HW_MechDog import MechDog\r\n')
                    time.sleep(0.3)
                    response2 = transport.read(500).decode('utf-8', errors='ignore')

                    if 'Error' not in response2 and 'Traceback' not in response2:
                        print("Robot: HiWonder MechDog")
                    else:
                        print("Robot: Unknown MicroPython robot")
                else:
                    print("Device: Unknown type")
                    print(f"Response: {response[:200]}")

                transport.disconnect()

                if profile_name:
                    # Update profile with BLE settings
                    profile = load_profile(profile_name)
                    if profile:
                        profile.use_ble = True
                        profile.ble_address = address
                        if save_profile(profile):
                            print()
                            print(f"Updated profile '{profile_name}' for BLE connection.")
                    else:
                        print(f"Profile not found: {profile_name}")

                print()
                print("To use this device, configure a profile:")
                print("  ate robot profiles create my_ble_robot")
                print("  # Then edit to add BLE settings")

            else:
                print("Connection failed.")
                print("Make sure the device is powered on and in range.")

        except ImportError:
            print("BLE support requires the 'bleak' library.")
            print("Install with: pip install bleak")
            sys.exit(1)
        except Exception as e:
            print(f"BLE connection failed: {e}")
            sys.exit(1)

    elif action == "info":
        print("BLE Robot Support")
        print("=" * 40)
        print()
        print("Supported robots with BLE:")
        for robot in KNOWN_ROBOTS.values():
            from .registry import ConnectionType
            if ConnectionType.BLUETOOTH in robot.connection_types:
                print(f"  - {robot.name} ({robot.manufacturer})")
                if robot.default_ports.get("ble_service_uuid"):
                    print(f"    Service: {robot.default_ports['ble_service_uuid']}")
        print()
        print("BLE UUIDs (ESP32/HM-10 compatible):")
        print("  Service: 0000ffe0-0000-1000-8000-00805f9b34fb")
        print("  Write:   0000ffe1-0000-1000-8000-00805f9b34fb")
        print("  Notify:  0000ffe2-0000-1000-8000-00805f9b34fb")
        print()
        print("Commands:")
        print("  ate robot ble discover    - Find BLE devices")
        print("  ate robot ble connect     - Test connection to device")
        print("  ate robot ble inspect     - Show device characteristics")
        print("  ate robot ble capture     - Capture phone app traffic")
        print("  ate robot ble analyze     - Analyze capture file")
        print("  ate robot ble info        - Show this information")

    elif action == "capture":
        # BLE traffic capture from phone app
        try:
            from .ble_capture import (
                capture_ios_interactive,
                capture_android_interactive,
                check_ios_device,
                check_android_device,
            )

            if platform == "auto":
                # Auto-detect platform
                ios_ok, _ = check_ios_device()
                android_ok, _ = check_android_device()

                if ios_ok:
                    platform = "ios"
                elif android_ok:
                    platform = "android"
                else:
                    print("No mobile device detected.")
                    print()
                    print("Connect your iPhone or Android phone via USB.")
                    print()
                    print("For iOS: Connect via Lightning/USB-C cable")
                    print("For Android: Enable USB debugging and connect via USB")
                    sys.exit(1)

            if platform == "ios":
                success = capture_ios_interactive(output)
            else:
                success = capture_android_interactive(output)

            if success:
                print()
                print(f"Next step: Analyze the capture with:")
                print(f"  ate robot ble analyze {output}")

        except ImportError as e:
            print(f"BLE capture requires additional dependencies: {e}")
            sys.exit(1)

    elif action == "analyze":
        # Analyze BLE capture file
        if not capture_file:
            print("Usage: ate robot ble analyze <capture_file>")
            print()
            print("First capture traffic:")
            print("  ate robot ble capture -o capture.pklg")
            sys.exit(1)

        try:
            from .ble_capture import analyze_capture

            analysis = analyze_capture(capture_file)

            if analysis:
                print(analysis.summary())

                if generate_code or output != "capture.pklg":
                    code = analysis.generate_python_code()

                    # If output looks like a .py file, save there
                    if output.endswith(".py"):
                        with open(output, "w") as f:
                            f.write(code)
                        print(f"\nGenerated code saved to: {output}")
                    elif generate_code:
                        print("\n" + "=" * 60)
                        print("GENERATED PYTHON CODE")
                        print("=" * 60)
                        print(code)

        except ImportError as e:
            print(f"BLE analysis requires tshark: {e}")
            print("Install with: brew install wireshark")
            sys.exit(1)

    elif action == "inspect":
        # Inspect BLE device characteristics
        if not address:
            print("Usage: ate robot ble inspect <device_name_or_address>")
            print()
            print("First discover devices:")
            print("  ate robot ble discover")
            sys.exit(1)

        try:
            from .ble_capture import inspect_ble_device

            if not inspect_ble_device(address):
                sys.exit(1)

        except ImportError as e:
            print(f"BLE inspection requires bleak: {e}")
            print("Install with: pip install bleak")
            sys.exit(1)

    elif action == "pickup":
        # Pure-BLE ball pickup using action groups and locomotion
        if not address:
            # Try to find MechDog automatically
            print("Scanning for MechDog...")
            try:
                import asyncio
                from bleak import BleakScanner

                async def find_mechdog():
                    devices = await BleakScanner.discover(timeout=5.0)
                    for d in devices:
                        if "mechdog" in (d.name or "").lower():
                            return d.address
                    return None

                address = asyncio.run(find_mechdog())

                if not address:
                    print("MechDog not found! Make sure it's powered on.")
                    print("Or specify address: ate robot ble pickup --address AA:BB:CC:DD")
                    sys.exit(1)

                print(f"Found MechDog: {address}")

            except ImportError:
                print("BLE requires bleak: pip install bleak")
                sys.exit(1)

        try:
            from .ble_capture import ble_pickup_sequence

            print()
            print("=" * 60)
            print("BLE BALL PICKUP SEQUENCE")
            print("=" * 60)
            print()
            print("This uses BLE-only commands:")
            print("- Action groups (CMD|2|1|X|$) for arm control")
            print("- Locomotion (CMD|3|X|$) for walking")
            print()
            print("NOTE: If arm doesn't respond, connect USB serial for")
            print("direct servo control: ate robot test mechdog --port <port>")
            print()

            import asyncio
            success = asyncio.run(ble_pickup_sequence(address))

            if success:
                print("\n✓ Pickup sequence complete!")
            else:
                print("\n✗ Pickup failed. Try USB serial for arm control.")
                sys.exit(1)

        except ImportError as e:
            print(f"BLE pickup requires bleak: {e}")
            print("Install with: pip install bleak")
            sys.exit(1)

    elif action == "test-locomotion":
        # Quick test of BLE locomotion commands
        if not address:
            print("Usage: ate robot ble test-locomotion --address <address>")
            sys.exit(1)

        try:
            import asyncio
            from bleak import BleakClient, BleakScanner

            async def test_locomotion():
                print(f"Connecting to {address}...")

                # Find device
                devices = await BleakScanner.discover(timeout=5.0)
                device = None
                for d in devices:
                    if address.lower() in (d.address or "").lower() or address.lower() in (d.name or "").lower():
                        device = d
                        break

                if not device:
                    print("Device not found!")
                    return False

                async with BleakClient(device) as client:
                    print(f"Connected: {client.is_connected}")

                    FFE1 = "0000ffe1-0000-1000-8000-00805f9b34fb"
                    FFE2 = "0000ffe2-0000-1000-8000-00805f9b34fb"

                    responses = []
                    def handler(s, d):
                        try:
                            responses.append(d.decode('ascii'))
                        except:
                            pass

                    await client.start_notify(FFE2, handler)

                    # Battery
                    print("\nBattery check...")
                    await client.write_gatt_char(FFE1, b"CMD|6|$")
                    await asyncio.sleep(1.0)
                    for r in responses:
                        if "CMD|6|" in r:
                            parts = r.split("|")
                            if len(parts) >= 3:
                                try:
                                    mv = int(parts[2])
                                    print(f"  Battery: {mv/1000:.2f}V")
                                except:
                                    pass

                    # Forward
                    print("\nWalking forward (1s)...")
                    await client.write_gatt_char(FFE1, b"CMD|3|3|$")
                    await asyncio.sleep(1.0)
                    await client.write_gatt_char(FFE1, b"CMD|3|0|$")

                    # Backward
                    print("Walking backward (1s)...")
                    await client.write_gatt_char(FFE1, b"CMD|3|7|$")
                    await asyncio.sleep(1.0)
                    await client.write_gatt_char(FFE1, b"CMD|3|0|$")

                    await client.stop_notify(FFE2)
                    print("\n✓ Locomotion test complete!")
                    return True

            asyncio.run(test_locomotion())

        except ImportError:
            print("BLE requires bleak: pip install bleak")
            sys.exit(1)
        except Exception as e:
            print(f"Test failed: {e}")
            sys.exit(1)

    else:
        print(f"Unknown action: {action}")
        print("Available actions: discover, connect, inspect, capture, analyze, pickup, test-locomotion, info")
        sys.exit(1)


def robot_list_command(archetype: Optional[str] = None):
    """
    List known robot types.

    ate robot list
    ate robot list --archetype quadruped
    """
    robots = RobotRegistry.list_all()

    if archetype:
        robots = [r for r in robots if r.archetype == archetype]

    print("Known Robot Types:\n")
    print(f"{'ID':<25} {'Name':<15} {'Manufacturer':<15} {'Archetype':<12}")
    print("-" * 70)

    for robot in robots:
        print(f"{robot.id:<25} {robot.name:<15} {robot.manufacturer:<15} {robot.archetype:<12}")

    print(f"\n{len(robots)} robot type(s)")
    print("\nFor detailed info: ate robot info <robot_type>")


def robot_info_command(robot_type: Optional[str] = None, profile_name: Optional[str] = None):
    """
    Show robot type or profile information.

    ate robot info hiwonder_mechdog
    ate robot info --profile my_mechdog
    """
    if profile_name:
        # Show profile info
        profile = load_profile(profile_name)
        if not profile:
            print(f"Profile not found: {profile_name}")
            sys.exit(1)

        print(f"Profile: {profile.name}")
        print(f"Robot Type: {profile.robot_type}")
        print(f"Serial Port: {profile.serial_port or '(not set)'}")
        print(f"Camera IP: {profile.camera_ip or '(not set)'}")
        print(f"Has Camera: {profile.has_camera}")
        print(f"Has Arm: {profile.has_arm}")

        # Try to load and show capabilities
        if profile.robot_type in KNOWN_ROBOTS:
            rtype = KNOWN_ROBOTS[profile.robot_type]
            print(f"\nCapabilities: {', '.join(rtype.capabilities)}")
            if rtype.optional_capabilities:
                print(f"Optional: {', '.join(rtype.optional_capabilities)}")

        return

    if not robot_type:
        print("Usage: ate robot info <robot_type>")
        print("   or: ate robot info --profile <profile_name>")
        sys.exit(1)

    rtype = KNOWN_ROBOTS.get(robot_type)
    if not rtype:
        print(f"Unknown robot type: {robot_type}")
        print("\nAvailable types:")
        for r in KNOWN_ROBOTS.values():
            print(f"  {r.id}")
        sys.exit(1)

    print(f"\n{rtype.name}")
    print("=" * 40)
    print(f"ID: {rtype.id}")
    print(f"Manufacturer: {rtype.manufacturer}")
    print(f"Archetype: {rtype.archetype}")
    print(f"\nDescription: {rtype.description}")

    print(f"\nConnection Types: {', '.join(c.name for c in rtype.connection_types)}")
    if rtype.serial_patterns:
        print(f"Serial Patterns: {', '.join(rtype.serial_patterns)}")
    if rtype.default_ports:
        print(f"Default Ports: {rtype.default_ports}")

    print(f"\nCapabilities:")
    for cap in sorted(rtype.capabilities):
        print(f"  ✓ {cap}")

    if rtype.optional_capabilities:
        print(f"\nOptional Capabilities:")
        for cap in sorted(rtype.optional_capabilities):
            print(f"  ○ {cap}")

    print(f"\nDriver: {rtype.driver_module}.{rtype.driver_class}")

    if rtype.setup_url:
        print(f"\nDocumentation: {rtype.setup_url}")


def robot_setup_command(
    port: Optional[str] = None,
    camera_ip: Optional[str] = None,
    robot_type: str = "hiwonder_mechdog",
    name: Optional[str] = None,
    non_interactive: bool = False,
):
    """
    Interactive setup wizard.

    ate robot setup
    ate robot setup --port /dev/cu.usbserial-10 --camera-ip 192.168.1.100
    """
    print("Robot Setup Wizard")
    print("=" * 40)
    print()

    # Step 1: Discover devices if not specified
    if not port:
        print("Scanning for robots...")
        serial_robots = discover_serial_robots()

        if serial_robots:
            print("\nFound serial devices:")
            for i, robot in enumerate(serial_robots):
                type_hint = f" [{robot.robot_type}]" if robot.robot_type else ""
                print(f"  [{i+1}] {robot.port}{type_hint}")

            if not non_interactive:
                try:
                    choice = input("\nSelect device number (or press Enter to skip): ")
                    if choice.strip():
                        idx = int(choice) - 1
                        if 0 <= idx < len(serial_robots):
                            port = serial_robots[idx].port
                            if serial_robots[idx].robot_type:
                                robot_type = serial_robots[idx].robot_type
                except (ValueError, KeyboardInterrupt):
                    pass
            elif serial_robots:
                # Auto-select first identified robot in non-interactive mode
                for robot in serial_robots:
                    if robot.robot_type:
                        port = robot.port
                        robot_type = robot.robot_type
                        break
        else:
            print("No serial devices found.")

    # Step 2: Discover cameras if not specified
    if not camera_ip:
        print("\nScanning for network cameras (this may take a few seconds)...")
        cameras = discover_network_cameras(timeout=1.5)

        if cameras:
            print("\nFound network cameras:")
            for i, cam in enumerate(cameras):
                print(f"  [{i+1}] {cam.ip}")

            if not non_interactive:
                try:
                    choice = input("\nSelect camera number (or press Enter to skip): ")
                    if choice.strip():
                        idx = int(choice) - 1
                        if 0 <= idx < len(cameras):
                            camera_ip = cameras[idx].ip
                except (ValueError, KeyboardInterrupt):
                    pass
            elif cameras:
                camera_ip = cameras[0].ip
        else:
            print("No network cameras found.")

    # Step 3: Get name
    if not name:
        if non_interactive:
            name = f"robot_{robot_type.split('_')[-1]}"
        else:
            default_name = f"my_{robot_type.split('_')[-1]}"
            name = input(f"\nProfile name [{default_name}]: ").strip() or default_name

    # Step 4: Create profile
    profile = create_profile_from_discovery(
        name=name,
        serial_port=port,
        camera_ip=camera_ip,
        robot_type=robot_type,
    )

    # Show summary
    print("\n" + "=" * 40)
    print("Configuration Summary")
    print("=" * 40)
    print(f"Name: {profile.name}")
    print(f"Robot Type: {profile.robot_type}")
    print(f"Serial Port: {profile.serial_port or '(not set)'}")
    print(f"Camera IP: {profile.camera_ip or '(not set)'}")
    print(f"Has Camera: {profile.has_camera}")

    # Step 5: Save profile
    if not non_interactive:
        confirm = input("\nSave this profile? [Y/n]: ")
        if confirm.lower() == 'n':
            print("Profile not saved.")
            return

    if save_profile(profile):
        print(f"\nProfile saved to ~/.ate/robots/{profile.name}.json")
        print(f"\nTo use this robot:")
        print(f"  ate record demo --profile {profile.name}")
        print(f"\nTo view capabilities:")
        print(f"  ate robot test {profile.name}")
    else:
        print("Failed to save profile.")
        sys.exit(1)


def robot_test_command(profile_name: str, capability: Optional[str] = None, verbose: bool = False):
    """
    Test robot capabilities.

    ate robot test my_mechdog
    ate robot test my_mechdog --capability camera
    """
    profile = load_profile(profile_name)
    if not profile:
        print(f"Profile not found: {profile_name}")
        sys.exit(1)

    print(f"Testing robot: {profile.name}")
    print(f"Type: {profile.robot_type}")
    print()

    # Create robot instance
    manager = RobotManager()
    managed = manager.load(profile_name)

    if not managed:
        print("Failed to load robot configuration")
        sys.exit(1)

    # Connect
    print("Connecting...")
    if not manager.connect(profile_name):
        print("Connection failed")
        sys.exit(1)

    print("Connected!\n")

    try:
        robot = manager.get(profile_name)

        if capability:
            # Test specific capability
            result = test_capability(robot, capability)
            print(f"Testing {capability}...")
            for test in result.get("tests", []):
                status = "✓" if test["status"] == "passed" else "✗"
                print(f"  {status} {test['name']}: {test.get('message', test.get('error', ''))}")
            print(f"\nOverall: {result['status'].upper()}")
        else:
            # Show all capabilities
            caps = get_capabilities(robot)
            print("Available Capabilities:")
            print("-" * 40)
            for name, info in caps.items():
                print(f"  ✓ {name} ({len(info.methods)} methods)")

            if verbose:
                print("\nMethods:")
                print(format_methods(get_methods(robot)))

            # Quick tests
            print("\nRunning capability tests...")
            for cap_name in caps.keys():
                result = test_capability(robot, cap_name)
                status = "✓" if result["status"] == "passed" else "✗"
                print(f"  {status} {cap_name}: {result['status']}")

    finally:
        manager.disconnect(profile_name)
        print("\nDisconnected.")


def robot_approach_command(
    profile_name: str,
    duration: float = 30.0,
    target_distance: float = 0.15,
    speed: float = 0.3,
    detect_colors: Optional[list] = None,
    dry_run: bool = False,
):
    """
    Approach detected targets.

    ate robot approach my_mechdog
    ate robot approach my_mechdog --duration 60 --target-distance 0.2
    """
    import time
    from ..behaviors import ApproachTarget, ApproachConfig, BehaviorStatus
    from ..behaviors.tree import Blackboard
    from ..detection.trash_detector import TrashDetector
    from ..interfaces import VisualDistanceEstimator

    profile = load_profile(profile_name)
    if not profile:
        print(f"Profile not found: {profile_name}")
        sys.exit(1)

    print(f"Approach Mode: {profile.name}")
    print(f"Target distance: {target_distance}m")
    print(f"Speed: {speed}")
    print()

    # Create robot instance
    manager = RobotManager()
    managed = manager.load(profile_name)

    if not managed:
        print("Failed to load robot configuration")
        sys.exit(1)

    # Connect
    print("Connecting...")
    if not manager.connect(profile_name):
        print("Connection failed")
        sys.exit(1)

    print("Connected!\n")

    try:
        robot = manager.get(profile_name)
        info = robot.get_info()
        print(f"Capabilities: {[c.name for c in info.capabilities]}")

        # Check for required capabilities
        has_camera = hasattr(robot, 'get_image') and hasattr(robot, 'has_camera') and robot.has_camera()
        has_locomotion = hasattr(robot, 'walk') or hasattr(robot, 'drive')

        if not has_camera:
            print("Error: Robot does not have camera capability")
            sys.exit(1)

        if not has_locomotion:
            print("Error: Robot does not have locomotion capability")
            sys.exit(1)

        # Initialize detector
        detector = TrashDetector()
        if detect_colors:
            print(f"Detecting colors: {detect_colors}")

        # Initialize visual distance estimator
        res = robot.get_resolution()
        visual_estimator = VisualDistanceEstimator(
            image_width=res[0] or 640,
            image_height=res[1] or 480,
        )

        # Configure approach behavior
        config = ApproachConfig(
            target_distance=target_distance,
            center_tolerance=0.15,
            approach_speed=speed,
            slow_distance=target_distance * 2,
            use_visual_distance=True,
        )

        # Stand ready
        if hasattr(robot, 'stand'):
            robot.stand()
            time.sleep(0.5)

        print("Scanning for targets...")
        start_time = time.time()

        # Scanning positions
        scan_positions = [
            ("center", 0, 0),
            ("left", 0, 0.4),
            ("right", 0, -0.4),
        ]

        blackboard = Blackboard()
        target_found = False

        while time.time() - start_time < duration and not target_found:
            for name, pitch, yaw in scan_positions:
                if time.time() - start_time >= duration:
                    break

                print(f"\nLooking {name}...")
                if hasattr(robot, 'set_body_orientation'):
                    robot.set_body_orientation(pitch=pitch, yaw=yaw)
                time.sleep(0.5)

                # Get image and detect
                image = robot.get_image()
                if not image.data:
                    continue

                detections = detector.detect(image)
                if not detections:
                    print(f"  No targets")
                    continue

                # Found target!
                target = detections[0]
                print(f"  Target: {target.class_name} at ({target.bbox.x}, {target.bbox.y})")

                # Estimate distance
                dist_reading = visual_estimator.estimate_from_detection(
                    bbox_width=int(target.bbox.width),
                    object_type=target.class_name,
                )
                print(f"  Estimated distance: {dist_reading.distance:.2f}m")

                # Store in blackboard
                blackboard.set("target_detection", target)
                blackboard.set("detections", detections)
                target_found = True
                break

        if not target_found:
            print("\nNo targets found during scan period.")
            if hasattr(robot, 'set_body_orientation'):
                robot.set_body_orientation(0, 0, 0)
            return

        # Reset pose for approach
        if hasattr(robot, 'set_body_orientation'):
            robot.set_body_orientation(0, 0, 0)
            time.sleep(0.3)

        if dry_run:
            print("\n[DRY RUN] Would approach target but stopping here.")
            return

        # Create approach behavior
        distance_sensor = robot if hasattr(robot, 'get_distance') else None

        approach = ApproachTarget(
            locomotion=robot,
            camera=robot,
            distance_sensor=distance_sensor,
            config=config,
        )
        approach.blackboard = blackboard

        print("\n--- Starting Approach ---")
        print("Press Ctrl+C to stop\n")

        try:
            approach_start = time.time()
            while time.time() - approach_start < duration:
                # Get fresh detection
                image = robot.get_image()
                if image.data:
                    detections = detector.detect(image)
                    if detections:
                        blackboard.set("target_detection", detections[0])
                        blackboard.set("detections", detections)

                # Tick behavior
                status = approach.tick()

                state = blackboard.get("approach_state")
                distance = blackboard.get("target_distance")
                print(f"  State: {state}, Distance: {distance:.2f}m" if distance else f"  State: {state}")

                if status == BehaviorStatus.SUCCESS:
                    print("\n=== TARGET REACHED ===")
                    break
                elif status == BehaviorStatus.FAILURE:
                    print("\n=== APPROACH FAILED ===")
                    break

                time.sleep(0.2)

        except KeyboardInterrupt:
            print("\n\nStopping...")

        # Stop movement
        if hasattr(robot, 'stop'):
            robot.stop()

    finally:
        manager.disconnect(profile_name)
        print("\nDisconnected.")


def robot_profiles_command(action: str, name: Optional[str] = None, template: Optional[str] = None):
    """
    Manage saved profiles.

    ate robot profiles list
    ate robot profiles show my_mechdog
    ate robot profiles delete my_mechdog
    ate robot profiles create my_dog --template mechdog_camera
    """
    if action == "list":
        profiles = list_profiles()

        if not profiles:
            print("No saved profiles.")
            print("\nCreate one with: ate robot setup")
            return

        print("Saved Profiles:\n")
        print(f"{'Name':<20} {'Type':<25} {'Port':<25}")
        print("-" * 70)

        for p in profiles:
            port = p.serial_port or "(no port)"
            print(f"{p.name:<20} {p.robot_type:<25} {port:<25}")

    elif action == "show":
        if not name:
            print("Usage: ate robot profiles show <name>")
            sys.exit(1)
        robot_info_command(profile_name=name)

    elif action == "delete":
        if not name:
            print("Usage: ate robot profiles delete <name>")
            sys.exit(1)

        if delete_profile(name):
            print(f"Deleted profile: {name}")
        else:
            print(f"Profile not found: {name}")
            sys.exit(1)

    elif action == "create":
        if not name:
            print("Usage: ate robot profiles create <name> [--template <template>]")
            sys.exit(1)

        if template:
            profile = get_template(template)
            if not profile:
                print(f"Template not found: {template}")
                print(f"Available templates: {', '.join(list_templates())}")
                sys.exit(1)
            profile.name = name
        else:
            profile = RobotProfile(name=name, robot_type="hiwonder_mechdog")

        if save_profile(profile):
            print(f"Created profile: {name}")
            print(f"Edit at: ~/.ate/robots/{name}.yaml")
        else:
            print("Failed to create profile")
            sys.exit(1)

    elif action == "templates":
        print("Available Templates:\n")
        for tname in list_templates():
            tmpl = get_template(tname)
            if tmpl:
                print(f"  {tname}")
                print(f"    {tmpl.description}")
                print()

    else:
        print(f"Unknown action: {action}")
        print("Available actions: list, show, delete, create, templates")
        sys.exit(1)


def robot_calibrate_command(
    action: str,
    port: Optional[str] = None,
    camera_url: Optional[str] = None,
    name: str = "robot",
    robot_type: str = "unknown",
    servo_id: Optional[int] = None,
    pose_name: Optional[str] = None,
):
    """
    Visual calibration for robot servos and poses.

    ate robot calibrate start --port /dev/cu.usbserial-10 --name my_mechdog
    ate robot calibrate gripper --port /dev/cu.usbserial-10 --servo 11
    ate robot calibrate list
    ate robot calibrate poses my_mechdog
    """
    if action == "start":
        # Full interactive calibration
        if not port:
            # Try to discover
            serial_robots = discover_serial_robots()
            if serial_robots:
                port = serial_robots[0].port
                print(f"Auto-detected: {port}")
            else:
                print("No serial port specified and none discovered.")
                print("Usage: ate robot calibrate start --port /dev/cu.usbserial-10")
                sys.exit(1)

        calibrator = VisualCalibrator(
            serial_port=port,
            robot_model=robot_type,
            robot_name=name,
        )

        if camera_url:
            calibrator.set_camera(camera_url)

        try:
            calibration = calibrator.run_interactive()
            save_calibration(calibration)
            print(f"\nCalibration saved as: {name}")
        except KeyboardInterrupt:
            print("\nCalibration cancelled.")
        except Exception as e:
            print(f"\nCalibration failed: {e}")
            sys.exit(1)

    elif action == "gripper":
        # Quick gripper-only calibration
        if not port:
            serial_robots = discover_serial_robots()
            if serial_robots:
                port = serial_robots[0].port
            else:
                print("No serial port found. Use --port to specify.")
                sys.exit(1)

        sid = servo_id or 11  # Default gripper servo
        print(f"Quick gripper calibration on servo {sid}...")

        try:
            gripper = quick_gripper_calibration(port, gripper_servo_id=sid)
            print(f"\nGripper calibrated:")
            print(f"  Open: {gripper.positions.get('open', 'N/A')}")
            print(f"  Closed: {gripper.positions.get('closed', 'N/A')}")
            print(f"  Range: {gripper.min_value} - {gripper.max_value}")
        except Exception as e:
            print(f"Calibration failed: {e}")
            sys.exit(1)

    elif action == "list":
        # List saved calibrations
        cals = list_calibrations()
        if not cals:
            print("No calibrations saved.")
            print("\nRun: ate robot calibrate start --port <port> --name <name>")
            return

        print("Saved Calibrations:\n")
        for cal_name in cals:
            cal = load_calibration(cal_name)
            if cal:
                servo_count = len(cal.servos)
                pose_count = len(cal.poses)
                print(f"  {cal_name}")
                print(f"    Model: {cal.robot_model}, Servos: {servo_count}, Poses: {pose_count}")
            else:
                print(f"  {cal_name} (error loading)")

    elif action == "poses":
        # Show poses for a calibration
        if not name or name == "robot":
            print("Usage: ate robot calibrate poses <calibration_name>")
            sys.exit(1)

        cal = load_calibration(name)
        if not cal:
            print(f"Calibration not found: {name}")
            sys.exit(1)

        if not cal.poses:
            print(f"No poses saved for {name}")
            return

        print(f"Poses for {name}:\n")
        for pose_name, pose in cal.poses.items():
            print(f"  {pose_name}")
            if pose.description:
                print(f"    {pose.description}")
            print(f"    Servos: {len(pose.servo_positions)}, Time: {pose.transition_time_ms}ms")

    elif action == "record":
        # Record a new pose
        if not name or name == "robot":
            print("Usage: ate robot calibrate record <calibration_name> --pose <pose_name>")
            sys.exit(1)

        if not pose_name:
            print("Usage: ate robot calibrate record <name> --pose <pose_name>")
            sys.exit(1)

        cal = load_calibration(name)
        if not cal:
            print(f"Calibration not found: {name}")
            sys.exit(1)

        if not cal.serial_port:
            print("Calibration has no serial port configured.")
            sys.exit(1)

        calibrator = VisualCalibrator(
            serial_port=cal.serial_port,
            robot_model=cal.robot_model,
            robot_name=cal.robot_name,
        )
        calibrator.calibration = cal

        if cal.camera_url:
            calibrator.set_camera(cal.camera_url)

        if not calibrator.connect():
            print("Failed to connect to robot")
            sys.exit(1)

        try:
            calibrator.send_command("from HW_MechDog import MechDog; dog = MechDog()", wait=1.5)
            desc = input("Pose description (optional): ").strip()
            pose = calibrator.record_pose(pose_name, desc)
            save_calibration(calibrator.calibration)
            print(f"Recorded pose '{pose_name}' with {len(pose.servo_positions)} servos")
        finally:
            calibrator.disconnect()

    elif action == "apply":
        # Apply a saved pose
        if not name or name == "robot":
            print("Usage: ate robot calibrate apply <calibration_name> --pose <pose_name>")
            sys.exit(1)

        if not pose_name:
            print("Usage: ate robot calibrate apply <name> --pose <pose_name>")
            sys.exit(1)

        cal = load_calibration(name)
        if not cal:
            print(f"Calibration not found: {name}")
            sys.exit(1)

        pose = cal.get_pose(pose_name)
        if not pose:
            print(f"Pose not found: {pose_name}")
            print(f"Available poses: {', '.join(cal.poses.keys())}")
            sys.exit(1)

        if not cal.serial_port:
            print("Calibration has no serial port configured.")
            sys.exit(1)

        calibrator = VisualCalibrator(
            serial_port=cal.serial_port,
            robot_model=cal.robot_model,
            robot_name=cal.robot_name,
        )
        calibrator.calibration = cal

        if not calibrator.connect():
            print("Failed to connect to robot")
            sys.exit(1)

        try:
            calibrator.send_command("from HW_MechDog import MechDog; dog = MechDog()", wait=1.5)
            print(f"Applying pose: {pose_name}")
            success = calibrator.apply_pose(pose)
            if success:
                print("Pose applied successfully")
            else:
                print("Some servos failed to move")
        finally:
            calibrator.disconnect()

    elif action == "direction":
        # Direction calibration via Twitch Test
        from .direction_calibration import run_direction_calibration
        from .calibration_state import CalibrationState

        if not port:
            # Try to discover
            serial_robots = discover_serial_robots()
            if serial_robots:
                port = serial_robots[0].port
                print(f"Auto-detected: {port}")
            else:
                print("No serial port specified and none discovered.")
                print("Usage: ate robot calibrate direction --port /dev/cu.usbserial-10 --name my_robot")
                sys.exit(1)

        # Run direction calibration
        mappings = run_direction_calibration(
            serial_port=port,
            robot_name=name,
            arm_servos=[8, 9, 10, 11],  # MechDog arm servos
        )

        if mappings:
            print("\nDirection calibration complete!")
            print("You can now run behaviors with correct directions.")
        else:
            print("\nDirection calibration failed.")
            print("Ensure ball and arm markers are visible to webcam.")
            sys.exit(1)

    elif action == "status":
        # Show calibration status
        from .calibration_state import CalibrationState

        if not name or name == "robot":
            # List all calibration states
            states = CalibrationState.list_all()
            if not states:
                print("No calibration states found.")
                print("\nStart with: ate robot calibrate start --name <robot_name>")
                return

            print("Calibration States:\n")
            for state_name in states:
                state = CalibrationState.load(state_name)
                current = state.get_current_stage()
                print(f"  {state_name}: {current}")

            print("\nFor details: ate robot calibrate status <name>")
        else:
            # Show specific robot's status
            state = CalibrationState.load(name)
            state.print_status()

    elif action == "reset":
        # Reset calibration state
        from .calibration_state import CalibrationState

        if not name or name == "robot":
            print("Usage: ate robot calibrate reset <name>")
            sys.exit(1)

        state = CalibrationState.load(name)
        confirm = input(f"Reset all calibration for '{name}'? [y/N]: ")
        if confirm.lower() == 'y':
            state.reset()
            print(f"Calibration reset for: {name}")
        else:
            print("Cancelled.")

    else:
        print(f"Unknown action: {action}")
        print("Available actions: start, gripper, direction, status, list, poses, record, apply, reset")
        sys.exit(1)


def robot_label_command(
    port: Optional[str] = None,
    name: str = "robot",
    robot_type: str = "unknown",
    webcam_id: int = 0,
    camera_url: Optional[str] = None,
):
    """
    Interactive visual labeling session.

    ate robot label --port /dev/cu.usbserial-10 --name my_mechdog
    ate robot label --port /dev/cu.usbserial-10 --camera http://192.168.50.98:80/capture
    """
    if not port:
        # Try to discover
        serial_robots = discover_serial_robots()
        if serial_robots:
            port = serial_robots[0].port
            print(f"Auto-detected: {port}")
        else:
            print("No serial port specified and none discovered.")
            print("Usage: ate robot label --port /dev/cu.usbserial-10")
            sys.exit(1)

    visual_label_command(
        port=port,
        name=name,
        robot_type=robot_type,
        webcam_id=webcam_id,
        camera_url=camera_url,
    )


def robot_skills_command(
    action: str,
    name: Optional[str] = None,
    skill_name: Optional[str] = None,
):
    """
    Manage generated robot skills.

    ate robot skills list
    ate robot skills show my_mechdog
    ate robot skills export my_mechdog pickup
    """
    if action == "list":
        libraries = list_skill_libraries()
        if not libraries:
            print("No skill libraries saved.")
            print("\nRun: ate robot label --port <port> --name <name>")
            return

        print("Saved Skill Libraries:\n")
        for lib_name in libraries:
            lib = load_skill_library(lib_name)
            if lib:
                action_count = len(lib.actions)
                print(f"  {lib_name}")
                print(f"    Model: {lib.robot_model}, Actions: {action_count}")
            else:
                print(f"  {lib_name} (error loading)")

    elif action == "show":
        if not name:
            print("Usage: ate robot skills show <library_name>")
            sys.exit(1)

        lib = load_skill_library(name)
        if not lib:
            print(f"Skill library not found: {name}")
            sys.exit(1)

        print(f"\nSkill Library: {lib.robot_name}")
        print(f"Model: {lib.robot_model}")
        print(f"Created: {lib.created_at}")

        if lib.servo_labels:
            print(f"\nLabeled Servos:")
            for sid, label in lib.servo_labels.items():
                print(f"  Servo {sid}: {label}")

        if lib.joint_groups:
            print(f"\nJoint Groups:")
            for group, ids in lib.joint_groups.items():
                print(f"  {group}: {ids}")

        if lib.actions:
            print(f"\nActions:")
            for action_name, act in lib.actions.items():
                print(f"  {action_name}: {len(act.steps)} steps ({act.action_type.value})")
                if act.description:
                    print(f"    {act.description}")

    elif action == "export":
        if not name:
            print("Usage: ate robot skills export <library_name> [skill_name]")
            sys.exit(1)

        lib = load_skill_library(name)
        if not lib:
            print(f"Skill library not found: {name}")
            sys.exit(1)

        # Load calibration for skill generation
        cal = load_calibration(name)
        if not cal:
            print(f"No calibration found for: {name}")
            sys.exit(1)

        labeler = DualCameraLabeler(
            serial_port=cal.serial_port or "",
            robot_name=name,
            robot_model=cal.robot_model,
        )
        labeler.calibrator.calibration = cal
        labeler.library = lib

        from pathlib import Path
        skills_dir = Path.home() / ".ate" / "skills" / name
        skills_dir.mkdir(parents=True, exist_ok=True)

        if skill_name:
            # Export single skill
            act = lib.actions.get(skill_name)
            if not act:
                print(f"Action not found: {skill_name}")
                print(f"Available: {list(lib.actions.keys())}")
                sys.exit(1)

            code = labeler.generate_skill_code(act)
            path = skills_dir / f"{skill_name}.py"
            with open(path, 'w') as f:
                f.write(code)
            print(f"Exported: {path}")
        else:
            # Export all skills
            for act_name, act in lib.actions.items():
                code = labeler.generate_skill_code(act)
                path = skills_dir / f"{act_name}.py"
                with open(path, 'w') as f:
                    f.write(code)
                print(f"Exported: {path}")

    else:
        print(f"Unknown action: {action}")
        print("Available actions: list, show, export")
        sys.exit(1)


def robot_upload_command(
    name: str,
    project_id: Optional[str] = None,
    include_images: bool = True,
):
    """
    Upload skill library to FoodforThought.

    Creates artifacts with proper data lineage:
    raw (images) → processed (calibration) → labeled (poses) → skill (code)

    ate robot upload mechdog
    ate robot upload mechdog --project-id abc123
    ate robot upload mechdog --no-images
    """
    # Check login status
    config_file = Path.home() / ".ate" / "config.json"
    if not config_file.exists():
        print("Not logged in. Run 'ate login' first.")
        sys.exit(1)

    # Load calibration
    cal = load_calibration(name)
    if not cal:
        print(f"No calibration found for: {name}")
        print("\nAvailable calibrations:")
        for cal_name in list_calibrations():
            print(f"  - {cal_name}")
        sys.exit(1)

    # Load skill library
    lib = load_skill_library(name)
    if not lib:
        print(f"No skill library found for: {name}")
        print("Run 'ate robot label' first to create skills.")
        sys.exit(1)

    print(f"Uploading skill library: {name}")
    print(f"  Robot model: {lib.robot_model}")
    print(f"  Actions: {len(lib.actions)}")
    print(f"  Poses: {len(cal.poses)}")
    print(f"  Servos: {len(cal.servos)}")
    if include_images:
        img_dir = Path.home() / ".ate" / "skill_images" / name
        if img_dir.exists():
            img_count = len(list(img_dir.glob("*.jpg")))
            print(f"  Images: {img_count}")
    print()

    try:
        result = upload_skill_library(
            robot_name=name,
            project_id=project_id,
            include_images=include_images,
        )

        print("Upload complete!")
        print(f"  Project ID: {result['project_id']}")
        print(f"  Artifacts created: {len(result['artifacts'])}")
        print()
        print("Artifacts:")
        for art in result['artifacts']:
            print(f"  [{art['stage']}] {art['name']}")

        print()
        print(f"View at: https://www.kindly.fyi/foodforthought/projects/{result['project_id']}")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Upload failed: {e}")
        sys.exit(1)


def robot_map_servos_command(
    port: Optional[str] = None,
    num_servos: int = 13,
    use_camera: bool = False,
    camera_index: int = 0,
    wifi_camera_ip: Optional[str] = None,
    output: Optional[str] = None,
    save_images: bool = False,
    upload: bool = False,
    project_id: Optional[str] = None,
):
    """
    Map all servos and generate primitive skills using LLM-guided exploration.

    ate robot map-servos --port /dev/cu.usbserial-10
    ate robot map-servos --port /dev/cu.usbserial-10 --camera --output ./my_robot
    ate robot map-servos --port /dev/cu.usbserial-10 --wifi-camera 192.168.4.1
    """
    from .servo_mapper import run_servo_mapping

    if not port:
        # Try to discover
        serial_robots = discover_serial_robots()
        if serial_robots:
            port = serial_robots[0].port
            print(f"Auto-detected: {port}")
        else:
            print("No serial port specified and none discovered.")
            print("Usage: ate robot map-servos --port /dev/cu.usbserial-10")
            sys.exit(1)

    output_file = output or f"./servo_mappings_{port.split('/')[-1]}"

    results = run_servo_mapping(
        serial_port=port,
        num_servos=num_servos,
        use_camera=use_camera,
        camera_index=camera_index,
        wifi_camera_ip=wifi_camera_ip,
        use_proxy=True,  # Use metered LLM access
        output_file=output_file,
        save_images=save_images,
    )

    if results.get("python_code"):
        print("\n" + "=" * 60)
        print("GENERATED PYTHON CODE:")
        print("=" * 60)
        print(results["python_code"][:2000])  # First 2000 chars
        if len(results["python_code"]) > 2000:
            print(f"\n... (see {output_file}.py for full code)")

    # Upload to FoodforThought if requested
    if upload:
        from .servo_mapper import upload_servo_mapping
        print("\n" + "=" * 60)
        print("UPLOADING TO FOODFORTHOUGHT")
        print("=" * 60)
        try:
            upload_result = upload_servo_mapping(
                results=results,
                output_file=output_file,
                project_id=project_id,
            )
            print(f"\nUpload complete!")
            print(f"  Project ID: {upload_result['project_id']}")
            print(f"  Artifacts created: {len(upload_result['artifacts'])}")
            for art in upload_result['artifacts']:
                print(f"    [{art['stage']}] {art['name']}")
            print(f"\nView at: https://www.kindly.fyi/foodforthought/projects/{upload_result['project_id']}")
        except Exception as e:
            print(f"Upload failed: {e}")
            print("Servo mapping saved locally. Run 'ate robot upload' to retry.")


def robot_upload_calibration_command(
    calibration_file: str,
    robot_slug: Optional[str] = None,
    robot_name: Optional[str] = None,
    method: str = "llm_vision",
    publish: bool = False,
):
    """
    Upload a calibration to the community registry.

    ate robot upload-calibration ./servo_mappings.json --robot-slug mechdog-mini
    ate robot upload-calibration ./calibration.json --publish
    """
    import json
    import requests
    from .skill_upload import SkillLibraryUploader

    # Load calibration file
    if not os.path.exists(calibration_file):
        print(f"Error: Calibration file not found: {calibration_file}")
        sys.exit(1)

    with open(calibration_file, 'r') as f:
        calibration_data = json.load(f)

    # Get API credentials
    try:
        uploader = SkillLibraryUploader()
    except Exception as e:
        print(f"Error initializing uploader: {e}")
        sys.exit(1)

    base_url = os.environ.get("FOODFORTHOUGHT_API_URL", "https://www.kindly.fyi")

    # Prepare calibration payload
    payload = {
        "name": calibration_data.get("name", f"Calibration from {calibration_file}"),
        "description": calibration_data.get("description", "Community-contributed calibration"),
        "version": calibration_data.get("version", "1.0.0"),
        "method": method,
        "confidence": calibration_data.get("confidence", 0.8),
    }

    # Add robot identification
    if robot_slug:
        payload["robotSlug"] = robot_slug
    elif calibration_data.get("robot_slug"):
        payload["robotSlug"] = calibration_data["robot_slug"]
    elif calibration_data.get("robot_id"):
        payload["robotId"] = calibration_data["robot_id"]
    else:
        print("Error: Must specify --robot-slug or include robot_slug/robot_id in calibration file")
        sys.exit(1)

    # Add kinematic data
    if calibration_data.get("urdf"):
        payload["urdfContent"] = calibration_data["urdf"]
    if calibration_data.get("dh_parameters"):
        payload["dhParameters"] = calibration_data["dh_parameters"]
    if calibration_data.get("joint_mappings") or calibration_data.get("mappings"):
        payload["jointMappings"] = calibration_data.get("joint_mappings") or calibration_data.get("mappings")
    if calibration_data.get("servo_mappings"):
        payload["servoMappings"] = calibration_data["servo_mappings"]
    if calibration_data.get("python_code"):
        payload["pythonCode"] = calibration_data["python_code"]
    if calibration_data.get("primitives"):
        payload["generatedPrimitives"] = calibration_data["primitives"]

    # Hardware fingerprint
    if calibration_data.get("firmware_version"):
        payload["firmwareVersion"] = calibration_data["firmware_version"]
    if calibration_data.get("port"):
        payload["serialPortName"] = calibration_data["port"]

    print("Uploading calibration to community registry...")
    print(f"  Robot: {payload.get('robotSlug', payload.get('robotId', 'Unknown'))}")
    print(f"  Method: {method}")
    print()

    try:
        # Use the uploader's pre-configured headers
        headers = uploader.headers
        response = requests.post(
            f"{base_url}/api/robot-calibrations",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as e:
        print(f"Error uploading calibration: {e}")
        if hasattr(e.response, 'json'):
            try:
                print(f"Details: {e.response.json()}")
            except:
                pass
        sys.exit(1)

    print("[OK] Calibration uploaded successfully!")
    print(f"  ID: {result['id']}")
    print(f"  Name: {result['name']}")
    print(f"  Status: {result['status']}")
    print()

    if publish:
        print("Publishing calibration...")
        try:
            publish_response = requests.patch(
                f"{base_url}/api/robot-calibrations/{result['id']}",
                json={"status": "published"},
                headers=headers,
            )
            publish_response.raise_for_status()
            print("[OK] Calibration published!")
        except requests.RequestException as e:
            print(f"Warning: Failed to publish: {e}")
            print("Calibration saved as draft. Publish manually when ready.")
    else:
        print("Calibration saved as draft. To publish:")
        print(f"  ate robot publish-calibration {result['id']}")

    print()
    print("Other users can now find and use your calibration!")
    print("Thank you for contributing to the community.")


def robot_identify_command(
    robot_slug: Optional[str] = None,
    robot_name: Optional[str] = None,
    port: Optional[str] = None,
):
    """
    Search the community calibration registry for matching calibrations.

    ate robot identify mechdog-mini
    ate robot identify --port /dev/cu.usbserial-10
    """
    import requests

    base_url = os.environ.get("FOODFORTHOUGHT_API_URL", "https://www.kindly.fyi")

    print("Searching community calibration registry...")
    print()

    # Build search query
    params = {"status": "published"}
    if robot_slug:
        params["robotSlug"] = robot_slug
    if robot_name:
        params["search"] = robot_name

    try:
        response = requests.get(f"{base_url}/api/robot-calibrations", params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        # Handle 404 (endpoint not deployed yet) or network errors
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
            print("The calibration registry is being set up.")
            print()
            print("Be the first to calibrate this robot!")
            print("  1. Run: ate robot generate-markers")
            print("  2. Print and attach markers to your robot")
            print("  3. Run: ate robot calibrate --method aruco")
            print("  4. Run: ate robot upload-calibration <file>")
            print()
            print("Your calibration will help everyone with this robot model.")
            return
        print(f"Error fetching calibrations: {e}")
        sys.exit(1)

    calibrations = data.get("calibrations", [])

    if not calibrations:
        print("No matching calibrations found in the community registry.")
        print()
        print("Be the first to calibrate this robot!")
        print("  1. Run: ate robot generate-markers")
        print("  2. Print and attach markers to your robot")
        print("  3. Run: ate robot calibrate --upload")
        print()
        print("Your calibration will help everyone with this robot model.")
        return

    print(f"Found {len(calibrations)} calibration(s):")
    print()

    for i, cal in enumerate(calibrations, 1):
        robot = cal.get("robot", {})
        author = cal.get("author", {})
        verifications = cal.get("_count", {}).get("verifications", 0)

        verified_badge = " [VERIFIED]" if cal.get("verified") else ""
        featured_badge = " [FEATURED]" if cal.get("featured") else ""

        print(f"{i}. {cal['name']}{verified_badge}{featured_badge}")
        print(f"   Robot: {robot.get('name', 'Unknown')} ({robot.get('manufacturer', 'Unknown')})")
        print(f"   Method: {cal['method']}")
        print(f"   Confidence: {cal['confidence']:.0%}")
        print(f"   Verified by: {verifications} user(s)")
        print(f"   Author: {author.get('name', 'Unknown')}")
        print(f"   ID: {cal['id']}")
        print()

    print("To download a calibration:")
    print("  ate robot download <calibration-id>")
    print()
    print("To verify a calibration works on your robot:")
    print("  ate robot verify <calibration-id>")


def robot_generate_markers_command(
    output: str = "aruco_markers.pdf",
    count: int = 12,
    size: float = 30.0,
    robot_name: Optional[str] = None,
    page_size: str = "letter",
    preset: Optional[str] = None,
    list_presets: bool = False,
):
    """
    Generate printable ArUco markers for robot calibration.

    ate robot generate-markers
    ate robot generate-markers --count 6 --size 40
    ate robot generate-markers --robot-name "My MechDog" -o my_markers.pdf
    ate robot generate-markers --preset mechdog-mini
    """
    try:
        from .marker_generator import generate_marker_pdf, list_presets as get_presets, get_preset_markers
        from reportlab.lib.pagesizes import LETTER, A4
    except ImportError as e:
        print(f"Error: Missing dependencies for marker generation.")
        print(f"Install with: pip install opencv-contrib-python reportlab pillow")
        print(f"Details: {e}")
        sys.exit(1)

    # List presets and exit
    if list_presets:
        presets = get_presets()
        print("Available robot presets:")
        print()
        for p in presets:
            print(f"  {p['name']:20} {p['robot_name']:30} ({p['marker_count']} markers)")
        print()
        print("Usage: ate robot generate-markers --preset mechdog-mini")
        return

    page = LETTER if page_size == "letter" else A4

    # Use preset if specified
    marker_specs = None
    if preset:
        try:
            marker_specs, preset_robot_name = get_preset_markers(preset)
            if not robot_name:
                robot_name = preset_robot_name
            count = len(marker_specs)
            print(f"Using preset: {preset}")
            print(f"  Robot: {robot_name}")
            print(f"  Markers: {count} (with optimized sizes per joint)")
        except KeyError as e:
            print(f"Error: {e}")
            print("\nRun 'ate robot generate-markers --list-presets' to see available presets.")
            sys.exit(1)
    else:
        print(f"Generating {count} ArUco markers...")
        print(f"  Size: {size}mm (uniform)")

    print(f"  Page: {page_size}")
    print(f"  Output: {output}")
    print()

    try:
        if marker_specs:
            # Use preset specs with variable sizes
            result = generate_marker_pdf(
                output_path=output,
                marker_specs=marker_specs,
                page_size=page,
                robot_name=robot_name,
                include_instructions=True,
            )
        else:
            # Use uniform size
            result = generate_marker_pdf(
                output_path=output,
                count=count,
                size_mm=size,
                page_size=page,
                robot_name=robot_name,
                include_instructions=True,
            )

        print(f"[OK] Markers saved to: {result}")
        print()
        print("Next steps:")
        print("  1. Print the PDF at 100% scale (do not 'fit to page')")
        print("  2. Cut out markers along the dashed lines")
        print("  3. Attach to your robot's moving segments")
        print("  4. Run: ate robot calibrate --method aruco")
        print()
        print("Your calibration can be shared with the community!")
        print("First user to calibrate a robot model helps everyone else.")
    except Exception as e:
        print(f"Error generating markers: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def robot_urdf_command(
    action: str = "generate",
    reset: bool = False,
    frames: int = 20,
    camera: int = 0,
    marker_size: float = 0.025,
    output: Optional[str] = None,
    ble_address: Optional[str] = None,
    robot_name: str = "mechdog",
    urdf_file: Optional[str] = None,
    bridge: bool = False,
    launch: bool = False,
):
    """
    URDF generation and Artifex integration command.

    ate robot urdf generate              # Generate URDF from markers
    ate robot urdf generate --reset      # Reset robot pose first
    ate robot urdf open                  # Open in Artifex Desktop
    ate robot urdf info                  # Show URDF details
    """
    import asyncio
    import cv2
    import numpy as np
    import re
    import subprocess
    from datetime import datetime

    # Default paths
    urdf_dir = Path(__file__).parent.parent.parent / "urdf_generation"
    urdf_dir.mkdir(exist_ok=True)
    default_urdf = urdf_dir / "mechdog_calibrated.urdf"

    if action == "generate":
        print("=" * 60)
        print("ATE URDF GENERATION")
        print("=" * 60)
        print(f"\nSettings:")
        print(f"  Marker size: {marker_size * 1000:.0f}mm")
        print(f"  Camera index: {camera}")
        print(f"  Frames: {frames}")
        print(f"  Robot name: {robot_name}")

        # ArUco setup
        ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        ARUCO_PARAMS = cv2.aruco.DetectorParameters()

        # Reset robot pose if requested
        if reset:
            print("\n--- Resetting Robot Pose ---")
            try:
                async def do_reset():
                    from bleak import BleakClient, BleakScanner

                    address = ble_address
                    if not address:
                        # Auto-discover MechDog
                        print("Scanning for MechDog...")
                        devices = await BleakScanner.discover(timeout=5.0)
                        for d in devices:
                            if d.name and "MechDog" in d.name:
                                address = d.address
                                print(f"Found: {d.name} ({address})")
                                break

                    if not address:
                        print("! MechDog not found - skipping reset")
                        return False

                    FFE1 = "0000ffe1-0000-1000-8000-00805f9b34fb"

                    async with BleakClient(address) as client:
                        print(f"Connected to {address}")

                        async def send(cmd: str, delay: float = 0.5):
                            await client.write_gatt_char(FFE1, (cmd + "\n").encode())
                            await asyncio.sleep(delay)

                        # Reset sequence
                        print("  Sit...")
                        await send("CMD|2|1|4|$", 2.0)
                        print("  Stand...")
                        await send("CMD|2|1|3|$", 2.0)
                        print("  Arm home...")
                        await send("CMD|7|8|$", 1.5)
                        print("  Done")
                        return True

                asyncio.run(do_reset())
                print("Waiting for robot to settle...")
                import time
                time.sleep(2.0)

            except ImportError:
                print("! bleak not installed - install with: pip install bleak")
            except Exception as e:
                print(f"! Reset failed: {e}")
                print("  Continuing with current pose...")

        # Open camera
        print("\n--- Capturing Markers ---")
        cap = cv2.VideoCapture(camera)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            sys.exit(1)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        import time
        time.sleep(1)

        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read from camera")
            sys.exit(1)

        h, w = frame.shape[:2]
        focal_length = w * 0.8
        camera_matrix = np.array([
            [focal_length, 0, w / 2],
            [0, focal_length, h / 2],
            [0, 0, 1]
        ], dtype=np.float32)
        dist_coeffs = np.zeros(5, dtype=np.float32)

        print(f"Camera: {w}x{h}")

        # Capture markers over multiple frames
        all_markers = {}
        detector = cv2.aruco.ArucoDetector(ARUCO_DICT, ARUCO_PARAMS)

        for i in range(frames):
            for _ in range(2):
                cap.read()

            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray)

            if ids is not None:
                for j, marker_id in enumerate(ids.flatten()):
                    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                        [corners[j]], marker_size, camera_matrix, dist_coeffs
                    )
                    mid = int(marker_id)
                    if mid not in all_markers:
                        all_markers[mid] = {"positions": [], "rotations": [], "corners": corners[j][0].tolist()}
                    all_markers[mid]["positions"].append(tvecs[0][0].tolist())
                    all_markers[mid]["rotations"].append(rvecs[0][0].tolist())

            print(f"  Frame {i+1}/{frames}: {len(all_markers)} markers", end='\r')

        print()
        cap.release()

        # Calculate averages
        for mid, data in all_markers.items():
            positions = np.array(data["positions"])
            rotations = np.array(data["rotations"])
            data["avg_position"] = positions.mean(axis=0).tolist()
            data["std_position"] = positions.std(axis=0).tolist()
            data["avg_rotation"] = rotations.mean(axis=0).tolist()
            data["detection_count"] = len(positions)

        print(f"\nDetected {len(all_markers)} markers: {sorted(all_markers.keys())}")

        # Save marker data
        marker_data = {
            "timestamp": datetime.now().isoformat(),
            "marker_size_m": marker_size,
            "markers": all_markers,
            "camera_matrix": camera_matrix.tolist(),
        }
        marker_json = urdf_dir / "marker_data.json"
        with open(marker_json, "w") as f:
            json.dump(marker_data, f, indent=2)
        print(f"Saved: {marker_json}")

        # Generate URDF
        print("\n--- Generating URDF ---")
        urdf_path = Path(output) if output else default_urdf
        _generate_urdf_from_markers(all_markers, urdf_path, robot_name)
        print(f"\nURDF saved to: {urdf_path}")
        print("\nTo open in Artifex Desktop:")
        print(f"  ate robot urdf open")

    elif action == "open":
        # Resolve URDF file
        urdf_path = Path(urdf_file) if urdf_file else default_urdf

        if not urdf_path.exists():
            print(f"Error: URDF not found: {urdf_path}")
            print("\nGenerate one first:")
            print("  ate robot urdf generate")
            sys.exit(1)

        # Show info
        _show_urdf_info(urdf_path)

        if bridge:
            # Try bridge sync
            print("\n--- Syncing via ATE Bridge ---")
            success = asyncio.run(_sync_urdf_bridge(urdf_path))
            if not success and launch:
                _launch_artifex(urdf_path)
        else:
            # Direct launch
            _launch_artifex(urdf_path)

    elif action == "info":
        urdf_path = Path(urdf_file) if urdf_file else default_urdf

        if not urdf_path.exists():
            print(f"Error: URDF not found: {urdf_path}")
            sys.exit(1)

        _show_urdf_info(urdf_path)

    else:
        print("Usage: ate robot urdf <generate|open|info>")
        sys.exit(1)


def _generate_urdf_from_markers(markers: dict, output_path: Path, robot_name: str = "mechdog"):
    """Generate URDF from detected marker positions."""
    from datetime import datetime

    detected = list(markers.keys())

    # Find body reference marker
    body_marker = 0 if 0 in markers else 7 if 7 in markers else detected[0] if detected else None
    if not body_marker:
        print("Error: No markers detected!")
        return

    import numpy as np
    body_pos = np.array(markers[body_marker]["avg_position"])

    # Calculate relative positions
    relative_positions = {}
    for mid, data in markers.items():
        pos = np.array(data["avg_position"])
        relative_positions[mid] = (pos - body_pos).tolist()

    # Build URDF
    urdf = f'''<?xml version="1.0"?>
<robot name="{robot_name}" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!--
    {robot_name.upper()} URDF - Generated by ATE CLI
    Date: {datetime.now().isoformat()}
    Markers detected: {detected}

    Generated with: ate robot urdf generate
  -->

  <!-- Materials -->
  <material name="orange"><color rgba="1.0 0.5 0.0 1.0"/></material>
  <material name="black"><color rgba="0.1 0.1 0.1 1.0"/></material>
  <material name="gray"><color rgba="0.5 0.5 0.5 1.0"/></material>

  <!-- Base Link -->
  <link name="base_link">
    <visual><geometry><box size="0.01 0.01 0.01"/></geometry></visual>
  </link>

  <!-- Body -->
  <link name="body">
    <visual>
      <geometry><box size="0.18 0.10 0.06"/></geometry>
      <material name="orange"/>
    </visual>
    <collision><geometry><box size="0.18 0.10 0.06"/></geometry></collision>
    <inertial>
      <mass value="0.8"/>
      <inertia ixx="0.002" ixy="0" ixz="0" iyy="0.003" iyz="0" izz="0.002"/>
    </inertial>
  </link>

  <joint name="body_joint" type="fixed">
    <parent link="base_link"/>
    <child link="body"/>
    <origin xyz="0 0 0.12"/>
  </joint>

  <!-- Arm -->
'''
    # Arm configuration
    arm_offset = "0.09 0 0.02"
    if 1 in markers:
        rel = relative_positions[1]
        arm_offset = f"{rel[0]:.4f} {rel[1]:.4f} {rel[2] + 0.02:.4f}"

    urdf += f'''  <link name="arm_link1">
    <visual>
      <origin xyz="0.035 0 0"/>
      <geometry><box size="0.07 0.03 0.03"/></geometry>
      <material name="gray"/>
    </visual>
    <inertial><mass value="0.08"/><inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/></inertial>
  </link>

  <joint name="arm_shoulder_joint" type="revolute">
    <parent link="body"/>
    <child link="arm_link1"/>
    <origin xyz="{arm_offset}"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="5.0" velocity="2.0"/>
  </joint>

  <link name="arm_link2">
    <visual>
      <origin xyz="0.04 0 0"/>
      <geometry><box size="0.08 0.025 0.025"/></geometry>
      <material name="gray"/>
    </visual>
    <inertial><mass value="0.06"/><inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/></inertial>
  </link>

  <joint name="arm_elbow_joint" type="revolute">
    <parent link="arm_link1"/>
    <child link="arm_link2"/>
    <origin xyz="0.07 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="3.0" velocity="2.0"/>
  </joint>

  <link name="gripper_base">
    <visual><geometry><box size="0.03 0.04 0.02"/></geometry><material name="black"/></visual>
    <inertial><mass value="0.03"/><inertia ixx="0.00001" ixy="0" ixz="0" iyy="0.00001" iyz="0" izz="0.00001"/></inertial>
  </link>

  <joint name="gripper_base_joint" type="fixed">
    <parent link="arm_link2"/>
    <child link="gripper_base"/>
    <origin xyz="0.08 0 0"/>
  </joint>

  <link name="gripper_left_finger">
    <visual><origin xyz="0.015 0 0"/><geometry><box size="0.03 0.005 0.015"/></geometry><material name="black"/></visual>
    <inertial><mass value="0.01"/><inertia ixx="0.000001" ixy="0" ixz="0" iyy="0.000001" iyz="0" izz="0.000001"/></inertial>
  </link>

  <joint name="gripper_left_joint" type="prismatic">
    <parent link="gripper_base"/>
    <child link="gripper_left_finger"/>
    <origin xyz="0.01 0.012 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.012" upper="0" effort="1.0" velocity="0.5"/>
  </joint>

  <link name="gripper_right_finger">
    <visual><origin xyz="0.015 0 0"/><geometry><box size="0.03 0.005 0.015"/></geometry><material name="black"/></visual>
    <inertial><mass value="0.01"/><inertia ixx="0.000001" ixy="0" ixz="0" iyy="0.000001" iyz="0" izz="0.000001"/></inertial>
  </link>

  <joint name="gripper_right_joint" type="prismatic">
    <parent link="gripper_base"/>
    <child link="gripper_right_finger"/>
    <origin xyz="0.01 -0.012 0"/>
    <axis xyz="0 -1 0"/>
    <limit lower="-0.012" upper="0" effort="1.0" velocity="0.5"/>
  </joint>

  <!-- Legs -->
'''

    # Generate legs
    legs = [
        ("front_left", 0.07, 0.05, 13),
        ("front_right", 0.07, -0.05, 14),
        ("rear_left", -0.07, 0.05, 15),
        ("rear_right", -0.07, -0.05, 16),
    ]

    for leg_name, x_def, y_def, marker_id in legs:
        x_off = relative_positions[marker_id][0] if marker_id in markers else x_def
        y_off = relative_positions[marker_id][1] if marker_id in markers else y_def

        urdf += f'''  <!-- {leg_name.replace("_", " ").title()} Leg -->
  <link name="{leg_name}_hip">
    <visual><geometry><cylinder radius="0.012" length="0.025"/></geometry><material name="gray"/></visual>
    <inertial><mass value="0.03"/><inertia ixx="0.00001" ixy="0" ixz="0" iyy="0.00001" iyz="0" izz="0.00001"/></inertial>
  </link>
  <joint name="{leg_name}_hip_joint" type="revolute">
    <parent link="body"/><child link="{leg_name}_hip"/>
    <origin xyz="{x_off:.4f} {y_off:.4f} -0.02" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/><limit lower="-0.5" upper="0.5" effort="3.0" velocity="2.0"/>
  </joint>

  <link name="{leg_name}_thigh">
    <visual><origin xyz="0 0 -0.03"/><geometry><box size="0.025 0.02 0.06"/></geometry><material name="orange"/></visual>
    <inertial><mass value="0.05"/><inertia ixx="0.00005" ixy="0" ixz="0" iyy="0.00005" iyz="0" izz="0.00001"/></inertial>
  </link>
  <joint name="{leg_name}_thigh_joint" type="revolute">
    <parent link="{leg_name}_hip"/><child link="{leg_name}_thigh"/>
    <origin xyz="0 0 -0.015" rpy="-1.5708 0 0"/>
    <axis xyz="0 1 0"/><limit lower="-1.57" upper="1.57" effort="5.0" velocity="2.0"/>
  </joint>

  <link name="{leg_name}_shin">
    <visual><origin xyz="0 0 -0.025"/><geometry><box size="0.02 0.015 0.05"/></geometry><material name="orange"/></visual>
    <inertial><mass value="0.04"/><inertia ixx="0.00003" ixy="0" ixz="0" iyy="0.00003" iyz="0" izz="0.000005"/></inertial>
  </link>
  <joint name="{leg_name}_knee_joint" type="revolute">
    <parent link="{leg_name}_thigh"/><child link="{leg_name}_shin"/>
    <origin xyz="0 0 -0.06"/><axis xyz="0 1 0"/><limit lower="-2.5" upper="0" effort="4.0" velocity="2.0"/>
  </joint>

  <link name="{leg_name}_foot">
    <visual><geometry><sphere radius="0.012"/></geometry><material name="black"/></visual>
    <collision><geometry><sphere radius="0.012"/></geometry></collision>
    <inertial><mass value="0.01"/><inertia ixx="0.000001" ixy="0" ixz="0" iyy="0.000001" iyz="0" izz="0.000001"/></inertial>
  </link>
  <joint name="{leg_name}_foot_joint" type="fixed">
    <parent link="{leg_name}_shin"/><child link="{leg_name}_foot"/>
    <origin xyz="0 0 -0.05"/>
  </joint>

'''

    urdf += "</robot>\n"

    # Write URDF
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(urdf)

    # Count elements
    import re
    links = len(re.findall(r'<link\s+name=', urdf))
    joints = len(re.findall(r'<joint\s+name=', urdf))
    print(f"Generated: {links} links, {joints} joints")


def _show_urdf_info(urdf_path: Path):
    """Display information about a URDF file."""
    import re

    with open(urdf_path, 'r') as f:
        content = f.read()

    robot_match = re.search(r'<robot\s+name="([^"]+)"', content)
    robot_name = robot_match.group(1) if robot_match else "unknown"

    joints = re.findall(r'<joint\s+name="([^"]+)"', content)
    links = re.findall(r'<link\s+name="([^"]+)"', content)
    revolute = len(re.findall(r'type="revolute"', content))
    prismatic = len(re.findall(r'type="prismatic"', content))
    fixed = len(re.findall(r'type="fixed"', content))

    print(f"\n--- URDF Information ---")
    print(f"Robot: {robot_name}")
    print(f"File: {urdf_path}")
    print(f"Size: {urdf_path.stat().st_size} bytes")
    print(f"\nStructure:")
    print(f"  Links: {len(links)}")
    print(f"  Joints: {len(joints)}")
    print(f"    - Revolute: {revolute}")
    print(f"    - Prismatic: {prismatic}")
    print(f"    - Fixed: {fixed}")


async def _sync_urdf_bridge(urdf_path: Path) -> bool:
    """Sync URDF to Artifex via ATE bridge server."""
    try:
        import websockets
    except ImportError:
        print("Installing websockets...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "websockets", "-q"])
        import websockets

    try:
        with open(urdf_path, 'r') as f:
            urdf_content = f.read()

        async with websockets.connect('ws://localhost:8765', open_timeout=5) as ws:
            print("Connected to ATE bridge server")

            request = {"id": 1, "action": "sync_urdf", "params": {"urdf": urdf_content}}
            await ws.send(json.dumps(request))
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            result = json.loads(response)

            if "error" in result:
                print(f"Sync failed: {result['error']}")
                return False

            if result.get("result"):
                joints = result["result"].get("joints", [])
                print(f"URDF synced to Artifex! ({len(joints)} joints)")
                return True

    except ConnectionRefusedError:
        print("ATE bridge server not running")
        print("  Start with: python -m ate.bridge_server")
    except asyncio.TimeoutError:
        print("Connection timeout")
    except Exception as e:
        print(f"Error: {e}")

    return False


def _launch_artifex(urdf_path: Optional[Path] = None) -> bool:
    """Launch Artifex Desktop with optional URDF file."""
    import subprocess

    print("\n--- Launching Artifex Desktop ---")

    # Find Artifex
    artifex_paths = [
        Path("/Applications/Artifex.app"),
        Path.home() / "Applications/Artifex.app",
        Path(__file__).parent.parent.parent.parent / "artifex-desktop/dist/mac-arm64/Artifex.app",
        Path(__file__).parent.parent.parent.parent / "artifex-desktop/dist/mac/Artifex.app",
    ]

    artifex_app = None
    for p in artifex_paths:
        if p.exists():
            artifex_app = p
            break

    if not artifex_app:
        print("Artifex Desktop not found")
        print("\nInstall from: https://kindly.fyi/artifex")
        if urdf_path:
            print(f"\nOr manually open: {urdf_path}")
        return False

    print(f"Found: {artifex_app}")

    try:
        if urdf_path:
            cmd = ["open", "-a", str(artifex_app), str(urdf_path.absolute())]
            print(f"Opening: {urdf_path.name}")
        else:
            cmd = ["open", str(artifex_app)]

        subprocess.run(cmd, check=True)
        print("Artifex Desktop launched")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Launch failed: {e}")
        return False


def register_robot_parser(subparsers):
    """
    Register the robot command with argparse.

    Call this from the main CLI to add robot commands.
    """
    robot_parser = subparsers.add_parser("robot",
        help="Robot discovery, setup, and management",
        description="""Robot management commands.

Discover robots, set up configurations, and test capabilities.

EXAMPLES:
    ate robot discover              # Find robots on network/USB
    ate robot list                  # List known robot types
    ate robot info hiwonder_mechdog # Show robot type info
    ate robot setup                 # Interactive setup wizard
    ate robot test my_mechdog       # Test robot capabilities
    ate robot profiles list         # List saved profiles
""")
    robot_subparsers = robot_parser.add_subparsers(dest="robot_action", help="Robot action")

    # robot discover
    discover_parser = robot_subparsers.add_parser("discover", help="Find robots on network and USB")
    discover_parser.add_argument("--subnet", help="Network subnet to scan (e.g., 192.168.1)")
    discover_parser.add_argument("--timeout", type=float, default=3.0, help="Scan timeout (default: 3s)")
    discover_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # robot ble - Bluetooth Low Energy discovery and connection
    ble_parser = robot_subparsers.add_parser("ble",
        help="Bluetooth Low Energy robot discovery and connection",
        description="""Discover and connect to robots via Bluetooth Low Energy.

BLE provides wireless control without WiFi infrastructure - useful for
outdoor robots or when USB is inconvenient.

EXAMPLES:
    ate robot ble discover              # Scan for BLE robots
    ate robot ble discover --filter MechDog  # Filter by name
    ate robot ble connect AA:BB:CC:DD:EE:FF  # Test connection
    ate robot ble info                  # Show BLE-capable robots
""")
    ble_subparsers = ble_parser.add_subparsers(dest="ble_action", help="BLE action")

    # ble discover
    ble_discover = ble_subparsers.add_parser("discover", help="Scan for BLE devices")
    ble_discover.add_argument("--timeout", type=float, default=10.0,
                             help="Scan timeout in seconds (default: 10)")
    ble_discover.add_argument("--filter", dest="name_filter",
                             help="Filter devices by name (e.g., MechDog, ESP32)")
    ble_discover.add_argument("--json", action="store_true", dest="json_output",
                             help="Output as JSON")

    # ble connect
    ble_connect = ble_subparsers.add_parser("connect", help="Test connection to BLE device")
    ble_connect.add_argument("address", help="BLE device address (e.g., AA:BB:CC:DD:EE:FF)")
    ble_connect.add_argument("-p", "--profile", dest="profile_name",
                            help="Update profile with BLE settings")

    # ble info
    ble_subparsers.add_parser("info", help="Show BLE-capable robots and UUIDs")

    # ble capture - Capture traffic from phone app
    ble_capture = ble_subparsers.add_parser("capture",
        help="Capture BLE traffic from phone app for protocol reverse-engineering",
        description="""Capture BLE traffic while using a phone app to control your robot.

This automates the workflow for reverse-engineering undocumented BLE protocols:
1. Guides you through setting up PacketLogger (iOS) or HCI snoop (Android)
2. Captures traffic while you operate the phone app
3. Saves capture file for analysis

EXAMPLES:
    ate robot ble capture                     # Auto-detect platform
    ate robot ble capture --platform ios      # Force iOS capture
    ate robot ble capture -o my_capture.pklg  # Specify output file
""")
    ble_capture.add_argument("-p", "--platform", choices=["ios", "android", "auto"],
                            default="auto", help="Mobile platform (default: auto-detect)")
    ble_capture.add_argument("-o", "--output", default="capture.pklg",
                            help="Output file path (default: capture.pklg)")

    # ble analyze - Analyze capture file
    ble_analyze = ble_subparsers.add_parser("analyze",
        help="Analyze BLE capture file to decode protocol commands",
        description="""Analyze a BLE capture file (.pklg or .btsnoop) to decode the protocol.

Extracts write commands and notifications, identifies the protocol format,
and optionally generates Python code to replay the discovered commands.

EXAMPLES:
    ate robot ble analyze capture.pklg           # Decode and display commands
    ate robot ble analyze capture.pklg --generate # Also generate Python code
    ate robot ble analyze capture.pklg -o protocol.py  # Save code to file
""")
    ble_analyze.add_argument("capture_file", help="Path to capture file (.pklg or .btsnoop)")
    ble_analyze.add_argument("-g", "--generate", action="store_true",
                            help="Generate Python replay code")
    ble_analyze.add_argument("-o", "--output", help="Output file for generated code")

    # ble inspect - Inspect device characteristics
    ble_inspect = ble_subparsers.add_parser("inspect",
        help="Inspect BLE device services and characteristics",
        description="""Connect to a BLE device and show its service/characteristic map.

Shows which characteristics support write vs notify, helping you understand
the correct configuration for communication.

EXAMPLES:
    ate robot ble inspect mechdog_00              # Inspect by device name
    ate robot ble inspect AA:BB:CC:DD:EE:FF       # Inspect by address
""")
    ble_inspect.add_argument("address", help="Device address or name to inspect")

    # robot list
    list_parser = robot_subparsers.add_parser("list", help="List known robot types")
    list_parser.add_argument("--archetype", choices=["quadruped", "humanoid", "arm", "custom"],
                            help="Filter by archetype")

    # robot info
    info_parser = robot_subparsers.add_parser("info", help="Show robot type or profile info")
    info_parser.add_argument("robot_type", nargs="?", help="Robot type ID")
    info_parser.add_argument("-p", "--profile", help="Show profile instead of type")

    # robot setup
    setup_parser = robot_subparsers.add_parser("setup", help="Interactive setup wizard")
    setup_parser.add_argument("--port", help="Serial port")
    setup_parser.add_argument("--camera-ip", help="Camera IP address")
    setup_parser.add_argument("--type", dest="robot_type", default="hiwonder_mechdog",
                             help="Robot type (default: hiwonder_mechdog)")
    setup_parser.add_argument("--name", help="Profile name")
    setup_parser.add_argument("--non-interactive", action="store_true",
                             help="Use defaults, no prompts")

    # robot test
    test_parser = robot_subparsers.add_parser("test", help="Test robot capabilities")
    test_parser.add_argument("profile", help="Profile name")
    test_parser.add_argument("-c", "--capability", help="Specific capability to test")
    test_parser.add_argument("-v", "--verbose", action="store_true", help="Show method details")

    # robot approach
    approach_parser = robot_subparsers.add_parser("approach",
        help="Approach detected targets",
        description="""Scan for targets and approach them using visual servoing.

Works with any robot that has camera and locomotion capabilities.
Uses visual distance estimation when no hardware distance sensor is available.

EXAMPLES:
    ate robot approach my_mechdog                    # Basic approach
    ate robot approach my_mechdog --target-distance 0.2  # Stop 20cm from target
    ate robot approach my_mechdog --dry-run          # Scan only, no movement
    ate robot approach my_mechdog --speed 0.5        # Faster approach
""")
    approach_parser.add_argument("profile", help="Profile name")
    approach_parser.add_argument("-d", "--duration", type=float, default=30.0,
                                help="Maximum duration in seconds (default: 30)")
    approach_parser.add_argument("-t", "--target-distance", type=float, default=0.15,
                                help="Distance to stop from target in meters (default: 0.15)")
    approach_parser.add_argument("-s", "--speed", type=float, default=0.3,
                                help="Approach speed (default: 0.3)")
    approach_parser.add_argument("--detect-colors", nargs="+",
                                help="Colors to detect (red, blue, green, etc.)")
    approach_parser.add_argument("--dry-run", action="store_true",
                                help="Scan and detect but don't move")

    # robot profiles
    profiles_parser = robot_subparsers.add_parser("profiles", help="Manage saved profiles")
    profiles_subparsers = profiles_parser.add_subparsers(dest="profiles_action", help="Profile action")

    profiles_subparsers.add_parser("list", help="List saved profiles")

    profiles_show = profiles_subparsers.add_parser("show", help="Show profile details")
    profiles_show.add_argument("name", help="Profile name")

    profiles_delete = profiles_subparsers.add_parser("delete", help="Delete profile")
    profiles_delete.add_argument("name", help="Profile name")

    profiles_create = profiles_subparsers.add_parser("create", help="Create new profile")
    profiles_create.add_argument("name", help="Profile name")
    profiles_create.add_argument("-t", "--template", help="Template to use")

    profiles_subparsers.add_parser("templates", help="List available templates")

    # robot calibrate
    calibrate_parser = robot_subparsers.add_parser("calibrate",
        help="Visual calibration for robot servos and poses",
        description="""Visual calibration wizard with webcam feedback.

Interactively discover servo ranges, record named positions (poses),
and build a calibration profile for your robot.

EXAMPLES:
    ate robot calibrate start --port /dev/cu.usbserial-10 --name my_mechdog
    ate robot calibrate gripper --port /dev/cu.usbserial-10 --servo 11
    ate robot calibrate list
    ate robot calibrate poses my_mechdog
    ate robot calibrate record my_mechdog --pose gripper_open
    ate robot calibrate apply my_mechdog --pose gripper_closed
""")
    calibrate_subparsers = calibrate_parser.add_subparsers(dest="calibrate_action", help="Calibration action")

    # calibrate start
    cal_start = calibrate_subparsers.add_parser("start", help="Run interactive calibration wizard")
    cal_start.add_argument("--port", help="Serial port")
    cal_start.add_argument("--camera", dest="camera_url", help="Camera URL for visual feedback")
    cal_start.add_argument("--name", default="robot", help="Calibration name (default: robot)")
    cal_start.add_argument("--type", dest="robot_type", default="unknown", help="Robot type")

    # calibrate gripper
    cal_gripper = calibrate_subparsers.add_parser("gripper", help="Quick gripper-only calibration")
    cal_gripper.add_argument("--port", help="Serial port")
    cal_gripper.add_argument("--servo", type=int, default=11, help="Gripper servo ID (default: 11)")

    # calibrate list
    calibrate_subparsers.add_parser("list", help="List saved calibrations")

    # calibrate poses
    cal_poses = calibrate_subparsers.add_parser("poses", help="Show poses for a calibration")
    cal_poses.add_argument("name", help="Calibration name")

    # calibrate record
    cal_record = calibrate_subparsers.add_parser("record", help="Record current position as a pose")
    cal_record.add_argument("name", help="Calibration name")
    cal_record.add_argument("--pose", required=True, help="Name for the pose")

    # calibrate apply
    cal_apply = calibrate_subparsers.add_parser("apply", help="Apply a saved pose")
    cal_apply.add_argument("name", help="Calibration name")
    cal_apply.add_argument("--pose", required=True, help="Pose to apply")

    # calibrate direction - THE CRITICAL STEP
    cal_direction = calibrate_subparsers.add_parser("direction",
        help="Direction calibration via Twitch Test (CRITICAL)",
        description="""Determine which servo direction moves TOWARD the target.

This is the CRITICAL step that was missing! Without direction calibration,
the robot doesn't know if positive servo values move the gripper toward
or away from the target.

Process:
1. Place a green ball in front of the robot
2. Ensure ArUco markers on arm are visible to webcam
3. For each servo, measure distance to ball before/after small movement
4. Record whether positive values move toward or away from target

EXAMPLES:
    ate robot calibrate direction --port /dev/cu.usbserial-10 --name my_mechdog
    ate robot calibrate direction --name my_mechdog
""")
    cal_direction.add_argument("--port", help="Serial port")
    cal_direction.add_argument("--name", default="robot", help="Robot name")

    # calibrate status - Show calibration progress
    cal_status = calibrate_subparsers.add_parser("status",
        help="Show calibration status and next steps",
        description="""Show the calibration status for a robot.

Displays which calibration stages are complete and what needs to be done next.
This enforces the proper calibration workflow.

EXAMPLES:
    ate robot calibrate status                 # List all robots
    ate robot calibrate status my_mechdog      # Show specific robot
""")
    cal_status.add_argument("name", nargs="?", default="robot", help="Robot name")

    # calibrate reset - Reset calibration state
    cal_reset = calibrate_subparsers.add_parser("reset",
        help="Reset calibration state for a robot",
        description="""Reset all calibration progress for a robot.

Use this if you need to recalibrate from scratch.
""")
    cal_reset.add_argument("name", help="Robot name")

    # robot label - Visual labeling with dual cameras
    label_parser = robot_subparsers.add_parser("label",
        help="Visual servo/pose/action labeling with dual cameras",
        description="""Interactive visual labeling session using webcam + robot camera.

Creates a "bedrock" of basic skills by:
1. Discovering and labeling servos by their physical effect
2. Recording named poses with visual confirmation
3. Sequencing poses into multi-step actions
4. Generating reusable Python skill code

EXAMPLES:
    ate robot label --name my_mechdog
    ate robot label --port /dev/cu.usbserial-10 --camera http://192.168.50.98:80/capture
    ate robot label --webcam 1 --name mechdog
""")
    label_parser.add_argument("--port", help="Serial port (auto-detects if not specified)")
    label_parser.add_argument("--name", default="robot", help="Robot name for saving (default: robot)")
    label_parser.add_argument("--type", dest="robot_type", default="hiwonder_mechdog", help="Robot type")
    label_parser.add_argument("--webcam", type=int, default=0, dest="webcam_id",
                             help="Webcam device ID (default: 0)")
    label_parser.add_argument("--camera", dest="camera_url",
                             help="Robot camera URL (e.g., http://192.168.50.98:80/capture)")

    # robot skills - Manage generated skills
    skills_parser = robot_subparsers.add_parser("skills",
        help="Manage generated robot skills",
        description="""Manage skill libraries created from visual labeling.

View, export, and manage the Python skill code generated from labeled
poses and actions.

EXAMPLES:
    ate robot skills list
    ate robot skills show my_mechdog
    ate robot skills export my_mechdog
    ate robot skills export my_mechdog pickup
""")
    skills_subparsers = skills_parser.add_subparsers(dest="skills_action", help="Skills action")

    skills_subparsers.add_parser("list", help="List saved skill libraries")

    skills_show = skills_subparsers.add_parser("show", help="Show skill library details")
    skills_show.add_argument("name", help="Library name")

    skills_export = skills_subparsers.add_parser("export", help="Export skills as Python code")
    skills_export.add_argument("name", help="Library name")
    skills_export.add_argument("skill", nargs="?", help="Specific skill to export (exports all if omitted)")

    # robot upload - Upload skill library to FoodforThought
    upload_parser = robot_subparsers.add_parser("upload",
        help="Upload skill library to FoodforThought",
        description="""Upload calibration, poses, and skills to FoodforThought platform.

Creates artifacts with full data lineage:
  raw (images) → processed (calibration) → labeled (poses) → skill (code)

Requires authentication. Run 'ate login' first.

EXAMPLES:
    ate robot upload mechdog
    ate robot upload mechdog --project-id abc123
    ate robot upload mechdog --no-images
""")
    upload_parser.add_argument("name", help="Robot name (matches calibration/library)")
    upload_parser.add_argument("--project-id", dest="project_id", help="Existing project ID (creates new if omitted)")
    upload_parser.add_argument("--no-images", action="store_true", dest="no_images",
                              help="Skip uploading pose images")

    # robot teach - Fast keyboard-driven teaching mode
    teach_parser = robot_subparsers.add_parser("teach",
        help="Fast keyboard-driven teaching mode with live preview",
        description="""Real-time teaching interface for quick skill development.

Opens a live webcam preview with keyboard controls:
  ↑/↓     Select servo
  ←/→     Adjust position (hold Shift for fine control)
  S       Save current position as a pose
  A       Create action from saved poses
  P       Playback last action
  C       Clear recorded poses
  R       Reset to center positions
  +/-     Adjust step size
  Q       Quit and save

Much faster iteration than menu-driven labeling.

EXAMPLES:
    ate robot teach --port /dev/cu.usbserial-10 --name mechdog
    ate robot teach --port /dev/cu.usbserial-10 --webcam 1
""")
    teach_parser.add_argument("--port", required=True, help="Serial port")
    teach_parser.add_argument("--name", default="robot", help="Robot name for saving")
    teach_parser.add_argument("--type", dest="robot_type", default="hiwonder_mechdog", help="Robot type")
    teach_parser.add_argument("--webcam", type=int, default=0, dest="webcam_id", help="Webcam device ID")
    teach_parser.add_argument("--camera", dest="camera_url", help="Robot camera URL (optional)")

    # robot primitives - List and inspect programmatic primitives
    primitives_parser = robot_subparsers.add_parser("primitives",
        help="List and inspect skill primitives",
        description="""View the programmatic skill library.

Shows all primitives, compound skills, and behaviors with their
hardware requirements, servo targets, and step sequences.

EXAMPLES:
    ate robot primitives list
    ate robot primitives show gripper_open
    ate robot primitives show pickup
    ate robot primitives show fetch
""")
    primitives_subparsers = primitives_parser.add_subparsers(dest="primitives_action", help="Primitives action")

    primitives_subparsers.add_parser("list", help="List all primitives, compounds, and behaviors")

    primitives_show = primitives_subparsers.add_parser("show", help="Show details of a specific skill")
    primitives_show.add_argument("name", help="Skill name")

    # robot map-servos - LLM-guided servo mapping
    map_servos_parser = robot_subparsers.add_parser("map-servos",
        help="Map all servos and generate primitive skills using LLM",
        description="""LLM-guided servo mapping and primitive generation.

Uses an AI agent to systematically probe each servo, analyze its function
(via camera or position feedback), and generate named positions and
primitive skills.

This automates the tedious process of discovering what each servo does
and creates reusable skill code.

EXAMPLES:
    ate robot map-servos --port /dev/cu.usbserial-10
    ate robot map-servos --port /dev/cu.usbserial-10 --camera
    ate robot map-servos --port /dev/cu.usbserial-10 --wifi-camera 192.168.4.1
    ate robot map-servos --num-servos 6 --output ./my_arm
""")
    map_servos_parser.add_argument("--port", help="Serial port (auto-detects if not specified)")
    map_servos_parser.add_argument("--num-servos", type=int, default=13,
                                   help="Number of servos to probe (default: 13)")
    map_servos_parser.add_argument("--camera", action="store_true", dest="use_camera",
                                   help="Use webcam for visual verification")
    map_servos_parser.add_argument("--camera-index", type=int, default=0,
                                   help="Webcam device index (default: 0)")
    map_servos_parser.add_argument("--wifi-camera", dest="wifi_camera_ip",
                                   help="Use robot's WiFi camera at IP (e.g., 192.168.4.1)")
    map_servos_parser.add_argument("--output", "-o", help="Output file prefix (default: ./servo_mappings_<port>)")
    map_servos_parser.add_argument("--save-images", action="store_true",
                                   help="Save camera images during probing")
    map_servos_parser.add_argument("--upload", action="store_true",
                                   help="Upload servo mappings to FoodforThought after mapping")
    map_servos_parser.add_argument("--project-id", dest="project_id",
                                   help="Project ID for upload (creates new if not specified)")

    # robot generate-markers - Generate printable ArUco markers
    markers_parser = robot_subparsers.add_parser("generate-markers",
        help="Generate printable ArUco markers for calibration",
        description="""Generate a PDF with printable ArUco markers for robot calibration.

These markers enable precise visual system identification:
- Attach markers to each joint/segment of your robot
- Run calibration to discover kinematics automatically
- Share your calibration with the community!

The PDF includes:
- Markers with cutting guides
- Joint labels and IDs
- Setup instructions

EXAMPLES:
    ate robot generate-markers
    ate robot generate-markers --count 6 --size 40
    ate robot generate-markers --robot-name "My MechDog" -o my_markers.pdf
""")
    markers_parser.add_argument("--output", "-o", default="aruco_markers.pdf",
                               help="Output PDF path (default: aruco_markers.pdf)")
    markers_parser.add_argument("--count", "-n", type=int, default=12,
                               help="Number of markers to generate (default: 12)")
    markers_parser.add_argument("--size", type=float, default=30.0,
                               help="Marker size in millimeters (default: 30)")
    markers_parser.add_argument("--robot-name",
                               help="Optional robot name for labeling")
    markers_parser.add_argument("--page-size", choices=["letter", "a4"], default="letter",
                               help="Page size (default: letter)")
    markers_parser.add_argument("--preset",
                               help="Use robot-specific preset (e.g., mechdog-mini, unitree-go1, xarm-6)")
    markers_parser.add_argument("--list-presets", action="store_true",
                               help="List available robot presets")

    # robot identify - Search community calibration registry
    identify_parser = robot_subparsers.add_parser("identify",
        help="Search community calibration registry for your robot",
        description="""Search the FoodforThought community calibration registry.

Find calibrations shared by other users for your robot model.
When a community member calibrates a robot, everyone benefits!

EXAMPLES:
    ate robot identify mechdog-mini
    ate robot identify --search "MechDog"
    ate robot identify --port /dev/cu.usbserial-10  # Auto-detect robot type
""")
    identify_parser.add_argument("robot_slug", nargs="?",
                                help="Robot model slug (e.g., mechdog-mini)")
    identify_parser.add_argument("--search", dest="robot_name",
                                help="Search by robot name")
    identify_parser.add_argument("--port",
                                help="Serial port (for auto-detection)")

    # robot upload-calibration - Upload calibration to community registry
    upload_cal_parser = robot_subparsers.add_parser("upload-calibration",
        help="Upload a calibration to the community registry",
        description="""Upload your calibration to share with the community.

Your calibration helps everyone with the same robot model!
First user to calibrate a robot benefits the entire community.

EXAMPLES:
    ate robot upload-calibration ./servo_mappings.json --robot-slug mechdog-mini
    ate robot upload-calibration ./calibration.json --publish
""")
    upload_cal_parser.add_argument("calibration_file",
                                  help="Path to calibration JSON file")
    upload_cal_parser.add_argument("--robot-slug",
                                  help="Robot model slug")
    upload_cal_parser.add_argument("--robot-name",
                                  help="Robot name (for search)")
    upload_cal_parser.add_argument("--method",
                                  choices=["aruco_marker", "llm_vision", "manual", "urdf_import", "twitch_test", "direction_calibration"],
                                  default="llm_vision",
                                  help="Calibration method (default: llm_vision)")
    upload_cal_parser.add_argument("--publish", action="store_true",
                                  help="Publish immediately (default: save as draft)")

    # robot behavior - Run high-level behaviors with perception
    behavior_parser = robot_subparsers.add_parser("behavior",
        help="Execute high-level behaviors with perception",
        description="""Run complex behaviors that combine primitives with perception.

Behaviors include closed-loop control using camera feedback:
- Detect targets
- Align to center them in view
- Approach until close enough
- Execute manipulation sequences
- Verify success

EXAMPLES:
    ate robot behavior pickup_green_ball --simulate
    ate robot behavior pickup_green_ball --profile my_mechdog
    ate robot behavior pickup_green_ball --camera-ip 192.168.4.1
""")
    behavior_parser.add_argument("behavior", nargs="?", default="pickup_green_ball",
                                help="Behavior to execute (default: pickup_green_ball)")
    behavior_parser.add_argument("-p", "--profile", dest="profile_name",
                                help="Robot profile for real execution")
    behavior_parser.add_argument("--camera-ip", dest="camera_ip",
                                help="WiFi camera IP address")
    behavior_parser.add_argument("--simulate", action="store_true",
                                help="Run in simulation mode (no real robot)")

    # robot urdf - URDF generation and Artifex integration
    urdf_parser = robot_subparsers.add_parser("urdf",
        help="Generate URDF from ArUco markers and open in Artifex",
        description="""Generate URDF from visual ArUco marker detection.

This command captures ArUco markers attached to robot links via webcam,
computes their 3D positions, and generates a calibrated URDF file.
The URDF can then be opened directly in Artifex Desktop for visualization.

WORKFLOW:
1. Attach ArUco markers (4x4_50 dictionary, 25mm) to robot links
2. Run 'ate robot urdf generate' to capture and create URDF
3. Run 'ate robot urdf open' to view in Artifex Desktop

EXAMPLES:
    ate robot urdf generate                    # Capture markers and generate URDF
    ate robot urdf generate --reset            # Reset robot pose first (BLE)
    ate robot urdf generate --frames 50        # More frames for accuracy
    ate robot urdf open                        # Open in Artifex Desktop
    ate robot urdf open --bridge               # Sync via ATE bridge server
    ate robot urdf info                        # Show URDF details
""")
    urdf_subparsers = urdf_parser.add_subparsers(dest="urdf_action", help="URDF action")

    # urdf generate
    urdf_generate = urdf_subparsers.add_parser("generate",
        help="Generate URDF from ArUco marker detection")
    urdf_generate.add_argument("--reset", action="store_true",
                              help="Reset robot pose via BLE before capture")
    urdf_generate.add_argument("--frames", type=int, default=20,
                              help="Number of frames to capture (default: 20)")
    urdf_generate.add_argument("--camera", type=int, default=0,
                              help="Camera index (default: 0)")
    urdf_generate.add_argument("--marker-size", dest="marker_size", type=float, default=0.025,
                              help="Marker size in meters (default: 0.025)")
    urdf_generate.add_argument("--output", "-o",
                              help="Output URDF path (default: urdf_generation/mechdog_calibrated.urdf)")
    urdf_generate.add_argument("--ble-address", dest="ble_address",
                              help="BLE address for robot reset (default: auto-detect)")
    urdf_generate.add_argument("--robot-name", dest="robot_name", default="mechdog",
                              help="Robot name in URDF (default: mechdog)")

    # urdf open
    urdf_open = urdf_subparsers.add_parser("open",
        help="Open URDF in Artifex Desktop")
    urdf_open.add_argument("urdf_file", nargs="?",
                          help="URDF file to open (default: last generated)")
    urdf_open.add_argument("--bridge", action="store_true",
                          help="Sync via ATE bridge server instead of direct launch")
    urdf_open.add_argument("--launch", action="store_true",
                          help="Force launch Artifex even if bridge fails")

    # urdf info
    urdf_info = urdf_subparsers.add_parser("info",
        help="Show information about a URDF file")
    urdf_info.add_argument("urdf_file", nargs="?",
                          help="URDF file to inspect (default: last generated)")

    return robot_parser


def handle_robot_command(args):
    """
    Handle robot command dispatch.

    Call this from the main CLI command handler.
    """
    if args.robot_action == "discover":
        robot_discover_command(
            subnet=args.subnet,
            timeout=args.timeout,
            json_output=args.json
        )

    elif args.robot_action == "ble":
        action = getattr(args, "ble_action", None) or "info"
        robot_ble_command(
            action=action,
            timeout=getattr(args, "timeout", 10.0),
            address=getattr(args, "address", None),
            name_filter=getattr(args, "name_filter", None),
            profile_name=getattr(args, "profile_name", None),
            json_output=getattr(args, "json_output", False),
            # New capture/analyze arguments
            platform=getattr(args, "platform", "auto"),
            output=getattr(args, "output", "capture.pklg"),
            capture_file=getattr(args, "capture_file", None),
            generate_code=getattr(args, "generate", False),
        )

    elif args.robot_action == "list":
        robot_list_command(archetype=args.archetype)

    elif args.robot_action == "info":
        robot_info_command(
            robot_type=args.robot_type,
            profile_name=args.profile
        )

    elif args.robot_action == "setup":
        robot_setup_command(
            port=args.port,
            camera_ip=args.camera_ip,
            robot_type=args.robot_type,
            name=args.name,
            non_interactive=args.non_interactive
        )

    elif args.robot_action == "test":
        robot_test_command(
            profile_name=args.profile,
            capability=args.capability,
            verbose=args.verbose
        )

    elif args.robot_action == "approach":
        robot_approach_command(
            profile_name=args.profile,
            duration=args.duration,
            target_distance=args.target_distance,
            speed=args.speed,
            detect_colors=args.detect_colors,
            dry_run=args.dry_run
        )

    elif args.robot_action == "profiles":
        if args.profiles_action == "list":
            robot_profiles_command("list")
        elif args.profiles_action == "show":
            robot_profiles_command("show", name=args.name)
        elif args.profiles_action == "delete":
            robot_profiles_command("delete", name=args.name)
        elif args.profiles_action == "create":
            robot_profiles_command("create", name=args.name, template=getattr(args, "template", None))
        elif args.profiles_action == "templates":
            robot_profiles_command("templates")
        else:
            print("Usage: ate robot profiles <list|show|delete|create|templates>")

    elif args.robot_action == "calibrate":
        action = getattr(args, "calibrate_action", None)
        if action == "start":
            robot_calibrate_command(
                action="start",
                port=args.port,
                camera_url=args.camera_url,
                name=args.name,
                robot_type=args.robot_type,
            )
        elif action == "gripper":
            robot_calibrate_command(
                action="gripper",
                port=args.port,
                servo_id=args.servo,
            )
        elif action == "list":
            robot_calibrate_command(action="list")
        elif action == "poses":
            robot_calibrate_command(action="poses", name=args.name)
        elif action == "record":
            robot_calibrate_command(
                action="record",
                name=args.name,
                pose_name=args.pose,
            )
        elif action == "apply":
            robot_calibrate_command(
                action="apply",
                name=args.name,
                pose_name=args.pose,
            )
        elif action == "direction":
            robot_calibrate_command(
                action="direction",
                port=getattr(args, "port", None),
                name=getattr(args, "name", "robot"),
            )
        elif action == "status":
            robot_calibrate_command(
                action="status",
                name=getattr(args, "name", "robot"),
            )
        elif action == "reset":
            robot_calibrate_command(
                action="reset",
                name=args.name,
            )
        else:
            print("Usage: ate robot calibrate <start|gripper|direction|status|list|poses|record|apply|reset>")

    elif args.robot_action == "label":
        robot_label_command(
            port=args.port,
            name=args.name,
            robot_type=args.robot_type,
            webcam_id=args.webcam_id,
            camera_url=args.camera_url,
        )

    elif args.robot_action == "skills":
        action = getattr(args, "skills_action", None)
        if action == "list":
            robot_skills_command("list")
        elif action == "show":
            robot_skills_command("show", name=args.name)
        elif action == "export":
            robot_skills_command("export", name=args.name, skill_name=getattr(args, "skill", None))
        else:
            print("Usage: ate robot skills <list|show|export>")

    elif args.robot_action == "upload":
        robot_upload_command(
            name=args.name,
            project_id=getattr(args, "project_id", None),
            include_images=not getattr(args, "no_images", False),
        )

    elif args.robot_action == "teach":
        teach_command(
            port=args.port,
            name=args.name,
            robot_type=args.robot_type,
            webcam_id=args.webcam_id,
            camera_url=getattr(args, "camera_url", None),
        )

    elif args.robot_action == "behavior":
        robot_behavior_command(
            profile_name=getattr(args, "profile_name", None),
            behavior=args.behavior,
            camera_ip=getattr(args, "camera_ip", None),
            simulate=getattr(args, "simulate", False),
        )

    elif args.robot_action == "primitives":
        action = getattr(args, "primitives_action", None) or "list"
        name = getattr(args, "name", None)
        robot_primitives_command(action=action, name=name)

    elif args.robot_action == "map-servos":
        robot_map_servos_command(
            port=getattr(args, "port", None),
            num_servos=getattr(args, "num_servos", 13),
            use_camera=getattr(args, "use_camera", False),
            camera_index=getattr(args, "camera_index", 0),
            wifi_camera_ip=getattr(args, "wifi_camera_ip", None),
            output=getattr(args, "output", None),
            save_images=getattr(args, "save_images", False),
            upload=getattr(args, "upload", False),
            project_id=getattr(args, "project_id", None),
        )

    elif args.robot_action == "generate-markers":
        robot_generate_markers_command(
            output=getattr(args, "output", "aruco_markers.pdf"),
            count=getattr(args, "count", 12),
            size=getattr(args, "size", 30.0),
            robot_name=getattr(args, "robot_name", None),
            page_size=getattr(args, "page_size", "letter"),
            preset=getattr(args, "preset", None),
            list_presets=getattr(args, "list_presets", False),
        )

    elif args.robot_action == "identify":
        robot_identify_command(
            robot_slug=getattr(args, "robot_slug", None),
            robot_name=getattr(args, "robot_name", None),
            port=getattr(args, "port", None),
        )

    elif args.robot_action == "upload-calibration":
        robot_upload_calibration_command(
            calibration_file=args.calibration_file,
            robot_slug=getattr(args, "robot_slug", None),
            robot_name=getattr(args, "robot_name", None),
            method=getattr(args, "method", "llm_vision"),
            publish=getattr(args, "publish", False),
        )

    elif args.robot_action == "urdf":
        action = getattr(args, "urdf_action", None)
        if action == "generate":
            robot_urdf_command(
                action="generate",
                reset=getattr(args, "reset", False),
                frames=getattr(args, "frames", 20),
                camera=getattr(args, "camera", 0),
                marker_size=getattr(args, "marker_size", 0.025),
                output=getattr(args, "output", None),
                ble_address=getattr(args, "ble_address", None),
                robot_name=getattr(args, "robot_name", "mechdog"),
            )
        elif action == "open":
            robot_urdf_command(
                action="open",
                urdf_file=getattr(args, "urdf_file", None),
                bridge=getattr(args, "bridge", False),
                launch=getattr(args, "launch", False),
            )
        elif action == "info":
            robot_urdf_command(
                action="info",
                urdf_file=getattr(args, "urdf_file", None),
            )
        else:
            print("Usage: ate robot urdf <generate|open|info>")
            print("\nExamples:")
            print("  ate robot urdf generate              # Generate URDF from markers")
            print("  ate robot urdf generate --reset      # Reset robot pose first")
            print("  ate robot urdf open                  # Open in Artifex Desktop")
            print("  ate robot urdf info                  # Show URDF details")

    else:
        print("Usage: ate robot <discover|ble|list|info|setup|test|approach|profiles|calibrate|label|skills|upload|teach|behavior|primitives|map-servos|generate-markers|identify|upload-calibration|urdf>")
        print("\nRun 'ate robot --help' for more information.")
