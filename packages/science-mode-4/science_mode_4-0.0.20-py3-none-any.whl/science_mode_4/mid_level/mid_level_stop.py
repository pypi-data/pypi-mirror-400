"""Provides classes for mid level Stop"""

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.protocol.types import ResultAndError


class PacketMidLevelStop(Packet):
    """Packet for mid level Stop"""

    def __init__(self):
        super().__init__()
        self._command = Commands.MID_LEVEL_STOP


class PacketMidLevelStopAck(PacketAck):
    """Packet for mid level Stop acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.MID_LEVEL_STOP_ACK
        self._result_error = ResultAndError.NO_ERROR

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
