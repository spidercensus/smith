import json
import logging
from platform import python_version_tuple, system, uname
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
import inotify.adapters
import os.path

LOG = logging.Logger(__name__)

CONFIG_FILE = 'config.json'


def fatal(msg):
    LOG.error(msg)
    exit(1)


def load_config(filename):
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

            if 'operation' not in watch:
                watch['operation'] = 'copy'
            if watch['operation'] not in ['copy', 'move']:
                fatal("operation attribute must be either copy or move: {} ".format(watch))

            if 'recursive' not in watch:
                watch['recursive'] = False
            if watch['recursive'] not in [True, False]:
                fatal("recursive attribute must be either True or False: {}".format(watch))
        if 'verbose' in contents and contents['verbose']:
            pass
        LOG.info(contents)
    return contents


def inotify_supported():
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


def copy(source, dest):
    print("copy({},{})".format(source, dest))
    pass


def move(source, dest):
    pass


def sync(source, dest):
    pass


def watch_inotify(w_conf):
    print("watch_inotify: {}".format(w_conf))
    i = inotify.adapters.Inotify()
    i.add_watch(w_conf['source'])
    for event in i.event_gen(yield_nones=False):
        if 'IN_CLOSE_WRITE' in event[1]:
            source = os.path.join(w_conf['source'], event[-1])
            dest = os.path.join(w_conf['dest'], event[-1])
            if w_conf['operation'] is 'copy':
                copy(source, dest)


def watch_legacy(w_conf):
    print("watch_legacy: {}".format(w_conf))


def init_watchers(watches, method):
    exec_future = None
    with ThreadPoolExecutor(max_workers=len(watches)) as executor:
        for watch in watches:
            exec_future = executor.submit(method, watch)
    return exec_future


if __name__=="__main__":
    config = load_config(CONFIG_FILE)
    watch_method = watch_inotify if inotify_supported() else watch_legacy
    init_watchers(config['watches'], watch_method)
