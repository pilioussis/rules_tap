import shutil
from contextlib import ExitStack
from .chunk_from_test_case import chunk_time_tracker, run_tests
from .common import RUNTIME_DIR
from .logs_to_chunks import create_chunks
from .config import get_loggers

def clear_workdir():
	if RUNTIME_DIR.exists():
		shutil.rmtree(RUNTIME_DIR)
	RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

def runtime_extraction(config):
	clear_workdir()

	runtime_loggers = get_loggers(config=config)

	with ExitStack() as stack:
		# Start listening for start/stop signals
		time_chunks = stack.enter_context(chunk_time_tracker())

		for logger in runtime_loggers:
			stack.enter_context(logger.context_manager(logger.logfile, **logger.logger_args))

		# Run code to start capturing logs
		run_tests()

	# Pluck useful sections in the logs to embeddable chunks
	create_chunks(runtime_loggers, time_chunks)

	