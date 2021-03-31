from git3_client.dlt.contract import get_factory_contract, get_repository_contract
from git3_client.dlt.repository import get_all_remote_commits

from git3_client.gitInternals.gitCommit import get_all_local_commits
from git3_client.gitInternals.gitIndex import get_status, is_stage_empty

from git3_client.utils.utils import read_repo_name

def pull():
    print('Pulling')
    changed, _, _ = get_status()
    # we are checking if there a changed files in the working copy or files staged which have not been committed.
    # if one case is true, pull won't be executed
    if len(changed) > 0 or not is_stage_empty():
        print("You have local changes. Add and commit those first")
        return
    
    repo_name = read_repo_name()
    git_factory = get_factory_contract()
    git_repo_address = git_factory.functions.gitRepositories(repo_name).call()
    if git_repo_address == '0x0000000000000000000000000000000000000000':
        print('No such repository')
        return
    repo_contract = get_repository_contract(git_repo_address)
    headCid = repo_contract.functions.headCid().call()
    
    remote_commits = get_all_remote_commits(headCid, repo_name)
    #extract only the sha1 hash
    remote_commits_sha1 = [e['sha1'] for e in remote_commits]
    print(remote_commits_sha1)

    local_commits = get_all_local_commits()
    print(local_commits)
    if local_commits[0] == remote_commits_sha1[0]:
        print('Already up to date')
        return
    remote_to_local_difference = set(remote_commits_sha1) - set(local_commits)
    local_to_remote_difference = set(local_commits) - set(remote_commits_sha1)
    if len(local_to_remote_difference) == 0:
        print('We can download and unpack all of it :)')
        print(remote_to_local_difference)
    #print(local_to_remote_difference, len(local_to_remote_difference))
    #TODO: get all remote and local commits and get the difference
    #use the difference to know which commits and trees need to be downloaded
    #Go through the most recent commit, get the trees and files and merge those with the local files
    #Go throug all other commits and unpack the commits and trees