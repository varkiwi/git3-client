import os

from git3Client.gitCommands.branch import get_active_branch

from git3Client.gitInternals.gitIndex import get_status_workspace, get_status_commit
from git3Client.gitInternals.gitCommit import read_commit_entries
from git3Client.gitInternals.gitObject import read_object
from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.utils.utils import get_repo_root_path, read_file, write_file, remove_files_from_repo

def print_checkout_error(changed, new, deleted):
    print('error: Your local changes to the following file would be overwritten by checkout:')
    if len(changed) is not 0:
        print('  {}'.format(changed[0]))
    elif len(new) is not 0:
        print('  {}'.format(new[0]))
    elif len(deleted) is not 0:
        print('  {}'.format(deleted[0]))
    print('Please commit your changes before you switch branches.')
    exit(1)

def checkout(branch):
    if branch is None:
        print('fatal: Branch name not given.')
        exit(1)
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)
    # check if branch exists
    if not os.path.isfile('{}/.git/refs/heads/{}'.format(repo_root_path, branch)):
        print('error: pathspec \'{}\' did not match any file(s) known to git3'.format(branch))
        exit(1)

    active_branch = get_active_branch()
    
    if active_branch == branch:
        print('Already on \'{}\''.format(branch))
        exit(0)
    
    current_commit_hash = read_file('{}/.git/refs/heads/{}'.format(repo_root_path, active_branch)).decode("utf-8").strip()
    target_commit_hash = read_file('{}/.git/refs/heads/{}'.format(repo_root_path, branch)).decode("utf-8").strip()
    
    if current_commit_hash == target_commit_hash:
        # switch branch when the hashes are the same.
        # we don't have to do anything else
        write_file('{}/.git/HEAD'.format(repo_root_path, branch), 'ref: refs/heads/{}'.format(branch), binary='')

    changed, new, deleted = get_status_workspace()
    if len(changed) is not 0 or len(new) is not 0 or len(deleted) is not 0:
        print_checkout_error(changed, new, deleted)
    
    changed, new, deleted = get_status_commit()
    if len(changed) is not 0 or len(new) is not 0 or len(deleted) is not 0:
        print_checkout_error(changed, new, deleted)

    commit_entries = read_commit_entries(target_commit_hash)

    # we are deleting all the files in the repo
    # there might be a better way, where we iterate over all of the files,
    # hash and compare the hashes. If there is no difference, leave as is, otherwise
    # overwrite. We would also need to check for files which are not in the index!
    # Maybe something at a later point in time :)
    remove_files_from_repo()

    for filename in commit_entries:
        object_type, data = read_object(commit_entries[filename])
        assert object_type == 'blob'
        write_file('{}/{}'.format(repo_root_path, filename), data.decode('utf-8'), binary='')

    #todo: update index
    #todo: update HEAD