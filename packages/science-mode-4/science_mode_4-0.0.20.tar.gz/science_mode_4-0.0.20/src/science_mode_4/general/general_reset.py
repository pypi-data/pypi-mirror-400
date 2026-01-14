"""Provides classes for general Reset"""

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.protocol.types import ResultAndError


class PacketGeneralReset(Packet):
    """Packet for general Reset"""


    def __init__(self):
        super().__init__()
        self._command = Commands.RESET


class PacketGeneralResetAck(PacketAck):
    """Packet for general Reset acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.RESET_ACK
        self._result_error = ResultAndError.NO_ERROR

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
