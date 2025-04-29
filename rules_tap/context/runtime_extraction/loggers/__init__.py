from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
import contextlib
from rules_tap.common import ContextConfig
from .sql import log_sql_to_file, sql_line_processor
from .stack_trace import log_stack_trace_info_to_file, stack_trace_line_processor

@dataclass
class RuntimeLogger:
	context_manager: contextlib.contextmanager
	logfile: Path
	line_processor: Callable[[str], str]
	logger_args: dict = field(default_factory=dict)
	

def get_loggers(config: ContextConfig) -> list[RuntimeLogger]:
	return [
		RuntimeLogger(
			context_manager=log_stack_trace_info_to_file,
			logger_args=dict(module_names=config.module_names),
			logfile=config.stack_trace_log_file,
			line_processor=stack_trace_line_processor,
		),
		RuntimeLogger(
			context_manager=log_sql_to_file,
			logfile=config.sql_log_file,
			line_processor=sql_line_processor,
		),
	]