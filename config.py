import time
import multiprocessing
from json import load

pool_processors = multiprocessing.cpu_count()
file_chunk_size = 10 * 1024 * 1024

ip_range = "240.0.0.0/4"
ip_zones = '240.{}.0.0/16'
# We need to stick with those to avoid conflicting with base imple

# We can take as input the paramters from JSON or manually append them in this file + 
# as arg during run
# JSON paramter might run in issue with IP check; hence best to avoid if crash
## JSON parameters

#def get_params(block_size_limit, number_transactions_per_block, tx_validation, block_validation, time_between_blocks_seconds):
#    return block_size_limit, number_transactions_per_block, tx_validation, block_validation, time_between_blocks_seconds

#with open("test.json") as f:
#    data = load(f)
#    get_params(data["block_size_limit"], data["number_transactions_per_block"], data["tx_validation"])

number_of_node_group_arguments = 4
network_name = 'test-net'
prefix = 'test-'
node_prefix = 'node-'
node_name = node_prefix + '{}.{}'
max_wait_time_bitcoin_runs_out = 30
rpc_user = 'admin'
rpc_password = 'admin'
rpc_port = 16333 # Make sure to configure the base
rpc_timeout = 3600
reference_node = 'node-0'
blocks_needed_to_make_coinbase_spendable = 100
max_in_mempool_ancestors = 25
log_prefix_timestamp = r'^([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}) '
log_error_grep = 'grep -E -i "WARN|FATAL|ERROR|CRITICAL|EXCEPTION" {} || true'
log_time_format = '%Y-%m-%d %H:%M:%S.%f'
log_line_run_start = 'RUN START '
log_line_run_end = 'RUN END '
smallest_amount = 1
smallest_amount_btc = 0.00000001
transaction_fee = 1000
amount_of_system_snapshots = 500
bitcoin_log_file_name = '/debug.log' # we use this for issues (IP connect + port issues)
data_dir = '../data/'
network_csv_file_name = 'network.csv'
ticks_csv_file_name = 'ticks.csv'
nodes_csv_file_name = 'nodes.csv'
args_csv_file_name = 'args.csv'
network_csv = data_dir + network_csv_file_name
ticks_csv = data_dir + ticks_csv_file_name
nodes_csv = data_dir + nodes_csv_file_name
args_csv = data_dir + args_csv_file_name
bitcoin_data_dir = '/data'
client_dir = bitcoin_data_dir + '/regtest'
log_file = data_dir + 'debug.log'
analysed_tick_infos_file_name = 'analysed_tick_infos.csv'
step_times_csv_file_name = 'step_times.csv'
consensus_chain_csv_file_name = 'consensus_chain.csv'
postprocessing_dir = '/postprocessing/'
node_config = '/node_config/'
btc_conf_file = node_config + '{}.conf'
consensus_chain_csv = postprocessing_dir + consensus_chain_csv_file_name
general_infos_csv = postprocessing_dir + 'general_infos.csv'
analysed_ticks_csv = postprocessing_dir + 'analysed_ticks.csv'
