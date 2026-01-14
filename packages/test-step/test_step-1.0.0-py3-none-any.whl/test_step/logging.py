#  Copyright (c) 2026 CUJO LLC

import logging
from logging import Logger

TRACE_NUM = 9
logging.addLevelName(TRACE_NUM, "TRACE")


def is_trace_enabled(logger: Logger):
    return logger.isEnabledFor(TRACE_NUM)


def trace(logger: Logger, message: str, *args, **kws):
    if is_trace_enabled(logger):
        # Yes, logger takes its '*args' as 'args'.
        # noinspection PyProtectedMember
        logger._log(TRACE_NUM, message, args, **kws)


default_log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default_handler': {
            'class': 'logging.StreamHandler',
            'level': 'TRACE',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'test_step': {
            'handlers': ['default_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'tests': {
            'handlers': ['default_handler'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
