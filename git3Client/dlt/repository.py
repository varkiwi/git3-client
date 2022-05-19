import binascii
import os
import time

from git3Client.config.config import MUMBAI_CHAINID

from git3Client.dlt.contract import get_factory_contract, get_facet_contract
from git3Client.dlt.provider import get_web3_provider
from git3Client.dlt.user import get_user_dlt_address
from git3Client.dlt.storageClient import getStorageClient

from git3Client.gitInternals.gitObject import read_object
from git3Client.gitInternals.gitTree import read_tree
from git3Client.gitInternals.fileMode import GIT_NORMAL_FILE_MODE, GIT_TREE_MODE

from git3Client.utils.utils import read_repo_name, get_current_gas_price, get_private_key, get_repo_root_path, get_chain_id

def push_new_cid(branchName, cid):
    repo_name = read_repo_name()
    if not repo_name.startswith('location:'):
        print('.git/name file has an error. Exiting...')
        return False
    tmp = repo_name.split('location:')[1].split(':')
    network = tmp[0].strip()
    user_key = tmp[1].strip()

    git_factory = get_factory_contract(network)
    user_address = get_user_dlt_address()

    repository = git_factory.functions.getRepository(user_key).call()

    git_repo_address = repository[2]

    branch_contract = get_facet_contract("GitBranch", git_repo_address, network)
    w3 = get_web3_provider(network)

    nonce = w3.eth.get_transaction_count(user_address)

    gas_price = get_current_gas_price(network)

    create_push_tx = branch_contract.functions.push(branchName, cid).buildTransaction({
        'chainId': get_chain_id(network),
        'gas': 746427,
        'gasPrice': w3.toWei(gas_price, 'gwei'),
        'nonce': nonce,
    })
    priv_key = bytes.fromhex(get_private_key())
    print('Signing transaction')
    signed_txn = w3.eth.account.sign_transaction(create_push_tx, private_key=priv_key)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print('Transaction hash {}'.format(binascii.hexlify(receipt['transactionHash']).decode()))
    if receipt['status']:
        print('Successfully pushed')
    else:
        print('Pushing failed')

def check_if_remote_ahead(remote_sha1):
    """
    Check if the remote repository is ahead. It get's the remote sha1 hash and checks if the file exists in the 
    .git/objects directory. If it does not exist, the remote repository is ahead of the local repository
    #TODO: WE will have to give this function a new name
    """
    if remote_sha1 == None:
        return False
    root_path = get_repo_root_path()
    path_to_check = os.path.join(root_path, '.git', 'objects', remote_sha1[:2], remote_sha1[2:])
    return not os.path.isfile(path_to_check) 


def get_all_remote_commits(commit_cid) -> list:
    """
    Gets all remote commits and returns those in a list

    Arguments:
        str: commit_cid: The cid of the starting commit
    Returns:
        list: List containing commits
    """
    all_commits = []
    client = getStorageClient()
    # load remote db
    remote_db = client.get_json(commit_cid)
    # load remode cid chain
    remote_object = client.get_json(remote_db['head_cid'])
    all_commits.append(remote_object)

    while len(remote_object['parents']) > 0:
        for parent in remote_object['parents']:
            remote_object = client.get_json(parent)
            all_commits.append(remote_object)

    return all_commits

def check_if_repo_created():
    """
    Checks if the repository has been already registered in the gitFactory contract
    If it hasn't, False is returned, otherwise True
    """
    repo_name = read_repo_name()
    if not repo_name.startswith('location:'):
        return False
    tmp = repo_name.split('location:')[1].split(':')
    network = tmp[0].strip()
    user_key = tmp[1].strip()

    w3 = get_web3_provider(network)
    if not w3.isConnected():
        #TODO: Throw an exception
        print('No connection. Establish a connection first')
        return False

    git_factory = get_factory_contract(network)

    return git_factory.functions.getRepository(user_key).call()[0]

def get_remote_branch_hash(branchName):
    """
    Get commit hash of remote branch branchName, return CID or None if no remote commits.
    """
    repo_name = read_repo_name()
    if not repo_name.startswith('location:'):
        return
    tmp = repo_name.split('location:')[1].split(':')
    network = tmp[0].strip()
    user_key = tmp[1].strip()

    git_factory = get_factory_contract(network)
    
    repository = git_factory.functions.getRepository(user_key).call()
    
    if not repository[0]:
        print('No such repository')
        return
    git_repo_address = repository[2]
    branch_contract = get_facet_contract("GitBranch", git_repo_address, network)

    branch = branch_contract.functions.getBranch(branchName).call()
    
    # check if the branch is active
    if not branch[0]:
        return None
    # if active, return head cid
    return branch[1]

