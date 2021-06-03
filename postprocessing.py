from bash import bitcoincmd
from clistats import CliStats
from parse import Parser
import config
import bash
import logging
import utils
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import subprocess
from runner import StepTimes
import time
import csv
import node as node_utils


class PostProcessing:
    def __init__(self, context, writer):
        self._context = context
        self._writer = writer
        self._pool = None
        self._thread_pool = None

    def execute(self):
        self._pool = Pool(config.pool_processors)
        self._thread_pool = ThreadPool(5)

        cli_stats = CliStats(self._context, self._writer)
        cli_stats.execute()

        logging.info(config.log_line_run_end + self._context.run_name)
        _flush_log_handlers()
        _extract_from_file(config.log_file, config.run_log,
                           config.log_line_run_start + self._context.run_name,
                           config.log_line_run_end + self._context.run_name)

        parser = Parser(self._context, self._writer)
        parser.execute()

        _collect_general_information()

        self._context.step_times.append(StepTimes(time.time(), 'postprocessing_end'))
        self._writer.write_csv(config.step_times_csv_file_name, StepTimes.csv_header, self._context.step_times)

        self._pool.close()
        self._thread_pool.close()
        logging.info('Executed post processing')

    def clean_up(self):
        node_utils.graceful_rm(self._thread_pool, self._context.nodes.values())
        logging.info('Removed all nodes')

        utils.sleep(1)

        bash.check_output(bitcoincmd.fix_data_dirs_permissions(self._context.run_dir))
        logging.info('Fixed permissions of dirs')


def _flush_log_handlers():
    for handler in logging.getLogger().handlers:
        handler.flush()
    logging.debug('Flushed all logging handlers')


def _extract_from_file(source, destination, start, end):
    with open(source, 'r') as source_file:
        with open(destination, 'w') as destination_file:
            write = False
            for line in source_file:
                if write:
                    if end in line:
                        destination_file.write(line)
                        break
                    else:
                        destination_file.write(line)
                if start in line:
                    destination_file.write(line)
                    write = True
    logging.debug('Extracted from file={} lines between start={} and end={} into file {}'
                  .format(source, destination, start, end))


def _collect_general_information():
    general_infos = {
        'total_memory': _try_cmd('cat /proc/meminfo | sed -n 1p | grep -ohE [0-9]+'),
        'cpu_model': _try_cmd("lscpu | grep -oP 'Model name:\s+\K(.*)'"),
        'cpus': _try_cmd("lscpu | grep -oP 'CPU\(s\):\s+\K([0-9]+)$'"),
    }

    with open(config.general_infos_csv, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(general_infos.keys())
        writer.writerow(general_infos.values())


def _try_cmd(cmd):
    try:
        return bash.check_output(cmd)
    except subprocess.CalledProcessError:
        return 'cmd={} failed'.format(cmd)
