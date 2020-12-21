import binascii

from dlt.contract import get_factory_contract
from dlt.provider import get_web3_provider
from dlt.user import get_user_dlt_address

from utils.utils import read_repo_name, get_current_gas_price

# CHAINID=80001
# this is matic mainnet
CHAINID=137

def create():
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    w3 = get_web3_provider()
    
    if repo_name == '':
        print('There is no repository name.')
        return
    #TODO: before creating tx and so on, check if this kind of repo exits already :)
    user_address = get_user_dlt_address()
    nonce = w3.eth.getTransactionCount(user_address)
    print('User address', user_address)
    gas_price = get_current_gas_price()
    # get current gas price
    print('Preparing transaction to create repository {}'.format(repo_name))
    create_repo_tx = git_factory.functions.createRepository(repo_name).buildTransaction({
        'chainId': CHAINID,
        'gas': 1947750,
        'gasPrice': w3.toWei(gas_price, 'gwei'),
        'nonce': nonce,
    })
    priv_key = bytes.fromhex(get_private_key())

    print('Signing transaction')
    signed_txn = w3.eth.account.sign_transaction(create_repo_tx, private_key=priv_key)

    print('Sending transaction')
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    #TODO: print a clickable link to blockexplorer
    print('Transaction hash {}'.format(binascii.hexlify(receipt['transactionHash']).decode()))
    if receipt['status']:
        print('Repository {:s} has been created'.format(repo_name))
    else:
        print('Creating {:s} repository failed'.format(repo_name))