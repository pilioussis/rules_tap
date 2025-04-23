import os
import logging.config
from django.conf import settings
from django.test.runner import DiscoverRunner
from django.db import connection
from .code import track_functions
from .logger import LOG_DIR, reset_logs, LOGGER_FORMAT
from .transform import transform_logs
INJECT_CONFIG = {
	'formatters': {
        'rules_tap_format': {
            'format': LOGGER_FORMAT,
        },
    },
'loggers': {
	'django.db.backends': {
		'level': 'DEBUG',
		'handlers': ['rules_tap_file'],
	}
},
	'handlers': {
		'rules_tap_file': {
			'level': 'DEBUG',
			'class': 'logging.FileHandler',
			'filename': os.path.join(LOG_DIR, 'sql.log'),
			'formatter': 'rules_tap_format',
		}
	},
}

def get_context():
	connection.force_debug_cursor = True
	reset_logs()
	logging.config.dictConfig({
		**settings.LOGGING,
		'formatters': {
			**settings.LOGGING['formatters'],
			**INJECT_CONFIG['formatters'],
		},
		'loggers': {
			**settings.LOGGING['loggers'],
			**INJECT_CONFIG['loggers'],
		},
		'handlers': {
			**settings.LOGGING['handlers'],
			**INJECT_CONFIG['handlers'],
		},
	})
	test_runner = DiscoverRunner(verbosity=2)
	tests_to_run = [
		'org.tests.OrgTests',
		'org.tests.WorkerTests',
	]

	with track_functions() as tracker:
		test_runner.keepdb = True
		test_runner.run_tests(tests_to_run)
	
	transform_logs()

	

	