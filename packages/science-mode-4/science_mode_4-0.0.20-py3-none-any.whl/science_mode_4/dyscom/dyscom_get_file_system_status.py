"""Provides packet classes for dyscom get with type file system status"""

# from dataclasses import dataclass

from typing import NamedTuple
from .dyscom_types import DyscomGetType
from .dyscom_get import PacketDyscomGet, PacketDyscomGetAck


class DyscomGetFileSystemStatusResult(NamedTuple):
    """Helper class for dyscom get with type file system status"""
    file_system_ready: bool
    used_size: int
    free_size: int


class PacketDyscomGetFileSystemStatus(PacketDyscomGet):
    """Packet for dyscom get with type file system status"""


    def __init__(self):
        super().__init__()
        self._type = DyscomGetType.FILESYSTEM_STATUS
        self._kind = int(self._type)


class PacketDyscomGetAckFileSystemStatus(PacketDyscomGetAck):
    """Packet for dyscom get for type file system status acknowledge"""


    def __init__(self, data: bytes):
        super().__init__(data)
        self._kind = int(DyscomGetType.FILESYSTEM_STATUS)
        self._file_system_ready = False
        self._used_size = 0
        self._free_size = 0

        if not data is None:
            self._file_system_ready = bool(data[2])
            self._used_size = int.from_bytes(data[3:11], "big")
            self._free_size = int.from_bytes(data[11:19], "big")


    @property
    def file_system_ready(self) -> bool:
        """Getter for file system ready"""
        return self._file_system_ready


    @property
    def used_size(self) -> int:
        """Getter for used size"""
        return self._used_size


    @property
    def free_size(self) -> int:
        """Getter for free size"""
        return self._free_size
