import binascii, os

from git3Client.config.config import MUMBAI_CHAINID

from git3Client.dlt.contract import get_factory_contract
from git3Client.dlt.provider import get_web3_provider
from git3Client.dlt.user import get_user_dlt_address

from git3Client.utils.utils import read_repo_name, get_current_gas_price, get_private_key, write_file, get_chain_id

def create(network):
    git_factory = get_factory_contract(network)
    repo_name = read_repo_name()
    if not repo_name.startswith('name:'):
        print('The string in file .git/name is not correct. Exiting creation of remote')
        return
    repo_name = repo_name.split('name:')[1].strip()

    w3 = get_web3_provider(network)
    
    if repo_name == '':
        print('There is no repository name.')
        return
    # #TODO: before creating tx and so on, check if this kind of repo exits already :)
    user_address = get_user_dlt_address()
    
    nonce = w3.eth.get_transaction_count(user_address)

    print('User address', user_address)
    gas_price = get_current_gas_price(network)

    print('Preparing transaction to create repository {}'.format(repo_name))
    create_repo_tx = git_factory.functions.createRepository(repo_name).buildTransaction({
        'chainId': get_chain_id(network),
        'gas': 3947750,
        'gasPrice': w3.toWei(gas_price, 'gwei'),
        'nonce': nonce,
    })

    priv_key = bytes.fromhex(get_private_key())
    print('Signing transaction')
    signed_txn = w3.eth.account.sign_transaction(create_repo_tx, private_key=priv_key)

    print('Sending transaction')
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    # #TODO: print a clickable link to blockexplorer
    print('Transaction hash {}'.format(binascii.hexlify(receipt['transactionHash']).decode()))
    if receipt['status']:
        print('Repository {:s} has been created'.format(repo_name))
        # going to replace the entry in the .git/name folder to location: <hash>
        user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
        user_key = '{}:0x{}'.format(network, binascii.hexlify(user_key).decode())
        #TODO: in case we are within a subdir of the repo, this is going to fail!
        write_file(os.path.join('.git', 'name'), str.encode('location: ' + user_key))
    else:
        print('Creating {:s} repository failed'.format(repo_name))