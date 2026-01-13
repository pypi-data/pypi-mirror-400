"""
HDF5 Serializer for Telemetry Data

Serializes trajectory recordings to HDF5 format, which is optimized
for machine learning training pipelines. Stores data as NumPy arrays
for efficient loading and processing.

Requires: h5py, numpy
"""

import io
import json
from typing import Dict, Any, List, Optional

from ..types import TrajectoryRecording, TrajectoryFrame, TrajectoryMetadata, TelemetrySource


def _check_dependencies():
    """Check if required dependencies are available."""
    try:
        import h5py
        import numpy as np
        return True
    except ImportError:
        return False


def serialize_to_hdf5(recording: TrajectoryRecording) -> bytes:
    """
    Serialize trajectory recording to HDF5 format.

    Creates an HDF5 file with:
    - /timestamps: Time array (N,)
    - /joint_positions: Position array (N, num_joints)
    - /joint_velocities: Velocity array (N, num_joints)
    - /joint_torques: Torque array (N, num_joints)
    - /joint_names: Joint name strings
    - /end_effector_poses: EE poses (N, 7) [x,y,z,qx,qy,qz,qw] (if available)
    - /events/*: Event data groups
    - Metadata stored as attributes on root group

    Args:
        recording: The trajectory recording to serialize

    Returns:
        HDF5 file as bytes

    Raises:
        ImportError: If h5py or numpy is not installed
    """
    try:
        import h5py
        import numpy as np
    except ImportError:
        raise ImportError(
            "HDF5 serialization requires h5py and numpy. "
            "Install with: pip install h5py numpy"
        )

    buffer = io.BytesIO()

    with h5py.File(buffer, "w") as f:
        # Store metadata as root attributes
        f.attrs["recording_id"] = recording.id
        f.attrs["robot_id"] = recording.robot_id
        f.attrs["skill_id"] = recording.skill_id or ""
        f.attrs["source"] = recording.source.value if isinstance(recording.source, TelemetrySource) else str(recording.source)
        f.attrs["success"] = recording.success
        f.attrs["duration"] = recording.metadata.duration
        f.attrs["frame_rate"] = recording.metadata.frame_rate
        f.attrs["total_frames"] = recording.metadata.total_frames

        if recording.start_time:
            f.attrs["start_time"] = recording.start_time.isoformat()
        if recording.end_time:
            f.attrs["end_time"] = recording.end_time.isoformat()

        if recording.metadata.skill_params:
            f.attrs["skill_params"] = json.dumps(recording.metadata.skill_params)
        if recording.metadata.tags:
            f.attrs["tags"] = json.dumps(recording.metadata.tags)

        if not recording.frames:
            # Empty recording
            return buffer.getvalue()

        # Get joint names from first frame
        joint_names = list(recording.frames[0].joint_positions.keys())
        n_joints = len(joint_names)
        n_frames = len(recording.frames)

        # Store joint names
        dt = h5py.special_dtype(vlen=str)
        joint_names_ds = f.create_dataset("joint_names", (n_joints,), dtype=dt)
        for i, name in enumerate(joint_names):
            joint_names_ds[i] = name

        # Create arrays
        timestamps = np.zeros(n_frames, dtype=np.float64)
        positions = np.zeros((n_frames, n_joints), dtype=np.float64)
        velocities = np.zeros((n_frames, n_joints), dtype=np.float64)
        torques = np.zeros((n_frames, n_joints), dtype=np.float64)
        accelerations = np.zeros((n_frames, n_joints), dtype=np.float64)

        # Check if we have end effector poses
        has_ee_poses = recording.frames[0].end_effector_pose is not None
        if has_ee_poses:
            ee_poses = np.zeros((n_frames, 7), dtype=np.float64)  # x,y,z,qx,qy,qz,qw

        # Check if we have control inputs
        ctrl_names = list(recording.frames[0].control_inputs.keys()) if recording.frames[0].control_inputs else []
        if ctrl_names:
            n_ctrl = len(ctrl_names)
            control_inputs = np.zeros((n_frames, n_ctrl), dtype=np.float64)
            ctrl_names_ds = f.create_dataset("control_names", (n_ctrl,), dtype=dt)
            for i, name in enumerate(ctrl_names):
                ctrl_names_ds[i] = name

        # Fill arrays
        for i, frame in enumerate(recording.frames):
            timestamps[i] = frame.timestamp

            for j, name in enumerate(joint_names):
                positions[i, j] = frame.joint_positions.get(name, 0.0)
                velocities[i, j] = frame.joint_velocities.get(name, 0.0)
                torques[i, j] = frame.joint_torques.get(name, 0.0)
                accelerations[i, j] = frame.joint_accelerations.get(name, 0.0)

            if has_ee_poses and frame.end_effector_pose:
                pose = frame.end_effector_pose
                ee_poses[i] = [
                    pose.position.x, pose.position.y, pose.position.z,
                    pose.orientation.x, pose.orientation.y,
                    pose.orientation.z, pose.orientation.w,
                ]

            if ctrl_names:
                for j, name in enumerate(ctrl_names):
                    control_inputs[i, j] = frame.control_inputs.get(name, 0.0)

        # Store datasets with compression
        f.create_dataset("timestamps", data=timestamps, compression="gzip", compression_opts=4)
        f.create_dataset("joint_positions", data=positions, compression="gzip", compression_opts=4)
        f.create_dataset("joint_velocities", data=velocities, compression="gzip", compression_opts=4)
        f.create_dataset("joint_torques", data=torques, compression="gzip", compression_opts=4)
        f.create_dataset("joint_accelerations", data=accelerations, compression="gzip", compression_opts=4)

        if has_ee_poses:
            f.create_dataset("end_effector_poses", data=ee_poses, compression="gzip", compression_opts=4)

        if ctrl_names:
            f.create_dataset("control_inputs", data=control_inputs, compression="gzip", compression_opts=4)

        # Store events
        if recording.events:
            events_grp = f.create_group("events")
            events_grp.attrs["count"] = len(recording.events)

            event_timestamps = np.zeros(len(recording.events), dtype=np.float64)
            event_types = []
            event_data = []

            for i, event in enumerate(recording.events):
                event_timestamps[i] = event.timestamp
                event_type = event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)
                event_types.append(event_type)
                event_data.append(json.dumps(event.data))

            events_grp.create_dataset("timestamps", data=event_timestamps)

            event_types_ds = events_grp.create_dataset("types", (len(event_types),), dtype=dt)
            for i, et in enumerate(event_types):
                event_types_ds[i] = et

            event_data_ds = events_grp.create_dataset("data", (len(event_data),), dtype=dt)
            for i, ed in enumerate(event_data):
                event_data_ds[i] = ed

        # Store contacts (if any frame has contacts)
        has_contacts = any(frame.contacts for frame in recording.frames)
        if has_contacts:
            contacts_grp = f.create_group("contacts")

            # Store as variable-length data per frame
            contact_counts = np.zeros(n_frames, dtype=np.int32)
            all_contact_data = []

            for i, frame in enumerate(recording.frames):
                contact_counts[i] = len(frame.contacts)
                for contact in frame.contacts:
                    all_contact_data.append({
                        "frame": i,
                        "body1": contact.body1,
                        "body2": contact.body2,
                        "force": contact.force,
                        "position": contact.position.to_list(),
                        "normal": contact.normal.to_list(),
                    })

            contacts_grp.create_dataset("counts_per_frame", data=contact_counts)
            if all_contact_data:
                contact_json_ds = contacts_grp.create_dataset(
                    "data", (len(all_contact_data),), dtype=dt
                )
                for i, cd in enumerate(all_contact_data):
                    contact_json_ds[i] = json.dumps(cd)

    return buffer.getvalue()


