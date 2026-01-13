"""
Body pose interfaces for robots with adjustable body position/orientation.

Primarily for legged robots that can:
- Adjust body height
- Tilt body (roll, pitch, yaw)
- Shift body position relative to feet

These are independent of locomotion - you can adjust pose while standing still.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple

from .types import (
    Vector3,
    Quaternion,
    Pose,
    ActionResult,
)


class BodyPoseInterface(ABC):
    """
    Interface for controlling robot body pose.

    Implemented by quadrupeds, bipeds, and other robots that can adjust
    their body position/orientation independent of locomotion.

    Coordinate frame:
    - Body origin is typically at the center of the robot
    - Z+ is up, X+ is forward, Y+ is left
    """

    # =========================================================================
    # Body height control
    # =========================================================================

    @abstractmethod
    def set_body_height(self, height: float) -> ActionResult:
        """
        Set body height above ground.

        Args:
            height: Height in meters (from nominal ground level)

        Returns:
            ActionResult
        """
        pass

    @abstractmethod
    def get_body_height(self) -> float:
        """
        Get current body height.

        Returns:
            Height in meters
        """
        pass

    def get_height_limits(self) -> Tuple[float, float]:
        """
        Get allowed body height range.

        Returns:
            (min_height, max_height) in meters
        """
        return (0.05, 0.30)  # Default for small quadrupeds

    # =========================================================================
    # Body orientation control
    # =========================================================================

    @abstractmethod
    def set_body_orientation(
        self,
        roll: float = 0.0,
        pitch: float = 0.0,
        yaw: float = 0.0
    ) -> ActionResult:
        """
        Set body orientation (tilt).

        Args:
            roll: Roll angle in radians (positive = right side down)
            pitch: Pitch angle in radians (positive = nose down)
            yaw: Yaw angle in radians (positive = turn left)

        Returns:
            ActionResult
        """
        pass

    @abstractmethod
    def get_body_orientation(self) -> Tuple[float, float, float]:
        """
        Get current body orientation.

        Returns:
            (roll, pitch, yaw) in radians
        """
        pass

    def get_orientation_limits(self) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        """
        Get allowed orientation ranges.

        Returns:
            ((roll_min, roll_max), (pitch_min, pitch_max), (yaw_min, yaw_max))
            All in radians
        """
        import math
        return (
            (-math.pi/6, math.pi/6),   # ±30° roll
            (-math.pi/6, math.pi/6),   # ±30° pitch
            (-math.pi/4, math.pi/4),   # ±45° yaw
        )

    # =========================================================================
    # Body position control
    # =========================================================================

    def set_body_position(self, offset: Vector3) -> ActionResult:
        """
        Shift body position relative to feet.

        This moves the body while keeping feet planted.

        Args:
            offset: Position offset from center (x=forward, y=left, z=up)

        Returns:
            ActionResult
        """
        return ActionResult.error("Body position shift not supported")

    def get_body_position(self) -> Vector3:
        """
        Get current body position offset.

        Returns:
            Vector3 offset from center
        """
        return Vector3.zero()

    # =========================================================================
    # Combined pose control
    # =========================================================================

    @abstractmethod
    def set_body_pose(
        self,
        height: Optional[float] = None,
        roll: Optional[float] = None,
        pitch: Optional[float] = None,
        yaw: Optional[float] = None,
        x_offset: Optional[float] = None,
        y_offset: Optional[float] = None
    ) -> ActionResult:
        """
        Set multiple body pose parameters at once.

        Args:
            height: Body height (None = keep current)
            roll, pitch, yaw: Orientation (None = keep current)
            x_offset, y_offset: Body position offset (None = keep current)

        Returns:
            ActionResult
        """
        pass

    def get_body_pose(self) -> dict:
        """
        Get complete body pose.

        Returns:
            Dict with height, roll, pitch, yaw, x_offset, y_offset
        """
        roll, pitch, yaw = self.get_body_orientation()
        pos = self.get_body_position()
        return {
            "height": self.get_body_height(),
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
            "x_offset": pos.x,
            "y_offset": pos.y,
        }

    # =========================================================================
    # Preset poses
    # =========================================================================

    def reset_pose(self) -> ActionResult:
        """
        Reset to default/neutral body pose.

        Returns:
            ActionResult
        """
        height_min, height_max = self.get_height_limits()
        default_height = (height_min + height_max) / 2
        return self.set_body_pose(
            height=default_height,
            roll=0.0,
            pitch=0.0,
            yaw=0.0,
            x_offset=0.0,
            y_offset=0.0
        )

    def lower_body(self, height: Optional[float] = None) -> ActionResult:
        """
        Lower body (for grasping objects on ground).

        Args:
            height: Target height (None = minimum safe height)

        Returns:
            ActionResult
        """
        if height is None:
            height = self.get_height_limits()[0] + 0.02  # 2cm above min
        return self.set_body_height(height)

    def raise_body(self, height: Optional[float] = None) -> ActionResult:
        """
        Raise body to maximum comfortable height.

        Args:
            height: Target height (None = default standing height)

        Returns:
            ActionResult
        """
        if height is None:
            height_min, height_max = self.get_height_limits()
            height = (height_min + height_max) / 2
        return self.set_body_height(height)

    def look_at(self, direction: Vector3) -> ActionResult:
        """
        Tilt body to "look" in a direction.

        Adjusts pitch and yaw to point forward axis toward direction.

        Args:
            direction: Direction to look (in robot base frame)

        Returns:
            ActionResult
        """
        import math

        # Calculate required yaw and pitch
        yaw = math.atan2(direction.y, direction.x)
        horizontal_dist = math.sqrt(direction.x**2 + direction.y**2)
        pitch = -math.atan2(direction.z, horizontal_dist)

        # Clamp to limits
        roll_lim, pitch_lim, yaw_lim = self.get_orientation_limits()
        pitch = max(pitch_lim[0], min(pitch_lim[1], pitch))
        yaw = max(yaw_lim[0], min(yaw_lim[1], yaw))

        return self.set_body_orientation(roll=0.0, pitch=pitch, yaw=yaw)
