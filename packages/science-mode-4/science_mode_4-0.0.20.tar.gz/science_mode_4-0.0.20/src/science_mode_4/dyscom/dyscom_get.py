"""Provides packet classes for dyscom get"""

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.utils.byte_builder import ByteBuilder
from .dyscom_types import DyscomGetType


class PacketDyscomGet(Packet):
    """Packet for dyscom get, use descendants of this class"""


    def __init__(self):
        super().__init__()
        self._command = Commands.DL_GET
        self._type = DyscomGetType.BATTERY


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.append_byte(self._type)
        return bb.get_bytes()


class PacketDyscomGetAck(PacketAck):
    """Packet for dyscom get acknowledge, use descendants of this class"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.DL_GET_ACK
        self._result_error = ResultAndError.NO_ERROR
        self._type = DyscomGetType.BATTERY

        if not data is None:
            self._result_error = ResultAndError(data[0])
            self._type = DyscomGetType(data[1])


    def get_kind(self, data: bytes) -> int:
        """Get kind from data"""        
        # use type as kind
        return data[1]


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error


    @property
    def type(self) -> DyscomGetType:
        """Getter for type"""
        return self._type
