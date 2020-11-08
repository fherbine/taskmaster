import copy
import logging
import os
import signal
import sys

from parser import TaskmasterDaemonParser
from task import Task
from server import Server
from manager import Manager
from logger import Logger

LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)


if __name__ == '__main__':
    logger = Logger(level=LOGLEVEL)
    logger.info('Parsing input configuration...', end='')
    parser = TaskmasterDaemonParser.from_command_line()
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
    logger.info('Start server on `localhost:9998`')
    server = Server(manager)
    server.serve()

    manager.stop_all()