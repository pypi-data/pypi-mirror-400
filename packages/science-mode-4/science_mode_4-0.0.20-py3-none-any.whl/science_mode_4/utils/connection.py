"""Provides a base class for a connection"""

from abc import ABC, abstractmethod

from .logger import logger


class Connection(ABC):
    """Abstract base class for connection"""


    @abstractmethod
    def open(self):
        """Open connection"""


    @abstractmethod
    def close(self):
        """Close connection"""


    @abstractmethod
    def is_open(self) -> bool:
        """Checks if connection is open"""


    def write(self, data: bytes):
        """Write data to connection"""
        logger().debug("Outgoing data, length: %d, bytes: %s", len(data), data.hex(" ").upper())


    def read(self) -> bytes:
        """Read all data from connection"""
        result = self._read_intern()
        if len(result) > 0:
            logger().debug("Incoming data, length: %d, bytes: %s", len(result), result.hex(" ").upper())
        return result


    @abstractmethod
    def clear_buffer(self):
        """Clear buffer from connection"""


    @abstractmethod
    def _read_intern(self):
        """Read all data from connection"""
