import os

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.utils.utils import get_repo_root_path

def checkout(branch):
    if branch is None:
        print('fatal: Branch name not given.')
        exit(1)
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)
    
    if not os.path.isfile('{}/.git/refs/heads/{}'.format(repo_root_path, branch)):
        print('error: pathspec \'{}\' did not match any file(s) known to git3'.format(branch))
        exit(1)