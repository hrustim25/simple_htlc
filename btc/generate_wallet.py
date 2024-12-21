import bitcoinlib

import sys
import random
import argparse

from bitcoinlib.wallets import Wallet

from bitcoinlib.mnemonic import Mnemonic

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name')
    parser.add_argument('--network')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    wallet_name = ''
    if args.name is not None:
        wallet_name = args.name
    else:
        wallet_name = 'wallet' + str(random.randint(0, 2**10))
    
    passphrase = Mnemonic().generate()
    print('Make sure to keep passphrase in secret!')
    print('Passphrase:')
    print(passphrase)

    network = 'testnet' if args.network is None else args.network

    w = Wallet.create(wallet_name, keys=passphrase, network=network)
    print(f'Generated wallet "{wallet_name}" using passphrase on network {network}')
    print('Wallet info:', w.info())
