from contextlib import ExitStack
from rules_tap.common import ContextConfig
from .chunk_from_test_case import chunk_time_tracker, run_tests
from .logs_to_chunks import create_chunks
from .loggers import get_loggers


def runtime_extraction(config: ContextConfig):
	runtime_loggers = get_loggers(config=config)

	with ExitStack() as stack:
		# Start listening for start/stop signals
		time_chunks = stack.enter_context(chunk_time_tracker())

		# Enable loggers for each type (SQL statements & Function traces)
		for logger in runtime_loggers:
			stack.enter_context(logger.context_manager(logger.logfile, **logger.logger_args))

		# Run code to start logging/capturing context
		run_tests()

	for t in time_chunks:
		print(t)

	# Pluck useful sections in the logs to embeddable chunks
	create_chunks(config, runtime_loggers, time_chunks)

	