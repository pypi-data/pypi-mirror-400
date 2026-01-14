"""Provides a class for a null connection"""


from .connection import Connection


class NullConnection(Connection):
    """Null connection class (only for testing)"""


    def __init__(self):
        self._is_open = False


    def open(self):
        self._is_open = True


    def close(self):
        self._is_open = False


    def is_open(self) -> bool:
        return self._is_open


    def write(self, data: bytes):
        pass


    def read(self) -> bytes:
        result = []
        return bytes(result)
