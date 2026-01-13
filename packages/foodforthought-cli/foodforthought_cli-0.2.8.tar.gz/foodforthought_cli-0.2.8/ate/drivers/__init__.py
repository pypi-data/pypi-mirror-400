"""
Hardware drivers for specific robots.

Each driver implements the appropriate interfaces from ate.interfaces.

Example:
    from ate.drivers import MechDogDriver

    # Connect to MechDog
    dog = MechDogDriver(port="/dev/cu.usbserial-10")
    dog.connect()

    # Use through abstract interface
    dog.stand()
    dog.walk(Vector3.forward(), speed=0.3)
    dog.set_body_height(0.15)
    dog.stop()

    # Disconnect
    dog.disconnect()
"""

from .mechdog import MechDogDriver

__all__ = [
    "MechDogDriver",
]
