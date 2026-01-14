"""Provides packet classes for dyscom get with type file info"""

from typing import NamedTuple

from science_mode_4.utils.byte_builder import ByteBuilder
from .dyscom_types import DyscomGetType
from .dyscom_helper import DyscomHelper
from .dyscom_get import PacketDyscomGet, PacketDyscomGetAck


class DyscomGetFileInfoResult(NamedTuple):
    """Helper class for dyscom get file info"""
    filename: str
    filesize: int
    checksum: int


class PacketDyscomGetFileInfo(PacketDyscomGet):
    """Packet for dyscom get with type file info"""


    def __init__(self, filename: str = ""):
        super().__init__()
        self._type = DyscomGetType.FILE_INFO
        self._kind = int(self._type)
        self._filename = filename


    def get_data(self) -> bytes:
        bb = ByteBuilder()
        bb.append_bytes(super().get_data())
        bb.append_bytes(DyscomHelper.str_to_bytes(self._filename, 128))
        # file size
        bb.append_value(0, 4, True)
        # checksum
        bb.append_value(0, 2, True)
        return bb.get_bytes()


class PacketDyscomGetAckFileInfo(PacketDyscomGetAck):
    """Packet for dyscom get for type file info acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._kind = int(DyscomGetType.FILE_INFO)
        self._filename = ""
        self._filesize = 0
        self._checksum = 0

        if not data is None:
            self._filename = DyscomHelper.bytes_to_str(data[2:130], 128)
            self._filesize = int.from_bytes(data[130:134], "big")
            self._checksum = int.from_bytes(data[134:136], "big")


    @property
    def filename(self) -> str:
        """Getter for filename"""
        return self._filename


    @property
    def filesize(self) -> int:
        """Getter for filesize"""
        return self._filesize


    @property
    def checksum(self) -> int:
        """Getter for checksum"""
        return self._checksum
