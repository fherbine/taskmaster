import argparse
import os
import sys

import yaml
from yaml import CLoader as Loader


class TaskmasterDaemonParser:
    """TaskmasterDeamonParser class.
    
    > See `supervisord`.
    """

    def __init__(self, conf_path):
        if not os.path.exists(conf_path):
            print('Unknown file or directory %s.' % conf_path)
            sys.exit(-1)
        
        try:
            with open(conf_path) as conf:
                self.configuration = yaml.load(conf, Loader=Loader)
        except:
            print('Unable to read configuration file %s' % conf_path)

    @classmethod
    def from_command_line(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--config_file',
            '-c',
            required=True,
            type=str,
        )
        args = parser.parse_args()
        return cls(args.config_file)


if __name__ == '__main__':
    daemon = TaskmasterDaemonParser.from_command_line()