def deserialize_from_hdf5(data: bytes) -> TrajectoryRecording:
    """
    Deserialize HDF5 data to TrajectoryRecording.

    Args:
        data: HDF5 file as bytes

    Returns:
        Parsed TrajectoryRecording

    Raises:
        ImportError: If h5py or numpy is not installed
    """
    try:
        import h5py
        import numpy as np
    except ImportError:
        raise ImportError(
            "HDF5 deserialization requires h5py and numpy. "
            "Install with: pip install h5py numpy"
        )

    from ..types import (
        TrajectoryRecording,
        TrajectoryFrame,
        TrajectoryMetadata,
        ExecutionEvent,
        EventType,
        TelemetrySource,
        Pose,
        Vector3,
        Quaternion,
        Contact,
    )

    buffer = io.BytesIO(data)

    frames: List[TrajectoryFrame] = []
    events: List[ExecutionEvent] = []

    with h5py.File(buffer, "r") as f:
        # Read metadata
        recording_id = f.attrs.get("recording_id", "")
        robot_id = f.attrs.get("robot_id", "")
        skill_id = f.attrs.get("skill_id", "") or None
        source_str = f.attrs.get("source", "hardware")
        success = bool(f.attrs.get("success", True))
        duration = float(f.attrs.get("duration", 0))
        frame_rate = float(f.attrs.get("frame_rate", 0))
        total_frames = int(f.attrs.get("total_frames", 0))

        try:
            source = TelemetrySource(source_str)
        except ValueError:
            source = TelemetrySource.HARDWARE

        skill_params = None
        if "skill_params" in f.attrs:
            try:
                skill_params = json.loads(f.attrs["skill_params"])
            except json.JSONDecodeError:
                pass

        tags = []
        if "tags" in f.attrs:
            try:
                tags = json.loads(f.attrs["tags"])
            except json.JSONDecodeError:
                pass

        # Read joint names
        joint_names = []
        if "joint_names" in f:
            joint_names = [name.decode("utf-8") if isinstance(name, bytes) else name
                         for name in f["joint_names"][:]]

        # Read control names
        ctrl_names = []
        if "control_names" in f:
            ctrl_names = [name.decode("utf-8") if isinstance(name, bytes) else name
                        for name in f["control_names"][:]]

        # Read data arrays
        timestamps = f["timestamps"][:] if "timestamps" in f else []
        positions = f["joint_positions"][:] if "joint_positions" in f else []
        velocities = f["joint_velocities"][:] if "joint_velocities" in f else []
        torques = f["joint_torques"][:] if "joint_torques" in f else []
        accelerations = f["joint_accelerations"][:] if "joint_accelerations" in f else []

        ee_poses = f["end_effector_poses"][:] if "end_effector_poses" in f else None
        control_inputs = f["control_inputs"][:] if "control_inputs" in f else None

        # Read contacts
        contacts_by_frame = {}
        if "contacts" in f:
            contacts_grp = f["contacts"]
            if "data" in contacts_grp:
                for contact_json in contacts_grp["data"][:]:
                    if isinstance(contact_json, bytes):
                        contact_json = contact_json.decode("utf-8")
                    try:
                        cd = json.loads(contact_json)
                        frame_idx = cd["frame"]
                        if frame_idx not in contacts_by_frame:
                            contacts_by_frame[frame_idx] = []
                        contacts_by_frame[frame_idx].append(Contact(
                            body1=cd["body1"],
                            body2=cd["body2"],
                            force=cd["force"],
                            position=Vector3.from_list(cd.get("position", [0, 0, 0])),
                            normal=Vector3.from_list(cd.get("normal", [0, 0, 1])),
                        ))
                    except (json.JSONDecodeError, KeyError):
                        pass

        # Build frames
        n_frames = len(timestamps)
        for i in range(n_frames):
            joint_pos = {}
            joint_vel = {}
            joint_tor = {}
            joint_acc = {}
            ctrl_inp = {}

            for j, name in enumerate(joint_names):
                if len(positions) > i and len(positions[i]) > j:
                    joint_pos[name] = float(positions[i][j])
                if len(velocities) > i and len(velocities[i]) > j:
                    joint_vel[name] = float(velocities[i][j])
                if len(torques) > i and len(torques[i]) > j:
                    joint_tor[name] = float(torques[i][j])
                if len(accelerations) > i and len(accelerations[i]) > j:
                    joint_acc[name] = float(accelerations[i][j])

            if control_inputs is not None:
                for j, name in enumerate(ctrl_names):
                    if len(control_inputs[i]) > j:
                        ctrl_inp[name] = float(control_inputs[i][j])

            ee_pose = None
            if ee_poses is not None and len(ee_poses) > i:
                p = ee_poses[i]
                ee_pose = Pose(
                    position=Vector3(x=p[0], y=p[1], z=p[2]),
                    orientation=Quaternion(x=p[3], y=p[4], z=p[5], w=p[6]),
                )

            frame = TrajectoryFrame(
                timestamp=float(timestamps[i]),
                joint_positions=joint_pos,
                joint_velocities=joint_vel,
                joint_torques=joint_tor,
                joint_accelerations=joint_acc,
                end_effector_pose=ee_pose,
                contacts=contacts_by_frame.get(i, []),
                control_inputs=ctrl_inp,
            )
            frames.append(frame)

        # Read events
        if "events" in f:
            events_grp = f["events"]
            event_timestamps = events_grp["timestamps"][:] if "timestamps" in events_grp else []
            event_types = events_grp["types"][:] if "types" in events_grp else []
            event_data = events_grp["data"][:] if "data" in events_grp else []

            for i in range(len(event_timestamps)):
                event_type_str = event_types[i]
                if isinstance(event_type_str, bytes):
                    event_type_str = event_type_str.decode("utf-8")

                try:
                    event_type = EventType(event_type_str)
                except ValueError:
                    event_type = event_type_str

                event_data_dict = {}
                if i < len(event_data):
                    ed = event_data[i]
                    if isinstance(ed, bytes):
                        ed = ed.decode("utf-8")
                    try:
                        event_data_dict = json.loads(ed)
                    except json.JSONDecodeError:
                        pass

                events.append(ExecutionEvent(
                    timestamp=float(event_timestamps[i]),
                    event_type=event_type,
                    data=event_data_dict,
                ))

    # Build recording
    recording = TrajectoryRecording(
        id=recording_id,
        robot_id=robot_id,
        skill_id=skill_id,
        source=source,
        success=success,
        frames=frames,
        events=events,
        metadata=TrajectoryMetadata(
            duration=duration,
            frame_rate=frame_rate,
            total_frames=total_frames,
            skill_params=skill_params,
            tags=tags,
            joint_names=joint_names,
        ),
    )

    return recording


