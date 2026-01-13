"""
Upload skill libraries and calibrations to FoodforThought.

Creates artifacts with proper lineage:
- Raw: pose images from dual cameras
- Processed: servo calibration data
- Labeled: named poses with semantic labels
- Skill: generated Python skill code
"""

import os
import json
import base64
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from .calibration import RobotCalibration, load_calibration
from .visual_labeler import SkillLibrary, load_skill_library


# API configuration
BASE_URL = os.getenv("ATE_API_URL", "https://www.kindly.fyi/api")
CONFIG_FILE = Path.home() / ".ate" / "config.json"


class SkillLibraryUploader:
    """
    Uploads skill libraries to FoodforThought.

    Creates a complete data lineage:
    raw (images) → processed (calibration) → labeled (poses) → skill (code)
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
        }

        token = None

        # Load from config file (device auth flow)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    config = json.load(f)
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

    def get_or_create_project(self, name: str, description: str = "") -> str:
        """Get existing project or create a new one."""
        # Try to find existing project
        try:
            projects = self._request("GET", "/projects")
            for project in projects.get("projects", []):
                if project.get("name") == name:
                    return project["id"]
        except Exception:
            pass

        # Create new project
        response = self._request("POST", "/projects", json={
            "name": name,
            "description": description or f"Robot skill library for {name}",
            "visibility": "private",
        })
        return response.get("project", {}).get("id")

    def upload_skill_library(
        self,
        library: SkillLibrary,
        calibration: RobotCalibration,
        project_id: Optional[str] = None,
        include_images: bool = True,
    ) -> Dict[str, Any]:
        """
        Upload a complete skill library to FoodforThought.

        Creates artifacts with lineage:
        1. Raw: pose images
        2. Processed: servo calibration
        3. Labeled: poses with semantic labels
        4. Skill: generated Python code

        Args:
            library: SkillLibrary to upload
            calibration: RobotCalibration with servo data
            project_id: Optional project ID (will create if not provided)
            include_images: Whether to upload pose images

        Returns:
            Dict with artifact IDs and URLs
        """
        result = {
            "project_id": None,
            "artifacts": [],
            "lineage": [],
        }

        # Get or create project
        if not project_id:
            project_id = self.get_or_create_project(
                f"{library.robot_name}_skills",
                f"Skill library for {library.robot_model}",
            )
        result["project_id"] = project_id

        # 1. Upload pose images as raw artifacts
        image_artifact_ids = []
        if include_images:
            images_dir = Path.home() / ".ate" / "skill_images" / library.robot_name
            if images_dir.exists():
                for img_path in images_dir.glob("*.jpg"):
                    try:
                        artifact_id = self._upload_image_artifact(
                            project_id=project_id,
                            image_path=img_path,
                            robot_name=library.robot_name,
                        )
                        image_artifact_ids.append(artifact_id)
                        result["artifacts"].append({
                            "id": artifact_id,
                            "stage": "raw",
                            "name": img_path.stem,
                        })
                    except Exception as e:
                        print(f"Warning: Failed to upload {img_path.name}: {e}")

        # 2. Upload calibration as processed artifact
        calibration_artifact_id = self._upload_calibration_artifact(
            project_id=project_id,
            calibration=calibration,
            parent_ids=image_artifact_ids[:5] if image_artifact_ids else None,  # Link to some images
        )
        result["artifacts"].append({
            "id": calibration_artifact_id,
            "stage": "processed",
            "name": f"{library.robot_name}_calibration",
        })

        # 3. Upload poses as labeled artifacts
        pose_artifact_ids = []
        for pose_name, pose in calibration.poses.items():
            pose_artifact_id = self._upload_pose_artifact(
                project_id=project_id,
                pose_name=pose_name,
                pose=pose,
                calibration=calibration,
                parent_id=calibration_artifact_id,
            )
            pose_artifact_ids.append(pose_artifact_id)
            result["artifacts"].append({
                "id": pose_artifact_id,
                "stage": "labeled",
                "name": pose_name,
            })

        # 4. Upload skills as skill artifacts
        for action_name, action in library.actions.items():
            skill_artifact_id = self._upload_skill_artifact(
                project_id=project_id,
                action_name=action_name,
                action=action,
                library=library,
                calibration=calibration,
                trained_on=pose_artifact_ids,  # Skills trained on poses
            )
            result["artifacts"].append({
                "id": skill_artifact_id,
                "stage": "skill",
                "name": action_name,
            })

        return result

    def _upload_image_artifact(
        self,
        project_id: str,
        image_path: Path,
        robot_name: str,
    ) -> str:
        """Upload an image as a raw artifact."""
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        response = self._request("POST", "/artifacts", json={
            "projectId": project_id,
            "name": image_path.stem,
            "stage": "raw",
            "type": "dataset",
            "metadata": {
                "robot_name": robot_name,
                "image_type": "pose_capture",
                "filename": image_path.name,
                "format": "jpeg",
                "source": "visual_labeler",
                "captured_at": datetime.now().isoformat(),
            },
        })
        return response.get("artifact", {}).get("id")

    def _upload_calibration_artifact(
        self,
        project_id: str,
        calibration: RobotCalibration,
        parent_ids: Optional[List[str]] = None,
    ) -> str:
        """Upload servo calibration as a processed artifact."""
        # Serialize calibration
        calibration_data = {
            "robot_model": calibration.robot_model,
            "robot_name": calibration.robot_name,
            "serial_port": calibration.serial_port,
            "baud_rate": calibration.baud_rate,
            "camera_url": calibration.camera_url,
            "servos": {
                str(sid): {
                    "servo_id": s.servo_id,
                    "name": s.name,
                    "joint_type": s.joint_type.value,
                    "min_value": s.min_value,
                    "max_value": s.max_value,
                    "center_value": s.center_value,
                    "positions": s.positions,
                }
                for sid, s in calibration.servos.items()
            },
            "calibrated_at": calibration.calibrated_at,
        }

        response = self._request("POST", "/artifacts", json={
            "projectId": project_id,
            "name": f"{calibration.robot_name}_calibration",
            "stage": "processed",
            "type": "dataset",
            "metadata": {
                "robot_model": calibration.robot_model,
                "robot_name": calibration.robot_name,
                "servo_count": len(calibration.servos),
                "pose_count": len(calibration.poses),
                "calibration_data": calibration_data,
                "source": "visual_labeler",
            },
        })
        return response.get("artifact", {}).get("id")

    def _upload_pose_artifact(
        self,
        project_id: str,
        pose_name: str,
        pose,
        calibration: RobotCalibration,
        parent_id: str,
    ) -> str:
        """Upload a named pose as a labeled artifact."""
        # Build pose data with semantic labels
        servo_labels = {}
        for sid, value in pose.servo_positions.items():
            servo_cal = calibration.servos.get(sid)
            if servo_cal:
                servo_labels[str(sid)] = {
                    "name": servo_cal.name,
                    "joint_type": servo_cal.joint_type.value,
                    "value": value,
                    "normalized": (value - servo_cal.min_value) / max(1, servo_cal.max_value - servo_cal.min_value),
                }

        response = self._request("POST", "/artifacts", json={
            "projectId": project_id,
            "name": pose_name,
            "stage": "labeled",
            "type": "dataset",
            "parentArtifactId": parent_id,
            "transformationType": "labeling",
            "transformationNotes": f"Pose '{pose_name}' labeled from calibration",
            "metadata": {
                "robot_name": calibration.robot_name,
                "pose_name": pose_name,
                "description": pose.description,
                "servo_positions": pose.servo_positions,
                "servo_labels": servo_labels,
                "transition_time_ms": pose.transition_time_ms,
                "image_path": pose.image_path,
                "source": "visual_labeler",
            },
        })
        return response.get("artifact", {}).get("id")

    def _upload_skill_artifact(
        self,
        project_id: str,
        action_name: str,
        action,
        library: SkillLibrary,
        calibration: RobotCalibration,
        trained_on: List[str],
    ) -> str:
        """Upload a generated skill as a skill artifact."""
        # Generate skill code
        from .visual_labeler import DualCameraLabeler
        labeler = DualCameraLabeler(
            serial_port=calibration.serial_port or "",
            robot_name=library.robot_name,
            robot_model=library.robot_model,
        )
        labeler.calibrator.calibration = calibration
        skill_code = labeler.generate_skill_code(action)

        response = self._request("POST", "/artifacts", json={
            "projectId": project_id,
            "name": action_name,
            "stage": "skill",
            "type": "code",
            "trainedOn": trained_on,
            "trainingNotes": f"Skill '{action_name}' generated from {len(action.steps)} poses",
            "metadata": {
                "robot_model": library.robot_model,
                "robot_name": library.robot_name,
                "action_type": action.action_type.value,
                "description": action.description,
                "steps": [s.to_dict() for s in action.steps],
                "skill_code": skill_code,
                "tags": action.tags,
                "source": "visual_labeler",
                "generated_at": datetime.now().isoformat(),
            },
        })
        return response.get("artifact", {}).get("id")


def upload_skill_library(
    robot_name: str,
    project_id: Optional[str] = None,
    include_images: bool = True,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to upload a skill library.

    Args:
        robot_name: Name of the robot (matches calibration/library filenames)
        project_id: Optional project ID
        include_images: Whether to upload pose images
        api_key: Optional API key

    Returns:
        Dict with upload results
    """
    # Load calibration
    calibration = load_calibration(robot_name)
    if not calibration:
        raise ValueError(f"No calibration found for: {robot_name}")

    # Load skill library
    library = load_skill_library(robot_name)
    if not library:
        raise ValueError(f"No skill library found for: {robot_name}")

    uploader = SkillLibraryUploader(api_key=api_key)
    return uploader.upload_skill_library(
        library=library,
        calibration=calibration,
        project_id=project_id,
        include_images=include_images,
    )
