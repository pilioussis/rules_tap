import shutil
from contextlib import ExitStack
from django.test.runner import DiscoverRunner
from .loggers import LOGGERS
from .chunk_time_tracker import chunk_time_tracker
from .common import RUNTIME_DIR
from .create_chunks import create_chunks


def runtime_extraction():
	test_runner = DiscoverRunner(verbosity=2)
	tests_to_run = [
		'org.tests',
	]

	if RUNTIME_DIR.exists():
		shutil.rmtree(RUNTIME_DIR)
	RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

	with ExitStack() as stack:
		time_chunks = stack.enter_context(chunk_time_tracker())
		for logger in LOGGERS:
			stack.enter_context(logger.context_manager(logger.logfile))

		test_runner.keepdb = True
		test_runner.run_tests(tests_to_run)

	create_chunks(time_chunks)

	