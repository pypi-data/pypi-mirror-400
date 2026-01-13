"""
Perception interfaces for robot sensors.

Supports:
- RGB cameras
- Depth cameras (stereo, ToF, structured light)
- LiDAR (2D and 3D)
- IMU
- Force/Torque sensors

Design principle: Return raw sensor data in standard formats.
Processing (object detection, SLAM, etc.) happens at higher levels.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Callable, Tuple
from enum import Enum, auto

from .types import (
    Vector3,
    Quaternion,
    Pose,
    Image,
    DepthImage,
    PointCloud,
    IMUReading,
    ForceTorqueReading,
    ActionResult,
)


class CameraInterface(ABC):
    """
    Interface for RGB cameras.

    Can be:
    - Fixed mount (e.g., head camera)
    - On end-effector (e.g., wrist camera)
    - External (e.g., Intel RealSense)
    """

    @abstractmethod
    def get_image(self) -> Image:
        """
        Capture current frame.

        Returns:
            Image with RGB data
        """
        pass

    @abstractmethod
    def get_resolution(self) -> Tuple[int, int]:
        """
        Get camera resolution.

        Returns:
            (width, height) in pixels
        """
        pass

    @abstractmethod
    def get_intrinsics(self) -> dict:
        """
        Get camera intrinsic parameters.

        Returns:
            Dict with:
                - fx, fy: focal lengths
                - cx, cy: principal point
                - distortion: distortion coefficients
        """
        pass

    def get_frame_id(self) -> str:
        """Get coordinate frame ID for this camera."""
        return "camera"

    def set_resolution(self, width: int, height: int) -> ActionResult:
        """Set camera resolution."""
        return ActionResult.error("Resolution change not supported")

    def set_exposure(self, exposure_ms: float) -> ActionResult:
        """Set exposure time in milliseconds."""
        return ActionResult.error("Exposure control not supported")

    # =========================================================================
    # Streaming (optional)
    # =========================================================================

    def start_streaming(self, callback: Callable[[Image], None]) -> ActionResult:
        """
        Start continuous image streaming.

        Args:
            callback: Function called with each new frame
        """
        return ActionResult.error("Streaming not supported")

    def stop_streaming(self) -> ActionResult:
        """Stop image streaming."""
        return ActionResult.error("Streaming not supported")

    def get_fps(self) -> float:
        """Get current frame rate."""
        return 0.0


class DepthCameraInterface(CameraInterface):
    """
    Interface for depth cameras.

    Extends CameraInterface with depth-specific methods.
    Implemented by: RealSense, Kinect, stereo cameras, ToF sensors.
    """

    @abstractmethod
    def get_depth_image(self) -> DepthImage:
        """
        Capture current depth frame.

        Returns:
            DepthImage with depth values
        """
        pass

    @abstractmethod
    def get_point_cloud(self) -> PointCloud:
        """
        Get 3D point cloud from depth data.

        Returns:
            PointCloud in camera frame
        """
        pass

    def get_rgbd(self) -> Tuple[Image, DepthImage]:
        """
        Get aligned RGB and depth images.

        Returns:
            (rgb_image, depth_image) tuple
        """
        return (self.get_image(), self.get_depth_image())

    def get_depth_range(self) -> Tuple[float, float]:
        """
        Get valid depth range.

        Returns:
            (min_depth, max_depth) in meters
        """
        return (0.1, 10.0)

    def point_to_3d(self, x: int, y: int) -> Optional[Vector3]:
        """
        Convert pixel coordinates to 3D point.

        Args:
            x, y: Pixel coordinates

        Returns:
            Vector3 in camera frame, or None if invalid depth
        """
        depth = self.get_depth_image()
        # Implementation depends on depth format
        return None


class LidarInterface(ABC):
    """
    Interface for LiDAR sensors.

    Supports:
    - 2D LiDAR (RPLIDAR, Hokuyo)
    - 3D LiDAR (Velodyne, Ouster, Livox)
    """

    @abstractmethod
    def get_scan(self) -> PointCloud:
        """
        Get current LiDAR scan.

        Returns:
            PointCloud in sensor frame
        """
        pass

    @abstractmethod
    def get_range(self) -> Tuple[float, float]:
        """
        Get measurement range.

        Returns:
            (min_range, max_range) in meters
        """
        pass

    def get_frame_id(self) -> str:
        """Get coordinate frame ID for this LiDAR."""
        return "lidar"

    def is_3d(self) -> bool:
        """Check if this is a 3D LiDAR."""
        return True

    def get_angular_resolution(self) -> float:
        """Get angular resolution in radians."""
        return 0.01  # ~0.5 degrees default

    # =========================================================================
    # 2D LiDAR specific
    # =========================================================================

    def get_scan_2d(self) -> List[Tuple[float, float]]:
        """
        Get 2D scan as list of (angle, distance) pairs.

        Returns:
            List of (angle_rad, distance_m) tuples
        """
        # Default: project 3D to 2D
        cloud = self.get_scan()
        scan_2d = []
        import math
        for point in cloud.points:
            angle = math.atan2(point.y, point.x)
            distance = math.sqrt(point.x**2 + point.y**2)
            scan_2d.append((angle, distance))
        return scan_2d


class IMUInterface(ABC):
    """
    Interface for Inertial Measurement Units.

    Provides:
    - Orientation (from gyro integration or sensor fusion)
    - Angular velocity (from gyroscope)
    - Linear acceleration (from accelerometer)
    """

    @abstractmethod
    def get_reading(self) -> IMUReading:
        """
        Get current IMU reading.

        Returns:
            IMUReading with orientation, angular velocity, acceleration
        """
        pass

    @abstractmethod
    def get_orientation(self) -> Quaternion:
        """
        Get current orientation.

        Returns:
            Quaternion representing orientation
        """
        pass

    def get_euler(self) -> Tuple[float, float, float]:
        """
        Get orientation as Euler angles.

        Returns:
            (roll, pitch, yaw) in radians
        """
        return self.get_orientation().to_euler()

    def get_angular_velocity(self) -> Vector3:
        """
        Get angular velocity.

        Returns:
            Vector3 in rad/s
        """
        return self.get_reading().angular_velocity

    def get_linear_acceleration(self) -> Vector3:
        """
        Get linear acceleration.

        Returns:
            Vector3 in m/s² (includes gravity)
        """
        return self.get_reading().linear_acceleration

    def calibrate(self) -> ActionResult:
        """
        Calibrate IMU (set current orientation as reference).

        Robot should be stationary and level.
        """
        return ActionResult.error("Calibration not supported")

    def get_frame_id(self) -> str:
        """Get coordinate frame ID for this IMU."""
        return "imu"


class ForceTorqueInterface(ABC):
    """
    Interface for force-torque sensors.

    Typically mounted at wrist (between arm and gripper).
    """

    @abstractmethod
    def get_reading(self) -> ForceTorqueReading:
        """
        Get current force-torque reading.

        Returns:
            ForceTorqueReading with force and torque vectors
        """
        pass

    @abstractmethod
    def get_force(self) -> Vector3:
        """
        Get force vector.

        Returns:
            Vector3 in Newtons
        """
        pass

    @abstractmethod
    def get_torque(self) -> Vector3:
        """
        Get torque vector.

        Returns:
            Vector3 in Nm
        """
        pass

    def zero(self) -> ActionResult:
        """
        Zero the sensor (set current reading as offset).

        Call when no external load is applied.
        """
        return ActionResult.error("Zeroing not supported")

    def get_frame_id(self) -> str:
        """Get coordinate frame ID for this sensor."""
        return "ft_sensor"

    def is_in_contact(self, threshold: float = 1.0) -> bool:
        """
        Check if sensor detects contact.

        Args:
            threshold: Force threshold in Newtons

        Returns:
            True if force magnitude exceeds threshold
        """
        return self.get_force().magnitude() > threshold
