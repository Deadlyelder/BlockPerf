#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from simulationfiles import nodes_config
from simulationfiles import ticks_config
import sys
import argparse
import simulation_cmd
import config
import os
import bitcoin
import utils
import run_cmd
from json import dumps as dump_json
import logging


def _parse_args():
    parser = argparse.ArgumentParser()

    args = parser.parse_known_args(sys.argv[1:])[0]
    utils.update_args(args)

    return args


def main():
    cmd_parser = argparse.ArgumentParser(
    description='BlockPerf',
    usage='''<command> [<args>]

    The commands are:
    nodes       creates the {} for a run
    network     creates peer {} for a run
    simulate    executes a simulation based on the {} nd {}
    run         runs all above commands
    '''.format(
        config.nodes_csv_file_name,
        config.network_csv_file_name,
        config.nodes_csv_file_name,
        config.network_csv_file_name,
    ))

    cmd_parser.add_argument('command', help='Subcommand to run')

    args = cmd_parser.parse_args(sys.argv[1:2])
    command = args.command
    if command not in commands:
        print('Unrecognized command')
        cmd_parser.print_help()
        exit(1)
    # use dispatch pattern to invoke method with same name

    if not os.path.exists(config.data_dir):
        os.makedirs(config.data_dir)

    bitcoin.SelectParams('regtest')

    args = _parse_args()
    utils.config_logger(args.verbose)
    logging.info("Arguments called with: {}".format(sys.argv))

    logging.info('Executing command={}'.format(command))
    commands[command]()


if __name__ == '__main__':
    main()
