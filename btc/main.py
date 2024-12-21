import bitcoinlib
import bitcoinlib.keys
import bitcoinlib.scripts
import bitcoinlib.services
import bitcoinlib.services.bitcoind
import bitcoinlib.services.services
from bitcoinlib.wallets import wallet_create_or_open
from bitcoinlib.transactions import Input, Output, Transaction

import bitcoinlib.wallets
import requests
import argparse
import hashlib

import random

def get_request_json(method, params=[]):
    template_request_data = {
        "jsonrpc": "2.0",
        "method": "getblockchaininfo",
        "params": [],
        "id": "getblock.io"
    }
    template_request_data['method'] = method
    template_request_data['params'] = params
    return template_request_data

def send_json_rpc(url, json_body):
    headers_mapping = {'Content-Type': 'application/json'}
    return requests.post(url=url, headers=headers_mapping, json=json_body)

def gen_secret_number():
    parts = [random.choice(range(0, 2**32)) for i in range(8)]
    result = 0
    for value in parts:
        result = (result << 32) + value
    return result

def create_htlc_script(secret_number, author_pubkey, partner_pubkey):
    secret_bytes = secret_number.to_bytes(length=32)
    secret_hash = hashlib.sha256(secret_bytes).hexdigest()

    # unlock_script = <author/partner sig> <secret_hex>
    lock_script = f'OP_SHA256 {secret_hash} OP_EQUAL ' \
    'OP_IF ' \
        f'{partner_pubkey} OP_CHECKSIG ' \
    'OP_ELSE ' \
        '60 OP_CHECKSEQUENCEVERIFY ' \
        f'{author_pubkey} OP_CHECKSIG'
    'OP_ENDIF'
    script = bitcoinlib.scripts.Script.parse_str(lock_script)
    return script

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name')
    parser.add_argument('--network')
    parser.add_argument('--node_url')
    parser.add_argument('--partner_pubkey')
    parser.add_argument('--partner_pkh')
    parser.add_argument('--btc_amount')
    return parser.parse_args()


args = get_args()

if args.name is None or args.partner_pubkey is None or args.partner_pkh is None:
    print('No wallet name or partner public key/pubkey hash found')
    exit(1)

if args.btc_amount is None:
    print('No btc swap amount found')
    exit(1)

if args.node_url is None:
    print('No bitcoin node url found')
    exit(1)

name = args.name
network = args.network if args.network is not None else 'testnet'
w_author = wallet_create_or_open(name, network=network)

node_url = args.node_url

author_pubkey = w_author.get_key().key_public.hex()
partner_pubkey = args.partner_pubkey
partner_pubkeyhash = args.partner_pkh

secret = gen_secret_number()
create_htlc_script(secret_number=secret, author_pubkey=author_pubkey, partner_pubkey=partner_pubkey)

if node_url is None:
    print('No node url found')
    exit(1)

secret_number = gen_secret_number()
lock_script = create_htlc_script(secret_number, author_pubkey, partner_pubkey)

part = 'tb1qfl6y6gseheccxdetuv0re3lp295zdm2umr3nh8'
version = 1
fee = 10000

outputs = [Output(10000, partner_pubkeyhash, network=network, lock_script=lock_script)]

start_htlc_tx = Transaction(outputs=outputs, network=network, version=version, fee=fee)

for utxo in w_author.utxos(network=network):
    start_htlc_tx.add_input(prev_txid=utxo.txid, output_n=utxo.index, script_sig=utxo.script_sig)
for i in range(len(start_htlc_tx.inputs)):
    input = start_htlc_tx.inputs[i]
    public_key = input.keys[0]
    private_key = w_author.get_private_key(public_key)
    signature = private_key.sign(start_htlc_tx.raw_hex()[i * 64:(i + 1) * 64])
    start_htlc_tx.sign(i, signature)

# Verification
assert start_htlc_tx.verify()

send_tx_json = get_request_json('sendrawtransaction', params=[start_htlc_tx.raw_hex(), None])
response = send_json_rpc(node_url, send_tx_json)
print('Send tx response:', response.json())
