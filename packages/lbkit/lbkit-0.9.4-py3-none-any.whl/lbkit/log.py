import logging
import inspect
import os
import sys
from lbkit.misc import Color

class Logger(logging.getLoggerClass()):

    def __init__(self, *args, **kwargs):
        super(Logger, self).__init__(*args, **kwargs)
        self.logenv = os.environ.get("LOG")
        if self.logenv is None:
            formatter = logging.Formatter('%(message)s')
            self._set_handler(logging.INFO, formatter)
        else:
            formatter = logging.Formatter('%(asctime)s %(message)s')
            if self.logenv == "info":
                self._set_handler(logging.INFO, formatter)
            elif self.logenv == "warn":
                self._set_handler(logging.WARNING, formatter)
            elif self.logenv != "error":
                self._set_handler(logging.DEBUG, formatter)
        self._set_handler(logging.ERROR, formatter)

    def _set_handler(self, level, formatter):
        if level == logging.ERROR:
            handler = logging.StreamHandler()
        else:
            handler = logging.StreamHandler(sys.stdout)
            handler.addFilter(lambda record: record.levelno < logging.ERROR)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        self.addHandler(handler)


    def error(self, msg, *args, **kwargs):
        if self.logenv:
            uptrace = kwargs.get("uptrace", 0)
            uptrace += 1
            stack = inspect.stack()[uptrace]
            filename = os.path.basename(stack.filename)
            msg = "ERROR: " + f"[{filename}:{stack.lineno}] " + Color.RED + msg + Color.RESET_ALL
        else:
            msg = "ERROR: " + Color.RED + msg + Color.RESET_ALL
        kwargs.pop("uptrace", None)
        super(Logger, self).error(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.logenv:
            uptrace = kwargs.get("uptrace", 0)
            uptrace += 1
            stack = inspect.stack()[uptrace]
            filename = os.path.basename(stack.filename)
            msg = "DEBUG: " + f"[{filename}:{stack.lineno}] " + msg
        else:
            msg = "DEBUG: " + msg
        kwargs.pop("uptrace", None)
        super(Logger, self).debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.logenv:
            uptrace = kwargs.get("uptrace", 0)
            uptrace += 1
            stack = inspect.stack()[uptrace]
            filename = os.path.basename(stack.filename)
            msg = "INFO:  " + f"[{filename}:{stack.lineno}] " + msg
        else:
            msg = "INFO:  " + msg
        kwargs.pop("uptrace", None)
        super(Logger, self).info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        if self.logenv:
            uptrace = kwargs.get("uptrace", 0)
            uptrace += 1
            stack = inspect.stack()[uptrace]
            filename = os.path.basename(stack.filename)
            msg = "WARN:  " + f"[{filename}:{stack.lineno}] " + Color.YELLOW + msg + Color.RESET_ALL
        else:
            msg = "WARN:  " + Color.YELLOW + msg + Color.RESET_ALL
        kwargs.pop("uptrace", None)
        super(Logger, self).warning(msg, *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        if self.logenv:
            uptrace = kwargs.get("uptrace", 0)
            uptrace += 1
            stack = inspect.stack()[uptrace]
            filename = os.path.basename(stack.filename)
            msg = "SUCC:  " + f"[{filename}:{stack.lineno}] " + Color.GREEN + msg + Color.RESET_ALL
        else:
            msg = "SUCC:  " + Color.GREEN + msg + Color.RESET_ALL
        kwargs.pop("uptrace", None)
        super(Logger, self).info(msg, *args, **kwargs)

