"""
Telemetry module for FoodforThought CLI

Provides tools for collecting, serializing, and uploading robot telemetry data
from simulations and hardware executions.
"""

from .types import (
    Pose,
    Contact,
    TrajectoryFrame,
    TrajectoryMetadata,
    TrajectoryRecording,
    ExecutionEvent,
    SensorReading,
)
from .collector import TelemetryCollector
from .context import record_trajectory

__all__ = [
    # Types
    "Pose",
    "Contact",
    "TrajectoryFrame",
    "TrajectoryMetadata",
    "TrajectoryRecording",
    "ExecutionEvent",
    "SensorReading",
    # Collector
    "TelemetryCollector",
    # Context manager
    "record_trajectory",
]
