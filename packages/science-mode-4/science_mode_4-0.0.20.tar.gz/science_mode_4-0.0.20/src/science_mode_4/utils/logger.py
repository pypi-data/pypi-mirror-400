"""Provides a logger"""

import logging


class Logger:
    """Singleton for custom logger. By default a StreamHandler with a custom formatter is added
    and log level set to INFO"""

    _instance = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            # because __init__ would be called every time we use Logger, initialize everything here
            cls._logger = logging.getLogger("science_mode_4")
            cls._console_handler = None
            cls._initialize(cls)
        return cls._instance


    @property
    def logger(self) -> logging.Logger:
        """Getter for logger"""
        return self._logger


    def _initialize(self):
        self._logger.setLevel(logging.INFO)

        formatter = logging.Formatter("{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")

        self._console_handler = logging.StreamHandler()
        self._console_handler.setFormatter(formatter)
        self._logger.addHandler(self._console_handler)



def logger() -> logging.Logger:
    """Shortcut to access custom logger"""
    return Logger().logger
