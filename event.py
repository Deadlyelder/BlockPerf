import config
import logging
import time
import utils
from bitcoin.rpc import JSONRPCError
import math


class Event:

    def __init__(self, context):
        self._context = context
        self._txs_count = self._blocks_count = 0

    def execute(self):
        try:
            utils.check_for_file(config.ticks_csv)
            with open(config.ticks_csv, 'r') as file:

                start_time = time.time()
                for i, line in enumerate(file):
                    actual_start = time.time()
                    planned_start = start_time + i * self._context.args.tick_duration

                    self._txs_count = self._blocks_count = 0

                    line = line.rstrip()
                    cmds = line.split(',')
                    for cmd in cmds:
                        self._execute_cmd(cmd)

                    planned_start_next_tick = start_time + (i + 1) * self._context.args.tick_duration
                    current_time = time.time()
                    duration = current_time - actual_start
                    logging.info('Tick={}; planned_start={}, actual_start={} and duration={:F},'
                                 ' created no. of txs={} and blocks={}'
                                 .format(i, planned_start, actual_start, duration,
                                         self._txs_count, self._blocks_count))

                    if current_time < planned_start_next_tick:
                        difference = planned_start_next_tick - current_time
                        utils.sleep(difference)
        except:
            print("Issue with run, check the triggers")

    def _execute_cmd(self, cmd):
        # Generate the tx and other operations
        cmd_parts = cmd.split(' ')

        if cmd_parts[0] == 'tx':
            node = self._context.nodes[cmd_parts[1]]
            try:
                node.generate_tx()
            except JSONRPCError:
                logging.exception('{} error, cannot connect'.format(node.name))
            self._txs_count += 1
        elif cmd_parts[0] == 'block':
            node = self._context.nodes[cmd_parts[1]]
            try:
                node.generate_blocks()
            except JSONRPCError:
                logging.exception('{} error, cannot connect'.format(node.name))
            self._blocks_count += 1
        elif len(cmd) == 0:
            pass
        else:
            print("Check the commands and IP")

def _calc_analyze_skip_ticks(blocks_per_tick, tx_per_tick):
    return max([1, math.ceil(1/blocks_per_tick), math.ceil(1/tx_per_tick)])


class SimulationException(Exception):
    pass
