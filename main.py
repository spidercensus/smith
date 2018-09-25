import inotify.adapters
import json
import logging
from platform import platform, python_version_tuple, system, uname


CONFIG_FILE = 'config.json'


def fatal(msg):
    logging.error(msg)
    exit(1)


def loadConfig(filename):
    contents = None
    try:
        with open(filename, 'r') as fh:
            contents = json.load(fh)
    except Exception as e:
        fatal("Exception encountered while loading config file {}: {}".format(filename, e))
    if contents is not None:
        if 'watches' not in contents:
            fatal("Config file {} is missing key 'watches'".format(filename))
        for watch in contents['watches']:
            keys = ['source', 'dest']
            for key in keys:
                if key not in watch:
                    fatal("Each 'watches' element must contain source and dest:\n{}".format(watch))

    return contents


def is_inotify_supported():
    supported = True
    kernel = uname().release.split('-')[0].split('.')[:2]
    kernel = float('.'.join(kernel))
    if system().lower() != 'linux':
        supported = False
    elif python_version_tuple()[0] != '3':
        supported = False
    elif kernel < 2.6:
        supported = False
    return supported


def watch(w_conf):
    pass


def watch_legacy(w_conf):
    pass


if __name__=="__main__":
    config = loadConfig(CONFIG_FILE)