"""
Upload demonstrations to FoodforThought.

Converts interface recordings to the FoodforThought telemetry format
and uploads them as artifacts for labeling and training.
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from .demonstration import Demonstration, load_demonstration
from .session import RecordingSession


# API configuration
BASE_URL = os.getenv("ATE_API_URL", "https://www.kindly.fyi/api")
CONFIG_FILE = Path.home() / ".ate" / "config.json"


class DemonstrationUploader:
    """
    Uploads demonstrations to FoodforThought.

    Handles authentication and converts the interface-based recording
    format to the FoodforThought telemetry ingest format.
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        api_key: Optional[str] = None,
    ):
        """
        Initialize uploader.

        Args:
            base_url: FoodforThought API URL
            api_key: API key (or set ATE_API_KEY env var)
        """
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
        }

        token = None

        # Try to load from config file first (device auth flow)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    config = json.load(f)
                    # Prefer access_token from device auth flow
                    token = config.get("access_token") or config.get("api_key")
            except Exception:
                pass

        # Override with explicit api_key or env var
        if api_key:
            token = api_key
        elif os.getenv("ATE_API_KEY"):
            token = os.getenv("ATE_API_KEY")

        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        else:
            raise ValueError(
                "Not logged in. Run 'ate login' to authenticate."
            )

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def upload(
        self,
        demonstration: Demonstration,
        project_id: Optional[str] = None,
        skill_id: Optional[str] = None,
        create_labeling_task: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload a demonstration to FoodforThought.

        Args:
            demonstration: Demonstration object to upload
            project_id: Optional project ID to associate with
            skill_id: Optional skill ID this demonstrates
            create_labeling_task: Create a labeling task for annotation

        Returns:
            Response dict with artifactId and optional taskId
        """
        # Convert to telemetry ingest format
        recording_data = self._convert_to_telemetry_format(
            demonstration,
            skill_id=skill_id,
        )

        if create_labeling_task:
            recording_data["createLabelingTask"] = True

        # Upload via telemetry ingest API
        response = self._request("POST", "/telemetry/ingest", json=recording_data)

        return {
            "success": True,
            "artifactId": response.get("data", {}).get("artifactId"),
            "taskId": response.get("data", {}).get("taskId"),
            "url": f"https://foodforthought.kindly.fyi/artifacts/{response.get('data', {}).get('artifactId', '')}",
        }

    def upload_file(
        self,
        path: str,
        project_id: Optional[str] = None,
        skill_id: Optional[str] = None,
        create_labeling_task: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload a demonstration file to FoodforThought.

        Args:
            path: Path to .demonstration file
            project_id: Optional project ID
            skill_id: Optional skill ID
            create_labeling_task: Create labeling task

        Returns:
            Response dict with artifactId
        """
        demonstration = load_demonstration(path)
        return self.upload(
            demonstration,
            project_id=project_id,
            skill_id=skill_id,
            create_labeling_task=create_labeling_task,
        )

    def upload_session(
        self,
        session: RecordingSession,
        project_id: Optional[str] = None,
        skill_id: Optional[str] = None,
        create_labeling_task: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload a recording session directly to FoodforThought.

        Args:
            session: RecordingSession to upload
            project_id: Optional project ID
            skill_id: Optional skill ID
            create_labeling_task: Create labeling task

        Returns:
            Response dict with artifactId
        """
        # Convert session to demonstration
        metadata = session.get_metadata()
        demonstration = Demonstration(
            metadata=metadata,
            calls=session.calls,
            segments=[],
        )

        return self.upload(
            demonstration,
            project_id=project_id,
            skill_id=skill_id,
            create_labeling_task=create_labeling_task,
        )

    def _convert_to_telemetry_format(
        self,
        demonstration: Demonstration,
        skill_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Convert demonstration to FoodforThought telemetry ingest format.

        The telemetry format is designed for time-series data from robots.
        We map interface calls to this format while preserving the
        abstract nature of the recording.
        """
        metadata = demonstration.metadata

        # Convert calls to telemetry frames
        frames = []
        for call in demonstration.calls:
            frame = {
                "timestamp": call.timestamp,
                "relativeTime": call.relative_time,
                "type": "interface_call",
                "data": {
                    "interface": call.interface,
                    "method": call.method,
                    "args": call.args,
                    "kwargs": call.kwargs,
                    "result": call.result,
                    "success": call.success,
                },
            }
            if call.error:
                frame["data"]["error"] = call.error
            frames.append(frame)

        # Convert segments to events
        events = []
        for segment in demonstration.segments:
            events.append({
                "type": "task_segment",
                "startTime": segment.start_time,
                "endTime": segment.end_time,
                "label": segment.label,
                "description": segment.description,
                "confidence": segment.confidence,
            })

        # Build recording data
        start_time = datetime.fromtimestamp(metadata.start_time).isoformat() if metadata.start_time else None
        end_time = datetime.fromtimestamp(metadata.end_time).isoformat() if metadata.end_time else None

        recording_data = {
            "recording": {
                "id": metadata.id,
                "robotId": metadata.robot_model,
                "skillId": skill_id or "demonstration",
                "source": "interface_recording",
                "startTime": start_time,
                "endTime": end_time,
                "success": all(c.success for c in demonstration.calls),
                "metadata": {
                    "name": metadata.name,
                    "description": metadata.description,
                    "robotName": metadata.robot_name,
                    "robotModel": metadata.robot_model,
                    "robotArchetype": metadata.robot_archetype,
                    "capabilities": metadata.capabilities,
                    "duration": metadata.duration,
                    "callCount": len(demonstration.calls),
                    "segmentCount": len(demonstration.segments),
                    "interfacesUsed": demonstration.get_interfaces_used(),
                    "tags": metadata.tags + ["interface_recording"],
                },
                "frames": frames,
                "events": events,
            },
        }

        return recording_data


def upload_demonstration(
    path_or_demonstration,
    project_id: Optional[str] = None,
    skill_id: Optional[str] = None,
    create_labeling_task: bool = False,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to upload a demonstration.

    Args:
        path_or_demonstration: Path to .demonstration file or Demonstration object
        project_id: Optional project ID
        skill_id: Optional skill ID
        create_labeling_task: Create labeling task
        api_key: Optional API key

    Returns:
        Response dict with artifactId
    """
    uploader = DemonstrationUploader(api_key=api_key)

    if isinstance(path_or_demonstration, str):
        return uploader.upload_file(
            path_or_demonstration,
            project_id=project_id,
            skill_id=skill_id,
            create_labeling_task=create_labeling_task,
        )
    elif isinstance(path_or_demonstration, Demonstration):
        return uploader.upload(
            path_or_demonstration,
            project_id=project_id,
            skill_id=skill_id,
            create_labeling_task=create_labeling_task,
        )
    elif isinstance(path_or_demonstration, RecordingSession):
        return uploader.upload_session(
            path_or_demonstration,
            project_id=project_id,
            skill_id=skill_id,
            create_labeling_task=create_labeling_task,
        )
    else:
        raise TypeError(f"Expected path, Demonstration, or RecordingSession, got {type(path_or_demonstration)}")
