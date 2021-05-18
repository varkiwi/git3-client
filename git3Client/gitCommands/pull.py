import os

from git3Client.dlt.contract import get_factory_contract, get_repository_contract, get_facet_contract
from git3Client.dlt.repository import get_all_remote_commits

from git3Client.gitInternals.gitCommit import get_all_local_commits, unpack_files_of_commit
from git3Client.gitInternals.gitIndex import get_status, is_stage_empty

from git3Client.utils.utils import read_repo_name, get_repo_root_path, read_file, write_file

def pull():
    print('Pulling')
    changed, _, _ = get_status()
    # we are checking if there a changed files in the working copy or files staged which have not been committed.
    # if one case is true, pull won't be executed
    if len(changed) > 0 or not is_stage_empty():
        print("You have local changes. Add and commit those first")
        return
    
    repo_name = read_repo_name()
    if not repo_name.startswith('location:'):
        # Need to check if the return is handled by the calling function
        print('.git/name file has an error. Exiting...')
        return False
    user_key = repo_name.split('location:')[1].strip()
    
    git_factory = get_factory_contract()
    repository = git_factory.functions.getRepository(user_key).call()
    
    if not repository[0]:
        print('No such repository')
        return
    git_repo_address = repository[2]
    #repo_contract = get_repository_contract(git_repo_address)
    branch_contract = get_facet_contract("GitBranch", git_repo_address)
    branch = branch_contract.functions.getBranch('main').call()
    headCid = branch[1]
    # repo_contract = get_repository_contract(git_repo_address)
    # headCid = repo_contract.functions.headCid().call()
    
    remote_commits = get_all_remote_commits(headCid, repo_name)
    # print(remote_commits)
    #extract only the sha1 hash
    remote_commits_sha1 = [e['sha1'] for e in remote_commits]
    # print('Remote commits:', remote_commits_sha1)

    root_path = get_repo_root_path()
    #TODO: for branching this has to be resolved differently, through the HEAD file
    local_commit = read_file('/'.join([root_path, '.git/refs/heads/master'])).decode().strip()
    local_commits = get_all_local_commits(local_commit)
    # print('Local commits: ', local_commits)
    if local_commits[0] == remote_commits_sha1[0]:
        print('Already up to date')
        return

    remote_to_local_difference = set(remote_commits_sha1) - set(local_commits)
    local_to_remote_difference = set(local_commits) - set(remote_commits_sha1)
    
    if len(remote_to_local_difference) == 0 and len(local_to_remote_difference) > 0:
        print('You are ahead of remote branch')
        return
    elif len(remote_to_local_difference) == 0 and len(local_to_remote_difference) == 0:
        print('Nothing to pull')
        return
    elif len(local_to_remote_difference) == 0:
        print('We can download and unpack all of the following set :)')
        # alright, we filtered what needs to be downloaded and unpacked
        # check clone on how to do that!
        remote_commits = list(filter(lambda x: x['sha1'] in remote_to_local_difference, remote_commits))
        repo_name = root_path.split('/')[-1]
        #unpack files from the newest commit
        first = True
        for commit in remote_commits:
            unpack_files_of_commit(root_path, commit, first)
            first = False
        master_path = os.path.join(root_path, '.git', 'refs', 'heads', 'master')
        write_file(master_path, (remote_commits[0]['sha1'] + '\n').encode())

    ################################################
    #print(local_to_remote_difference, len(local_to_remote_difference))
    #TODO: get all remote and local commits and get the difference
    #use the difference to know which commits and trees need to be downloaded
    #Go through the most recent commit, get the trees and files and merge those with the local files
    #Go throug all other commits and unpack the commits and trees