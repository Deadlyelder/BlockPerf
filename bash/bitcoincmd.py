import config

""" Control the custom nodes throughout """

daemon = 'bitcoind '
args = {
    'regtest':            '-regtest',
    'datadir':            '-datadir=' + config.bitcoin_data_dir,

    # log all events relevant for parsing
    'debug':              '-debug=cmpctblock -debug=net -debug=mempool', # For mempool
    'logtimemicros':      '-logtimemicros', # DO NOT CHANGE TO OTHER UNIT

    'onlynet':            '-onlynet=ipv4',
    'dnsseed':            '-dnsseed=0', # Set to 0 to avoid fall back to hardcoded one

    'reindex':            '-reindex', # for correct order of transactions 
    'checkmempool':       '-checkmempool=0', # To have store of mempool
    'keypool':            '-keypool=1', # Keypool of wallet address

    # RPC configuration
    'rpcuser':            '-rpcuser=admin',
    'rpcpassword':        '-rpcpassword=admin',
    'rpcallowip':         '-rpcallowip=1.1.1.1/0.0.0.0',
    'rpcservertimeout':   '-rpcservertimeout=' + str(config.rpc_timeout),
}


def start(name, ip, path, connect_to_ips):
    return_args = args.copy()
    cmd = transform_to_cmd(return_args)
    for _ip in connect_to_ips:
        cmd += ' -connect=' + str(_ip)

def exec_cmd(node, cmd):
    return './btcd {}{} {}'.format(config.prefix, node, cmd)

def transform_to_cmd(args_to_transform):
    return daemon + ' '.join(args_to_transform.values())

def rm_peers(node):
    return exec_cmd(node, 'rm -f {}/regtest/peers.dat'.format(config.bitcoin_data_dir))

def check_if_running(name):
    return 'test -t 0 {{{{.State.Running}}}} {0}{1}'.format(config.prefix, name)

