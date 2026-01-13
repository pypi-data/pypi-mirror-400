"""
Context Manager for Telemetry Recording

Provides a convenient context manager API for trajectory recording.
"""

from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Generator

from .collector import TelemetryCollector
from .types import (
    TrajectoryRecording,
    Pose,
    Contact,
    EventType,
)


class RecordingContext:
    """
    Context object yielded by record_trajectory context manager.

    Provides methods for recording frames and events during execution.
    """

    def __init__(self, collector: TelemetryCollector):
        self._collector = collector
        self.success = True
        self._error: Optional[Exception] = None

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
        """
        self._collector.record_frame(
            joint_positions=joint_positions,
            joint_velocities=joint_velocities,
            joint_torques=joint_torques,
            joint_accelerations=joint_accelerations,
            end_effector_pose=end_effector_pose,
            contacts=contacts,
            sensor_readings=sensor_readings,
            control_inputs=control_inputs,
            timestamp=timestamp,
        )

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
        self._collector.log_event(event_type, data)

    def log_contact(self, force: float, body1: str = "gripper", body2: str = "object") -> None:
        """Convenience method to log a contact event."""
        self.log_event(EventType.CONTACT, {
            "force": force,
            "body1": body1,
            "body2": body2,
        })

    def log_grasp(self, force: float, object_id: Optional[str] = None) -> None:
        """Convenience method to log a grasp event."""
        self.log_event(EventType.GRASP, {
            "force": force,
            "objectId": object_id,
        })

    def log_release(self, object_id: Optional[str] = None) -> None:
        """Convenience method to log a release event."""
        self.log_event(EventType.RELEASE, {
            "objectId": object_id,
        })

    def log_waypoint(self, waypoint_id: str, pose: Optional[Pose] = None) -> None:
        """Convenience method to log a waypoint reached event."""
        data = {"waypointId": waypoint_id}
        if pose:
            data["pose"] = pose.to_dict()
        self.log_event(EventType.WAYPOINT_REACHED, data)

    def log_error(self, error: str, recoverable: bool = True) -> None:
        """Convenience method to log an error event."""
        self.log_event(EventType.ERROR, {
            "error": error,
            "recoverable": recoverable,
        })
        if not recoverable:
            self.success = False

    def log_recovery(self, action: str) -> None:
        """Convenience method to log a recovery event."""
        self.log_event(EventType.RECOVERY, {
            "action": action,
        })

    @property
    def recording_id(self) -> Optional[str]:
        """Get the current recording ID."""
        return self._collector.current_recording_id

    @property
    def frame_count(self) -> int:
        """Get the current frame count."""
        return self._collector.frame_count


@contextmanager
def record_trajectory(
    robot_id: str,
    skill_id: Optional[str] = None,
    skill_params: Optional[Dict[str, Any]] = None,
    source: str = "hardware",
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    auto_upload: bool = True,
    project_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Generator[RecordingContext, None, None]:
    """
    Context manager for trajectory recording.

    Automatically handles recording lifecycle, including starting, stopping,
    and uploading telemetry data.

    Usage:
        from ate.telemetry import record_trajectory

        with record_trajectory("my_robot", skill_id="pick_and_place") as recorder:
            while executing:
                recorder.record_frame(
                    joint_positions=get_joint_positions(),
                    end_effector_pose=get_ee_pose(),
                )

            # Set success based on execution result
            recorder.success = True

    Args:
        robot_id: Unique identifier for the robot
        skill_id: ID of the skill being executed (optional)
        skill_params: Parameters passed to the skill
        source: Source of telemetry ('simulation', 'hardware', 'fleet')
        api_url: FoodforThought API URL (defaults to env var)
        api_key: API key for authentication (defaults to env var)
        auto_upload: Whether to automatically upload completed recordings
        project_id: Default project ID for artifact creation
        metadata: Additional metadata for the recording

    Yields:
        RecordingContext: Context object for recording frames and events
    """
    collector = TelemetryCollector(
        robot_id=robot_id,
        api_url=api_url,
        api_key=api_key,
        auto_upload=auto_upload,
        project_id=project_id,
    )

    collector.start_recording(
        skill_id=skill_id,
        skill_params=skill_params,
        source=source,
        metadata=metadata,
    )

    ctx = RecordingContext(collector)

    try:
        yield ctx
    except Exception as e:
        ctx.success = False
        ctx._error = e
        collector.log_event(EventType.ERROR, {
            "error": str(e),
            "type": type(e).__name__,
            "recoverable": False,
        })
        raise
    finally:
        collector.stop_recording(ctx.success)


# Convenience functions for common recording patterns

def record_skill_execution(
    robot_id: str,
    skill_id: str,
    execute_fn,
    skill_params: Optional[Dict[str, Any]] = None,
    source: str = "hardware",
    frame_rate: float = 50.0,
    get_joint_positions=None,
    get_joint_velocities=None,
    get_joint_torques=None,
    get_ee_pose=None,
    **kwargs,
) -> TrajectoryRecording:
    """
    Record a skill execution with automatic frame capture.

    This is a higher-level function that wraps the context manager
    and handles frame recording automatically at a specified rate.

    Usage:
        def my_skill(robot, params):
            robot.move_to(params["target"])
            robot.grasp()
            return True

        recording = record_skill_execution(
            robot_id="robot-123",
            skill_id="grasp_object",
            execute_fn=lambda: my_skill(robot, {"target": [0.5, 0.3, 0.1]}),
            skill_params={"target": [0.5, 0.3, 0.1]},
            get_joint_positions=robot.get_joint_positions,
        )

    Args:
        robot_id: Unique identifier for the robot
        skill_id: ID of the skill being executed
        execute_fn: Function to execute (returns bool for success)
        skill_params: Parameters passed to the skill
        source: Source of telemetry
        frame_rate: Rate at which to record frames (Hz)
        get_joint_positions: Function to get joint positions
        get_joint_velocities: Function to get joint velocities
        get_joint_torques: Function to get joint torques
        get_ee_pose: Function to get end effector pose
        **kwargs: Additional arguments passed to record_trajectory

    Returns:
        The completed TrajectoryRecording
    """
    import threading
    import time

    recording_thread_stop = threading.Event()
    recording_exception = None

    collector = TelemetryCollector(robot_id=robot_id, **kwargs)
    collector.start_recording(skill_id=skill_id, skill_params=skill_params, source=source)

    def recording_loop():
        nonlocal recording_exception
        interval = 1.0 / frame_rate
        try:
            while not recording_thread_stop.is_set():
                # Get current state
                joint_positions = get_joint_positions() if get_joint_positions else {}
                joint_velocities = get_joint_velocities() if get_joint_velocities else None
                joint_torques = get_joint_torques() if get_joint_torques else None
                ee_pose = get_ee_pose() if get_ee_pose else None

                collector.record_frame(
                    joint_positions=joint_positions,
                    joint_velocities=joint_velocities,
                    joint_torques=joint_torques,
                    end_effector_pose=ee_pose,
                )

                time.sleep(interval)
        except Exception as e:
            recording_exception = e

    # Start recording thread
    record_thread = threading.Thread(target=recording_loop, daemon=True)
    record_thread.start()

    try:
        # Execute the skill
        success = execute_fn()
    except Exception as e:
        success = False
        collector.log_event(EventType.ERROR, {"error": str(e)})
        raise
    finally:
        # Stop recording thread
        recording_thread_stop.set()
        record_thread.join(timeout=1.0)

        # Stop recording
        recording = collector.stop_recording(success=success)

    if recording_exception:
        raise recording_exception

    return recording
