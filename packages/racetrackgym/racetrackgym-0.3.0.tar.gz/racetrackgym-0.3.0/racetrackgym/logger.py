import logging
from typing import ClassVar


class RTLogger:
    _logger = None
    _LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
    _DATE_FORMAT = "%H:%M:%S"

    class ColorfulFormatter(logging.Formatter):
        NC = "\033[0m"
        BOLD = "\033[1m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        CYAN = "\033[96m"
        GRAY = "\033[90m"

        FORMATS: ClassVar[dict] = {
            logging.DEBUG: GRAY + "[%(asctime)s] [%(levelname)s] %(message)s" + NC,
            logging.INFO: CYAN + "[%(asctime)s] [%(levelname)s] %(message)s" + NC,
            logging.WARNING: YELLOW + BOLD + "[%(asctime)s] [%(levelname)s] %(message)s" + NC,
            logging.ERROR: RED + BOLD + "[%(asctime)s] [%(levelname)s] %(message)s" + NC,
            logging.CRITICAL: RED + BOLD + "[%(asctime)s] [%(levelname)s] %(message)s" + NC,
        }

        def format(self, record):
            log_fmt = RTLogger.ColorfulFormatter.FORMATS.get(
                record.levelno,
                RTLogger.ColorfulFormatter.GRAY
                + RTLogger._LOGGING_FORMAT
                + RTLogger.ColorfulFormatter.NC,
            )
            formatter = logging.Formatter(log_fmt, datefmt=RTLogger._DATE_FORMAT)
            return formatter.format(record)

    @staticmethod
    def get_logger():
        if RTLogger._logger is None:
            RTLogger._logger = logging.getLogger(__name__)
            RTLogger._logger.setLevel(logging.INFO)
            stdout_handler = logging.StreamHandler()

            RTLogger._logger.addHandler(stdout_handler)
        return RTLogger._logger

    @staticmethod
    def set_colorize(colorize: bool = False):
        new_formatter = (
            RTLogger.ColorfulFormatter()
            if colorize
            else logging.Formatter(RTLogger._LOGGING_FORMAT, datefmt=RTLogger._DATE_FORMAT)
        )
        RTLogger._logger.handlers[0].setFormatter(new_formatter)
