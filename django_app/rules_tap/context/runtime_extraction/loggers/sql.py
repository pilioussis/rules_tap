import logging.config
from pathlib import Path
from contextlib import contextmanager
from django.conf import settings
from django.db import connection
from rules_tap.context.runtime_extraction.common import LOGGER_FORMAT


def get_net_config(prev_config: dict, logfile: Path):
    inject_config = {
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
                'filename': logfile,
                'formatter': 'rules_tap_format',
            }
        },
    }
        
    new = {
        **prev_config,
        'formatters': {
            **settings.LOGGING['formatters'],
            **inject_config['formatters'],
        },
        'loggers': {
            **settings.LOGGING['loggers'],
            **inject_config['loggers'],
        },
        'handlers': {
            **settings.LOGGING['handlers'],
            **inject_config['handlers'],
        },
    }
    return new


@contextmanager
def log_sql_to_file(logfile: Path):
    # Store previous values to restore them on context manager exit
    prev_config = settings.LOGGING
    prev_force_debug_cursor = connection.force_debug_cursor

    new_config = get_net_config(settings.LOGGING, logfile)
    logging.config.dictConfig(new_config)
    connection.force_debug_cursor = True
        
    try:
        yield
    finally:
        logging.config.dictConfig(prev_config)
        connection.force_debug_cursor = prev_force_debug_cursor

def sql_line_processor(line: str):

    if not any(k in line for k in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
        # Ignore statements like COMMIT and SAVEPOINT and ALTER
        return ''
    return line[9:]
