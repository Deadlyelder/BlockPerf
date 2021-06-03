import logging
import os
import subprocess

def check_output(cmd, lvl=logging.INFO):
    ## To keep logging result for post-proc
    output = check_output_without_log(cmd)
    for line in output.splitlines():
        logging.log(lvl, line.strip())
    return output


def check_output_without_log(cmd):
    logging.info(cmd)
    output = subprocess.check_output(cmd, shell=True, executable='/bin/bash')
    encoded_output = output.decode('utf-8').rstrip()
    return encoded_output


def call_silent(cmd):
    # Daemon run
    # Else it terminates when other command is called
    # Maybe change with screen or tmux?
    logging.info(cmd)
    with open(os.devnull, 'w') as devnull:
        return subprocess.call(cmd, shell=True, executable='/bin/bash', stderr=devnull, stdout=devnull)
