import logging
import os
import signal
import subprocess
import threading
import time

from logger import Logger


def handle_process_restart_behavior(process, behavior, returncodes, callback):
    process.wait()

    Logger(level=logging.DEBUG).debug((
        f'Process {process.pid} ({process.args}) exited,'
        f' with returncode {process.returncode}.'
        f' Expected returncodes: {returncodes}. Policy: autorestart {behavior}.'
    ))

    if behavior.upper() == 'ALWAYS' or (
        behavior.upper() == 'UNEXPECTED'
        and process.returncode not in returncodes
    ):
        try:
            callback()
        except:
            #XXX: Hack
            return


class Task:
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

        self.processes = list()
        self.start_time = -1
        self.stdout = ''
        self.stderr = ''
        self.trynum = 1
        self.threads = list()

        self.log = Logger(level=logging.INFO)
        
        for key, value in env.items():
            self.env[key] = value

        if 'stdout' in kwargs:
            self.stdout = kwargs['stdout']

        if 'stderr' in kwargs:
            self.stderr = kwargs['stderr']

        self.log.info('task %s initialized.' % self.name)
        
        if autostart:
            self.run()
    
    def _initchildproc(self):
        os.umask(self.umask)

    def restart(self, retry=False, from_thread=False):
        self.stop(from_thread)
        self.run(retry=retry)

    def define_restart_policy(self, process):
        thr = threading.Thread(
            target=handle_process_restart_behavior,
            args=(
                process,
                self.autorestart,
                self.exitcodes,
                lambda *_: self.restart(retry=True, from_thread=True),
            ),
            daemon=True,
        )
        thr.start()
        self.threads.append(thr)

    def run(self, retry=False):
        self.trynum = 1 if not retry else (self.trynum + 1)

        if self.trynum > self.startretries:
            self.log.warning('%s reached the maximum number of retries.' % self.name)
            return
        
        self.log.info('Try to start {}. Retry attempt {}, max retries: {}, cmd: `{}`'.format(
            self.name,
            self.trynum,
            self.startretries,
            self.cmd,
        ))

        try:
            for virtual_pid in range(self.numprocs):
                process = subprocess.Popen(
                    self.cmd.split(),
                    stderr=self.stderr if self.stderr else subprocess.PIPE,
                    stdout=self.stdout if self.stdout else subprocess.PIPE,
                    env=self.env,
                    cwd=self.workingdir,
                    preexec_fn=self._initchildproc,
                )
                self.processes.append(process)
                self.start_time = time.time()

                if process.returncode in self.exitcodes:
                    self.define_restart_policy(process)
                    self.log.success((
                        f'{self.name}: process number {virtual_pid} started.'
                        f' Exited directly, with returncode {process.returncode}'
                    ))
                    self.start_time = -2
                    self.trynum = 1
                    continue
                else:
                    try:
                        process.wait(timeout=self.starttime)

                        if process.returncode in self.exitcodes:
                            self.define_restart_policy(process)
                            self.log.success((
                                f'{self.name}: process number {virtual_pid} started.'
                                f' Exited directly, with returncode {process.returncode}'
                            ))
                            self.start_time = -2
                            self.trynum = 1
                            continue
                    except subprocess.TimeoutExpired:
                        self.define_restart_policy(process)
                        self.log.success(f'{self.name}: process number {virtual_pid} started.')
                        self.trynum = 1
                        continue

                    # retry
                    self.restart(retry=True)
        except:
            # retry
            self.log.warning('%s startup failed.' % self.name)
            self.restart(retry=True)
    
    def stop(self, from_thread=False):
        for process in self.processes:
            self.log.info(f'Send SIG{self.stopsignal} to {process.pid}.')
            process.send_signal(getattr(signal, 'SIG' + self.stopsignal))

            try:
                process.wait(self.stoptime)
            except subprocess.TimeoutExpired:
                self.log.info(f'Force kill {process.pid}.')
                process.kill()

        if not from_thread:
            for thr in self.threads:
                thr.join(.1)

        self.processes = list()
        self.threads = list()
        self.start_time = -3

    @property
    def uptime(self):
        if self.start_time == -1:
            return 'not started'
        if self.start_time == -2:
            return 'finished'
        if self.start_time == -3:
            return 'stopped'
        upt = int(time.time() - self.start_time)
        return '{}:{}:{}'.format(int(upt / 3600), int(upt / 60 % 60), int(upt % 60))
    
    def send_command(self, command):
        self.log.info(f'task {self.name}, command received {command}.')
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