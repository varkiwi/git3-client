import os, operator

from git3Client.exceptions.NoRepositoryError import NoRepositoryError

from git3Client.gitInternals.fileMode import GIT_NORMAL_FILE_MODE
from git3Client.gitInternals.gitIndex import read_index, write_index
from git3Client.gitInternals.gitObject import hash_object
from git3Client.gitInternals.IndexEntry import IndexEntry

from git3Client.utils.utils import list_files_in_dir, get_repo_root_path, read_file

def branch():
    """Add all file paths to git index."""
    try:
        repo_root_path = get_repo_root_path()
    except NoRepositoryError as nre:
        print(nre)
        exit(1)

    branches = list_files_in_dir('{}/.git/refs/heads'.format(repo_root_path))
    branches.sort()
    result = ''
    for branch in branches:
        result += '* {}\n'.format(branch)
    print(result)