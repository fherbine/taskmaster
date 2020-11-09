import argparse
import os
import logging
import re
import signal
import subprocess
import sys

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader

from controllers.logger import Logger

LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)


def _command_checker(command_string, *_):
    if re.match(r'.*[<>&|].*', command_string):
        return False, 'Forbidden token(s) in string'
    try:
        cmd, *_ = command_string.split()
        p = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.kill()
        p.wait()
        return True, ''
    except FileNotFoundError:
        return False, 'Command unknown %s' % cmd


def _int_checker(integer, min, max, *_):
    return (True, '') if (integer >= min and integer <= max) else (False, f'number must be between {min} and {max}')


def _str_checker(string, *args):
    if args:
        return (True, '') if string.upper() in args else (False, f'{string} not in {args}')
    return True, ''


def _umask_checker(umask, *_):
    umask = str(umask)
    for c in umask:
        if int(c) not in (0, 1, 2, 3, 4, 5, 6, 7):
            return False, 'umask is not valid.'
    return True, ''


def _path_checker(path, *_):
    return (True, '') if os.path.exists(path) else (False, 'Cannot find %s' % path)


def _to_list(item):
    if isinstance(item, list) or isinstance(item, tuple):
        return item
    return [item]


def _no_check(*args):
    return True, ''


CONFIGURATION_MAPPING = {
    "cmd": {"expected_type": str, "handler": _command_checker},
    "numprocs": {"expected_type": int, "handler": _int_checker, "args": (1, 20)},
    "umask": {"expected_type": int, "handler": _umask_checker},
    "workingdir": {"expected_type": str, "handler": _path_checker},
    "autostart": {"expected_type": bool},
    "autorestart": {"expected_type": str, "handler": _str_checker, "args": ('ALWAYS', 'NEVER', 'UNEXPECTED')},
    "exitcodes": {"expected_type": (int, list, tuple), "transform": _to_list},
    "startretries": {"expected_type": int, "handler": _int_checker, "args": (1, 100)},
    "starttime": {"expected_type": int, "handler": _int_checker, "args": (0, 3600)},
    "stopsignal": {"expected_type": str, "handler": _str_checker, "args": (
        'HUP', 'INT', 'QUIT', 'ILL', 'TRAP', 'ABRT', 'EMT', 'FPE', 'KILL',
        'BUS', 'SEGV', 'SYS', 'PIPE', 'ALRM', 'TERM', 'USR1', 'USR2', 'CHLD',
        'PWR', 'WINCH', 'URG', 'POLL', 'STOP', 'TSTP', 'CONT', 'TTIN', 'TTOU',
        'VTALRM', 'PROF', 'XCPU', 'XFSZ', 'WAITING', 'LWP', 'AIO'
    )},
    "stoptime": {"expected_type": int, "handler": _int_checker, "args": (0, 20)},
    "stdout": {"expected_type": str, "handler": _path_checker},
    "stderr": {"expected_type": str, "handler": _path_checker},
    "env": {"expected_type": dict},
}

REQUIRED_PARAMS = ['cmd', ]


class ParseError(Exception):
    pass


def diff_dict(d1, d2):
    diff = list()

    for key, val in d1.items():
        if key not in d2:
            diff.append(key)
            continue

        if val != d2[key]:
            diff.append(key)

    return(diff)


class TaskmasterDaemonParser:
    """TaskmasterDeamonParser class.

    > See `supervisord`.
    """

    def __init__(self, conf_path):
        self.conf_path = conf_path

        self.log = Logger(LOGLEVEL)

        if not os.path.exists(conf_path):
            print('Unknown file or directory %s.' % conf_path)
            sys.exit(-1)

        try:
            with open(conf_path) as conf:
                self.configuration = config = yaml.load(conf, Loader=Loader)
            self.log.debug('Configuration readed: %s' % self.configuration)
        except Exception:
            raise ParseError('Unable to read configuration file %s' % conf_path)

        if 'programs' not in config or len(config) > 1:
            raise ParseError((
                'config file is invalid, '
                'bad indentation or "program" section not found.'
            ))
        self.check_configuration()

    @classmethod
    def from_command_line(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--config_file',
            '-c',
            required=True,
            type=str,
        )
        args = parser.parse_args()
        return cls(args.config_file)

    def diff(self, parser):
        return diff_dict(self.configuration['programs'], parser.configuration['programs'])

    def refresh(self):
        try:
            parser = TaskmasterDaemonParser(self.conf_path)
        except ParseError as e:
            self.log.error(e)
            os.kill(os.getpid(), signal.SIGKILL)
        diff = self.diff(parser)
        self.configuration = parser.configuration
        return diff
    
    def check_configuration(self):
        programs = self.configuration.get('programs', {})

        for program_name, parameters in programs.items():

            for rparam in REQUIRED_PARAMS:
                if rparam not in parameters:
                    raise ParseError(f'{program_name}: Missing required parameter {rparam}')

            for parameter_key, pvalue in parameters.items():

                if parameter_key not in CONFIGURATION_MAPPING:
                    raise ParseError(f'Unknown parameter "{parameter_key}" in task {program_name}.')

                parameter_mapping = CONFIGURATION_MAPPING[parameter_key]
                expected_type = _to_list(parameter_mapping['expected_type'])
                handler = parameter_mapping.get('handler', _no_check)
                transform = parameter_mapping.get('transform')
                args = parameter_mapping.get('args', list())

                if not isinstance(pvalue, tuple(expected_type)):
                    actual_type = type(pvalue)
                    raise ParseError(f'{program_name}: {parameter_key}: Incorrect type {actual_type} instead of {expected_type}.')

                handler_return, handler_msg = handler(pvalue, *args)
                if not handler_return:
                    raise ParseError(f'{program_name}: {parameter_key}: {handler_msg}.')

                if transform is not None:
                    self.configuration['programs'][program_name][parameter_key] = transform(pvalue)


if __name__ == '__main__':
    daemon = TaskmasterDaemonParser.from_command_line()