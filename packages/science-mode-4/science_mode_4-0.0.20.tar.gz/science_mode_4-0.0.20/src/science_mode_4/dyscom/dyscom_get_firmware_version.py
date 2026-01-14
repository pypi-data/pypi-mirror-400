"""Provides packet classes for dyscom get with type firmware version"""

from .dyscom_types import DyscomGetType
from .dyscom_helper import DyscomHelper
from .dyscom_get import PacketDyscomGet, PacketDyscomGetAck


class PacketDyscomGetFirmwareVersion(PacketDyscomGet):
    """Packet for dyscom get with type firmware version"""


    def __init__(self):
        super().__init__()
        self._type = DyscomGetType.FIRMWARE_VERSION
        self._kind = int(self._type)


class PacketDyscomGetAckFirmwareVersion(PacketDyscomGetAck):
    """Packet for dyscom get for type firmware version acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._kind = int(DyscomGetType.FIRMWARE_VERSION)
        self._firmware_version = ""

        if not data is None:
            self._firmware_version = DyscomHelper.bytes_to_str(data[2:130], 128)


    @property
    def firmware_version(self) -> str:
        """Getter for firmware version"""
        return self._firmware_version
