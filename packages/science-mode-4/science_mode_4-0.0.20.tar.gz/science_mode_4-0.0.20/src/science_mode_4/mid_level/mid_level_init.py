"""Provides classes for mid level Init"""

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.utils.byte_builder import ByteBuilder


class PacketMidLevelInit(Packet):
    """Packet for mid level Init"""


    def __init__(self):
        super().__init__()
        self._command = Commands.MID_LEVEL_INIT
        self._do_stop_on_all_errors = False


    @property
    def do_stop_on_all_errors(self) -> bool:
        """Getter for do stop on all errors"""
        return self._do_stop_on_all_errors


    @do_stop_on_all_errors.setter
    def do_stop_on_all_errors(self, do_stop_on_all_errors: bool):
        """Setter for do stop on all errors"""
        self._do_stop_on_all_errors = do_stop_on_all_errors


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.append_byte(1 if self._do_stop_on_all_errors else 0)
        return bb.get_bytes()


class PacketMidLevelInitAck(PacketAck):
    """Packet for mid level Init acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.MID_LEVEL_INIT_ACK
        self._result_error = ResultAndError.NO_ERROR

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
