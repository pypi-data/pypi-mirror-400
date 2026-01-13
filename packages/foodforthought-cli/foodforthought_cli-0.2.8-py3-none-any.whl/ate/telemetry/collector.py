"""
Telemetry Collector for FoodforThought

Core class for collecting robot telemetry data from simulations and hardware,
with automatic buffering and upload to FoodforThought.
"""

import asyncio
import json
import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

import requests

from .types import (
    TelemetrySource,
    TelemetryBuffer,
    TrajectoryFrame,
    TrajectoryMetadata,
    TrajectoryRecording,
    ExecutionEvent,
    EventType,
    Pose,
    Contact,
)


class TelemetryCollector:
    """
    Collector for robot telemetry data.

    Handles buffering, batching, and uploading telemetry to FoodforThought.
    Supports both synchronous recording and automatic background uploads.

    Example usage:
        collector = TelemetryCollector("robot-123")
        collector.start_recording(skill_id="pick_and_place")

        while executing:
            collector.record_frame(
                joint_positions={"joint1": 0.5, "joint2": 1.2},
                joint_velocities={"joint1": 0.1, "joint2": -0.2},
            )

        recording = collector.stop_recording(success=True)
    """

    def __init__(
        self,
        robot_id: str,
        api_url: str = None,
        api_key: str = None,
        buffer_size: int = 36000,  # 10 minutes at 60Hz
        auto_upload: bool = True,
        upload_interval: float = 60.0,  # Upload every 60 seconds
        project_id: str = None,
    ):
        """
        Initialize the telemetry collector.

        Args:
            robot_id: Unique identifier for the robot
            api_url: FoodforThought API URL (defaults to env var or production)
            api_key: API key for authentication (defaults to env var)
            buffer_size: Maximum number of frames to buffer
            auto_upload: Whether to automatically upload completed recordings
            upload_interval: Interval for background uploads (seconds)
            project_id: Default project ID for artifact creation
        """
        self.robot_id = robot_id
        self.api_url = api_url or os.getenv("FFT_API_URL", "https://kindly.fyi/api")
        self.api_key = api_key or os.getenv("FFT_API_KEY") or os.getenv("ATE_API_KEY")
        self.project_id = project_id or os.getenv("FFT_PROJECT_ID")

        self.buffer = TelemetryBuffer(max_size=buffer_size)
        self.auto_upload = auto_upload
        self.upload_interval = upload_interval

        self._recording = False
        self._current_recording: Optional[TrajectoryRecording] = None
        self._upload_thread: Optional[threading.Thread] = None
        self._stop_upload_thread = threading.Event()

        # Validate API key
        if not self.api_key and auto_upload:
            print("Warning: No API key found. Set FFT_API_KEY or ATE_API_KEY environment variable.",
                  file=sys.stderr)

    def start_recording(
        self,
        skill_id: Optional[str] = None,
        skill_params: Optional[Dict[str, Any]] = None,
        source: str = "hardware",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start a new trajectory recording.

        Args:
            skill_id: ID of the skill being executed (optional)
            skill_params: Parameters passed to the skill
            source: Source of telemetry ('simulation', 'hardware', 'fleet')
            metadata: Additional metadata for the recording

        Returns:
            recording_id: Unique ID for this recording

        Raises:
            RuntimeError: If already recording
        """
        if self._recording:
            raise RuntimeError("Already recording. Call stop_recording() first.")

        recording_id = str(uuid4())

        # Parse source
        try:
            telemetry_source = TelemetrySource(source)
        except ValueError:
            telemetry_source = TelemetrySource.HARDWARE

        # Build metadata
        recording_metadata = TrajectoryMetadata(
            skill_params=skill_params,
        )

        # Merge additional metadata
        if metadata:
            if "environmentId" in metadata:
                recording_metadata.environment_id = metadata["environmentId"]
            if "robotVersion" in metadata:
                recording_metadata.robot_version = metadata["robotVersion"]
            if "urdfHash" in metadata:
                recording_metadata.urdf_hash = metadata["urdfHash"]
            if "tags" in metadata:
                recording_metadata.tags = metadata["tags"]
            if "jointNames" in metadata:
                recording_metadata.joint_names = metadata["jointNames"]

        self._current_recording = TrajectoryRecording(
            id=recording_id,
            robot_id=self.robot_id,
            skill_id=skill_id,
            source=telemetry_source,
            start_time=datetime.utcnow(),
            frames=[],
            events=[],
            metadata=recording_metadata,
        )

        self._recording = True
        self.buffer.clear()  # Clear any previous data

        # Log start event
        self.log_event(EventType.SKILL_START, {
            "skillId": skill_id,
            "skillParams": skill_params,
        })

        return recording_id

    def record_frame(
        self,
        joint_positions: Dict[str, float],
        joint_velocities: Optional[Dict[str, float]] = None,
        joint_torques: Optional[Dict[str, float]] = None,
        joint_accelerations: Optional[Dict[str, float]] = None,
        end_effector_pose: Optional[Pose] = None,
        contacts: Optional[List[Contact]] = None,
        sensor_readings: Optional[Dict[str, float]] = None,
        control_inputs: Optional[Dict[str, float]] = None,
        timestamp: Optional[float] = None,
    ) -> None:
        """
        Record a single frame of trajectory data.

        Args:
            joint_positions: Joint name -> position (radians or meters)
            joint_velocities: Joint name -> velocity
            joint_torques: Joint name -> torque
            joint_accelerations: Joint name -> acceleration
            end_effector_pose: Pose of the end effector
            contacts: List of contacts detected this frame
            sensor_readings: Sensor name -> value
            control_inputs: Control signal name -> value
            timestamp: Override timestamp (defaults to time since recording start)

        Raises:
            RuntimeError: If not currently recording
        """
        if not self._recording or not self._current_recording:
            raise RuntimeError("Not recording. Call start_recording() first.")

        # Calculate timestamp from recording start
        if timestamp is None:
            elapsed = (datetime.utcnow() - self._current_recording.start_time).total_seconds()
        else:
            elapsed = timestamp

        # Auto-detect joint names on first frame
        if not self._current_recording.metadata.joint_names:
            self._current_recording.metadata.joint_names = list(joint_positions.keys())

        frame = TrajectoryFrame(
            timestamp=elapsed,
            joint_positions=joint_positions,
            joint_velocities=joint_velocities or {},
            joint_torques=joint_torques or {},
            joint_accelerations=joint_accelerations or {},
            end_effector_pose=end_effector_pose,
            contacts=contacts or [],
            sensor_readings=sensor_readings or {},
            control_inputs=control_inputs or {},
        )

        self._current_recording.frames.append(frame)
        self.buffer.add(frame)

    def log_event(
        self,
        event_type: EventType,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an execution event.

        Args:
            event_type: Type of event (EventType enum or string)
            data: Additional event data
        """
        if not self._recording or not self._current_recording:
            # Allow logging events even when not recording for debugging
            return

        # Calculate timestamp
        elapsed = (datetime.utcnow() - self._current_recording.start_time).total_seconds()

        # Parse event type
        if isinstance(event_type, str):
            try:
                event_type = EventType(event_type)
            except ValueError:
                pass  # Keep as string if not in enum

        event = ExecutionEvent(
            timestamp=elapsed,
            event_type=event_type,
            data=data or {},
        )

        self._current_recording.events.append(event)
        self.buffer.add_event(event)

    def stop_recording(self, success: bool = True) -> TrajectoryRecording:
        """
        Stop recording and finalize the trajectory.

        Args:
            success: Whether the execution was successful

        Returns:
            The completed TrajectoryRecording

        Raises:
            RuntimeError: If not currently recording
        """
        if not self._recording or not self._current_recording:
            raise RuntimeError("Not recording.")

        # Finalize recording
        self._current_recording.end_time = datetime.utcnow()
        self._current_recording.success = success

        # Calculate metadata
        duration = (
            self._current_recording.end_time - self._current_recording.start_time
        ).total_seconds()

        self._current_recording.metadata.duration = duration
        self._current_recording.metadata.total_frames = len(self._current_recording.frames)

        if duration > 0 and self._current_recording.metadata.total_frames > 0:
            self._current_recording.metadata.frame_rate = (
                self._current_recording.metadata.total_frames / duration
            )

        # Log end event
        self.log_event(EventType.SKILL_END, {
            "success": success,
            "duration": duration,
            "frameCount": self._current_recording.metadata.total_frames,
        })

        recording = self._current_recording
        self._current_recording = None
        self._recording = False

        # Upload if auto_upload is enabled
        if self.auto_upload and self.api_key:
            self._upload_recording_sync(recording)

        return recording

    def _upload_recording_sync(self, recording: TrajectoryRecording) -> Optional[Dict]:
        """Synchronously upload a recording to FoodforThought."""
        try:
            # Serialize to JSON for upload
            data = self._serialize_recording(recording)

            headers = {
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # Upload telemetry data
            response = requests.post(
                f"{self.api_url}/telemetry/ingest",
                headers=headers,
                json={
                    "recording": data,
                    "projectId": self.project_id,
                    "robotId": recording.robot_id,
                    "skillId": recording.skill_id,
                },
                timeout=30,
            )
            response.raise_for_status()

            result = response.json()
            print(f"Uploaded recording {recording.id}: {result.get('artifactId', 'unknown')}")
            return result

        except requests.exceptions.RequestException as e:
            print(f"Failed to upload recording: {e}", file=sys.stderr)
            return None

    def _serialize_recording(self, recording: TrajectoryRecording) -> Dict[str, Any]:
        """Serialize recording to JSON-compatible dict."""
        return {
            "id": recording.id,
            "robotId": recording.robot_id,
            "skillId": recording.skill_id,
            "source": recording.source.value if isinstance(recording.source, TelemetrySource) else recording.source,
            "startTime": recording.start_time.isoformat() if recording.start_time else None,
            "endTime": recording.end_time.isoformat() if recording.end_time else None,
            "success": recording.success,
            "metadata": recording.metadata.to_dict(),
            "frames": [f.to_dict() for f in recording.frames],
            "events": [e.to_dict() for e in recording.events],
        }

    def export_to_json(self, recording: TrajectoryRecording) -> str:
        """Export recording to JSON string."""
        return json.dumps(self._serialize_recording(recording), indent=2)

    def export_to_file(self, recording: TrajectoryRecording, filepath: str, format: str = "json") -> None:
        """
        Export recording to file.

        Args:
            recording: The recording to export
            filepath: Output file path
            format: Export format ('json', 'mcap', 'hdf5')
        """
        if format == "json":
            with open(filepath, "w") as f:
                f.write(self.export_to_json(recording))
        elif format == "mcap":
            from .formats.mcap_serializer import serialize_to_mcap
            data = serialize_to_mcap(recording)
            with open(filepath, "wb") as f:
                f.write(data)
        elif format == "hdf5":
            from .formats.hdf5_serializer import serialize_to_hdf5
            data = serialize_to_hdf5(recording)
            with open(filepath, "wb") as f:
                f.write(data)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"Exported recording to {filepath}")

    @property
    def is_recording(self) -> bool:
        """Whether currently recording."""
        return self._recording

    @property
    def current_recording_id(self) -> Optional[str]:
        """ID of current recording, if any."""
        return self._current_recording.id if self._current_recording else None

    @property
    def frame_count(self) -> int:
        """Number of frames in current recording."""
        return len(self._current_recording.frames) if self._current_recording else 0

    def start_background_upload(self) -> None:
        """Start background thread for periodic uploads."""
        if self._upload_thread and self._upload_thread.is_alive():
            return

        self._stop_upload_thread.clear()
        self._upload_thread = threading.Thread(target=self._upload_loop, daemon=True)
        self._upload_thread.start()

    def stop_background_upload(self) -> None:
        """Stop background upload thread."""
        self._stop_upload_thread.set()
        if self._upload_thread:
            self._upload_thread.join(timeout=5)

    def _upload_loop(self) -> None:
        """Background upload loop."""
        while not self._stop_upload_thread.is_set():
            # Wait for interval or stop signal
            self._stop_upload_thread.wait(timeout=self.upload_interval)

            if self._stop_upload_thread.is_set():
                break

            # Upload buffered data if not currently recording
            # (during recording, data is uploaded on stop_recording)
            if not self._recording and not self.buffer.is_empty():
                frames, events = self.buffer.flush()
                if frames:
                    # Create a partial recording for upload
                    partial_recording = TrajectoryRecording(
                        id=str(uuid4()),
                        robot_id=self.robot_id,
                        source=TelemetrySource.FLEET,
                        start_time=datetime.utcnow(),
                        end_time=datetime.utcnow(),
                        success=True,
                        frames=frames,
                        events=events,
                    )
                    self._upload_recording_sync(partial_recording)
