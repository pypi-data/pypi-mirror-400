import os
import logging

_DEFAULT_LOG_LEVEL = 2

def _get_log_level(level):
    _LOG_LEVELS = {
        5: logging.DEBUG,
        4: logging.DEBUG,
        3: logging.INFO,
        2: logging.WARNING,
        1: logging.ERROR
    }

    try:
        level = int(level)
        return _LOG_LEVELS[level]
    except:
        logging.getLogger().error(
            "BLACKFIRE_LOG_LEVEL is set to %s however it should be a number between 1 and 4 (1: error, 2: warning, 3: info, 4: debug). Default is '%d'." % \
                (level, _DEFAULT_LOG_LEVEL)
        )
        return _LOG_LEVELS[_DEFAULT_LOG_LEVEL]

def _get_log_handler():
    log_file = os.environ.get('BLACKFIRE_LOG_FILE')

    formatter_info = "%(asctime)s %(levelname)s [pid:%(process)d, tid:%(thread)d] [%(name)s] "

    formatter_info += "[%(filename)s:%(lineno)d] - "
    formatter_info += "%(message).8192s"
    formatter = logging.Formatter(formatter_info)

    stderr_log_handler = logging.StreamHandler()
    stderr_log_handler.setFormatter(formatter)

    log_handler = stderr_log_handler  # default logger is stderr
    if log_file and log_file != "stderr":
        log_handler = logging.FileHandler(log_file, 'a')
        log_handler.setFormatter(formatter)

    return log_handler

_log_handler = _get_log_handler()
_log_level= _get_log_level(os.environ.get('BLACKFIRE_LOG_LEVEL', _DEFAULT_LOG_LEVEL))

def get_logger(name):
    logger = logging.getLogger(name)

    logger.setLevel(_log_level)
    logger.addHandler(_log_handler)

    return logger

# This function is used to bridge ddtrace logging to blackfire_conprof logging.
def bridge_ddtrace_logging():
    logger_dict = logging.root.manager.loggerDict

    for logger_name, logger_obj in logger_dict.items():
        if logger_name.startswith('ddtrace.profiling'):
            if isinstance(logger_obj, logging.Logger):
                logger_obj.addHandler(_log_handler)
                logger_obj.setLevel(_log_level)
