import csv
import random
import pandas
import config
import argparse
from simulationfiles import checkargs
import sys
import utils
import logging


def _create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--ip'
                        , default="127.0.0.1"
                        , type=checkargs.check_positive_int
                        , help='Set the IP of the distributed nodes'
                        )

    parser.add_argument('--connectivity'
                        , default=1
                        , type=checkargs.check_percentage
                        , help='Connectivity between nodes.'
                        )

    return parser


def create(unknown_arguments=False):
    logging.info('Called network config')

    utils.check_for_file(config.nodes_csv)
    nodes = utils.read_csv(config.nodes_csv)

    parser = _create_parser()
    if unknown_arguments:
        args = parser.parse_known_args(sys.argv[2:])[0]
    else:
        args = parser.parse_args(sys.argv[2:])
    logging.info("Parsed arguments in {}: {}".format(__name__, args))
    utils.update_args(args)

    random.seed(args.seed)

    header = _create_header(nodes)

    logging.info('Created {}:'.format(config.network_csv))

    with open(config.network_csv, "w") as file:
        writer = csv.writer(file)
    logging.info('End network config')


def _create_header(nodes):
    header = ['']
    for node in nodes:
        name = node.name
        header.append(name)

    return header

def _recursive_check(peers, visited=None, start=1):
    # neigbour check
    if visited is None:
        visited = {key: False for key in range(1, len(peers))}

    if visited[start]:
        return []
    visited[start] = True
    output = [start]
    for neighbour in range(1, len(peers)):
        if peers[start][neighbour] > 0:
            output.extend(_recursive_check(peers, visited, neighbour))
    return output


def read_connections():
    utils.check_for_file(config.network_csv)
    connections = {}
    network_config = pandas.read_csv(open(config.network_csv), index_col=0)

    for node_row, row in network_config.iterrows():
        connections[node_row] = []
        for node_column, value in row.iteritems():
            if node_column == node_row:
                pass
            elif value == 1:
                connections[node_row].append(node_column)

    return connections
