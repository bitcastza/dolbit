import argparse
import datetime
import copy
import os
import sys
import pprint
from requests.exceptions import HTTPError

from .models import Contract, ContractLine
from .utils import get_contracts
from .dolibarr import Dolibarr

CONTRACT_RENEW = 'renew'
CONTRACT_LIST = 'list'

CONTRACTS_ACTIONS = [
    CONTRACT_RENEW,
    CONTRACT_LIST,
]

def get_option_or_exit(option, env_variable, error_msg, parser):
    if not option:
        option = os.environ.get(env_variable)
        if not option:
            print(error_msg, file=sys.stderr)
            parser.print_help()
            sys.exit(1)
    return option

def renew_contracts(url, api_key):
    dol = Dolibarr(url=url, token=api_key)
    expired_contracts = get_contracts(dol, expired=True)
    new_contracts = []
    for contract in expired_contracts:
        new_contract = copy.deepcopy(contract)
        new_contract.pk = -1
        for line in new_contract.lines:
            line.pk = -1
            duration = line.end - line.start
            start = line.end + datetime.timedelta(days=1)
            line.start = start
            line.end = start + duration + datetime.timedelta(days=1)
        new_contract.date = datetime.datetime.utcnow().date()
        new_contracts.append(new_contract)

    for contract in new_contracts:
        try:
            print(f'Creating {contract}')
            contract.create(dol)
        except HTTPError as e:
            print(e.response.json())
    for contract in expired_contracts:
        print(f'Ending old contract {contract}')
        try:
            contract.end(dol)
        except HTTPError as e:
            print(e.response.json())
    pprint.pprint(new_contracts)

def list_contracts(url, api_key):
    dol = Dolibarr(url=url, token=api_key)
    expired_contracts = get_contracts(dol, expired=True)
    pprint.pprint(expired_contracts)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dolibarr automation tool for Bitcast')
    parser.add_argument('-s', '--site', help='the Dolibarr site to connect to. If not supplied, the environment varibale DOLBIT_SITE will be used')
    parser.add_argument('-k', '--key', help='the API key to use for authentication. If not supplied, the environment variable DOLBIT_KEY will be used')
    subparsers = parser.add_subparsers(help='manages functionality around contracts')
    contracts_parser = subparsers.add_parser('contract')
    contracts_parser.add_argument('action', choices=CONTRACTS_ACTIONS)
    args = parser.parse_args()

    api_key = get_option_or_exit(args.key,
                                 'DOLBIT_KEY',
                                 'No API key provided, unable to continue',
                                 parser)
    site = get_option_or_exit(args.site,
                              'DOLBIT_SITE',
                              'No Dolibarr URL provided, unable to continue',
                              parser)

    if args.action == CONTRACT_RENEW:
        renew_contracts(f'{site}/api/index.php', api_key)
    elif args.action == CONTRACT_LIST:
        list_contracts(f'{site}/api/index.php', api_key)

