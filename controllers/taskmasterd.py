import signal
import sys

from parser import TaskmasterDaemonParser
from task import Task
from server import Server
from manager import Manager


def stop_all():
    sys.exit(0)

if __name__ == '__main__':
    parser = TaskmasterDaemonParser.from_command_line()
    programs = list()

    #signal.signal(signal.SIGINT, lambda *_: stop_all())

    for program_name, program_params in parser.configuration.get('programs', {}).items():
        cmd = program_params.pop('cmd')
        task = Task(program_name, cmd, **program_params)
        programs.append(task)

    manager = Manager(programs)
    server = Server(manager)
    server.serve()

    manager.stop_all()