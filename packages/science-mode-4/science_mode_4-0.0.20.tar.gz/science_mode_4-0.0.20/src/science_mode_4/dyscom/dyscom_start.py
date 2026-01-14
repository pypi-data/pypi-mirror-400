"""Provides packet classes for dyscom start"""

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.types import ResultAndError
from science_mode_4.protocol.packet import Packet, PacketAck


class PacketDyscomStart(Packet):
    """Packet for dyscom start"""


    def __init__(self):
        super().__init__()
        self._command = Commands.DL_START


class PacketDyscomStartAck(PacketAck):
    """Packet for dyscom start acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.DL_START_ACK
        self._result_error = ResultAndError.NO_ERROR

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
