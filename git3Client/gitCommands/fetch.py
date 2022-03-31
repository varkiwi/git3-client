import os

from git3Client.dlt.contract import get_factory_contract, get_facet_contract
from git3Client.dlt.repository import get_all_remote_commits

from git3Client.gitInternals.gitCommit import get_all_local_commits, unpack_files_of_commit

from git3Client.utils.utils import read_repo_name, get_active_branch_hash, get_repo_root_path, write_file, get_branch_hash, get_current_branch_name

def fetch(branchName):
    """
    Downloads commits and objects from the remote repository
    """
    repo_name = read_repo_name()
    if not repo_name.startswith('location:'):
        # Need to check if the return is handled by the calling function
        print('.git/name file has an error. Exiting...')
        return False
    tmp = repo_name.split('location:')[1].split(':')
    network = tmp[0].strip()
    user_key = tmp[1].strip()

    git_factory = get_factory_contract(network)
    active_branch = get_current_branch_name()

    repository = git_factory.functions.getRepository(user_key).call()

    if not repository[0]:
        print('No such repository')
        return

    git_repo_address = repository[2]
    
    branch_contract = get_facet_contract("GitBranch", git_repo_address, network)

    # fetch_data will contain tuples in the following format
    # (branch_name, head_cid, head_commit_sha1 of branch)
    fetch_data = []

    # if branchName is none, the user called git3 fetch
    # so we collect data from all branches
    if branchName is None:
        branches = branch_contract.functions.getBranchNames().call()
        for branch_name in branches:
            # returns tuple (bool, headcid)
            branch = branch_contract.functions.getBranch(branch_name).call()
            branch_commit_hash = get_branch_hash(branch_name)
            fetch_data.append((branch_name, branch[1], branch_commit_hash))
    else:
        # returns tuple (bool, headcid)
        branch = branch_contract.functions.getBranch(branchName).call()

        if not branch[1]:
            print('fatal: couldn\'t find remote ref {}'.format(branchName))
            return False

        branch_commit_hash = get_branch_hash(branch_name)
        fetch_data.append((branch_name, branch[1], branch_commit_hash))

    repo_root_path = get_repo_root_path()
    fetch_head_data = ''
    # get all remote commits
    for data in fetch_data:
        remote_commits = get_all_remote_commits(data[1])

        #extract only the sha1 hash
        remote_commits_sha1 = [e['sha1'] for e in remote_commits]

        local_commits = get_all_local_commits(data[2])

        if data[0] != active_branch:
            not_for_merge = 'not-for-merge'
        else:
            not_for_merge = ''

        # preparing FETCH_HEAD file content
        fetch_head_data = '{}{}\t{}\t{}\'{}\' of {}\n'.format(
            fetch_head_data,
            remote_commits_sha1[0],
            not_for_merge,
            'branch ',
            data[0],
            git_repo_address
        )

        # write the remote commit to the refs/remotes/origin/[branchName] file
        write_file(
            os.path.join(repo_root_path, '.git/refs/remotes/origin/', data[0]),
            '{}\n'.format(remote_commits_sha1[0]),
            '')

        # check if we have any local commits
        # if local_commits length is zero, there are no local commits for that particular branch
        # so we need to download those!
        # if the first sha1 are equal, we don't need to download anything
        if len(local_commits) > 0 and local_commits[0] == remote_commits_sha1[0]:
            continue

        remote_to_local_difference = set(remote_commits_sha1) - set(local_commits)

        # transfer the data from ipfs into git objects on the local machine
        for commit_hash in remote_to_local_difference:
            for commit in remote_commits:
                if commit['sha1'] == commit_hash:
                    unpack_files_of_commit(repo_root_path, commit, False)
  
    path = os.path.join(repo_root_path, '.git', 'FETCH_HEAD')
    write_file(path, fetch_head_data, '')
