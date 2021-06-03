import config
import logging
import time
import systemmonitor
import threading
import queue
import math
import utils
from systemmonitor import CpuTimeSnapshot
from systemmonitor import MemorySnapshot


class Runner:
    def __init__(self, context, writer):
        self._context = context
        self._writer = writer
        self._prepare = None
        self._event = None
        self._postprocessing = None
        self._pill2kill = threading.Event()
        self._q_cpu_time = queue.Queue()
        self._q_memory = queue.Queue()
        self._system_monitor = threading.Thread(
            target=systemmonitor.run, args=(self._pill2kill,
                                            _calculate_frequency(
                                                self._context.args.tick_duration,
                                                self._context.args.amount_of_ticks),
                                            self._q_cpu_time, self._q_memory))

    def run(self):
        try:
            self._context.step_times.append(StepTimes(time.time(), 'started'))
            self._prepare.execute()
            logging.info('End')

            self._system_monitor.start()
            self._context.step_times.append(StepTimes(time.time(), 'simulation_start'))
            logging.info('Start')
            self._event.execute()
            logging.info('End')

            self._persist_system_snapshots()

            self._context.step_times.append(StepTimes(time.time(), 'postprocessing'))
            self._postprocessing.execute()
        except Exception as exce:
            return 0
            raise exce

    def _persist_system_snapshots(self):
        self._pill2kill.set()
        self._system_monitor.join()
        cpu_times = list(self._q_cpu_time.queue)
        memory = list(self._q_memory.queue)

        self._writer.write_csv(
            CpuTimeSnapshot.file_name,
            CpuTimeSnapshot.csv_header,
            cpu_times,
        )
        self._writer.write_csv(
            MemorySnapshot.file_name,
            MemorySnapshot.csv_header,
            memory,
        )
        logging.info('CPU Time {} and memory snapshot {}'.format(len(cpu_times), len(memory)))


class StepTimes:
    __slots__ = ['_timestamp', '_type']

    csv_header = ['timestamp', 'type']

    def __init__(self, timestamp, _type):
        self._timestamp = timestamp
        self._type = _type

    def vars_to_array(self):
        return [self._timestamp, self._type]


def _calculate_frequency(tick_duration, amount_of_ticks):
    frequency = math.ceil(tick_duration * amount_of_ticks / config.amount_of_system_snapshots)
    logging.info('With tick_duration={}, amount_of_ticks={} and amount_of_system_snapshots={}'
                 ' the system monitor takes snapshot it {}'
                 .format(tick_duration, amount_of_ticks, config.amount_of_system_snapshots, frequency))
    return frequency
