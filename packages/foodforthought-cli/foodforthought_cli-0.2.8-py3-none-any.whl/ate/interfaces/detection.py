"""
Object detection interface for robot perception.

This is a HIGHER-LEVEL interface that wraps camera interfaces
and ML models to provide semantic understanding of the environment.

Design principle: Models are pluggable - the interface abstracts
away the specific ML framework (YOLO, Detectron2, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from enum import Enum, auto

from .types import Vector3, Image, ActionResult


@dataclass
class BoundingBox:
    """2D bounding box in image coordinates."""
    x_min: float  # Left edge (pixels)
    y_min: float  # Top edge (pixels)
    x_max: float  # Right edge (pixels)
    y_max: float  # Bottom edge (pixels)

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def center(self) -> tuple:
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class Detection:
    """A detected object in an image."""
    class_name: str              # e.g., "trash", "bottle", "can"
    class_id: int               # Numeric class ID
    confidence: float           # 0.0 to 1.0
    bbox: BoundingBox           # 2D bounding box

    # Optional 3D info (if depth available)
    position_3d: Optional[Vector3] = None  # In camera frame
    distance: Optional[float] = None       # Distance in meters

    # Optional instance segmentation mask
    mask: Optional[Any] = None

    # Additional attributes (color, size estimates, etc.)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "class_name": self.class_name,
            "class_id": self.class_id,
            "confidence": self.confidence,
            "bbox": {
                "x_min": self.bbox.x_min,
                "y_min": self.bbox.y_min,
                "x_max": self.bbox.x_max,
                "y_max": self.bbox.y_max,
            },
            "position_3d": self.position_3d.to_dict() if self.position_3d else None,
            "distance": self.distance,
            "attributes": self.attributes,
        }


@dataclass
class DetectionResult:
    """Result of running object detection on an image."""
    detections: List[Detection]
    image: Optional[Image] = None  # Original image (optional)
    inference_time_ms: float = 0.0
    model_name: str = ""

    def filter_by_class(self, class_name: str) -> List[Detection]:
        """Get detections of a specific class."""
        return [d for d in self.detections if d.class_name == class_name]

    def filter_by_confidence(self, min_confidence: float) -> List[Detection]:
        """Get detections above confidence threshold."""
        return [d for d in self.detections if d.confidence >= min_confidence]

    def get_closest(self) -> Optional[Detection]:
        """Get the closest detected object (requires 3D info)."""
        with_distance = [d for d in self.detections if d.distance is not None]
        if not with_distance:
            return None
        return min(with_distance, key=lambda d: d.distance)


class ObjectDetectionInterface(ABC):
    """
    Interface for object detection capabilities.

    This abstracts the specific ML model and camera hardware,
    providing a unified API for detecting objects in the environment.

    Use cases:
    - Trash detection for cleanup tasks
    - Object manipulation (find and grasp)
    - Obstacle detection for navigation
    - Person detection for social robots
    """

    @abstractmethod
    def detect(self, image: Optional[Image] = None) -> DetectionResult:
        """
        Run object detection.

        Args:
            image: Image to process. If None, capture from camera.

        Returns:
            DetectionResult with all detections
        """
        pass

    @abstractmethod
    def get_classes(self) -> List[str]:
        """
        Get list of classes this detector can recognize.

        Returns:
            List of class names
        """
        pass

    def detect_class(self, class_name: str, min_confidence: float = 0.5) -> List[Detection]:
        """
        Detect objects of a specific class.

        Args:
            class_name: Class to detect (e.g., "bottle", "trash")
            min_confidence: Minimum confidence threshold

        Returns:
            List of detections of that class
        """
        result = self.detect()
        return [
            d for d in result.detections
            if d.class_name == class_name and d.confidence >= min_confidence
        ]

    def detect_any(self, class_names: List[str], min_confidence: float = 0.5) -> List[Detection]:
        """
        Detect objects of any of the specified classes.

        Args:
            class_names: List of classes to detect
            min_confidence: Minimum confidence threshold

        Returns:
            List of detections matching any class
        """
        result = self.detect()
        return [
            d for d in result.detections
            if d.class_name in class_names and d.confidence >= min_confidence
        ]

    def find_nearest(self, class_name: str) -> Optional[Detection]:
        """
        Find the nearest object of a class.

        Args:
            class_name: Class to find

        Returns:
            Detection of nearest object, or None
        """
        detections = self.detect_class(class_name)
        with_distance = [d for d in detections if d.distance is not None]
        if not with_distance:
            # Fall back to largest bounding box (likely closest)
            if detections:
                return max(detections, key=lambda d: d.bbox.area)
            return None
        return min(with_distance, key=lambda d: d.distance)

    # =========================================================================
    # Model management
    # =========================================================================

    def load_model(self, model_path: str) -> ActionResult:
        """Load a specific detection model."""
        return ActionResult.error("Custom model loading not supported")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {"classes": self.get_classes()}

    # =========================================================================
    # Streaming detection
    # =========================================================================

    def start_detection_stream(
        self,
        callback: Callable[[DetectionResult], None],
        min_confidence: float = 0.5
    ) -> ActionResult:
        """
        Start continuous detection with callbacks.

        Args:
            callback: Function called with each detection result
            min_confidence: Minimum confidence for callbacks
        """
        return ActionResult.error("Streaming detection not supported")

    def stop_detection_stream(self) -> ActionResult:
        """Stop the detection stream."""
        return ActionResult.error("Streaming detection not supported")


class TrashDetectionInterface(ObjectDetectionInterface):
    """
    Specialized detector for trash/litter.

    Recognizes common trash items:
    - Bottles (plastic, glass)
    - Cans
    - Paper/cardboard
    - Wrappers/packaging
    - Cigarette butts
    - General debris
    """

    TRASH_CLASSES = [
        "plastic_bottle",
        "glass_bottle",
        "can",
        "paper",
        "cardboard",
        "wrapper",
        "cigarette_butt",
        "debris",
        "trash",  # Generic
    ]

    def get_classes(self) -> List[str]:
        return self.TRASH_CLASSES

    def detect_trash(self, min_confidence: float = 0.5) -> List[Detection]:
        """
        Detect all trash items.

        Returns:
            List of trash detections
        """
        return self.detect_any(self.TRASH_CLASSES, min_confidence)

    def find_nearest_trash(self) -> Optional[Detection]:
        """
        Find the nearest trash item.

        Returns:
            Detection of nearest trash, or None
        """
        detections = self.detect_trash()
        with_distance = [d for d in detections if d.distance is not None]
        if not with_distance:
            if detections:
                return max(detections, key=lambda d: d.bbox.area)
            return None
        return min(with_distance, key=lambda d: d.distance)

    def is_trash_visible(self) -> bool:
        """Check if any trash is visible."""
        return len(self.detect_trash()) > 0
