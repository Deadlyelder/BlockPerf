import time
import logging
import config
import sys
import os
import re
from collections import namedtuple
import csv
from ast import literal_eval


def sleep(seconds):
    # Slepper for snapshots
    # Can be changed to minutes, kept to sec for precision
    logging.debug("Sleep for {} seconds".format(seconds))
    time.sleep(seconds)


def config_logger(verbose):
    log_formatter = logging.Formatter("%(asctime)s.%(msecs)03d000 [%(processName)s-%(threadName)-12.12s] "
                                      "[%(levelname)-5.5s]  %(message)s", "%Y-%m-%d %H:%M:%S")
    logging.Formatter.converter = time.gmtime
    root_logger = logging.getLogger()

    file_handler = logging.FileHandler(config.log_file, mode='w')
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    if verbose:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)


def check_for_file(file):
    """Incase file are missing, create them
    AWS Linux doesnt allow creating via script
    unless a shell is called inside"""
    if not os.path.isfile(file):
        command = re.split('\.|/', file)[-2]
        print("File={} not found"
              .format(file))
        exit(-1)


def read_csv(file_name):
    if os.path.isfile(file_name):
        with open(file_name, 'r') as file:
            try:
                reader = csv.reader(file)
                Object = namedtuple("Object", next(reader))
                objects = []
                for line in reader:
                    for i, var in enumerate(line):
                        try:
                            line[i] = literal_eval(var)
                        except ValueError:
                            pass
                        except SyntaxError:
                            pass
                    objects.append(Object._make(line))
                return objects
            except:
                logging.debug('Issue with file')
    else:
        return []


def read_args():
    objects = read_csv(config.args_csv)
    if len(objects) == 0:
        print("File={} is empty. Generate or put it on the file and then run"
              " `python3 main.py`".format(config.args_csv))
        exit(-1)
    elif len(objects) == 1:
        return objects[0]
    else:
        print("File={} has to many parameters."
              " `python3 main.py`".format(config.args_csv))
        exit(-1)

# TODO: Function to not overwrite the paramters and/or outputs from first run

def json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())
