import binascii, os

from git3_client.dlt.contract import get_factory_contract, get_repository_contract
from git3_client.dlt.repository import get_all_remote_commits
from git3_client.dlt.user import get_user_dlt_address

from git3_client.gitInternals.gitCommit import get_all_local_commits, unpack_files_of_tree

from git3_client.utils.utils import read_repo_name, get_local_master_hash, get_repo_root_path, write_file

def fetch():
    """
    Downloads commits and objects from the remote repository
    """
    git_factory = get_factory_contract()
    repo_name = read_repo_name()
    user_address = get_user_dlt_address()

    user_key = git_factory.functions.getUserRepoNameHash(user_address, repo_name).call()
    user_key = '0x{}'.format(binascii.hexlify(user_key).decode())
    repository = git_factory.functions.repositoryList(user_key).call()

    if not repository[0]:
        print('No such repository')
        return

    git_repo_address = repository[2]
    repo_contract = get_repository_contract(git_repo_address)

    branch = repo_contract.functions.branches('main').call()
    headCid = branch[1]
    
    remote_commits = get_all_remote_commits(headCid, repo_name)
    #extract only the sha1 hash
    remote_commits_sha1 = [e['sha1'] for e in remote_commits]

    local_sha1 = get_local_master_hash()
    local_commits = get_all_local_commits(local_sha1)
    if local_commits[0] == remote_commits_sha1[0]:
        return
    remote_to_local_difference = set(remote_commits_sha1) - set(local_commits)
    repo_root_path = get_repo_root_path()
    for commit_hash in remote_to_local_difference:
        for commit in remote_commits:
            if commit['sha1'] == commit_hash:
                unpack_files_of_commit(repo_root_path, commit, False)
    data = '{}\t\t{}\'{}\' of {}\n'.format(remote_commits_sha1[0], 'branch ', 'main', git_repo_address).encode()
    path = os.path.join(repo_root_path, '.git', 'FETCH_HEAD')
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    write_file(path, data)
    path = os.path.join(repo_root_path, '.git', 'refs/remote/origin/main')
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    write_file(path, remote_commits_sha1[0].encode())
