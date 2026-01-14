"""Provides packet classes for dyscom sys"""

from typing import NamedTuple

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.utils.byte_builder import ByteBuilder
from .dyscom_types import DyscomSysState, DyscomSysType
from .dyscom_helper import DyscomHelper


class DyscomSysResult(NamedTuple):
    """Helper class for dyscom sys result"""
    sys_type: DyscomSysType
    state: DyscomSysState
    filename: str


class PacketDyscomSys(Packet):
    """Packet for dyscom sys"""


    def __init__(self, sys_type: DyscomSysType = DyscomSysType.UNDEFINED, filename: str = ""):
        super().__init__()
        self._command = Commands.DL_SYS
        self._sys_type = sys_type
        self._filename = filename


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.append_bytes(DyscomHelper.str_to_bytes(self._filename, 128))
        bb.append_byte(self._sys_type)
        return bb.get_bytes()


class PacketDyscomSysAck(PacketAck):
    """Packet for dyscom sys"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.DL_SYS_ACK
        self._result_error = ResultAndError.NO_ERROR
        self._sys_type = DyscomSysType.UNDEFINED
        self._state = DyscomSysState.UNDEFINED
        self._filename = ""

        if not data is None:
            self._result_error = ResultAndError(data[0])
            self._sys_type = DyscomSysType(data[1])
            self._state = DyscomSysState(data[2])
            self._filename = DyscomHelper.bytes_to_str(data[3:131], 128)


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error


    @property
    def sys_type(self) -> DyscomSysType:
        """Getter for sys_type"""
        return self._sys_type


    @property
    def state(self) -> DyscomSysState:
        """Getter for state"""
        return self._state


    @property
    def filename(self) -> str:
        """Getter for _filename"""
        return self._filename
