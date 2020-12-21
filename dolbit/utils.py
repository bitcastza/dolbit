from .models import Contract

def get_contracts(dol, expired=False):
    result = dol.get('/contracts')
    contracts = []
    for contract_data in result:
        contract = Contract(contract_data)
        if (not expired) or (expired and contract.is_expired()):
            contracts.append(contract)
    return contracts
