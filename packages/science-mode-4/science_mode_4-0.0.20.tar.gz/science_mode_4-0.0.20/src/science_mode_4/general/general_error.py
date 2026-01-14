"""Provides classes for general Error"""

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.packet import PacketAck
from science_mode_4.protocol.types import ResultAndError


class PacketGeneralError(PacketAck):
    """Packet for general Error"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.GENERAL_ERROR
        self._result_error = ResultAndError.NO_ERROR

        if not data is None:
            self._result_error = ResultAndError(data[0])


    @property
    def result_error(self) -> ResultAndError:
        """Getter for ResultError"""
        return self._result_error
