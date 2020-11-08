from parser import TaskmasterDaemonParser
from task import Task


if __name__ == '__main__':
    parser = TaskmasterDaemonParser.from_command_line()

    for program_name, program_params in parser.configuration.get('programs', {}).items():
        cmd = program_params.pop('cmd')
        Task(program_name, cmd, **program_params)