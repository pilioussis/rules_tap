import logging
import os
import glob
import shutil
from pathlib import Path

# Determine the base directory (django_app/rules_tap)
OUTPUT_DIR = Path(__file__).resolve().parents[1] / 'out'
LOG_DIR = OUTPUT_DIR / 'log'
QUERY_DIR = OUTPUT_DIR / 'query'
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

def clear_dir(dir: Path):
	if not dir.exists():
		dir.mkdir(parents=True, exist_ok=True)
	else:
		files = glob.glob(str(dir / '*'))
		for f in files:
			os.remove(f)

def reset_logs():
	clear_dir(LOG_DIR)
	clear_dir(QUERY_DIR)
	CODE_LOG_FILE.touch(exist_ok=True)
	SQL_LOG_FILE.touch(exist_ok=True) 