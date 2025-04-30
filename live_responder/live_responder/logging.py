import logging
import re
from colorama import init

# This means after every print statement, colorama will issue a Style.RESET_ALL
init(autoreset=True)

LOGGER_NAME = "live_responder"

ansi_escape = re.compile(r'\x1b\[[0-9;]*m')

LOG_FORMAT_STRING = '%(levelname)s - %(message)s'


class PlainFormatter(logging.Formatter):
	def format(self, record):
		raw = super().format(record)
		return ansi_escape.sub('', raw)


def setup_logger(*, log_level: int = logging.INFO, disable_color: bool = False) -> logging.Logger:
	logger = logging.getLogger(LOGGER_NAME)
	logger.setLevel(log_level)

	FormatterClass = PlainFormatter if disable_color else logging.Formatter
	
	formatter = FormatterClass(LOG_FORMAT_STRING)

	if logger.handlers:
		# Prevent adding handlers multiple times
		logger.warning("Logger already has handlers, skipping setup")
		return logger

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)
	logger.addHandler(console_handler)
	return logger

logger = setup_logger()
