import argparse
import os
import sys
import dolibarr
import pprint

from .models import Contract, ContractLine

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
    print('renew')

def list_contracts(url, api_key):
    dol = dolibarr.Dolibarr(url=url, token=api_key)
    result = dol.call_list_api('/contracts')
    expired_contracts = []
    for contract_data in result:
        contract = Contract(contract_data)
        if contract.is_expired():
            expired_contracts.append(contract)
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

