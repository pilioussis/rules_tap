import logging.config
from pathlib import Path
from contextlib import contextmanager
from django.db import connection
from django.db.backends.utils import CursorWrapper
from rules_tap.common import LOGGER_FORMAT


def monkey_patch_with_logger(logfile: Path):
    logger = logging.getLogger('rules_tap.context.runtime_extraction.sql')
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(logfile)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(LOGGER_FORMAT)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # patch execute
    CursorWrapper._orig_execute = CursorWrapper.execute
    def execute(self, sql, params=None):
        logger.debug("SQL template: %s", sql)
        return CursorWrapper._orig_execute(self, sql, params)
    CursorWrapper.execute = execute

    # patch executemany
    CursorWrapper._orig_executemany = CursorWrapper.executemany
    def executemany(self, sql, param_list):
        logger.debug("SQL template (many): %s", sql)
        return CursorWrapper._orig_executemany(self, sql, param_list)
    CursorWrapper.executemany = executemany


@contextmanager
def log_sql_to_file(logfile: Path):
    # Store previous values to restore them on context manager exit
    prev_force_debug_cursor = connection.force_debug_cursor

    monkey_patch_with_logger(logfile)

    connection.force_debug_cursor = True
        
    try:
        yield
    finally:
        connection.force_debug_cursor = prev_force_debug_cursor


def sql_line_processor(line: str):

    if not any(k in line for k in ['SELECT']):
        # Ignore statements like COMMIT and SAVEPOINT and ALTER
        return ''
    if not 'SQL template:' in line:
        return ''
    return line[15:]
