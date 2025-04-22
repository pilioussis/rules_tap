import os
from django.conf import settings
from django.test.runner import DiscoverRunner
import logging.config
from org.models import OrgQuerySet, Org
from .code import track_functions
from .logger import LOG_DIR, reset_logs, LOGGER_FORMAT

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
	# import inspect
	# print(OrgQuerySet.viewable)
	# print(Org.objects.viewable)
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
	tests_to_run = ['org.tests.OrgTests']

	with track_functions() as tracker:
		test_runner.run_tests(tests_to_run)
		for k, v in tracker.get_results().items():
			print(f"{k}: {v}")
	