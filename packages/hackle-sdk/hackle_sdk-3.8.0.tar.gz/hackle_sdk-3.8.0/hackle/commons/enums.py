import logging


class Default(object):
    SDK_URL = 'https://sdk.hackle.io'
    EVENT_URL = 'https://event.hackle.io'
    MONITORING_URL = 'https://monitoring.hackle.io'


class LogLevels(object):
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
