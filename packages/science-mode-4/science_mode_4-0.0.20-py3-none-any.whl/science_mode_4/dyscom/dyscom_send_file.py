"""Provides packet classes for dyscom send file"""

import struct

from science_mode_4.protocol.commands import Commands
from science_mode_4.protocol.packet import Packet, PacketAck
from science_mode_4.utils.byte_builder import ByteBuilder


class PacketDyscomSendFile(PacketAck):
    """Packet for dyscom send file ack (this is technically not an acknowledge, but it is handled as such,
    because it is send automatically from device). This should probably never be used on PC side"""


    _unpack_func = struct.Struct(">IH").unpack


    def __init__(self, data: bytes):
        super().__init__(data)
        self._command = Commands.DL_SEND_FILE
        self._block_number = 0
        self._block_size = 0
        self._data: bytes = bytes()

        if not data is None:
            self._block_number, self._block_size = PacketDyscomSendFile._unpack_func(data[0:6])
            self._data = data[6:6+self._block_size]


    @property
    def block_number(self) -> int:
        """Getter for block number"""
        return self._block_number


    @property
    def block_size(self) -> int:
        """Getter for block size"""
        return self._block_size


    @property
    def data(self) -> bytes:
        """Getter for data"""
        return self._data


class PacketDyscomSendFileAck(Packet):
    """Packet for dyscom send file acknowledge (this is technically not a packet, but it is handled as such,
    because it is send from PC to device)"""


    def __init__(self, block_number: int = 0):
        super().__init__()
        self._command = Commands.DL_SEND_FILE_ACK
        self._block_number = block_number


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.append_value(self._block_number, 4, True)
        return bb.get_bytes()
