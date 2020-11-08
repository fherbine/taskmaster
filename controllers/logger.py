import logging


class Termcolors:
    REGULAR = '\033[0m'
    BOLD = '\033[1m'

    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGT = '\033[35m'
    CYAN = '\033[36m'
    LRED = '\033[91m'
    LGREEN = '\033[92m'
    LYLW = '\033[93m'
    LBLUE = '\033[94m'
    LMAGT = '\033[95m'
    LCYAN = '\033[96m'


class Logger:
    def __init__(self, level=logging.WARNING, prefix=''):
        self.prefix = prefix
        self.level = level

    def _message(self, msg, level='', color=Termcolors.REGULAR, bold=False, **kw):
        print(self.prefix, end='')
        if level:
            print(color + (Termcolors.BOLD if bold else '') + '[%s] ' % level.upper() + Termcolors.REGULAR, end='')
        print(msg)
    
    def info(self, msg, **kwargs):
        if self.level > logging.INFO:
            return
        self._message(msg, level='info', color=Termcolors.BLUE, bold=True, **kwargs)
    
    def success(self, msg, **kwargs):
        if self.level > logging.INFO:
            return
        self._message(msg, level='ok', color=Termcolors.LGREEN, bold=True, **kwargs)
    
    def warning(self, msg, **kwargs):
        if self.level > logging.WARNING:
            return
        self._message(msg, level='warning', color=Termcolors.YELLOW, bold=True, **kwargs)

    def error(self, msg, **kwargs):
        if self.level > logging.ERROR:
            return
        self._message(msg, level='error', color=Termcolors.LRED, bold=True, **kwargs)
    
    def debug(self, msg, **kwargs):
        if self.level > logging.DEBUG:
            return
        self._message(msg, level='debug', color=Termcolors.MAGT, bold=True, **kwargs)