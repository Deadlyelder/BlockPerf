from runner import Runner
import logging
import time
from postprocessing import PostProcessing
from event import Event
import config
from context import Context
from prepare import Prepare
from write import Writer
import utils
import sys
import argparse
from simulationfiles import checkargs


def _create_parser():
    parser = argparse.ArgumentParser()

    return parser


def run(unknown_arguments=False):
    for file in [config.ticks_csv, config.network_csv, config.nodes_csv]:
        utils.check_for_file(file)

    parser = _create_parser()
    if unknown_arguments:
        args = parser.parse_known_args(sys.argv[2:])[0]
    else:
        args = parser.parse_args(sys.argv[2:])
    logging.info("Parsed arguments")
    utils.update_args(args)

    context = Context()

    logging.info(config.log_line_run_start + context.run_name)

    tag = context.args.tag
    if hasattr(context.args, 'tag_appendix'):
        tag += context.args.tag_appendix
    writer = Writer(tag)
    runner = Runner(context, writer)

    prepare = Prepare(context)
    runner._prepare = prepare

    postprocessing = PostProcessing(context, writer)
    runner._postprocessing = postprocessing

    event = Event(context)
    runner._event = event

    start = time.time()

    runner.run()

    logging.info("The duration of the run was {} minutes".format(str(time.time() - start)))