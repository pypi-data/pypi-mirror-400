"""Provides packet classes for dyscom get with type list of measurement meta info"""

from .dyscom_types import DyscomGetType
from .dyscom_get import PacketDyscomGet, PacketDyscomGetAck


class PacketDyscomGetListOfMeasurementMetaInfo(PacketDyscomGet):
    """Packet for dyscom get with type list of measurement meta info"""


    def __init__(self):
        super().__init__()
        self._type = DyscomGetType.LIST_OF_MEASUREMENT_META_INFO
        self._kind = int(self._type)


class PacketDyscomGetAckListOfMeasurementMetaInfo(PacketDyscomGetAck):
    """Packet for dyscom get for type list of measurement meta info acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._kind = int(DyscomGetType.LIST_OF_MEASUREMENT_META_INFO)
        self._number_of_measurements = 0

        if not data is None:
            self._number_of_measurements = int.from_bytes(data[2:4], "big")


    @property
    def number_of_measurements(self) -> int:
        """Getter for number of measurements"""
        return self._number_of_measurements
