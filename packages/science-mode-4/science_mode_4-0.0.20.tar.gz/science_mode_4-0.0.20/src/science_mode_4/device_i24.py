"""Provides device class representing a I24"""

from .device import Device, DeviceCapability
from .utils.connection import Connection


class DeviceI24(Device):
    """Device class for a I24 device"""

    def __init__(self, conn: Connection):
        super().__init__(conn, [DeviceCapability.GENERAL,
                                DeviceCapability.DYSCOM])
