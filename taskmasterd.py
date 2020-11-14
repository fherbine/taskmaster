import copy
import logging
import os
import signal
import sys

from controllers.parser import (
    ParseError,
    TaskmasterDaemonParser,
)
from controllers.task import Task
from controllers.server import Server
from controllers.manager import Manager
from controllers.logger import Logger

LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)


if __name__ == '__main__':
    logger = Logger(level=LOGLEVEL)

    try:
        logger.info('Parsing input configuration...', end='')
        parser = TaskmasterDaemonParser.from_command_line()
    except ParseError as e:
        print("")
        logger.error(e)
        sys.exit(-1)

    logger.success('')
    logger.debug('Configuration retrieved: %s' % parser.configuration)
    programs = list()

    for program_name, program_params in parser.configuration.get('programs', {}).items():
        params = copy.deepcopy(program_params)
        cmd = params.pop('cmd')
        task = Task(program_name, cmd, **params)
        programs.append(task)

    logger.success('Tasks initialized.')
    manager = Manager(programs, parser)
    signal.signal(signal.SIGHUP, lambda *_: manager.load_tcp_command(
        {"command": "update"}
    ))

    logger.info('Start server on `localhost:9998`')
    server = Server(manager)
    try:
        server.serve()
    except OSError as e:
        if e.errno == 98:
            logger.error('Address *:9998 already in use.')
        else:
            raise
    except Exception:
        raise

    manager.stop_all()