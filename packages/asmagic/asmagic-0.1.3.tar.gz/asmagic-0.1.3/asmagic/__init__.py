"""
asmagic - Read Data from asMagic App

A Python library for subscribing to AR and IMU sensor data streams.

Example - AR Data:
    >>> from asmagic import ARDataSubscriber
    >>> 
    >>> sub = ARDataSubscriber("192.168.1.100")
    >>> 
    >>> # Get data - super simple!
    >>> data = sub.get()
    >>> if data:
    ...     print(data.timestamp)
    ...     print(data.velocity)
    ...     print(data.local_pose)
    >>> 
    >>> sub.close()

Example - IMU Data:
    >>> from asmagic import IMUDataSubscriber
    >>> 
    >>> sub = IMUDataSubscriber("192.168.1.100")
    >>> 
    >>> for data in sub:
    ...     print(data.accelerometer)
    ...     print(data.gyroscope)
"""

__version__ = "0.1.3"
__author__ = "ASMagic Team"

# Main exports
from .arDataSubscriber import ARDataSubscriber
from .imuDataSubscriber import IMUDataSubscriber

__all__ = [
    "ARDataSubscriber",
    "IMUDataSubscriber",
    "__version__",
]

