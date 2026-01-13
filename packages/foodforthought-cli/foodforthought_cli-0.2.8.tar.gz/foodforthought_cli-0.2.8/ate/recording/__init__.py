"""
Telemetry recording system for capturing robot demonstrations.

Records all interface method calls as transferable data that can be:
- Uploaded to FoodforThought
- Labeled by humans (task segmentation)
- Used to train policies
- Replayed on different hardware

Example:
    from ate.drivers import MechDogDriver
    from ate.recording import RecordingSession

    dog = MechDogDriver(port="/dev/cu.usbserial-10")
    dog.connect()

    # Record a demonstration
    with RecordingSession(dog, name="pickup_toy") as session:
        dog.stand()
        dog.walk(Vector3.forward(), speed=0.3)
        time.sleep(2)
        dog.stop()

    # Save the recording
    session.save("pickup_toy.demonstration")

    # Later: upload to FoodforThought
    session.upload()
"""

from .session import RecordingSession, RecordedCall
from .wrapper import RecordingWrapper
from .demonstration import Demonstration, load_demonstration
from .upload import DemonstrationUploader, upload_demonstration

__all__ = [
    "RecordingSession",
    "RecordedCall",
    "RecordingWrapper",
    "Demonstration",
    "load_demonstration",
    "DemonstrationUploader",
    "upload_demonstration",
]
