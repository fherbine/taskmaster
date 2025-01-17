# taskmaster @42

A 42 project whis is a basic reproduction of supervisor, which is a task manager.
Final grade: **125/100**

> [Project introduction](https://docs.google.com/presentation/d/1LcZcP-kSzcBjE6d3_cHoFy3v_VbIdg4a8T83Fyj7EQY/edit?usp=sharing) (slides)


## Taskmasterd (DAEMON)

### How to install

#### With virtual env (RECOMMENDED)
```sh
$ python3.8 -m venv ./env
$ source ./env/bin/activate
(env) $ pip install -r requirements.txt
```

#### Without virtual env
```sh
$ pip3 install --user -r requirements.txt
```

### How to run

#### With virtual env
```sh
$ source ./env/bin/activate
(env) $ python ./taskmasterd -c /path/to/your/config.yaml
```

#### Without virtual env
```sh
$ python3.8 ./taskmasterd -c /path/to/your/config.yaml
```

### Change log level

Before running you can change the log level by typing the following command:
```sh
$ export LOGLEVEL=[ERROR|WARNING|INFO(default)|DEBUG]
```

### About configuration

> Configuration file format is given in the [subject](./fr.subject.pdf).

#### Format
```yaml
programs:
    <task_name1>:
        cmd: <your command> # type: str, required
        numprocs: <number of process to run> # type: int, default is 1
        umask: <umask that will be used for this task> # type: int, default is 666
        workingdir: <working directory for your task> # type: str, default is the current path
        autostart: [true|false] # default is true
        autorestart: [unexpected|always|never] # default is unexpected
        exitcodes: <Expected exitcode(s)> # type str or list, default is 0
        startretries: <number of retries in case of `autorestart` policy> # type int, default is 2
        starttime: <time in seconds after startup for this task to be considered as started> # type int, default is 5
        stopsignal: <UNIX default termination signal> # type str, default is 'TERM'
        stoptime: <timeout for task after the task should be stopped with a stopsignal> # type int, default is 10
        env: <env variables to add to launch the task> # type dict, by default there isn't any added variables.
        stdout: <path to redirect STDOUT> # By default STDOUT is not redirected
        stderr: <path to redirect STDERR> # By default STDERR is not redirected
    <task_name2>:
        # And so on ...
```

#### Important notes

- If you use `tasmanagerctl.py` or `ctlweb`, their `stop` and `restart` functions will not be considered as 'unexpected' process termination. For these functions `autorestart` policy won't apply.
- If a task ended before its `starttime` but on the other hand, the returncode corresponds to an accepted `exitcodes` plus the `autorestart` policy is not 'always', this task will just be considered as _finished_ and it won't restart.

## TaskmanagerCtl (CLI controller)

- To launch the command line controller you have to launch it with `py`

## CtlWeb (WebApp controller)

- To launch the CTL web version you have to go into ./ctlweb/ and use ```sh npm run start```. Make sure your taskmasterd is already running when you launch it so you can see the processes running.

***

## Further information about this project

### TODOS

#### Mandatory

- [x] CTLs status command
- [x] CTLs stop/start/restart commands
- [x] CTLs upload command
- [x] CTLs stop_deamon command

- [x] YAML parser
    - [x] read YAML file from command line
    - [x] Error/undefined values/undefined behavior management
    - [x] Default values
    - [x] Required values
- [x] Deamon task management
    - [x] start/autostart tasks
    - [x] restart behaviors / policy
    - [x] timeouts (start / stop)
    - [x] STDOUT / STDERR
    - [x] env variables
    - [x] Handle `workingdir`
    - [x] umask
    - [x] SIGHUP to update config YAML
- [x] Handle CTLs commands

#### Bonuses

- [ ] Command on CTL side to change user (Daemon need to be started w/`sudo`).
- [x] Host/client architecture as `supervisord`/`supervisorctl`
    - [x] CLI client (`taskmanagerctl`)
    - [x] web client (`ctlweb`)
- [ ] Enhanced log system.
- [ ] Attach / Detach processes
- [ ] unittests
- [x] Wildcard for exicodes
