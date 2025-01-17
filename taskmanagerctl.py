import sys

from urllib import request, parse
import json

data = json.dumps({"command":"refresh"}).encode('utf-8')
req = request.Request("http://localhost:9998", data=data, headers={
    'content-type': 'application/json'
})
try:
    resp = request.urlopen(req)
    status = json.loads(resp.read().decode())
    for items in status:
        print(items["task"], items["uptime"], str(items["started_processes"]), str(items["pids"]))
except:
    print("http://localhost:9998 refused connection")

def getStatus():
    data = json.dumps({"command":"refresh"}).encode('utf-8')
    req = request.Request("http://localhost:9998", data=data, headers={
        'content-type': 'application/json'
    })
    try:
        resp = request.urlopen(req)
        status = json.loads(resp.read().decode())
        return (status);
    except:
        return ("error");

while (1):
    print('taskmaster> ', end="")
    line = input()
    tab = line.split()
    if not tab:
        continue
    line, args = tab[0], tab[1:]
    if 'exit' == line.strip():
        print('Found exit. Terminating the program')
        exit(0)
    elif 'help' == line and arg[0] == 'exit':
        print('exit    Exit the supervisor shell.')
    elif 'help' == line and not args:
        print('default commands (type help <topic>):\n=====================================\nstart\trestart\tstop\nupdate\tstatus\tstop_daemon')
    elif line == 'help' and args[0] == 'start':
        print('start <name>            Start a process\nstart <name> <name>     Start multiple processes or groups\nstart all               Start all processes')
    elif line == 'help' and args[0] == 'restart':
        print('restart <name>          Restart a process\nrestart <name> <name>   Restart multiple processes or groups\nrestart all             Restart all processes\nNote: restart does not reread config files. For that, see reread and update.')
    elif line == 'help' and args[0] == 'stop':
        print('stop <name>             Stop a process\nStop all processes in a group\nstop <name> <name>      Stop multiple processes or groups\nstop all                Stop all processes')
    elif line == 'help' and args[0] == 'update':
        print('update                  Reload config and add/remove as necessary, and will restart affected programs')
    elif line == 'help' and args[0] == 'stop_daemon':
        print('stop the daemon')
    elif 'start' == line and not args:
        print('Error: start requires a process name')
        print('start <name>            Start a process\nstart <name> <name>     Start multiple processes or groups\nstart all               Start all processes')
    elif 'start' == line and args:
        globalStatus = getStatus()
        if globalStatus == "error":
            print("http://localhost:9998 refused connection")
        else:
            availableTaskNames = [
                task_data["task"] for task_data in globalStatus
            ]
            for argName in args:
                if argName not in availableTaskNames:
                    print(argName, 'ERROR (no such process)')
            data = json.dumps({"command": "start", "args": args}).encode('utf-8')
            req = request.Request("http://localhost:9998", data=data, headers={
                'content-type': 'application/json'
            })
            try:
                resp = request.urlopen(req)
                status = json.loads(resp.read().decode())
                if isinstance(status, list):
                    for items in status:
                        print(items['task'], items['message'])
                elif isinstance(status, dict) and "error" not in status:
                    print(status['task'], status['message'])
            except:
                print("http://localhost:9998 refused connection")
    elif 'restart' == line and args:
        globalStatus = getStatus()
        if globalStatus == "error":
            print("http://localhost:9998 refused connection")
        else:
            availableTaskNames = [
                task_data["task"] for task_data in globalStatus
            ]
            for argName in args:
                if argName not in availableTaskNames:
                    print(argName, 'ERROR (no such process)')
            data = json.dumps({"command": "restart", "args": args}).encode('utf-8')
            req = request.Request("http://localhost:9998", data=data, headers={
                'content-type': 'application/json'
            })
            try:
                resp = request.urlopen(req)
                status = json.loads(resp.read().decode())
                if isinstance(status, list):
                    for items in status:
                        print(items['task'], items['message'])
                elif isinstance(status, dict) and "error" not in status:
                    print(status['task'], status['message'])
            except:
                print("http://localhost:9998 refused connection")
    elif 'restart' == line and not args:
        print('restart <name>          Restart a process\nrestart <name> <name>   Restart multiple processes or groups\nrestart all             Restart all processes\nNote: restart does not reread config files. For that, see reread and update.')
    elif 'stop' == line and not args:
        print('stop <name>             Stop a process\nStop all processes in a group\nstop <name> <name>      Stop multiple processes or groups\nstop all                Stop all processes')
    elif 'stop' == line and args:
        globalStatus = getStatus()
        if globalStatus == "error":
            print("http://localhost:9998 refused connection")
        else:
            availableTaskNames = [
                task_data["task"] for task_data in globalStatus
            ]
            for argName in args:
                if argName not in availableTaskNames:
                    print(argName, 'ERROR (no such process)')
            data = json.dumps({"command": "stop", "args": args}).encode('utf-8')
            req = request.Request("http://localhost:9998", data=data, headers={
                'content-type': 'application/json'
            })
            try:
                resp = request.urlopen(req)
                status = json.loads(resp.read().decode())
                if isinstance(status, list):
                    for items in status:
                        print(items['task'], items['message'])
                elif isinstance(status, dict) and "error" not in status:
                    print(status['task'], status['message'])
            except:
                print("http://localhost:9998 refused connection")
    elif 'stop_daemon' == line and not args:
        data = json.dumps({"command": "stop_daemon"}).encode('utf-8')
        req = request.Request("http://localhost:9998", data=data, headers={
            'content-type': 'application/json'
        })
        try:
            resp = request.urlopen(req)
            status = json.loads(resp.read().decode())
            print(status['updated_tasks'])
        except:
            print("http://localhost:9998 refused connection")
    elif 'update' == line and not args:
        data = json.dumps({"command": "update"}).encode('utf-8')
        req = request.Request("http://localhost:9998", data=data, headers={
            'content-type': 'application/json'
        })
        try:
            resp = request.urlopen(req)
            status = json.loads(resp.read().decode())
            print(status["raw_output"])
        except:
            print("http://localhost:9998 refused connection")
    elif 'update' == line and args:
        print('status <name>           Get status for a single process\nGet status for all processes in a group\nstatus <name> <name>    Get status for multiple named processes\nstatus                  Get all process status info')
    elif 'status' == line and not args:
        data = json.dumps({"command": "refresh"}).encode('utf-8')
        req = request.Request("http://localhost:9998", data=data, headers={
            'content-type': 'application/json'
        })
        try:
            resp = request.urlopen(req)
            status = json.loads(resp.read().decode())
            for items in status:
                print(items["task"], items["uptime"], str(items["started_processes"]), str(items["pids"]))
        except:
            print("http://localhost:9998 refused connection")
    elif 'status' == line and args:
        data = json.dumps({"command": "refresh"}).encode('utf-8')
        req = request.Request("http://localhost:9998", data=data, headers={
            'content-type': 'application/json'
        })
        try:
            resp = request.urlopen(req)
            status = json.loads(resp.read().decode())
            for items in status:
                for argname in args:
                    if (items["task"] == argname):
                        print(items["task"], items["uptime"], str(items["started_processes"]), str(items["pids"]))
        except:
            print("http://localhost:9998 refused connection")
    else:
        print('*** Unknown syntax: ' + str(tab))