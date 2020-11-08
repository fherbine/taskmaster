import os
import signal
import subprocess
import time

class Task:
    pid = 0
    start_time = '-1'
    processes = list()
    stdout = ''
    stderr = ''
    start_time = -1
    trynum = 1

    def __init__(self, name, cmd, numprocs=1, umask=666, workingdir=os.getcwd(), 
                 autostart=True, autorestart='unexpected', exitcodes=[0],
                 startretries=2, starttime=5, stopsignal='TERM', stoptime=10,
                 env={}, **kwargs):
        self.name = name
        self.cmd = cmd
        self.numprocs = numprocs
        self.umask = umask if umask else '000'
        self.workingdir = workingdir
        self.autostart = autostart
        self.autorestart = autorestart
        self.exitcodes = exitcodes
        self.startretries = startretries
        self.starttime = starttime
        self.stopsignal = stopsignal
        self.stoptime = stoptime
        self.env = os.environ
        
        for key, value in env.items():
            self.env[key] = value

        if 'stdout' in kwargs:
            self.stdout = kwargs['stdout']

        if 'stderr' in kwargs:
            self.stderr = kwargs['stderr']
        
        if autostart:
            self.run()
    
    def _initchildproc(self):
        os.umask(self.umask)

    def run(self, retry=False):
        self.trynum = 1 if not retry else (self.trynum + 1)

        if self.trynum > self.startretries:
            return

        try:
            for _ in range(self.numprocs):
                process = subprocess.Popen(
                    self.cmd.split(),
                    stderr=self.stderr if self.stderr else subprocess.PIPE,
                    stdout=self.stdout if self.stdout else subprocess.PIPE,
                    env=self.env,
                    cwd=self.workingdir,
                    preexec_fn=self._initchildproc,
                    shell=True,
                )
                self.processes.append(process)
                self.start_time = time.time()

                if process.returncode in self.exitcodes:
                    continue
                else:
                    try:
                        process.wait(timeout=self.starttime)
                    except subprocess.TimeoutExpired:
                        continue

                    # retry
                    self.stop()
                    self.run(retry=True)
        except:
            # retry
            self.stop()
            self.run(retry=True)
    
    def stop(self):
        for process in self.processes:
            process.send_signal(getattr(signal, 'SIG' + self.stopsignal))

            try:
                process.wait(self.stoptime)
            except subprocess.TimeoutExpired:
                process.kill()

    @property
    def uptime(self):
        if not self.start_time:
            return -1
        upt = int(time.time() - self.start_time)
        return '{}:{}:{}'.format(int(upt / 3600), int(upt / 60 % 60), int(upt % 60))
    
    def send_command(self, command):
        if command.upper() == 'START':
            self.run()
        elif command.upper() == 'RESTART':
            self.stop()
            self.run()
        elif command.upper() == 'STOP':
            self.stop()
        else:
            return {'error': True, 'message': 'Unknown command %s' % command, 'task': self.name}

        return {'task': self.name, 'message': command.lower() + 'ed'}