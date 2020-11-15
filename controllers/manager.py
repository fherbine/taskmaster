import copy
import logging
import os

from controllers.logger import Logger
from controllers.task import Task

LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)


class Manager:
    programs = list()

    def __init__(self, programs, parser):
        self.programs = programs
        self.parser = parser

        self.log = Logger(level=LOGLEVEL)

    def stop_all(self):
        for program in self.programs:
            program.stop()

            for thr in program.threads:
                thr.join(.1)

    def _get_program_by_name(self, name):
        for program in self.programs:
            if program.name == name:
                return program

    def _remove_program_by_name(self, name):
        for program in self.programs:
            if program.name == name:
                self.programs.remove(program)

    def update(self):
        self.log.info('Received update command.')
        diff = self.parser.refresh()
        self.log.info('Affected/new tasks: %s.' % diff)
        parser = self.parser
        programs_names = [program.name for program in self.programs]
        affected = list()

        if parser.configuration.get('programs', {}):
            for program_name, _program_params in parser.configuration.get('programs', {}).items():
                program_params = copy.deepcopy(_program_params)
                if program_name in programs_names and program_name not in diff:
                    # not affected
                    continue
                elif program_name in programs_names:
                    # affected -- w/restart
                    affected.append(program_name)
                    program = self._get_program_by_name(program_name)
                    cmd = program_params.pop('cmd')
                    program.update(program_name, cmd, **program_params)
                    continue
                # start affected/new programs
                cmd = program_params.pop('cmd')
                task = Task(program_name, cmd, **program_params)
                self.programs.append(task)

                if program_name in programs_names:
                    programs_names.remove(program_name)
        
        for program_name in programs_names:
            if program_name not in diff or program_name in affected:
                continue

            program = self._get_program_by_name(program_name)
            program.stop()
            self._remove_program_by_name(program_name)
        
        return {"raw_output": "Updated tasks %s" % diff, "updated_tasks": diff}

    def load_tcp_command(self, request):
        command = request.get('command', '')
        args = request.get('args', list())
        with_refresh = request.get('with_refresh', False)
        response = []

        if command.upper() == 'UPDATE':
            ret = self.update()

            if not with_refresh:
                return ret
        
        for program in self.programs:
            if program.name in args:
                args.remove(program.name)
                ret = program.send_command(command)

                if 'error' in ret:
                    response.append(dict(raw_output='{}: ERROR ({})'.format(
                        ret['task'],
                        ret['message'],
                    ), **ret))
                else:
                    response.append(dict(raw_output='{}: {}'.format(
                        ret['task'],
                        ret['message'],
                    ), **ret))

        if response and not with_refresh:
            return response if len(response) > 1 else response[0]
        
        if command.upper() == 'REFRESH' or with_refresh:
            if args:
                return [{
                    "task": program.name,
                    "uptime": program.uptime,
                    "started_processes": len(program.processes),
                    "pids": [p.pid for p in program.processes],
                } for program in self.programs if program.name in args]
            return [{
                "task": program.name,
                "uptime": program.uptime,
                "started_processes": len(program.processes),
                "pids": [p.pid for p in program.processes],
            } for program in self.programs]
        
        if command.upper() == 'STOP_DAEMON':
            self.stop_all()
            raise Exception
        
        return {
            'raw_output': '%s: ERROR (no such command)' % command,
            'error': True,
            'input_request': request,
            'message': 'no such process',
        }