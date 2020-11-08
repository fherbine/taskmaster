class Manager:
    programs = list()

    def __init__(self, programs):
        self.programs = programs

    def load_tcp_command(self, request):
        command = request.get('command', '')
        args = request.get('args', list())
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

            if response:
                return response if len(response) > 1 else response[0]
        
        if command.upper() == 'REFRESH':
            return [{"task": program.name, "uptime": program.uptime} for program in self.programs]
        
        return {
            'raw_output': '%s: ERROR (no such command)' % command,
            'error': True,
            'input_request': request,
            'message': 'no such process',
        }