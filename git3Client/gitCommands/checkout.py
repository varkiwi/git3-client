import os

from git3Client.gitCommands.branch import get_active_branch

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.utils.utils import get_repo_root_path, read_file, write_file

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