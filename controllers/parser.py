import argparse
import os
import sys

import yaml
try:
    from yaml import CLoader as Loader
except:
    from yaml import Loader as Loader


def diff_dict(d1, d2):
    diff = list()

    for key, val in d1.items():
        if key not in d2:
            diff.append(key)
            continue

        if val != d2[key]:
            diff.append(key)
    
    return(diff)

class TaskmasterDaemonParser:
    """TaskmasterDeamonParser class.
    
    > See `supervisord`.
    """

    def __init__(self, conf_path):
        self.conf_path = conf_path

        if not os.path.exists(conf_path):
            print('Unknown file or directory %s.' % conf_path)
            sys.exit(-1)
        
        try:
            with open(conf_path) as conf:
                self.configuration = config = yaml.load(conf, Loader=Loader)
        except:
            print('Unable to read configuration file %s' % conf_path)

        if not 'programs' in config or len(config) > 1:
            raise ValueError('config file is invalid')

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

    def diff(self, parser):
        return diff_dict(self.configuration['programs'], parser.configuration['programs'])

    def refresh(self):
        parser = TaskmasterDaemonParser(self.conf_path)
        diff = self.diff(parser)
        self.configuration = parser.configuration
        return diff


if __name__ == '__main__':
    daemon = TaskmasterDaemonParser.from_command_line()