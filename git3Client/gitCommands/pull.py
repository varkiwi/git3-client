import os

from git3Client.dlt.contract import get_factory_contract, get_facet_contract
from git3Client.dlt.repository import get_all_remote_commits

from git3Client.gitCommands.fetch import fetch
from git3Client.gitCommands.add import add

from git3Client.gitInternals.gitCommit import get_all_local_commits, unpack_files_of_commit, read_commit_entries
from git3Client.gitInternals.gitIndex import get_status_workspace, is_stage_empty
from git3Client.gitInternals.gitObject import read_object

from git3Client.utils.utils import read_repo_name, get_repo_root_path, read_file, write_file, get_active_branch_hash, get_current_branch_name, remove_files_from_repo

def pull():
    print('Pulling')
    changed, _, _ = get_status_workspace()
    # we are checking if there a changed files in the working copy or files staged which have not been committed.
    # if one case is true, pull won't be executed
    if len(changed) > 0 or not is_stage_empty():
        print("You have local changes. Add and commit those first")
        return

    repo_name = read_repo_name()
    if not repo_name.startswith('location:'):
        print('.git/name file has an error. Exiting...')
        return False
    tmp = repo_name.split('location:')[1].split(':')
    network = tmp[0].strip()
    user_key = tmp[1].strip()
    
    git_factory = get_factory_contract(network)
    repository = git_factory.functions.getRepository(user_key).call()
    
    if not repository[0]:
        print('No such repository')
        return
    git_repo_address = repository[2]

    activeBranch = get_current_branch_name()

    branch_contract = get_facet_contract("GitBranch", git_repo_address, network)

    branch = branch_contract.functions.getBranch(activeBranch).call()
    headCid = branch[1]

    remote_commits = get_all_remote_commits(headCid)

    #extract only the sha1 hash
    remote_commits_sha1 = [e['sha1'] for e in remote_commits]

    root_path = get_repo_root_path()
    local_commit = get_active_branch_hash()
    local_commits = get_all_local_commits(local_commit)

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
        # alright, we filtered what needs to be downloaded and unpacked
        # check clone on how to do that!
        remote_commits = list(filter(lambda x: x['sha1'] in remote_to_local_difference, remote_commits))
        repo_name = root_path.split('/')[-1]
        #unpack files from the newest commit
        first = True
        for commit in remote_commits:
            unpack_files_of_commit(root_path, commit, first)
            first = False
        refs_path = os.path.join(root_path, '.git', 'refs', 'heads', activeBranch)
        write_file(refs_path, (remote_commits[0]['sha1'] + '\n').encode())

        # we are deleting all the files in the repo
        # there might be a better way, where we iterate over all of the files,
        # hash and compare the hashes. If there is no difference, leave as is, otherwise
        # overwrite. We would also need to check for files which are not in the index!
        # Maybe something at a later point in time :)
        # Same at checkout
        commit_entries = read_commit_entries(remote_commits[0]['sha1'])
        remove_files_from_repo()

        files_to_add = []

        for filename in commit_entries:
            object_type, data = read_object(commit_entries[filename])
            assert object_type == 'blob'
            write_file('{}/{}'.format(root_path, filename), data.decode('utf-8'), binary='')
            files_to_add.append(filename)

        # remove index file
        os.remove('{}/.git/index'.format(root_path))
        add(files_to_add)
