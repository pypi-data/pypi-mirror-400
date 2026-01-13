"""
Recording wrapper for automatic telemetry capture.

Provides a simpler API than RecordingSession for cases where you
want to wrap a driver and record everything automatically.
"""

from typing import Optional
from ate.interfaces import RobotInterface
from .session import RecordingSession


class RecordingWrapper:
    """
    Wrapper that automatically records all driver interactions.

    Unlike RecordingSession (context manager), RecordingWrapper creates
    a persistent recording that captures everything until explicitly stopped.

    Usage:
        # Wrap a driver
        raw_driver = MechDogDriver(port="/dev/...")
        driver = RecordingWrapper(raw_driver, name="session_01")

        # Use driver normally - all calls are recorded
        driver.connect()
        driver.stand()
        driver.walk(Vector3.forward(), speed=0.3)
        driver.stop()
        driver.disconnect()

        # Save the recording
        driver.save_recording("session_01.demonstration")
    """

    def __init__(
        self,
        driver: RobotInterface,
        name: str = "recording",
        description: Optional[str] = None,
        auto_start: bool = True,
    ):
        """
        Initialize recording wrapper.

        Args:
            driver: Robot driver to wrap
            name: Recording name
            description: Optional description
            auto_start: Start recording immediately
        """
        self._driver = driver
        self._session = RecordingSession(
            driver,
            name=name,
            description=description,
        )

        if auto_start:
            self._session.start()

    def __getattr__(self, name: str):
        """Forward attribute access to wrapped driver."""
        return getattr(self._driver, name)

    def start_recording(self) -> None:
        """Start recording (if not already)."""
        self._session.start()

    def stop_recording(self) -> None:
        """Stop recording."""
        self._session.stop()

    def save_recording(self, path: str) -> None:
        """Save recording to file."""
        self._session.save(path)

    def get_recording_summary(self) -> str:
        """Get recording summary."""
        return self._session.summary()

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._session.is_recording

    @property
    def recording_duration(self) -> Optional[float]:
        """Get recording duration in seconds."""
        return self._session.duration

    @property
    def call_count(self) -> int:
        """Get number of recorded calls."""
        return len(self._session.calls)
