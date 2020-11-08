import sys


class Manager:
    programs = list()

    def __init__(self, programs):
        self.programs = programs

    def stop_all(self):
        for program in self.programs:
            for thr in program.threads:
                thr.join(.1)

    def load_tcp_command(self, request):
        command = request.get('command', '')
        args = request.get('args', list())
        with_refresh = request.get('with_refresh', False)
        response = []
        
        for program in self.programs:
            if program.name in args:
                args.remove(program.name)
                ret = program.send_command(command)

                if 'error' in ret:
                    response.append(dict(raw_output = '{}: ERROR ({})'.format(
                        ret['task'],
                        ret['message'],
                    ), **ret))
                else:
                    response.append(dict(raw_output = '{}: {}'.format(
                        ret['task'],
                        ret['message'],
                    ), **ret))

            if response and not with_refresh:
                return response if len(response) > 1 else response[0]
        
        if command.upper() == 'REFRESH' or with_refresh:
            return [{
                "task": program.name,
                "uptime": program.uptime,
                "started_processes": len(program.processes),
                "pids": [p.pid for p in program.processes],
            } for program in self.programs]
        
        if command.upper() == 'STOP_DAEMON' or with_refresh:
            self.stop_all()
            sys.exit(0)
        
        return {
            'raw_output': '%s: ERROR (no such command)' % command,
            'error': True,
            'input_request': request,
            'message': 'no such process',
        }