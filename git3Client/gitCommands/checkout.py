from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.utils.utils import list_files_in_dir, get_repo_root_path

def checkout(command):
    """
    Checkout or create a new branch
    """
    if command is None:
        print('Just a simple checkout')
    else:
        print('Creating a new branch')
    # """Add all file paths to git index."""
    # try:
    #     repo_root_path = get_repo_root_path()
    # except NoRepositoryError as nre:
    #     print(nre)
    #     exit(1)

    # branches = list_files_in_dir('{}/.git/refs/heads'.format(repo_root_path))
    # branches.sort()
    # result = ''
    # for branch in branches:
    #     result += '* {}\n'.format(branch)
    # print(result)