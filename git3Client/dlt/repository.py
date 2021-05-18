import binascii, os
import ipfshttpclient

from git3Client.dlt.contract import get_factory_contract, get_repository_contract, get_facet_contract
from git3Client.dlt.provider import get_web3_provider
from git3Client.dlt.user import get_user_dlt_address

from git3Client.gitInternals.gitObject import read_object
from git3Client.gitInternals.gitTree import read_tree
from git3Client.gitInternals.fileMode import GIT_NORMAL_FILE_MODE, GIT_TREE_MODE

from git3Client.utils.utils import read_repo_name, get_current_gas_price, get_private_key, get_repo_root_path

CHAINID = 80001
IPFS_CONNECTION = '/dns4/ipfs.infura.io/tcp/5001/https'
client = ipfshttpclient.connect(IPFS_CONNECTION)

def get_remote_cid_history():
    """
    Gets the full cid history of the repository and returns a list
    #TODO: Returns list?
    """
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    git_repo_address = git_factory.functions.gitRepositories(repo_name).call()
    repo_contract = get_repository_contract(git_repo_address)
    return repo_contract.functions.getCidHistory().call()

def push_new_cid(cid):
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    if not repo_name.startswith('location:'):
        # Need to check if the return is handled by the calling function
        print('.git/name file has an error. Exiting...')
        return False
    user_key = repo_name.split('location:')[1].strip()
    user_address = get_user_dlt_address()

    repository = git_factory.functions.getRepository(user_key).call()

    git_repo_address = repository[2]
    #repo_contract = get_repository_contract(git_repo_address)
    branch_contract = get_facet_contract("GitBranch", git_repo_address)
    w3 = get_web3_provider()

    # user_address = get_user_dlt_address()
    nonce = w3.eth.getTransactionCount(user_address)

    gas_price = get_current_gas_price()
    #create_push_tx = repo_contract.functions.push('main', cid).buildTransaction({
    create_push_tx = branch_contract.functions.push('main', cid).buildTransaction({
        'chainId': CHAINID,
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

#TODO: parameter repo_name can be removed I guess
def get_all_remote_commits(commit_cid, repo_name):
    """
    Gets all remote commits and returns those in a list
    """
    all_commits = []
    remote_object = client.get_json(commit_cid)
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
    user_key = repo_name.split('location:')[1].strip()

    w3 = get_web3_provider()
    if not w3.isConnected():
        #TODO: Throw an exception
        print('No connection. Establish a connection first')
        return False
    git_factory = get_factory_contract()
    # repoName = 'newRepo'
    # user_address = get_user_dlt_address()
    # user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    # user_key = '0x{}'.format(binascii.hexlify(user_key).decode())
    # print(user_key)
    return git_factory.functions.getRepository(user_key).call()[0]

def get_remote_master_hash():
    """
    Get commit hash of remote master branch, return CID or None if no remote commits.
    """
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    if not repo_name.startswith('location:'):
        return
    user_key = repo_name.split('location:')[1].strip()
    # user_address = get_user_dlt_address()

    # user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    # user_key = '0x{}'.format(binascii.hexlify(user_key).decode())
    repository = git_factory.functions.getRepository(user_key).call()
    
    if not repository[0]:
        print('No such repository')
        return
    git_repo_address = repository[2]
    branch_contract = get_facet_contract("GitBranch", git_repo_address)
    #TODO: Branch name
    branch = branch_contract.functions.getBranch('main').call()
    #repo_contract = get_repository_contract(git_repo_address)
    # headCid = repo_contract.functions.headCid().call()
    #branch = repo_contract.functions.branches('main').call()
    # check if the branch is active
    if not branch[0]:
        return None
    # if active, return head cid
    return branch[1]

def push_tree(tree_hash, folder_name):
    entries = read_tree(tree_hash)
    tree_entries = []
    for entry in entries:
        if entry[0] == GIT_NORMAL_FILE_MODE:
            obj_type, blob = read_object(entry[2])
            assert obj_type == 'blob'
            blob_to_push = {
                'type': 'blob',
                'content': blob.decode(),
                'sha1': entry[2]
            }
            cid = client.add_json(blob_to_push)
            print('Pushing {} to IPFS'.format(entry[1]))
            tree_entries.append({
                'mode': entry[0],
                'name': entry[1],
                'cid': cid
            })
        elif entry[0] == GIT_TREE_MODE:
            cid = push_tree(entry[2], entry[1])
            tree_entries.append({
                'mode': entry[0],
                'name': entry[1],
                'cid': cid
            })
    tree_to_push = {
        'type': 'tree',
        'entries': tree_entries,
        'name': folder_name,
        'sha1': tree_hash
    }
    cid = client.add_json(tree_to_push)
    return cid

def push_commit(commit_hash, remote_commit_hash, remote_commit_cid):
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
    for line in lines:
        if line.startswith('tree '):
            tree_hash = line[5:45]
            commit_to_push['tree'] = push_tree(tree_hash, '.')
        elif line.startswith('parent '):
            parent_cid = push_commit(line[7:47], remote_commit_hash, remote_commit_cid)
            commit_to_push['parents'].append(parent_cid)
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
    commit_cid = client.add_json(commit_to_push)
    return commit_cid
