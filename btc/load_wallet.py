from bitcoinlib.wallets import Wallet

import sys
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name')
    parser.add_argument('--network')
    parser.add_argument('--passphrase')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    if args.name is None or args.passphrase is None:
        print('Bad args')
        print('Usage: python3 load_wallet.py --name <wallet name> --network <network> --passphrase <passphrase as str>')
        exit(1)
    name = args.name
    passphrase = args.passphrase
    network = 'testnet' if args.network is None else args.network
    w = Wallet.create(name, keys=passphrase, network=network)
    print(f'Loaded bitcoin wallet "{name}" with passphrase')
    print('Wallet info:', w.info())
