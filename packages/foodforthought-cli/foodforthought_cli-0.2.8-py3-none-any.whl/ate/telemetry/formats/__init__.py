"""
Format serializers for telemetry data.

Supports:
- MCAP: ROS ecosystem standard, Foxglove compatible
- HDF5: ML-friendly format for training pipelines
- JSON: Human-readable, debugging
"""

from .mcap_serializer import serialize_to_mcap, deserialize_from_mcap
from .hdf5_serializer import serialize_to_hdf5, deserialize_from_hdf5

__all__ = [
    "serialize_to_mcap",
    "deserialize_from_mcap",
    "serialize_to_hdf5",
    "deserialize_from_hdf5",
]
