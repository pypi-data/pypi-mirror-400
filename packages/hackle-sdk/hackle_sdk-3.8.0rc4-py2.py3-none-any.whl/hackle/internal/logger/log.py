from hackle.logger import adapt_logger, NoOpLogger


class Log(object):
    __GLOBAL_LOGGER = NoOpLogger().logger

    @staticmethod
    def initialize(logger):
        if logger is not None:
            Log.__GLOBAL_LOGGER = adapt_logger(logger)

    @staticmethod
    def get():
        """
        :rtype: logging.Logger 
        """
        return Log.__GLOBAL_LOGGER
