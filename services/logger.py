import logging
from interfaces.i_logger import ILogger

class StructuredLogger(ILogger):
    def __init__(self, name: str = "Imobiliarias"):
        self._logger = logging.getLogger(name)
        
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def info(self, msg: str, **kwargs):
        extra_info = f" | {kwargs}" if kwargs else ""
        self._logger.info(f"{msg}{extra_info}")

    def error(self, msg: str, exc: Exception, **kwargs):
        extra_info = f" | {kwargs}" if kwargs else ""
        self._logger.error(f"{msg}{extra_info}", exc_info=exc)