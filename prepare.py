import config
import logging
import bash
from cmd import bitcoincmd
import os
import utils
import math
from multiprocessing.dummy import Pool as ThreadPool
import itertools
from bitcoin.rpc import DEFAULT_HTTP_TIMEOUT
import node as node_utils


class Prepare:
    def __init__(self, context):
        self._context = context
        self._pool = None

    def execute(self):
        self._pool = ThreadPool(5)
        self._prepare_simulation_dir()

        self._give_nodes_spendable_coins()

        self._start_nodes()

        self._pool.close()

    def _prepare_simulation_dir(self):
        if not os.path.exists(self._context.run_dir):
            os.makedirs(self._context.run_dir)

        if os.path.islink(config.soft_link_to_run_dir):
            # We need to create symlink and use shell in between
            bash.check_output('unlink {}'.format(config.soft_link_to_run_dir))
        bash.check_output('cd {}; ln -s {} {}'.format(config.data_dir, self._context.run_name, config.last_run))
        os.makedirs(config.postprocessing_dir)

        for file in [config.network_csv_file_name, config.ticks_csv_file_name,
                     config.nodes_csv_file_name, config.args_csv_file_name]:
            bash.check_output('cp {}{} {}'.format(config.data_dir, file, self._context.run_dir))
            bash.check_output('cd {}; ln -s ../{} {}'.format(config.postprocessing_dir, file, file))

        os.makedirs(config.node_config)
        self._pool.map(node_utils.create_conf_file, self._context.nodes.values())

        logging.info('Dir created')

    def _give_nodes_spendable_coins(self):
        # At start no node will have coins,
        # assign them manually to make for smooth run
        # We do this before the RPC is ready, making it perfect fit
        nodes = list(self._context.nodes.values())
        cbs = []
        for i, node in enumerate(nodes):
            cbs.append(
                self._pool.apply_async(
                    node_utils.start_node,
                    args=(node, (str(node.ip) for node in nodes[max(0, i - 5):i]))
                )
            )
        for cb in cbs:
            cb.get()

        self._pool.map(node_utils.check_startup_node, nodes)

        amount_of_tx_chains = _calc_number_of_tx_chains(
            self._context.args.txs_per_tick,
            self._context.args.blocks_per_tick,
            len(nodes)
        )
        logging.info('Each node got {} tx-chains'.format(amount_of_tx_chains))

        for i, node in enumerate(nodes):
            node_utils.wait_until_height_reached(node, i * amount_of_tx_chains)
            node.execute_rpc('generate', amount_of_tx_chains)
            logging.info('Generated {} blocks for node'.format(amount_of_tx_chains))

        node_utils.wait_until_height_reached(nodes[0], amount_of_tx_chains * len(nodes))
        nodes[0].generate_blocks(config.blocks_needed_to_make_coinbase_spendable)
        current_height = config.blocks_needed_to_make_coinbase_spendable + amount_of_tx_chains * len(nodes)

        self._pool.starmap(node_utils.wait_until_height_reached, zip(nodes, itertools.repeat(current_height)))

        self._pool.map(node_utils.transfer_coinbase_tx_to_normal_tx, nodes)

        for i, node in enumerate(nodes):
            node_utils.wait_until_height_reached(node, current_height + i)
            node.execute_rpc('generate', 1)

        current_height += len(nodes)
        self._context.first_block_height = current_height

        self._pool.starmap(node_utils.wait_until_height_reached, zip(
                nodes,
                itertools.repeat(current_height)
        ))

        self._pool.map(node_utils.rm_peers_file, nodes)
        node_utils.graceful_rm(self._pool, nodes)

    def _start_nodes(self):
        nodes = self._context.nodes.values()

        self._pool.map(node_utils.start_node, nodes)
        self._pool.starmap(node_utils.check_startup_node, zip(
            nodes,
            itertools.repeat(self._context.first_block_height)
        ))

        self._pool.starmap(node_utils.add_latency, zip(
            self._context.nodes.values(),
            itertools.repeat(self._context.zone.zones)
        ))

        logging.info('All nodes have started sucessfully')
        utils.sleep(1)

def _calc_number_of_tx_chains(txs_per_tick, blocks_per_tick, number_of_nodes):
    txs_per_block = txs_per_tick / blocks_per_tick
    txs_per_block_per_node = txs_per_block / number_of_nodes

    needed_tx_chains = (txs_per_block_per_node / config.max_in_mempool_ancestors) * 10 + 3
    return math.ceil(needed_tx_chains)