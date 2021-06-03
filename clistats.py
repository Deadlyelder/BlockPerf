import logging
from bitcoin.rpc import JSONRPCError
import utils
from simulationfiles import consensus
import config
import parse

class CliStats:
    def __init__(self, context, writer):
        self._context = context
        self._writer = writer

    def execute(self):
        _persist_consensus_chain(self._calc_consensus_chain())
        self._persist_node_stats()
        #logging.info('TRIGGER: EXEC')
        logging.info('stats')

    def _calc_consensus_chain(self):
        #print("TRIGGER: Consensus calculation")
        height = self._context.first_block_height
        nodes = self._context.nodes.values()
        #print(height, nodes)
        consensus_chain = []
        logging.info('Consensus chain starting at {}'.format(height))
        while True:
            block_hashes = {}
            failing_nodes = []
            block_hash = None
            for node in nodes:
                try:
                    diff = consensus.calc_difficulty(block_hash, height, parse.TickEvent)
                    block_hash = node.execute_rpc('getblockhash', height)
                    temp_diff = node.excecute_rpc('getdifficulty', diff)
                    #print(temp_diff)
                    # For each node we query itself to know the hash
                    if block_hash in block_hashes:
                        block_hashes[block_hash].append(node.name)
                    else:
                        block_hashes[block_hash] = [node.name]
                except JSONRPCError:
                    failing_nodes.append(node.name) #drops
            if len(failing_nodes) > 0:
                logging.info('Chain at {} because nodes={}'
                             ' see now more'.format(height, failing_nodes))
                break
            elif len(block_hashes) > 1:
                logging.info('Non-Consensus {} because'
                             ' nodes have different blocks ({})'.format(height, block_hashes))
                break
            else:
                consensus_chain.append(block_hash)
                height += 1

                logging.info('Added block {} to consensus chain'.format(block_hash))

        return consensus_chain

    def _persist_node_stats(self):
        # For danglers
        tips = []
        for node in self._context.nodes.values():
            tips.extend([Tip.from_dict(node.name, chain_tip) for chain_tip in node.execute_rpc('getchaintips')])

        self._writer.write_csv(Tip.file_name, Tip.csv_header, tips)
        logging.info('Collected and persisted {} tips'.format(len(tips)))


def _persist_consensus_chain(chain):
    # Avoid overwrites
    with open(config.consensus_chain_csv, 'w') as file:
        file.write('hash\n')
        file.writelines('\n'.join(chain))
        file.write('\n')


class Tip:
    __slots__ = ['_node', '_status', '_forklen']

    csv_header = ['node', 'status', 'forklen']
    file_name = 'fork.csv'

    def __init__(self, node, status, forklen):
        self._node = node
        self._status = status
        self._branchlen = forklen

    @classmethod
    def from_dict(cls, node, chain_tip):
        return cls(node, chain_tip['status'], chain_tip['forklen'])

    def vars_to_array(self):
        return [self._node, self._status, self._forklen]
