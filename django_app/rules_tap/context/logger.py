import logging
import os
import glob
import shutil
from pathlib import Path

# Determine the base directory (django_app/rules_tap)
BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / 'log'
LOG_DIR.mkdir(parents=True, exist_ok=True)
CODE_LOG_FILE = LOG_DIR / 'code.log'
SQL_LOG_FILE = LOG_DIR / 'sql.log'
CONTEXT_FILE = LOG_DIR / 'context.txt'


# Configure the logger
logger = logging.getLogger('rules_tap.code')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(CODE_LOG_FILE)
file_handler.setLevel(logging.DEBUG)

LOGGER_FORMAT = '%(asctime)s| %(message)s'

formatter = logging.Formatter(LOGGER_FORMAT)
file_handler.setFormatter(formatter)

# Avoid adding multiple handlers if logger already has handlers
if not logger.handlers:
	logger.addHandler(file_handler) 


def reset_logs():
	if not LOG_DIR.exists():
		LOG_DIR.mkdir(parents=True, exist_ok=True)
	else:
		files = glob.glob(str(LOG_DIR / '*'))
		for f in files:
			os.remove(f)
	CODE_LOG_FILE.touch(exist_ok=True)
	SQL_LOG_FILE.touch(exist_ok=True) 