"""Provides device class representing a P24"""

from .device import Device, DeviceCapability
from .utils.connection import Connection


class DeviceP24(Device):
    """Device class for a P24 device"""

    def __init__(self, conn: Connection):
        super().__init__(conn, [DeviceCapability.GENERAL,
                                DeviceCapability.LOW_LEVEL,
                                DeviceCapability.MID_LEVEL])
