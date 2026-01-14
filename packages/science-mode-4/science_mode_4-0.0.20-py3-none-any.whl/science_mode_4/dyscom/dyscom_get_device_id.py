"""Provides packet classes for dyscom get with type device id"""

from .dyscom_types import DyscomGetType
from .dyscom_helper import DyscomHelper
from .dyscom_get import PacketDyscomGet, PacketDyscomGetAck


class PacketDyscomGetDeviceId(PacketDyscomGet):
    """Packet for dyscom get with type device id"""


    def __init__(self):
        super().__init__()
        self._type = DyscomGetType.DEVICE_ID
        self._kind = int(self._type)


class PacketDyscomGetAckDeviceId(PacketDyscomGetAck):
    """Packet for dyscom get for type device id acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._kind = int(DyscomGetType.DEVICE_ID)
        self._device_id = ""

        if not data is None:
            self._device_id = DyscomHelper.bytes_to_str(data[2:130], 128)


    @property
    def device_id(self) -> str:
        """Getter for device id"""
        return self._device_id