def load_hdf5_for_training(
    filepath: str,
    normalize: bool = True,
    include_velocities: bool = True,
    include_torques: bool = False,
) -> Dict[str, Any]:
    """
    Load HDF5 file and prepare data for ML training.

    Returns NumPy arrays ready for use with PyTorch/TensorFlow.

    Args:
        filepath: Path to HDF5 file
        normalize: Whether to normalize joint data to [-1, 1]
        include_velocities: Include velocity data
        include_torques: Include torque data

    Returns:
        Dictionary with:
        - observations: Combined state array (N, obs_dim)
        - actions: Control inputs (N, action_dim) if available
        - timestamps: Time array (N,)
        - success: Whether execution succeeded
        - metadata: Recording metadata
    """
    try:
        import h5py
        import numpy as np
    except ImportError:
        raise ImportError("Requires h5py and numpy")

    with h5py.File(filepath, "r") as f:
        timestamps = f["timestamps"][:]
        positions = f["joint_positions"][:]
        n_frames, n_joints = positions.shape

        # Build observation array
        obs_components = [positions]

        if include_velocities and "joint_velocities" in f:
            obs_components.append(f["joint_velocities"][:])

        if include_torques and "joint_torques" in f:
            obs_components.append(f["joint_torques"][:])

        if "end_effector_poses" in f:
            obs_components.append(f["end_effector_poses"][:])

        observations = np.concatenate(obs_components, axis=1)

        # Normalize if requested
        if normalize:
            obs_mean = observations.mean(axis=0, keepdims=True)
            obs_std = observations.std(axis=0, keepdims=True) + 1e-8
            observations = (observations - obs_mean) / obs_std

        # Actions (control inputs)
        actions = None
        if "control_inputs" in f:
            actions = f["control_inputs"][:]

        # Metadata
        metadata = {
            "recording_id": f.attrs.get("recording_id", ""),
            "robot_id": f.attrs.get("robot_id", ""),
            "skill_id": f.attrs.get("skill_id", ""),
            "duration": float(f.attrs.get("duration", 0)),
            "frame_rate": float(f.attrs.get("frame_rate", 0)),
        }

        return {
            "observations": observations,
            "actions": actions,
            "timestamps": timestamps,
            "success": bool(f.attrs.get("success", True)),
            "metadata": metadata,
            "joint_names": [name.decode("utf-8") if isinstance(name, bytes) else name
                          for name in f["joint_names"][:]] if "joint_names" in f else [],
        }