def push_tree(tree_hash: str, folder_name: str, remote_database: dict) -> str:
    """
    Takes a tree hash and a folder name and pushed the blobs and tree to a remote storage.

    Arguments:
        str: tree_hash: Hash of the tree to be pushed
        str: folder_name: Name of folder
    Returns:
        str: CID of the last push data
    """
    # client = getStorageClient()
    entries = read_tree(tree_hash)
    tree_entries = []

    subdirFiles = remote_database
    for p in remote_database['path']:
        if p not in subdirFiles:
            subdirFiles[p] = { 'files': {}}
        subdirFiles = subdirFiles[p]

    for entry in entries:
        # adding all the necessary information to the remote database
        if entry[1] not in subdirFiles or 'commit_time' not in subdirFiles[entry[1]] or (int(remote_database['committer']['date_seconds']) > int(subdirFiles[entry[1]]['commit_time']) and subdirFiles[entry[1]]['sha1'] != entry[2]):
            if entry[1] not in subdirFiles:
                subdirFiles[entry[1]] = {}
            subdirFiles[entry[1]]['mode'] = entry[0]
            subdirFiles[entry[1]]['name'] = entry[1]
            subdirFiles[entry[1]]['sha1'] = entry[2]
            if entry[0] == GIT_TREE_MODE and 'files' not in  subdirFiles[entry[1]]:
                subdirFiles[entry[1]]['files'] = {}
            subdirFiles[entry[1]]['commit_message'] = remote_database['currentCommitMessage']
            subdirFiles[entry[1]]['commit_time'] = remote_database['committer']['date_seconds']

        if entry[0] == GIT_NORMAL_FILE_MODE:
            obj_type, blob = read_object(entry[2])
            assert obj_type == 'blob'
            blob_to_push = {
                'type': 'blob',
                'content': blob.decode(),
                'sha1': entry[2]
            }
            cid = push_data_to_storage(blob_to_push)

            print('Pushing {} to IPFS'.format(entry[1]))
        elif entry[0] == GIT_TREE_MODE:
            remote_database['path'].append(entry[1])
            remote_database['path'].append('files')
            cid = push_tree(entry[2], entry[1], remote_database)

            remote_database['path'].pop()

        if 'cid' not in subdirFiles[entry[1]] or (int(remote_database['committer']['date_seconds']) > int(subdirFiles[entry[1]]['commit_time']) and subdirFiles[entry[1]]['sha1'] != entry[2]):
            subdirFiles[entry[1]]['cid'] = cid
        
        tree_entries.append({
            'mode': entry[0],
            'name': entry[1],
            'cid': cid,
            'sha1': entry[2]
        })

    tree_to_push = {
        'type': 'tree',
        'entries': tree_entries,
        'name': folder_name,
        'sha1': tree_hash
    }
    cid = push_data_to_storage(tree_to_push)
    return cid

def push_commit(commit_hash, remote_commit_hash, remote_commit_cid, remote_database):
    """
    Used to push a commit, the tree it references and the blobs to ipfs. 

    commit_hash - The sha1 hash of the local commit object
    remote_commit_hash - The sha1 hash of the remote commit object. With this we know that we don't have to push that one
    """
    # we don't need to push a commit object if remote sha1 is equal to local sha1 hash
    if commit_hash == remote_commit_hash:
       return remote_commit_cid
    obj_type, commit = read_object(commit_hash)
    assert obj_type == 'commit'
    lines = commit.decode().splitlines()
    commit_to_push = {
        'type': 'commit',
        'parents': [],
        'sha1': commit_hash,
    }
    parents = []
    for line in lines:
        if line.startswith('tree '):
            tree_hash = line[5:45]
        elif line.startswith('parent '):
            parents.append(line[7:47])
        elif line.startswith('author'):
            splitted_line = line.split(' ')
            commit_to_push['author'] = {
                'name': splitted_line[1],
                'email': splitted_line[2],
                'date_seconds': splitted_line[3],
                'date_timestamp': splitted_line[4],
            }
        elif line.startswith('committer'):
            splitted_line = line.split(' ')
            commit_to_push['committer'] = {
                'name': splitted_line[1],
                'email': splitted_line[2],
                'date_seconds': splitted_line[3],
                'date_timestamp': splitted_line[4],
            }
        else:
            if line == '':
                space_commit_message = True
                
            if space_commit_message:
                commit_to_push['commit_message'] = line
                remote_database['currentCommitMessage'] = line
                remote_database['committer'] = commit_to_push['committer']

    commit_to_push['tree'] = push_tree(tree_hash, '.', remote_database)
    for parent in parents:
        parent_cid = push_commit(parent, remote_commit_hash, remote_commit_cid, remote_database)
        commit_to_push['parents'].append(parent_cid)

    commit_cid = push_data_to_storage(commit_to_push)
    return commit_cid


def push_data_to_storage(data):
    client = getStorageClient()
    time_to_sleep = 12
    while True:
        try:
            cid = client.add_json(data)
            break
        except:
            time.sleep(time_to_sleep)
            time_to_sleep += 2
            print(f'Due to too many requests, we will have to wait for {time_to_sleep} seconds')
    return cid