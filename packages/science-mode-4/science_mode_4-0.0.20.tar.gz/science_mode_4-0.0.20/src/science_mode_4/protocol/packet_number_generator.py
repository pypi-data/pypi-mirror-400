"""Provides a packet number generator"""


class PacketNumberGenerator():
    """Packet number generator class that increases number for each packet by 1"""


    def __init__(self):
        self._current_number = 0


    def get_next_number(self) -> int:
        """Returns next packet number, this function modifies state of class"""
        self._current_number += 1
        # packet number is a 6-bit value
        if self._current_number > 63:
            self._current_number = 0

        return self._current_number
