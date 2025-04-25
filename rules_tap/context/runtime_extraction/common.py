from rules_tap.common import OUT_DIR

LOGGER_FORMAT = '%(asctime)s| %(message)s'

RUNTIME_DIR = OUT_DIR / 'runtime'
SQL_LOG_FILE = RUNTIME_DIR / 'sql.log'
STACK_TRACE_LOG_FILE = RUNTIME_DIR / 'stack_trace.log'
