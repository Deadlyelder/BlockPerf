import json
import config
import argparse
import sys
import utils
import bash
from cmd import bitcoincmd
import logging
import csv
from collections import namedtuple

# To make it easier in the csv
node_groups = [
        {'argparse': '--group-a', 'variable': 'group_a', 'default':
            [10, 1, 200, config.pow]},
        {'argparse': '--group-b', 'variable': 'group_b', 'default': None},
        {'argparse': '--group-c', 'variable': 'group_c', 'default': None},
        {'argparse': '--group-d', 'variable': 'group_d', 'default': None},
        {'argparse': '--group-e', 'variable': 'group_e', 'default': None},
    ]


def _create_parser():
    parser = argparse.ArgumentParser()

    for node_group in node_groups:
        parser.add_argument(node_group['argparse']
                            , default=node_group['default']
                            , nargs='+'
                            , help='{}. Pass [amount] [share]'
                                   .format(node_group['variable'])
                            )
    return parser


def create(unknown_arguments=False):
    logging.info('Call nodes config')

    parser = _create_parser()
    if unknown_arguments:
        args = parser.parse_known_args(sys.argv[2:])[0]
    else:
        args = parser.parse_args(sys.argv[2:])
    logging.info("Parsed arguments in {}: {}".format(__name__, args))
    utils.update_args(args)

    nodes = []
    for index, node_group in enumerate(node_groups):
        node_args = getattr(args, node_group['variable'])
        if node_args:
            if len(node_args) != config.number_of_node_group_arguments:
                parser.exit(-1, 'Pass all {} arguments [amount] [share] for {}\n'
                            .format(config.number_of_node_group_arguments, node_group['variable']))

            nodes.extend(_create_node_group(node_args, node_group['variable'], index + 1))

    logging.info('Created {}:'.format(config.nodes_csv))
    print(json.dumps([node for node in nodes], indent=4))

    with open(config.nodes_csv, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['group', 'name', 'share', 'latency'])
        writer.writerows(
            [[node.group, node.name, node.share, node.latency] for node in nodes])
    logging.info('End nodes config')


def _create_node_group(node_args, group, index):
    amount = int(node_args[0])
    share = float(node_args[1])
    latency = int(node_args[2])

    nodes = []
    for i in range(amount):
        nodes.append(NodeConfig(group, config.node_name.format(index, i + 1), share/amount, latency))
    return nodes


NodeConfig = namedtuple('NodeConfig', 'group name share')
