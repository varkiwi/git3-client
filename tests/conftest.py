import pytest
import os
import shutil
import json
import re

from web3 import (
    EthereumTesterProvider,
    Web3,
)

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

from git3Client.gitCommands.init import init
from git3Client.gitCommands.add import add
from git3Client.gitCommands.commit import commit
from git3Client.gitCommands.create import create

REPO_FILES = ['Readme.md']
PRIVATE_KEY = ec.generate_private_key(ec.SECP256K1())

@pytest.fixture(scope='session')
def fund_user(w3):
    to = w3.geth.personal.import_raw_key(hex(PRIVATE_KEY.private_numbers().private_value), '')
    value = w3.toWei(1, 'ether')
    txn = {
        "from": w3.geth.personal.list_accounts()[0],
        "to": to,
        "value": value,
        "gas": 21000,
        "gasPrice": w3.eth.get_block('latest')["baseFeePerGas"] * 21000
    }
    txn_hash = w3.eth.send_transaction(txn)
    w3.eth.wait_for_transaction_receipt(txn_hash)
    return w3

@pytest.fixture(scope='session')
def deploy_contracts(eth_tester, fund_user):
    w3 = fund_user
    deploy_address = eth_tester.get_accounts()[0]
    facets_contracts = ['GitBranch', 'GitIssues', 'GitRepositoryManagement', 'GitTips']
    contract_information = []
    for facet in facets_contracts:    
        with open(os.path.join(os.path.abspath('.'), 'git3Client', 'artifacts', 'contracts', 'facets', f"{facet}.sol", f"{facet}.json")) as f:
            contract_data = json.loads(f.read())

        contract = w3.eth.contract(abi=contract_data['abi'], bytecode=contract_data['bytecode'])
        function_signatures = []
        for function in contract.all_functions():
            function_signatures.append(Web3.toHex(Web3.sha3(text=str(function).split("Function")[1].replace(">", ""))[0:4]))
            
        tx_hash = contract.constructor().transact({'from': deploy_address})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, 180)
        contract_information.append([tx_receipt.contractAddress, function_signatures])

    # deplying GitContractRegistry
    with open(os.path.join(os.path.abspath('.'), 'git3Client', 'artifacts', 'contracts', 'GitContractRegistry.sol', "GitContractRegistry.json")) as f:
        contract_data = json.loads(f.read())
    contract = w3.eth.contract(abi=contract_data['abi'], bytecode=contract_data['bytecode'])
    tx_hash = contract.constructor(contract_information).transact({'from': deploy_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, 180)

    # deplying GitFactory
    with open(os.path.join(os.path.abspath('.'), 'git3Client', 'artifacts', 'contracts','GitFactory.sol', 'GitFactory.json')) as f:
        contract_data = json.loads(f.read())

    git3_factory = w3.eth.contract(abi=contract_data['abi'], bytecode=contract_data['bytecode'][2:])
    tx_hash = git3_factory.constructor(deploy_address).transact({'from': deploy_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, 180)

    return git3_factory(tx_receipt.contractAddress)

@pytest.fixture(scope='session')
def tester_provider():
    return EthereumTesterProvider()

@pytest.fixture(scope='session')
def eth_tester(tester_provider):
    return tester_provider.ethereum_tester

@pytest.fixture(scope='session')
def w3(tester_provider):
    return Web3(tester_provider)

@pytest.fixture
def patch_web3_provider(mocker, w3):
    mocker.patch('git3Client.gitCommands.create.get_web3_provider', return_value=w3)

@pytest.fixture
def patch_git_factory_for_create(mocker, deploy_contracts):
    mocker.patch('git3Client.gitCommands.create.get_factory_contract', return_value=deploy_contracts)

@pytest.fixture
def patch_get_current_gas_price_for_create(mocker):
    mocker.patch('git3Client.gitCommands.create.get_current_gas_price', return_value=None)

@pytest.fixture
def patch_push_data_to_storage_for_push(mocker):
    mocker.patch('git3Client.gitCommands.push.push_data_to_storage', return_value='AwesomeCID')

@pytest.fixture
def patch_check_if_repo_created_for_push(mocker):
    mocker.patch('git3Client.gitCommands.push.check_if_repo_created', return_value='true')

@pytest.fixture
def patch_push_new_cid_for_push(mocker):
    mocker.patch('git3Client.gitCommands.push.push_new_cid', return_value='true')

@pytest.fixture
def move_to_root_and_back():
    current_path = os.getcwd()
    os.chdir('/')
    yield
    os.chdir(current_path)

@pytest.fixture
def create_file():
    with open('Readme.md', 'w') as f:
        f.write('test text in Readme.md\n')
    yield

@pytest.fixture
def add_file_to_index():
    add(REPO_FILES)
    yield

@pytest.fixture
def remove_identify_path_from_config():
    with open(os.path.join('.git', 'config'), 'r') as f:
        content = f.read()
    content = re.sub('IdentityFile = .*identity', '', content)
    with open(os.path.join('.git', 'config'), 'w') as f:
        f.write(content)

@pytest.fixture
def delete_local_config_file():
    os.remove(os.path.join('.git', 'config'))

@pytest.fixture
def create_local_config_file_with_identity_file():
    serialized_private = PRIVATE_KEY.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(os.path.join('.git', 'identity'), 'wb') as f:
        f.write(serialized_private)
    
    config_content = f"[user]\n\temail = test@test.com\n\tname = pytester\n\tIdentityFile = {os.path.join(os.path.abspath('.'), '.git', 'identity')}"
    print(config_content)
    with open(os.path.join('.git', 'config'), 'w') as f:
        f.write(config_content)
    yield

@pytest.fixture
def create_repository():
    start_path = os.path.abspath(os.getcwd())
    repo_name = 'git3_test_repository'
    print('Init repo')
    init(repo_name)
    os.chdir(repo_name)
    yield start_path, repo_name

@pytest.fixture
def cleanup_repository(create_repository):
    yield

    start_path, repo_name = create_repository
    print('Delete repo')
    os.chdir(start_path)
    shutil.rmtree(repo_name)

@pytest.fixture
def change_content_of_name_file():
    with open(os.path.join(os.path.abspath('.'), '.git', 'name'), 'w') as f:
        f.write('wrong text in name file')

@pytest.fixture
def change_repository_name_in_name_file():
    with open(os.path.join(os.path.abspath('.'), '.git', 'name'), 'w') as f:
        f.write('name:')

@pytest.fixture
def prepare_local_repo_till_commit(cleanup_repository, create_file, add_file_to_index, create_local_config_file_with_identity_file):
    """
    Combines multiple fixture into one. This fixture creates a local git repository, creates a local file
    and adds it to the index. It also creates a local config file.
    """
    yield

@pytest.fixture
def prepare_local_repo_till_create(prepare_local_repo_till_commit):
    """
    This fixture prepares a repository until is is possible to commit and commits the local file
    """
    commit(message="1st commit message")
    yield

@pytest.fixture
def mock_successful_push(mocker, request):
    for key in request.param:
        mocker.patch("git3Client.gitCommands.push." + key, return_value=request.param[key])