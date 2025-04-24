from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import contextlib

from .sql import log_sql_to_file, sql_line_processor
from .stack_trace import log_stack_trace_info_to_file, stack_trace_line_processor
from ..common import SQL_LOG_FILE, STACK_TRACE_LOG_FILE

@dataclass
class RuntimeLogger:
	context_manager: contextlib.contextmanager
	logfile: Path
	line_processor: Callable[[str], str]

LOGGERS = [
	RuntimeLogger(
		context_manager=log_stack_trace_info_to_file,
		logfile=STACK_TRACE_LOG_FILE,
		line_processor=stack_trace_line_processor,
	),
	RuntimeLogger(
		context_manager=log_sql_to_file,
		logfile=SQL_LOG_FILE,
		line_processor=sql_line_processor,
	),
]