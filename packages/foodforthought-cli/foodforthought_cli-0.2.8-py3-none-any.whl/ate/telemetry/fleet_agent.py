"""
Fleet Telemetry Agent

Background agent for continuous telemetry collection from deployed fleet robots.
Runs on each robot to collect and periodically upload telemetry to FoodforThought.

Usage:
    agent = FleetTelemetryAgent(
        robot_id="robot-001",
        api_key="fft_xxx",
    )
    await agent.start()
"""

import asyncio
import os
import sys
import signal
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any
from uuid import uuid4

from .collector import TelemetryCollector
from .types import (
    TrajectoryRecording,
    TrajectoryFrame,
    TrajectoryMetadata,
    TelemetrySource,
    TelemetryBuffer,
    ExecutionEvent,
    EventType,
)


class FleetTelemetryAgent:
    """
    Background agent for fleet robot telemetry collection.

    Runs continuously on a deployed robot, collecting state data and
    periodically uploading to FoodforThought for analysis and training.

    Features:
    - Configurable collection frequency
    - Automatic batching and upload
    - Graceful shutdown handling
    - State provider callback for robot-specific integration
    """

    def __init__(
        self,
        robot_id: str,
        api_url: str = None,
        api_key: str = None,
        collection_interval: float = 0.02,  # 50Hz
        upload_interval: float = 60.0,  # Upload every minute
        buffer_size: int = 3600,  # 1 minute at 50Hz
        project_id: str = None,
        state_provider: Callable[[], Dict[str, float]] = None,
        velocity_provider: Callable[[], Dict[str, float]] = None,
        torque_provider: Callable[[], Dict[str, float]] = None,
    ):
        """
        Initialize the fleet telemetry agent.

        Args:
            robot_id: Unique identifier for this robot
            api_url: FoodforThought API URL
            api_key: API key for authentication
            collection_interval: Time between state samples (seconds)
            upload_interval: Time between uploads (seconds)
            buffer_size: Maximum frames to buffer
            project_id: FFT project ID for artifacts
            state_provider: Callback returning joint positions dict
            velocity_provider: Callback returning joint velocities dict
            torque_provider: Callback returning joint torques dict
        """
        self.robot_id = robot_id
        self.api_url = api_url or os.getenv("FFT_API_URL", "https://kindly.fyi/api")
        self.api_key = api_key or os.getenv("FFT_API_KEY") or os.getenv("ATE_API_KEY")
        self.project_id = project_id or os.getenv("FFT_PROJECT_ID")

        self.collection_interval = collection_interval
        self.upload_interval = upload_interval
        self.buffer_size = buffer_size

        self.state_provider = state_provider
        self.velocity_provider = velocity_provider
        self.torque_provider = torque_provider

        self.collector = TelemetryCollector(
            robot_id=robot_id,
            api_url=self.api_url,
            api_key=self.api_key,
            buffer_size=buffer_size,
            auto_upload=False,  # We handle uploads manually
            project_id=project_id,
        )

        self._running = False
        self._buffer = TelemetryBuffer(max_size=buffer_size)
        self._start_time: Optional[datetime] = None
        self._frame_count = 0
        self._upload_count = 0
        self._last_upload_time: Optional[float] = None

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n[FleetAgent] Received signal {signum}, shutting down...")
        self.stop()

    async def start(self) -> None:
        """Start the telemetry agent."""
        if self._running:
            print("[FleetAgent] Already running")
            return

        if not self.api_key:
            print("[FleetAgent] Warning: No API key configured, telemetry will not be uploaded",
                  file=sys.stderr)

        self._running = True
        self._start_time = datetime.utcnow()
        self._frame_count = 0
        self._upload_count = 0

        print(f"[FleetAgent] Starting telemetry collection for robot {self.robot_id}")
        print(f"[FleetAgent] Collection interval: {self.collection_interval}s ({1/self.collection_interval:.1f}Hz)")
        print(f"[FleetAgent] Upload interval: {self.upload_interval}s")

        # Start collection and upload tasks
        await asyncio.gather(
            self._collection_loop(),
            self._upload_loop(),
        )

    def stop(self) -> None:
        """Stop the telemetry agent."""
        self._running = False

        # Upload any remaining data
        if not self._buffer.is_empty():
            print(f"[FleetAgent] Uploading final {self._buffer.frame_count} frames...")
            asyncio.create_task(self._upload_buffer())

        print(f"[FleetAgent] Stopped. Collected {self._frame_count} frames, {self._upload_count} uploads.")

    async def _collection_loop(self) -> None:
        """Main collection loop - samples state at configured frequency."""
        while self._running:
            try:
                # Get current state from providers
                state = await self._get_robot_state()

                if state:
                    self._buffer.add(state)
                    self._frame_count += 1

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                print(f"[FleetAgent] Collection error: {e}", file=sys.stderr)
                await asyncio.sleep(1.0)  # Back off on error

    async def _upload_loop(self) -> None:
        """Upload loop - periodically uploads buffered data."""
        while self._running:
            await asyncio.sleep(self.upload_interval)

            if not self._buffer.is_empty():
                await self._upload_buffer()

    async def _get_robot_state(self) -> Optional[TrajectoryFrame]:
        """Get current robot state from providers."""
        try:
            joint_positions = {}
            joint_velocities = {}
            joint_torques = {}

            if self.state_provider:
                result = self.state_provider()
                if asyncio.iscoroutine(result):
                    joint_positions = await result
                else:
                    joint_positions = result

            if self.velocity_provider:
                result = self.velocity_provider()
                if asyncio.iscoroutine(result):
                    joint_velocities = await result
                else:
                    joint_velocities = result

            if self.torque_provider:
                result = self.torque_provider()
                if asyncio.iscoroutine(result):
                    joint_torques = await result
                else:
                    joint_torques = result

            # Calculate timestamp from start
            elapsed = (datetime.utcnow() - self._start_time).total_seconds()

            return TrajectoryFrame(
                timestamp=elapsed,
                joint_positions=joint_positions,
                joint_velocities=joint_velocities,
                joint_torques=joint_torques,
            )

        except Exception as e:
            print(f"[FleetAgent] State provider error: {e}", file=sys.stderr)
            return None

    async def _upload_buffer(self) -> None:
        """Upload buffered frames to FoodforThought."""
        if self._buffer.is_empty():
            return

        frames, events = self._buffer.flush()

        # Create recording from buffered frames
        recording_id = str(uuid4())
        now = datetime.utcnow()

        recording = TrajectoryRecording(
            id=recording_id,
            robot_id=self.robot_id,
            source=TelemetrySource.FLEET,
            start_time=now,
            end_time=now,
            success=True,
            frames=frames,
            events=events,
            metadata=TrajectoryMetadata(
                duration=self.upload_interval,
                total_frames=len(frames),
                frame_rate=len(frames) / self.upload_interval if self.upload_interval > 0 else 0,
                tags=["fleet", "continuous"],
            ),
        )

        # Upload using collector
        result = self.collector._upload_recording_sync(recording)

        if result:
            self._upload_count += 1
            self._last_upload_time = time.time()
            print(f"[FleetAgent] Uploaded {len(frames)} frames (total: {self._upload_count})")

    def log_event(self, event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
        """Log an execution event."""
        elapsed = (datetime.utcnow() - self._start_time).total_seconds() if self._start_time else 0

        event = ExecutionEvent(
            timestamp=elapsed,
            event_type=event_type,
            data=data or {},
        )
        self._buffer.add_event(event)

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = 0
        if self._start_time:
            uptime = (datetime.utcnow() - self._start_time).total_seconds()

        return {
            "running": self._running,
            "robot_id": self.robot_id,
            "uptime": uptime,
            "frame_count": self._frame_count,
            "upload_count": self._upload_count,
            "buffer_size": self._buffer.frame_count,
            "last_upload": self._last_upload_time,
            "collection_hz": 1 / self.collection_interval if self.collection_interval > 0 else 0,
        }


# ============================================================================
# ROS2 Integration
# ============================================================================

class ROS2TelemetryAgent(FleetTelemetryAgent):
    """
    Fleet telemetry agent with ROS2 integration.

    Subscribes to joint_states topic for automatic state collection.
    """

    def __init__(
        self,
        robot_id: str,
        joint_states_topic: str = "/joint_states",
        **kwargs,
    ):
        """
        Initialize ROS2 telemetry agent.

        Args:
            robot_id: Unique identifier for this robot
            joint_states_topic: ROS2 topic for joint states
            **kwargs: Additional arguments passed to FleetTelemetryAgent
        """
        super().__init__(robot_id, **kwargs)
        self.joint_states_topic = joint_states_topic
        self._latest_state: Dict[str, float] = {}
        self._latest_velocity: Dict[str, float] = {}
        self._latest_effort: Dict[str, float] = {}

        # Set providers to use ROS2 state
        self.state_provider = self._get_ros2_positions
        self.velocity_provider = self._get_ros2_velocities
        self.torque_provider = self._get_ros2_efforts

    def _get_ros2_positions(self) -> Dict[str, float]:
        """Get positions from ROS2 joint_states."""
        return self._latest_state.copy()

    def _get_ros2_velocities(self) -> Dict[str, float]:
        """Get velocities from ROS2 joint_states."""
        return self._latest_velocity.copy()

    def _get_ros2_efforts(self) -> Dict[str, float]:
        """Get efforts from ROS2 joint_states."""
        return self._latest_effort.copy()

    def update_joint_states(
        self,
        names: List[str],
        positions: List[float],
        velocities: Optional[List[float]] = None,
        efforts: Optional[List[float]] = None,
    ) -> None:
        """
        Update joint states from ROS2 callback.

        Call this from your ROS2 joint_states subscriber callback.

        Args:
            names: Joint names
            positions: Joint positions (radians)
            velocities: Joint velocities (rad/s)
            efforts: Joint efforts (Nm)
        """
        for i, name in enumerate(names):
            if i < len(positions):
                self._latest_state[name] = positions[i]
            if velocities and i < len(velocities):
                self._latest_velocity[name] = velocities[i]
            if efforts and i < len(efforts):
                self._latest_effort[name] = efforts[i]


# ============================================================================
# Standalone Runner
# ============================================================================

async def run_fleet_agent(
    robot_id: str,
    api_key: str = None,
    collection_hz: float = 50.0,
    upload_interval: float = 60.0,
    daemon: bool = False,
) -> None:
    """
    Run the fleet telemetry agent.

    This is a convenience function for running the agent from the command line.

    Args:
        robot_id: Unique identifier for this robot
        api_key: FoodforThought API key
        collection_hz: Collection frequency in Hz
        upload_interval: Upload interval in seconds
        daemon: Run as daemon (detach from terminal)
    """
    if daemon:
        # Daemonize the process
        import os
        pid = os.fork()
        if pid > 0:
            print(f"[FleetAgent] Started as daemon (PID: {pid})")
            sys.exit(0)
        os.setsid()

    agent = FleetTelemetryAgent(
        robot_id=robot_id,
        api_key=api_key,
        collection_interval=1.0 / collection_hz,
        upload_interval=upload_interval,
    )

    await agent.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fleet Telemetry Agent")
    parser.add_argument("robot_id", help="Unique robot identifier")
    parser.add_argument("--api-key", help="FoodforThought API key")
    parser.add_argument("--collection-hz", type=float, default=50.0, help="Collection frequency")
    parser.add_argument("--upload-interval", type=float, default=60.0, help="Upload interval")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    asyncio.run(run_fleet_agent(
        robot_id=args.robot_id,
        api_key=args.api_key,
        collection_hz=args.collection_hz,
        upload_interval=args.upload_interval,
        daemon=args.daemon,
    ))
