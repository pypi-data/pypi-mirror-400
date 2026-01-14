"""Provides packet classes for dyscom get with type operation mode"""

from .dyscom_types import DyscomGetType, DyscomGetOperationModeType
from .dyscom_get import PacketDyscomGet, PacketDyscomGetAck


class PacketDyscomGetOperationMode(PacketDyscomGet):
    """Packet for dyscom get with type operation mode"""


    def __init__(self):
        super().__init__()
        self._type = DyscomGetType.OPERATION_MODE
        self._kind = int(self._type)


class PacketDyscomGetAckOperationMode(PacketDyscomGetAck):
    """Packet for dyscom get for type operation mode acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._kind = int(DyscomGetType.OPERATION_MODE)
        self._operation_mode = DyscomGetOperationModeType.UNDEFINED

        if not data is None:
            self._operation_mode = DyscomGetOperationModeType(data[2])


    @property
    def operation_mode(self) -> DyscomGetOperationModeType:
        """Getter for operation mode"""
        return self._operation_mode
